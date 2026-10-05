"""Loopback-only contract tests for the host simulator diagnostic UI."""

from __future__ import annotations

import argparse
import http.client
import json
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.simulator_webui import BIND_HOST, LoopbackServer, action_command  # noqa: E402

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
        self.server = LoopbackServer(self.adapter, self.web_root, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port

    def tearDown(self) -> None:
        process = self.server.bridge.process
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.assertFalse(self.thread.is_alive(), "loopback server thread was not stopped")
        self.assertIsNotNone(process.poll(), "simulator child was left running")
        self.assertEqual(process.returncode, 0)

    def request(self, method: str, path: str, payload: object | None = None, host: str | None = None):
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


if __name__ == "__main__":
    unittest.main()
