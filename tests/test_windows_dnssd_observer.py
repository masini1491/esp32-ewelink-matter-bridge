import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
import windows_dnssd_observer as observer
from ewelink_capture_analyzer import analyze


class FakeDnsSdBackend:
    def __init__(self, names, resolved):
        self.names = names
        self.resolved = resolved
        self.browse_calls = []
        self.resolve_calls = []

    def browse(self, service_type, timeout):
        self.browse_calls.append((service_type, timeout))
        return self.names, False

    def resolve(self, name, timeout):
        self.resolve_calls.append((name, timeout))
        return self.resolved[name]


class WindowsDnsSdObserverTests(unittest.TestCase):
    def test_native_symbols_and_abi_are_available(self):
        self.assertTrue(observer.native_api_available())
        self.assertEqual(ctypes_size(observer.DnsServiceCancel), ctypes_size_pointer())
        self.assertEqual(observer.DnsServiceBrowseRequest.Version.offset, 0)
        self.assertEqual(observer.DnsServiceResolveRequest.Version.offset, 0)

    def test_synthetic_browse_resolve_shapes_d1_compatible_capture(self):
        service = observer.ResolvedService("eWeLink-synthetic._ewelink._tcp.local.", 8081, {"encrypt": "1", "id": "SYNTHETIC-ID", "data1": "cipher"})
        backend = FakeDnsSdBackend([service.instance_name], {service.instance_name: service})
        result = observer.observe(backend, 5)
        self.assertEqual(backend.browse_calls[0][0], observer.SERVICE_TYPE)
        self.assertEqual(result["service_type"], observer.SERVICE_TYPE)
        self.assertEqual(len(result["captures"]), 1)
        sanitized = analyze(result["captures"][0])
        serialized = json.dumps(sanitized, sort_keys=True)
        self.assertEqual(sanitized["classification"], "ENCRYPTED")
        self.assertNotIn("SYNTHETIC-ID", serialized)
        self.assertNotIn("cipher", serialized.lower())

    def test_multiple_services_are_bounded(self):
        services = [observer.ResolvedService(f"eWeLink-{index}._ewelink._tcp.local.", 8081, {}) for index in range(observer.MAX_SERVICES + 2)]
        backend = FakeDnsSdBackend([item.instance_name for item in services], {item.instance_name: item for item in services})
        result = observer.observe(backend, 5)
        self.assertEqual(len(result["captures"]), observer.MAX_SERVICES)
        self.assertTrue(result["truncated"])

    def test_bounds_and_fixed_service_scope_fail_closed(self):
        with self.assertRaises(ValueError):
            observer._require_service_type("_http._tcp.local.")
        with self.assertRaises(ValueError):
            observer._require_timeout(31)
        with self.assertRaises(ValueError):
            observer.d1_capture(observer.ResolvedService("eWeLink.invalid", 8081, {"data1": "x" * (observer.MAX_TXT_VALUE_CHARS + 1)}))

    def test_synthetic_timeout_budget_prevents_unbounded_resolve(self):
        service = observer.ResolvedService("eWeLink-synthetic._ewelink._tcp.local.", 8081, {})

        class ExpiredBackend(FakeDnsSdBackend):
            def browse(self, service_type, timeout):
                return [service.instance_name], False

        original = observer.time.monotonic
        ticks = iter((100, 102))
        observer.time.monotonic = lambda: next(ticks)
        try:
            backend = ExpiredBackend([], {service.instance_name: service})
            with self.assertRaises(TimeoutError):
                observer.observe(backend, 1)
        finally:
            observer.time.monotonic = original

    def test_synthetic_native_cancel_callbacks_are_bounded(self):
        class FakeNativeApi:
            def __init__(self):
                self.browse_cancelled = False
                self.resolve_cancelled = False

            def DnsServiceBrowse(self, request, _cancel):
                self.browse_callback = request._obj.pBrowseCallback
                return observer.DNS_REQUEST_PENDING

            def DnsServiceBrowseCancel(self, _cancel):
                self.browse_cancelled = True
                self.browse_callback(observer.ERROR_CANCELLED, None, None)
                return 0

            def DnsServiceResolve(self, request, _cancel):
                self.resolve_callback = request._obj.pResolveCompletionCallback
                return observer.DNS_REQUEST_PENDING

            def DnsServiceResolveCancel(self, _cancel):
                self.resolve_cancelled = True
                self.resolve_callback(observer.ERROR_CANCELLED, None, None)
                return 0

            def DnsRecordListFree(self, _records, _kind):
                return None

            def DnsServiceFreeInstance(self, _instance):
                return None

        api = FakeNativeApi()
        backend = observer.NativeDnsSdBackend.__new__(observer.NativeDnsSdBackend)
        backend.api = api
        original_sleep = observer.time.sleep
        observer.time.sleep = lambda _timeout: None
        try:
            names, truncated = backend.browse(observer.SERVICE_TYPE, 0.1)
        finally:
            observer.time.sleep = original_sleep
        self.assertEqual(names, [])
        self.assertFalse(truncated)
        self.assertTrue(api.browse_cancelled)
        with self.assertRaises(RuntimeError):
            backend.resolve("eWeLink-synthetic._ewelink._tcp.local.", 0.01)
        self.assertTrue(api.resolve_cancelled)

    def test_machine_result_never_contains_host_or_address_fields(self):
        result = observer.machine_result([observer.ResolvedService("eWeLink-synthetic._ewelink._tcp.local.", 8081, {"encrypt": "0"})])
        capture = result["captures"][0]
        self.assertEqual(set(capture["service"]), {"name", "type", "port", "txt"})
        self.assertNotIn("host", json.dumps(result))
        self.assertNotIn("address", json.dumps(result))


def ctypes_size(structure):
    import ctypes
    return ctypes.sizeof(structure)


def ctypes_size_pointer():
    import ctypes
    return ctypes.sizeof(ctypes.c_void_p)


if __name__ == "__main__":
    unittest.main()
