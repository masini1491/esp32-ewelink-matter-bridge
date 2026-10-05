#!/usr/bin/env python3
"""Loopback-only Web UI adapter for the host synthetic simulator."""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

BIND_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_REQUEST_BYTES = 1024
MAX_ADAPTER_RESPONSE_BYTES = 16 * 1024
WEB_ROOT = Path(__file__).resolve().parents[1] / "webui"
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/assets/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/assets/styles.css": ("styles.css", "text/css; charset=utf-8"),
}


class AdapterError(RuntimeError):
    """Raised when the simulator child fails or rejects a bounded command."""


class SimulatorBridge:
    def __init__(self, executable: Path) -> None:
        self.process = subprocess.Popen(
            [str(executable)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            bufsize=1,
            shell=False,
        )

    def request(self, command: str) -> dict:
        if self.process.poll() is not None or self.process.stdin is None or self.process.stdout is None:
            raise AdapterError("simulator process is unavailable")
        try:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            line = self.process.stdout.readline(MAX_ADAPTER_RESPONSE_BYTES + 1)
        except (OSError, UnicodeError) as error:
            raise AdapterError("simulator request failed") from error
        if not line.endswith("\n") or len(line.encode("utf-8")) > MAX_ADAPTER_RESPONSE_BYTES:
            raise AdapterError("simulator response exceeded its size bound")
        try:
            response = json.loads(line)
        except (json.JSONDecodeError, UnicodeError) as error:
            raise AdapterError("simulator returned an invalid response") from error
        if not isinstance(response, dict):
            raise AdapterError("simulator returned an invalid response")
        if "error" in response:
            raise AdapterError(str(response["error"]))
        return response

    def close(self) -> int | None:
        if self.process.poll() is None:
            try:
                self.request("quit")
                return_code = self.process.wait(timeout=2)
            except (AdapterError, OSError, subprocess.TimeoutExpired):
                self.process.terminate()
                try:
                    return_code = self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    return_code = self.process.wait(timeout=2)
        else:
            return_code = self.process.returncode
        for pipe in (self.process.stdin, self.process.stdout, self.process.stderr):
            if pipe is not None:
                pipe.close()
        return return_code


def action_command(payload: object) -> str:
    if not isinstance(payload, dict) or not isinstance(payload.get("action"), str):
        raise ValueError("invalid action")
    action = payload["action"]
    allowed_lifecycle = {"connect", "disconnect", "stale", "reconnect"}
    if action in allowed_lifecycle and set(payload) == {"action"}:
        return action
    if action == "set_transport" and set(payload) == {"action", "result"}:
        result = payload["result"]
        if result in ("accepted", "rejected"):
            return f"transport {result}"
    if action in ("submit", "observe") and set(payload) == {"action", "channel", "state"}:
        channel = payload["channel"]
        state = payload["state"]
        if type(channel) is int and 0 <= channel < 4 and state in ("on", "off"):
            operation = "command" if action == "submit" else "observe"
            return f"{operation} {channel} {state}"
    raise ValueError("invalid action")


class LoopbackServer(HTTPServer):
    address_family = socket.AF_INET
    allow_reuse_address = True

    def __init__(self, executable: Path, web_root: Path = WEB_ROOT, port: int = DEFAULT_PORT) -> None:
        self.bridge = SimulatorBridge(executable)
        self.web_root = web_root
        try:
            super().__init__((BIND_HOST, port), RequestHandler)
        except OSError:
            self.bridge.close()
            raise

    def server_bind(self) -> None:
        super().server_bind()
        self.server_name = BIND_HOST
        self.server_port = self.server_address[1]

    def server_close(self) -> None:
        try:
            super().server_close()
        finally:
            self.bridge.close()


class RequestHandler(BaseHTTPRequestHandler):
    server: LoopbackServer

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; "
            "img-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._send(status, "application/json; charset=utf-8", json.dumps(payload).encode("utf-8"))

    def _host_is_loopback_origin(self) -> bool:
        try:
            host_header = self.headers.get("Host", "")
            parsed = urlsplit("//" + host_header)
            return parsed.hostname in ("127.0.0.1", "localhost") and parsed.port == self.server.server_port
        except ValueError:
            return False

    def do_GET(self) -> None:
        if not self._host_is_loopback_origin():
            self._json(403, {"error": "loopback origin required"})
            return
        path = urlsplit(self.path).path
        if path == "/api/state":
            try:
                self._json(200, self.server.bridge.request("state"))
            except AdapterError:
                self._json(503, {"error": "simulator unavailable"})
            return
        asset = ASSETS.get(path)
        if asset is None:
            self._json(404, {"error": "not found"})
            return
        filename, content_type = asset
        try:
            body = (self.server.web_root / filename).read_bytes()
        except OSError:
            self._json(503, {"error": "UI asset unavailable"})
            return
        self._send(200, content_type, body)

    def do_POST(self) -> None:
        if not self._host_is_loopback_origin():
            self._json(403, {"error": "loopback origin required"})
            return
        if urlsplit(self.path).path != "/api/actions":
            self._json(404, {"error": "not found"})
            return
        if self.headers.get("Transfer-Encoding") is not None:
            self._json(400, {"error": "invalid request"})
            return
        try:
            content_length = int(self.headers.get("Content-Length", ""))
            if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
                raise ValueError("invalid size")
            if self.headers.get_content_type() != "application/json":
                raise ValueError("invalid content type")
            payload = json.loads(self.rfile.read(content_length))
            command = action_command(payload)
        except (ValueError, TypeError, json.JSONDecodeError):
            self._json(400, {"error": "invalid request"})
            return
        try:
            self._json(200, self.server.bridge.request(command))
        except AdapterError as error:
            status = 409 if str(error) == "invalid_state" else 400
            self._json(status, {"error": "simulator action was not accepted"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the synthetic simulator Web UI on IPv4 loopback only.")
    parser.add_argument("--adapter", required=True, type=Path, help="path to bridge_simulator_adapter executable")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="loopback HTTP port (default: 8765)")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    executable = args.adapter.resolve()
    if not executable.is_file():
        parser.error("--adapter must name an existing simulator adapter executable")
    try:
        server = LoopbackServer(executable, port=args.port)
    except OSError:
        parser.error("could not start the loopback-only simulator UI")
    print(f"Synthetic simulator UI: http://{BIND_HOST}:{server.server_port}/ (no hardware connection)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
