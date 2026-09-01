#!/usr/bin/env python3
"""Bounded Windows DNS-SD observer for future D3 use.

This module binds the Windows 10+ ``dnsapi.dll`` DNS-SD APIs.  It has no raw
DNS packet implementation and must only be launched for live use through the
existing D2A direct-child runner after separate authorization.
"""
import argparse
import ctypes
import json
import os
import threading
import time
import sys
from ctypes import wintypes
from dataclasses import dataclass

SERVICE_TYPE = "_ewelink._tcp.local."
MAX_TIMEOUT_SECONDS = 30
MAX_SERVICES = 8
MAX_TXT_PROPERTIES = 32
MAX_TXT_KEY_CHARS = 128
MAX_TXT_VALUE_CHARS = 4096
MAX_TXT_TOTAL_CHARS = 16 * 1024
DNS_REQUEST_PENDING = 9506
ERROR_CANCELLED = 1223
DNS_TYPE_PTR = 12
DNS_FREE_RECORD_LIST = 1
CANCEL_GRACE_SECONDS = 2
MIN_RESOLVE_SECONDS = 1
PROCESS_LIFETIME_RESOLVES = []


class DnsServiceCancel(ctypes.Structure):
    _fields_ = [("reserved", ctypes.c_void_p)]


class DnsPtrData(ctypes.Structure):
    _fields_ = [("pNameHost", ctypes.c_wchar_p)]


class DnsRecordData(ctypes.Union):
    _fields_ = [("PTR", DnsPtrData), ("raw", ctypes.c_ubyte * ctypes.sizeof(ctypes.c_void_p))]


class DnsRecord(ctypes.Structure):
    pass


DnsRecord._fields_ = [
    ("pNext", ctypes.POINTER(DnsRecord)),
    ("pName", ctypes.c_wchar_p),
    ("wType", wintypes.WORD),
    ("wDataLength", wintypes.WORD),
    ("flags", wintypes.DWORD),
    ("dwTtl", wintypes.DWORD),
    ("dwReserved", wintypes.DWORD),
    ("Data", DnsRecordData),
]


BrowseCallback = ctypes.WINFUNCTYPE(None, wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(DnsRecord))


class DnsServiceBrowseRequest(ctypes.Structure):
    _fields_ = [
        ("Version", wintypes.ULONG),
        ("InterfaceIndex", wintypes.ULONG),
        ("QueryName", ctypes.c_wchar_p),
        ("pBrowseCallback", BrowseCallback),
        ("pQueryContext", ctypes.c_void_p),
    ]


class DnsServiceInstance(ctypes.Structure):
    _fields_ = [
        ("pszInstanceName", ctypes.c_wchar_p),
        ("pszHostName", ctypes.c_wchar_p),
        ("ip4Address", ctypes.c_void_p),
        ("ip6Address", ctypes.c_void_p),
        ("wPort", wintypes.WORD),
        ("wPriority", wintypes.WORD),
        ("wWeight", wintypes.WORD),
        ("dwPropertyCount", wintypes.DWORD),
        ("keys", ctypes.POINTER(ctypes.c_wchar_p)),
        ("values", ctypes.POINTER(ctypes.c_wchar_p)),
        ("dwInterfaceIndex", wintypes.DWORD),
    ]


ResolveCallback = ctypes.WINFUNCTYPE(None, wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(DnsServiceInstance))


class DnsServiceResolveRequest(ctypes.Structure):
    _fields_ = [
        ("Version", wintypes.ULONG),
        ("InterfaceIndex", wintypes.ULONG),
        ("QueryName", ctypes.c_wchar_p),
        ("pResolveCompletionCallback", ResolveCallback),
        ("pQueryContext", ctypes.c_void_p),
    ]


@dataclass(frozen=True)
class ResolvedService:
    instance_name: str
    port: int
    txt: dict


def _require_timeout(timeout):
    if not 0 < timeout <= MAX_TIMEOUT_SECONDS:
        raise ValueError("timeout must be greater than zero and within the hard limit")


def _browse_budget(timeout):
    """Reserve both native cancellation grace periods and a useful resolve slice."""
    _require_timeout(timeout)
    available = timeout - (2 * CANCEL_GRACE_SECONDS) - MIN_RESOLVE_SECONDS
    if available <= 0:
        raise ValueError("timeout is too short for bounded browse and resolve")
    return min(timeout / 2, available)


