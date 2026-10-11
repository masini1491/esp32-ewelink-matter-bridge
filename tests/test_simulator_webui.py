"""Loopback-only contract tests for the host simulator diagnostic UI."""

from __future__ import annotations

import argparse
import http.client
import io
import json
import os
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.simulator_webui import (
    BIND_HOST,
    LoopbackServer,
    SimulatorBridge,
    SimulatorProtocolError,
    SimulatorTimeoutError,
    action_command,
)  # noqa: E402


class FakeStdout:
    def __init__(self, response: str, block: bool = False) -> None:
        self.response = response
        self.block = block
        self.released = threading.Event()

    def readline(self, _size: int) -> str:
        if self.block:
            self.released.wait()
        return self.response

    def release(self) -> None:
        self.released.set()

    def close(self) -> None:
        self.release()


class FakeProcess:
    def __init__(self, response: str, *, block: bool = False, returncode: int | None = None) -> None:
        self.stdin = io.StringIO()
        self.stdout = FakeStdout(response, block)
        self.stderr = None
        self.returncode = returncode

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.returncode = -15
        self.stdout.release()

    def kill(self) -> None:
        self.returncode = -9
        self.stdout.release()

    def wait(self, timeout: float | None = None) -> int:
        if self.returncode is None:
            raise AssertionError("fake child was not stopped")
        return self.returncode

_parser = argparse.ArgumentParser()
_parser.add_argument("--adapter", type=Path, required=True)
_parser.add_argument("--web-root", type=Path, required=True)
_args, _unittest_args = _parser.parse_known_args()
sys.argv = [sys.argv[0], *_unittest_args]


class SimulatorWebUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = _args.adapter.resolve()
        cls.web_root = _args.web_root.resolve()

    def setUp(self) -> None:
        self.server: LoopbackServer | None = None
        self.bridge: SimulatorBridge | None = None
        self.thread: threading.Thread | None = None
        self.expected_child_returncode: int | None = 0

    def start_server(self) -> None:
        if self.server is not None:
            return
        self.server = LoopbackServer(self.adapter, self.web_root, port=0)
        self.bridge = self.server.bridge
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port

    def tearDown(self) -> None:
        process = None
        if self.server is not None:
            process = self.server.bridge.process
            self.server.shutdown()
            self.server.server_close()
            assert self.thread is not None
            self.thread.join(timeout=2)
            self.assertFalse(self.thread.is_alive(), "loopback server thread was not stopped")
        elif self.bridge is not None:
            process = self.bridge.process
            self.bridge.close()
        if process is not None:
            self.assertIsNotNone(process.poll(), "simulator child was left running")
        if process is not None and self.expected_child_returncode is not None:
            self.assertEqual(process.returncode, self.expected_child_returncode)

    def request(self, method: str, path: str, payload: object | None = None, host: str | None = None):
        self.start_server()
        connection = http.client.HTTPConnection(BIND_HOST, self.port, timeout=2)
        headers = {"Host": host or f"{BIND_HOST}:{self.port}"}
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload)
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        result = response.status, response.getheader("Content-Type"), response.read()
        connection.close()
        return result

    def state(self) -> dict:
        status, _, body = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        return json.loads(body)

    def action(self, action: dict) -> dict:
        status, _, body = self.request("POST", "/api/actions", action)
        self.assertEqual(status, 200, body)
        return json.loads(body)

    def install_child(self, behavior: str) -> None:
        if self.server is not None:
            self.server.bridge.close()
        elif self.bridge is not None:
            self.bridge.close()
        if os.name == "nt":
            executable = Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
            scripts = {
                "hang": "$null = [Console]::In.ReadLine(); Start-Sleep -Seconds 30",
                "partial": "$null = [Console]::In.ReadLine(); [Console]::Out.Write('{\"partial\":'); [Console]::Out.Flush(); Start-Sleep -Seconds 30",
                "malformed": "$null = [Console]::In.ReadLine(); [Console]::Out.WriteLine('not-json'); Start-Sleep -Seconds 30",
                "oversized": "$null = [Console]::In.ReadLine(); [Console]::Out.WriteLine('x' * 20000); Start-Sleep -Seconds 30",
                "exit": "exit 0",
            }
            arguments = ("-NoLogo", "-NoProfile", "-NonInteractive", "-Command", scripts[behavior])
        else:
            executable = Path(sys.executable)
            scripts = {
                "hang": "import sys,time; sys.stdin.readline(); time.sleep(30)",
                "partial": "import sys,time; sys.stdin.readline(); sys.stdout.write('{\"partial\":'); sys.stdout.flush(); time.sleep(30)",
                "malformed": "import sys,time; sys.stdin.readline(); print('not-json',flush=True); time.sleep(30)",
                "oversized": "import sys,time; sys.stdin.readline(); print('x'*20000,flush=True); time.sleep(30)",
                "exit": "raise SystemExit(0)",
                "ignore_terminate": "import signal,sys,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); sys.stdin.readline(); time.sleep(30)",
            }
            arguments = ("-c", scripts[behavior])
        self.bridge = SimulatorBridge(executable, arguments)
        if self.server is not None:
            self.server.bridge = self.bridge
        self.expected_child_returncode = None

    def install_response(self, response: str, *, block: bool = False, returncode: int | None = None) -> FakeProcess:
        if self.server is not None:
            self.server.bridge.close()
        elif self.bridge is not None:
            self.bridge.close()
        self.bridge = SimulatorBridge.__new__(SimulatorBridge)
        self.bridge.process = FakeProcess(response, block=block, returncode=returncode)  # type: ignore[assignment]
        self.bridge._request_lock = threading.Lock()
        self.expected_child_returncode = None
        return self.bridge.process  # type: ignore[return-value]

    def test_assets_are_self_contained_and_simulator_labeled(self) -> None:
        status, content_type, page = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertTrue(content_type.startswith("text/html"))
        self.assertIn(b"SIMULATOR ONLY", page)
        self.assertIn(b"Nothing here connects to a CK-BL602", page)
        self.assertEqual(len(self.state()["channels"]), 4)
        for path in ("/assets/app.js", "/assets/styles.css"):
            status, _, body = self.request("GET", path)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 0)
            self.assertNotIn(b"https://", body)

    def test_acceptance_waits_for_observation_then_converges(self) -> None:
        state = self.action({"action": "connect"})
        self.assertEqual(state["availability"], "available")
        state = self.action({"action": "set_transport", "result": "accepted"})
        state = self.action({"action": "submit", "channel": 0, "state": "on"})
        channel = state["channels"][0]
        self.assertEqual(channel["observed_state"], "unknown")
        self.assertFalse(channel["fresh"])
        self.assertEqual(channel["pending_state"], "on")
        self.assertEqual(channel["transport_disposition"], "accepted")
        state = self.action({"action": "observe", "channel": 0, "state": "on"})
        channel = state["channels"][0]
        self.assertEqual(channel["observed_state"], "on")
        self.assertTrue(channel["fresh"])
        self.assertEqual(channel["convergence"], "matched")

    def test_lifecycle_rejection_stale_and_reconnect_are_visible(self) -> None:
        state = self.action({"action": "connect"})
        state = self.action({"action": "set_transport", "result": "rejected"})
        state = self.action({"action": "submit", "channel": 1, "state": "off"})
        self.assertEqual(state["channels"][1]["transport_disposition"], "rejected")
        self.assertEqual(state["channels"][1]["observed_state"], "unknown")
        state = self.action({"action": "observe", "channel": 1, "state": "on"})
        self.assertEqual(state["channels"][1]["convergence"], "rejected")
        stale = self.action({"action": "stale"})
        self.assertEqual(stale["availability"], "unavailable")
        self.assertFalse(stale["channels"][1]["fresh"])
        disconnected = self.action({"action": "disconnect"})
        self.assertEqual(disconnected["availability"], "unavailable")
        state = self.action({"action": "reconnect"})
        self.assertEqual(state["availability"], "available")
        self.assertFalse(state["channels"][1]["fresh"])
        self.assertEqual(state["channels"][1]["observed_state"], "on")
        state = self.action({"action": "connect"})
        self.assertEqual(state["availability"], "available")

    def test_four_channels_are_independent(self) -> None:
        self.action({"action": "connect"})
        for index, state_name in enumerate(("on", "off", "on", "off")):
            self.action({"action": "observe", "channel": index, "state": state_name})
        self.action({"action": "set_transport", "result": "accepted"})
        state = self.action({"action": "submit", "channel": 2, "state": "off"})
        self.assertEqual([item["observed_state"] for item in state["channels"]], ["on", "off", "on", "off"])
        self.assertEqual([item["pending_state"] for item in state["channels"]], [None, None, "off", None])
        state = self.action({"action": "observe", "channel": 2, "state": "off"})
        self.assertEqual([item["observed_state"] for item in state["channels"]], ["on", "off", "off", "off"])
        self.assertEqual([item["convergence"] for item in state["channels"]], ["none", "none", "matched", "none"])

    def test_invalid_actions_and_non_loopback_host_are_rejected(self) -> None:
        status, _, _ = self.request("POST", "/api/actions", {"action": "submit", "channel": 4, "state": "on"})
        self.assertEqual(status, 400)
        status, _, _ = self.request("GET", "/api/state", host=f"192.0.2.44:{self.port}")
        self.assertEqual(status, 403)
        with self.assertRaises(ValueError):
            action_command({"action": "observe", "channel": True, "state": "on"})

    def test_child_without_response_times_out_and_is_reaped(self) -> None:
        self.install_child("hang")
        assert self.bridge is not None
        process = self.bridge.process
        started = time.monotonic()
        with patch("tools.simulator_webui.IPC_TIMEOUT_SECONDS", 0.1):
            with self.assertRaises(SimulatorTimeoutError):
                self.bridge.request("state")
        self.assertLess(time.monotonic() - started, 4)
        self.assertIsNotNone(process.poll())

    @unittest.skipIf(os.name == "nt", "Windows terminate already forcibly stops the direct child")
    def test_timeout_escalates_to_kill_when_child_ignores_terminate(self) -> None:
        self.install_child("ignore_terminate")
        assert self.bridge is not None
        process = self.bridge.process
        started = time.monotonic()
        with patch("tools.simulator_webui.IPC_TIMEOUT_SECONDS", 0.1):
            with self.assertRaises(SimulatorTimeoutError):
                self.bridge.request("state")
        self.assertLess(time.monotonic() - started, 5)
        self.assertIsNotNone(process.poll())

    def test_partial_response_times_out_and_owned_child_stops(self) -> None:
        self.install_child("partial")
        assert self.bridge is not None
        process = self.bridge.process
        with patch("tools.simulator_webui.IPC_TIMEOUT_SECONDS", 0.1):
            with self.assertRaises(SimulatorTimeoutError):
                self.bridge.request("state")
        self.assertIsNotNone(process.poll())

    def test_malformed_response_fails_closed_and_stops_child(self) -> None:
        process = self.install_response("not-json\n")
        with self.assertRaises(SimulatorProtocolError):
            assert self.bridge is not None
            self.bridge.request("state")
        self.assertIsNotNone(process.poll())

    def test_oversized_response_fails_closed_and_stops_child(self) -> None:
        process = self.install_response("x" * 20000 + "\n")
        with self.assertRaises(SimulatorProtocolError):
            assert self.bridge is not None
            self.bridge.request("state")
        self.assertIsNotNone(process.poll())

    def test_child_exit_is_reported_as_unavailable(self) -> None:
        self.install_response("", returncode=0)
        assert self.bridge is not None
        with self.assertRaisesRegex(Exception, "unavailable"):
            self.bridge.request("state")

    def test_http_handler_returns_bounded_timeout_for_unresponsive_child(self) -> None:
        self.start_server()
        process = self.install_response("", block=True)
        assert self.server is not None and self.bridge is not None
        self.server.bridge = self.bridge
        with patch("tools.simulator_webui.IPC_TIMEOUT_SECONDS", 0.1):
            status, _, body = self.request("GET", "/api/state")
        self.assertEqual(status, 504)
        self.assertEqual(json.loads(body), {"error": "simulator response timed out"})
        self.assertIsNotNone(process.poll())

    def test_child_rejection_is_distinct_from_malformed_user_input(self) -> None:
        self.start_server()
        process = self.install_response('{"error":"invalid_state"}\n')
        assert self.server is not None and self.bridge is not None
        self.server.bridge = self.bridge
        status, _, body = self.request("POST", "/api/actions", {"action": "connect"})
        self.assertEqual(status, 409)
        self.assertEqual(json.loads(body), {"error": "simulator action was not accepted"})
        self.assertIsNone(process.poll())

    def test_close_does_not_wait_forever_for_quit_response(self) -> None:
        process = self.install_response("", block=True)
        assert self.bridge is not None
        started = time.monotonic()
        with patch("tools.simulator_webui.IPC_TIMEOUT_SECONDS", 0.1):
            self.bridge.close()
        self.assertLess(time.monotonic() - started, 4)
        self.assertIsNotNone(process.poll())


if __name__ == "__main__":
    unittest.main()
