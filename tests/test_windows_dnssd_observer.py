import json
import subprocess
import sys
import tempfile
import unittest
import weakref
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
import windows_dnssd_observer as observer
import bounded_result_runner as runner
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
    def setUp(self):
        observer.PROCESS_LIFETIME_RESOLVES.clear()

    def tearDown(self):
        observer.PROCESS_LIFETIME_RESOLVES.clear()

    def test_native_symbols_and_abi_are_available(self):
        self.assertTrue(observer.native_api_available())
        self.assertEqual(ctypes_size(observer.DnsServiceCancel), ctypes_size_pointer())
        self.assertEqual(observer.DnsServiceBrowseRequest.Version.offset, 0)
        self.assertEqual(observer.DnsServiceResolveRequest.Version.offset, 0)

    def test_synthetic_browse_resolve_shapes_d1_compatible_capture(self):
        service = observer.ResolvedService("eWeLink-synthetic._ewelink._tcp.local.", 8081, {"encrypt": "1", "id": "SYNTHETIC-ID", "data1": "cipher"})
        backend = FakeDnsSdBackend([service.instance_name], {service.instance_name: service})
        result = observer.observe(backend, 10)
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
        result = observer.observe(backend, 10)
        self.assertEqual(len(result["captures"]), 1)
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
        ticks = iter((100, 106))
        observer.time.monotonic = lambda: next(ticks)
        try:
            backend = ExpiredBackend([], {service.instance_name: service})
            with self.assertRaises(TimeoutError):
                observer.observe(backend, 6, clock=observer.time.monotonic)
        finally:
            observer.time.monotonic = original

    def test_browse_consumes_time_and_leaves_positive_resolve_budget(self):
        service = observer.ResolvedService("eWeLink-synthetic._ewelink._tcp.local.", 8081, {"encrypt": "0", "data1": "{", "data2": "}", "data3": "", "data4": ""})

        class Clock:
            now = 100.0

            def read(self):
                return self.now

        class TimedBackend(FakeDnsSdBackend):
            def browse(self, service_type, timeout):
                self.browse_calls.append((service_type, timeout))
                clock.now += 3
                return [service.instance_name], False

            def resolve(self, name, timeout):
                self.resolve_calls.append((name, timeout))
                clock.now += 1
                return self.resolved[name]

        clock = Clock()
        backend = TimedBackend([], {service.instance_name: service})
        result = observer.observe(backend, 10, clock.read)
        self.assertGreater(backend.resolve_calls[0][1], 0)
        self.assertLessEqual(clock.read(), 110)
        self.assertEqual(analyze(result["captures"][0])["classification"], "PLAINTEXT")

    def test_full_browse_budget_fails_closed_before_resolve(self):
        service = observer.ResolvedService("eWeLink-synthetic._ewelink._tcp.local.", 8081, {})

        class Clock:
            now = 100.0

            def read(self):
                return self.now

        class ExhaustingBackend(FakeDnsSdBackend):
            def browse(self, service_type, timeout):
                clock.now += 10
                return [service.instance_name], False

        clock = Clock()
        backend = ExhaustingBackend([], {service.instance_name: service})
        with self.assertRaises(TimeoutError):
            observer.observe(backend, 10, clock.read)
        self.assertEqual(backend.resolve_calls, [])

    def test_multiple_services_resolve_once_within_overall_deadline(self):
        services = [observer.ResolvedService(f"eWeLink-{index}._ewelink._tcp.local.", 8081, {}) for index in range(2)]

        class Clock:
            now = 100.0

            def read(self):
                return self.now

        class TimedBackend(FakeDnsSdBackend):
            def browse(self, service_type, timeout):
                clock.now += 3
                return self.names, False

            def resolve(self, name, timeout):
                self.resolve_calls.append((name, timeout))
                clock.now += 1
                return self.resolved[name]

        clock = Clock()
        backend = TimedBackend([item.instance_name for item in services], {item.instance_name: item for item in services})
        result = observer.observe(backend, 10, clock.read)
        self.assertEqual(len(backend.resolve_calls), 1)
        self.assertTrue(result["truncated"])
        self.assertLessEqual(clock.read(), 110)

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
        with self.assertRaises(TimeoutError):
            backend.resolve("eWeLink-synthetic._ewelink._tcp.local.", 0.01)
        self.assertTrue(api.resolve_cancelled)

    def test_first_result_survives_late_and_duplicate_callbacks(self):
        class FakeNativeApi:
            def DnsServiceResolve(self, request, _cancel):
                self.callback = request._obj.pResolveCompletionCallback
                self.first_name = ctypes.create_unicode_buffer("eWeLink-first._ewelink._tcp.local.")
                first = observer.DnsServiceInstance()
                first.pszInstanceName = ctypes.cast(self.first_name, ctypes.c_wchar_p)
                first.wPort = 8081
                self.callback(0, None, ctypes.pointer(first))
                return observer.DNS_REQUEST_PENDING

            def DnsServiceResolveCancel(self, _cancel):
                return 0

            def DnsServiceFreeInstance(self, _instance):
                return None

            def late_success(self, name):
                name_buffer = ctypes.create_unicode_buffer(name)
                late = observer.DnsServiceInstance()
                late.pszInstanceName = ctypes.cast(name_buffer, ctypes.c_wchar_p)
                late.wPort = 8082
                self.callback(0, None, ctypes.pointer(late))

        import ctypes
        api = FakeNativeApi()
        backend = observer.NativeDnsSdBackend.__new__(observer.NativeDnsSdBackend)
        backend.api = api
        accepted = backend.resolve("eWeLink-first._ewelink._tcp.local.", 1)
        operation = observer.PROCESS_LIFETIME_RESOLVES[-1]
        api.late_success("eWeLink-second._ewelink._tcp.local.")
        api.late_success("eWeLink-third._ewelink._tcp.local.")
        self.assertEqual(accepted.instance_name, "eWeLink-first._ewelink._tcp.local.")
        self.assertIs(operation.first_result, accepted)
        self.assertEqual(operation.callback_count, 3)
        self.assertEqual(operation.ignored_callback_count, 2)

    def test_timeout_cancel_keeps_operation_alive_for_late_callback(self):
        class FakeNativeApi:
            def DnsServiceResolve(self, request, _cancel):
                self.callback = request._obj.pResolveCompletionCallback
                return observer.DNS_REQUEST_PENDING

            def DnsServiceResolveCancel(self, _cancel):
                self.cancelled = True
                return 0

            def DnsServiceFreeInstance(self, _instance):
                return None

        import ctypes
        api = FakeNativeApi()
        api.cancelled = False
        backend = observer.NativeDnsSdBackend.__new__(observer.NativeDnsSdBackend)
        backend.api = api
        with self.assertRaises(TimeoutError):
            backend.resolve("eWeLink-timeout._ewelink._tcp.local.", 0.01)
        operation = observer.PROCESS_LIFETIME_RESOLVES[-1]
        self.assertTrue(api.cancelled)
        self.assertTrue(operation.cancel_attempted)
        name_buffer = ctypes.create_unicode_buffer("eWeLink-late._ewelink._tcp.local.")
        late = observer.DnsServiceInstance()
        late.pszInstanceName = ctypes.cast(name_buffer, ctypes.c_wchar_p)
        late.wPort = 8081
        api.callback(0, None, ctypes.pointer(late))
        self.assertEqual(operation.first_result.instance_name, "eWeLink-late._ewelink._tcp.local.")

    def test_malformed_late_callback_is_ignored_and_registry_is_strong(self):
        class FakeNativeApi:
            def DnsServiceResolve(self, request, _cancel):
                self.callback = request._obj.pResolveCompletionCallback
                return observer.DNS_REQUEST_PENDING

            def DnsServiceResolveCancel(self, _cancel):
                return 0

            def DnsServiceFreeInstance(self, _instance):
                return None

        import ctypes
        api = FakeNativeApi()
        backend = observer.NativeDnsSdBackend.__new__(observer.NativeDnsSdBackend)
        backend.api = api
        with self.assertRaises(TimeoutError):
            backend.resolve("eWeLink-timeout._ewelink._tcp.local.", 0.01)
        operation = observer.PROCESS_LIFETIME_RESOLVES[-1]
        ref = weakref.ref(operation)
        malformed = observer.DnsServiceInstance()
        malformed.dwPropertyCount = observer.MAX_TXT_PROPERTIES + 1
        api.callback(0, None, ctypes.pointer(malformed))
        del operation
        self.assertIsNotNone(ref())
        self.assertIsNotNone(ref().callback)
        self.assertIsNotNone(ref().request)
        self.assertIsNotNone(ref().cancel)
        self.assertEqual(ref().rejected_callback_count, 1)

    def test_native_txt_property_count_over_bound_fails_closed(self):
        native = observer.DnsServiceInstance()
        native.dwPropertyCount = observer.MAX_TXT_PROPERTIES + 1
        with self.assertRaises(ValueError):
            observer._service_from_native_instance(native)

    def test_machine_result_never_contains_host_or_address_fields(self):
        result = observer.machine_result([observer.ResolvedService("eWeLink-synthetic._ewelink._tcp.local.", 8081, {"encrypt": "0"})])
        capture = result["captures"][0]
        self.assertEqual(set(capture["service"]), {"name", "type", "port", "txt"})
        self.assertNotIn("host", json.dumps(result))
        self.assertNotIn("address", json.dumps(result))

    def test_terminal_hard_exit_flushes_without_clearing_resolve_registry(self):
        class TrackingStream:
            def __init__(self):
                self.output = ""
                self.flushed = False

            def write(self, text):
                self.output += text

            def flush(self):
                self.flushed = True

        exit_codes = []
        stream = TrackingStream()
        marker = object()
        observer.PROCESS_LIFETIME_RESOLVES.append(marker)
        result = observer.machine_result([])
        observer._write_and_hard_exit(result, 0, stream=stream, exit_func=exit_codes.append)
        self.assertTrue(stream.flushed)
        self.assertEqual(json.loads(stream.output), result)
        self.assertEqual(exit_codes, [0])
        self.assertEqual(observer.PROCESS_LIFETIME_RESOLVES, [marker])

        error_stream = TrackingStream()
        error_payload = {"status": "OBSERVER_ERROR", "reason": "synthetic timeout"}
        observer._write_and_hard_exit(error_payload, 2, stream=error_stream, exit_func=exit_codes.append)
        self.assertTrue(error_stream.flushed)
        self.assertEqual(json.loads(error_stream.output), error_payload)
        self.assertEqual(exit_codes, [0, 2])
        self.assertEqual(observer.PROCESS_LIFETIME_RESOLVES, [marker])

    def test_success_hard_exit_subprocess_and_d2a_handoff(self):
        payload = observer.machine_result([])
        program = (
            "import atexit,json,sys; "
            "sys.path.insert(0, sys.argv[1]); "
            "import windows_dnssd_observer as observer; "
            "atexit.register(lambda: sys.stdout.write('NORMAL_FINALIZATION\\n')); "
            "observer.PROCESS_LIFETIME_RESOLVES.append(object()); "
            "observer._write_and_hard_exit(json.loads(sys.argv[2]), 0)"
        )
        tools_dir = str(Path(__file__).parents[1] / "tools")
        command = [sys.executable, "-c", program, tools_dir, json.dumps(payload)]
        direct = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(direct.returncode, 0)
        self.assertEqual(json.loads(direct.stdout), payload)
        self.assertNotIn("NORMAL_FINALIZATION", direct.stdout)
        self.assertEqual(direct.stderr, "")

        with tempfile.TemporaryDirectory() as temporary:
            result = runner.run_child(5, Path(temporary), command)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(result["returncode"], 0)
            self.assertGreater(result["stdout_bytes"], 0)
            raw_stdout = (Path(temporary) / result["run_id"] / result["raw_stdout"]).read_text(encoding="utf-8")
            self.assertEqual(json.loads(raw_stdout), payload)
            self.assertNotIn("NORMAL_FINALIZATION", raw_stdout)

    def test_error_hard_exit_subprocess_and_d2a_handoff(self):
        program = (
            "import atexit,sys; "
            "sys.path.insert(0, sys.argv[1]); "
            "import windows_dnssd_observer as observer; "
            "atexit.register(lambda: sys.stdout.write('NORMAL_FINALIZATION\\n')); "
            "sys.argv=['windows_dnssd_observer.py']; "
            "observer.NativeDnsSdBackend=lambda: type('B', (), {'browse': lambda self, service_type, timeout: (['synthetic._ewelink._tcp.local.'], False), 'resolve': lambda self, name, timeout: (observer.PROCESS_LIFETIME_RESOLVES.append(object()), (_ for _ in ()).throw(TimeoutError('synthetic timeout')))[1]})(); "
            "raise SystemExit(observer.main())"
        )
        tools_dir = str(Path(__file__).parents[1] / "tools")
        command = [sys.executable, "-c", program, tools_dir]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(json.loads(completed.stdout)["status"], "OBSERVER_ERROR")
        self.assertNotIn("NORMAL_FINALIZATION", completed.stdout)
        self.assertEqual(completed.stderr, "")

        with tempfile.TemporaryDirectory() as temporary:
            result = runner.run_child(5, Path(temporary), command)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(result["returncode"], 2)
            self.assertGreater(result["stdout_bytes"], 0)
            raw_stdout = (Path(temporary) / result["run_id"] / result["raw_stdout"]).read_text(encoding="utf-8")
            self.assertEqual(json.loads(raw_stdout)["status"], "OBSERVER_ERROR")
            self.assertNotIn("NORMAL_FINALIZATION", raw_stdout)


def ctypes_size(structure):
    import ctypes
    return ctypes.sizeof(structure)


def ctypes_size_pointer():
    import ctypes
    return ctypes.sizeof(ctypes.c_void_p)


if __name__ == "__main__":
    unittest.main()