def _require_service_type(service_type):
    if service_type != SERVICE_TYPE:
        raise ValueError("only _ewelink._tcp.local. is authorized")


def _bounded_service(service):
    if not isinstance(service, ResolvedService) or not isinstance(service.instance_name, str):
        raise ValueError("malformed resolved service")
    if not 1 <= service.port <= 65535 or not isinstance(service.txt, dict):
        raise ValueError("malformed resolved service")
    if len(service.txt) > MAX_TXT_PROPERTIES:
        raise ValueError("TXT property count exceeds bound")
    total = 0
    safe_txt = {}
    for key, value in service.txt.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("TXT keys and values must be strings")
        if len(key) > MAX_TXT_KEY_CHARS or len(value) > MAX_TXT_VALUE_CHARS:
            raise ValueError("TXT field exceeds bound")
        total += len(key) + len(value)
        if total > MAX_TXT_TOTAL_CHARS:
            raise ValueError("TXT total exceeds bound")
        safe_txt[key] = value
    return ResolvedService(service.instance_name, service.port, safe_txt)


def d1_capture(service):
    """Return one raw, D1-compatible capture for D2A-private stdout only."""
    service = _bounded_service(service)
    return {"service": {"name": service.instance_name, "type": SERVICE_TYPE, "port": service.port, "txt": service.txt}}


def machine_result(services, truncated=False):
    captures = [d1_capture(service) for service in services[:MAX_SERVICES]]
    return {"schema_version": 1, "service_type": SERVICE_TYPE, "captures": captures, "truncated": bool(truncated)}


def _service_from_native_instance(native):
    if native.dwPropertyCount > MAX_TXT_PROPERTIES:
        raise ValueError("TXT property count exceeds bound")
    if native.dwPropertyCount and (not native.keys or not native.values):
        raise ValueError("TXT property arrays are missing")
    txt = {native.keys[index]: native.values[index] for index in range(native.dwPropertyCount)}
    return _bounded_service(ResolvedService(native.pszInstanceName, native.wPort, txt))


class ResolveOperation:
    """Own one native resolve's ctypes state until the observer process exits."""

    def __init__(self, api, service_name):
        self.api = api
        self.service_name = service_name
        self.first_result = None
        self.first_result_event = threading.Event()
        self.callback_count = 0
        self.ignored_callback_count = 0
        self.rejected_callback_count = 0
        self.cancel_attempted = False
        self.cancel_status = None
        self.cancel = DnsServiceCancel()
        self.callback = ResolveCallback(self._on_callback)
        self.request = DnsServiceResolveRequest(1, 0, service_name, self.callback, None)

    def _on_callback(self, status, _context, instance):
        self.callback_count += 1
        try:
            if status != 0 or not instance:
                self.ignored_callback_count += 1
                return
            candidate = _service_from_native_instance(instance.contents)
            if self.first_result is None:
                self.first_result = candidate
                self.first_result_event.set()
            else:
                self.ignored_callback_count += 1
        except (TypeError, ValueError):
            self.rejected_callback_count += 1
        finally:
            if instance:
                self.api.DnsServiceFreeInstance(instance)

    def cancel_once(self):
        if not self.cancel_attempted:
            self.cancel_attempted = True
            self.cancel_status = self.api.DnsServiceResolveCancel(ctypes.byref(self.cancel))
        return self.cancel_status


