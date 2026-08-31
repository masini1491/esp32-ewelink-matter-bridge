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


class NativeDnsSdBackend:
    """Thin native binding; callbacks and cancel handles remain alive until completion."""

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
        completed = threading.Event()
        outcome = {"status": None, "service": None}

        @ResolveCallback
        def callback(status, _context, instance):
            try:
                outcome["status"] = status
                if status == 0 and instance:
                    native = instance.contents
                    count = min(native.dwPropertyCount, MAX_TXT_PROPERTIES)
                    txt = {native.keys[index]: native.values[index] for index in range(count)}
                    outcome["service"] = ResolvedService(native.pszInstanceName, native.wPort, txt)
            finally:
                if instance:
                    self.api.DnsServiceFreeInstance(instance)
                completed.set()

        request = DnsServiceResolveRequest(1, 0, service_name, callback, None)
        cancel = DnsServiceCancel()
        status = self.api.DnsServiceResolve(ctypes.byref(request), ctypes.byref(cancel))
        if status != DNS_REQUEST_PENDING:
            raise OSError(status, "DnsServiceResolve did not become pending")
        if not completed.wait(timeout):
            cancel_status = self.api.DnsServiceResolveCancel(ctypes.byref(cancel))
            if cancel_status not in (0, ERROR_CANCELLED):
                raise OSError(cancel_status, "DnsServiceResolveCancel failed")
            if not completed.wait(CANCEL_GRACE_SECONDS):
                raise RuntimeError("resolve callback did not arrive after cancellation")
        if outcome["status"] != 0 or outcome["service"] is None:
            raise RuntimeError("resolve did not return a service")
        return _bounded_service(outcome["service"])


def native_api_available():
    if os.name != "nt":
        return False
    try:
        NativeDnsSdBackend()
    except OSError:
        return False
    return True


def observe(backend, timeout):
    """Collect bounded resolved services through an injected DNS-SD backend."""
    _require_timeout(timeout)
    started = time.monotonic()
    names, truncated = backend.browse(SERVICE_TYPE, timeout)
    if not isinstance(names, list):
        raise ValueError("browse backend returned malformed names")
    services = []
    for name in names[:MAX_SERVICES]:
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError("resolve budget exhausted")
        services.append(_bounded_service(backend.resolve(name, remaining)))
    return machine_result(services, truncated or len(names) > MAX_SERVICES)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args()
    try:
        print(json.dumps(observe(NativeDnsSdBackend(), args.timeout), sort_keys=True, separators=(",", ":")))
    except (OSError, RuntimeError, TimeoutError, ValueError) as error:
        print(json.dumps({"status": "OBSERVER_ERROR", "reason": str(error)}, sort_keys=True, separators=(",", ":")))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
