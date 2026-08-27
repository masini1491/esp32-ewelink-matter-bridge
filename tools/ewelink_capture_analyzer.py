#!/usr/bin/env python3
"""Analyze a bounded, offline synthetic/eWeLink mDNS capture without network access."""
import hashlib
import json
import sys
from pathlib import Path

MAX_INPUT = 64 * 1024
MAX_FRAGMENT = 4096


def _alias(value):
    return "device-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def analyze(capture):
    raw = json.dumps(capture, sort_keys=True, separators=(",", ":"))
    if len(raw.encode()) > MAX_INPUT or not isinstance(capture, dict):
        return {"status": "MALFORMED", "classification": "UNKNOWN"}
    service = capture.get("service", {})
    txt = service.get("txt", {})
    name = service.get("name", "")
    if not isinstance(service, dict) or not isinstance(txt, dict) or not isinstance(name, str):
        return {"status": "MALFORMED", "classification": "UNKNOWN"}
    service_type = service.get("type")
    if service_type != "_ewelink._tcp.local." or not name.lower().startswith("ewelink"):
        return {"status": "IGNORED", "classification": "NOT_EWELINK"}
    if any(not isinstance(k, str) or not isinstance(v, (str, int, bool)) for k, v in txt.items()):
        return {"status": "MALFORMED", "classification": "UNKNOWN"}
    fragments = []
    for index in range(1, 5):
        key = f"data{index}"
        if key in txt:
            value = txt[key]
            if not isinstance(value, str) or len(value) > MAX_FRAGMENT:
                return {"status": "MALFORMED", "classification": "UNKNOWN"}
            fragments.append((index, value))
    result = {
        "status": "OK",
        "classification": "UNKNOWN",
        "service": {"type": service_type, "name_prefix": "ewelink", "port_present": "port" in service},
        "txt_keys": sorted(txt),
        "fragments": {"indices": [i for i, _ in fragments], "count": len(fragments), "lengths": [len(v) for _, v in fragments]},
    }
    if isinstance(txt.get("id"), str):
        result["device_alias"] = _alias(txt["id"])
    if "seq" in txt:
        result["seq"] = {"present": True, "type": type(txt["seq"]).__name__}
    if "encrypt" not in txt:
        result["classification"] = "UNKNOWN"
        return result
    encrypted = txt["encrypt"]
    if encrypted is True or encrypted == "1" or encrypted == "true":
        result["classification"] = "ENCRYPTED"
        result["encrypted"] = {"iv_present": isinstance(txt.get("iv"), str), "fragmented_payload_length": sum(len(v) for _, v in fragments)}
        return result
    if encrypted is not False and encrypted not in ("0", "false"):
        return {**result, "classification": "UNKNOWN", "status": "PARTIAL"}
    if len(fragments) != 4 or [i for i, _ in fragments] != [1, 2, 3, 4]:
        return {**result, "status": "PARTIAL", "classification": "UNKNOWN"}
    payload = "".join(v for _, v in fragments)
    try:
        document = json.loads(payload)
    except json.JSONDecodeError:
        return {**result, "status": "MALFORMED", "classification": "UNKNOWN"}
    if not isinstance(document, dict):
        return {**result, "status": "PARTIAL", "classification": "UNKNOWN"}
    result["classification"] = "PLAINTEXT"
    result["json"] = {"keys": sorted(document), "types": {k: type(v).__name__ for k, v in sorted(document.items())}}
    return result


def main():
    if len(sys.argv) != 2:
        print("usage: ewelink_capture_analyzer.py capture.json", file=sys.stderr)
        return 2
    try:
        capture = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        print(json.dumps(analyze(capture), sort_keys=True, separators=(",", ":")))
        return 0
    except (OSError, json.JSONDecodeError):
        print(json.dumps({"status": "MALFORMED", "classification": "UNKNOWN"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