class NativeDnsSdBackend:
    """Thin native binding; resolve ctypes objects remain alive until process exit."""

    def __init__(self):
        if os.name != "nt":
            raise OSError("Windows DNS-SD is only available on Windows")
        self.api = ctypes.WinDLL("dnsapi.dll", use_last_error=True)
        self.api.DnsServiceBrowse.argtypes = [ctypes.POINTER(DnsServiceBrowseRequest), ctypes.POINTER(DnsServiceCancel)]
        self.api.DnsServiceBrowse.restype = wintypes.DWORD
        self.api.DnsServiceBrowseCancel.argtypes = [ctypes.POINTER(DnsServiceCancel)]
        self.api.DnsServiceBrowseCancel.restype = wintypes.DWORD
        self.api.DnsServiceResolve.argtypes = [ctypes.POINTER(DnsServiceResolveRequest), ctypes.POINTER(DnsServiceCancel)]
        self.api.DnsServiceResolve.restype = wintypes.DWORD
        self.api.DnsServiceResolveCancel.argtypes = [ctypes.POINTER(DnsServiceCancel)]
        self.api.DnsServiceResolveCancel.restype = wintypes.DWORD
        self.api.DnsRecordListFree.argtypes = [ctypes.POINTER(DnsRecord), wintypes.DWORD]
        self.api.DnsRecordListFree.restype = None
        self.api.DnsServiceFreeInstance.argtypes = [ctypes.POINTER(DnsServiceInstance)]
        self.api.DnsServiceFreeInstance.restype = None

    def browse(self, service_type, timeout):
        _require_service_type(service_type)
        _require_timeout(timeout)
        discovered = []
        cancelled = threading.Event()

        @BrowseCallback
        def callback(status, _context, records):
            try:
                if status == 0 and records:
                    current = records
                    while current and len(discovered) < MAX_SERVICES:
                        record = current.contents
                        if record.wType == DNS_TYPE_PTR and record.Data.PTR.pNameHost:
                            discovered.append(record.Data.PTR.pNameHost)
                        current = record.pNext
                elif status == ERROR_CANCELLED:
                    cancelled.set()
            finally:
                if records:
                    self.api.DnsRecordListFree(records, DNS_FREE_RECORD_LIST)

        request = DnsServiceBrowseRequest(1, 0, service_type, callback, None)
        cancel = DnsServiceCancel()
        status = self.api.DnsServiceBrowse(ctypes.byref(request), ctypes.byref(cancel))
        if status != DNS_REQUEST_PENDING:
            raise OSError(status, "DnsServiceBrowse did not become pending")
        time.sleep(timeout)
        cancel_status = self.api.DnsServiceBrowseCancel(ctypes.byref(cancel))
        if cancel_status not in (0, ERROR_CANCELLED):
            raise OSError(cancel_status, "DnsServiceBrowseCancel failed")
        if not cancelled.wait(CANCEL_GRACE_SECONDS):
            raise RuntimeError("browse cancellation callback did not arrive")
        return discovered[:MAX_SERVICES], len(discovered) >= MAX_SERVICES

    def resolve(self, service_name, timeout):
        _require_timeout(timeout)
        operation = ResolveOperation(self.api, service_name)
        PROCESS_LIFETIME_RESOLVES.append(operation)
        status = self.api.DnsServiceResolve(ctypes.byref(operation.request), ctypes.byref(operation.cancel))
        if status != DNS_REQUEST_PENDING:
            raise OSError(status, "DnsServiceResolve did not become pending")
        if not operation.first_result_event.wait(timeout):
            cancel_status = operation.cancel_once()
            if cancel_status not in (0, ERROR_CANCELLED):
                raise OSError(cancel_status, "DnsServiceResolveCancel failed")
            raise TimeoutError("resolve did not produce an accepted result before deadline")
        return operation.first_result


def native_api_available():
    if os.name != "nt":
        return False
    try:
        NativeDnsSdBackend()
    except OSError:
        return False
    return True


def observe(backend, timeout, clock=time.monotonic):
    """Collect bounded resolved services through an injected DNS-SD backend."""
    browse_timeout = _browse_budget(timeout)
    deadline = clock() + timeout
    names, truncated = backend.browse(SERVICE_TYPE, browse_timeout)
    if not isinstance(names, list):
        raise ValueError("browse backend returned malformed names")
    if not names:
        return machine_result([], truncated)
    resolve_timeout = deadline - clock() - CANCEL_GRACE_SECONDS
    if resolve_timeout <= 0:
        raise TimeoutError("resolve budget exhausted")
    service = _bounded_service(backend.resolve(names[0], resolve_timeout))
    if clock() > deadline:
        raise TimeoutError("resolve exceeded overall deadline")
    return machine_result([service], truncated or len(names) > 1)


def _write_and_hard_exit(payload, code, stream=None, exit_func=os._exit):
    """Flush a terminal machine result before bypassing interpreter teardown."""
    if stream is None:
        stream = sys.stdout
    stream.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    stream.flush()
    exit_func(code)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args()
    try:
        result = observe(NativeDnsSdBackend(), args.timeout)
    except (OSError, RuntimeError, TimeoutError, ValueError) as error:
        _write_and_hard_exit({"status": "OBSERVER_ERROR", "reason": str(error)}, 2)
        raise AssertionError("hard error exit returned unexpectedly")
    _write_and_hard_exit(result, 0)
    raise AssertionError("hard success exit returned unexpectedly")


if __name__ == "__main__":
    raise SystemExit(main())
