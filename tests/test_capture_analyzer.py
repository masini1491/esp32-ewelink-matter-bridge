import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
from ewelink_capture_analyzer import analyze


def capture(txt, name="eWeLink-SYNTHETIC", service_type="_ewelink._tcp.local."):
    return {"synthetic": True, "service": {"name": name, "type": service_type, "port": 8081, "txt": txt}}


class CaptureAnalyzerTests(unittest.TestCase):
    def test_plaintext_order_and_structure(self):
        payload = json.dumps({"switches": [True, False], "uiid": 999}, separators=(",", ":"))
        parts = [payload[:4], payload[4:9], payload[9:14], payload[14:]]
        result = analyze(capture({"id": "SYNTHETIC-DEVICE-001", "encrypt": "0", "data1": parts[0], "data2": parts[1], "data3": parts[2], "data4": parts[3]}))
        self.assertEqual(result["classification"], "PLAINTEXT")
        self.assertEqual(result["json"]["keys"], ["switches", "uiid"])
        self.assertNotIn("SYNTHETIC-DEVICE-001", json.dumps(result))

    def test_encrypted_is_shape_only(self):
        result = analyze(capture({"id": "SECRET-LIKE-ID", "encrypt": "1", "iv": "FIXED-IV", "data1": "cipher", "data2": "text", "data3": "", "data4": ""}))
        output = json.dumps(result)
        self.assertEqual(result["classification"], "ENCRYPTED")
        self.assertNotIn("FIXED-IV", output)
        self.assertNotIn("cipher", output.lower())
        self.assertNotIn("SECRET-LIKE-ID", output)

    def test_missing_middle_and_encrypt_are_unknown(self):
        partial = analyze(capture({"encrypt": False, "data1": "{", "data3": "}"}))
        unknown = analyze(capture({"data1": "{}"}))
        self.assertEqual(partial["classification"], "UNKNOWN")
        self.assertEqual(partial["status"], "PARTIAL")
        self.assertEqual(unknown["classification"], "UNKNOWN")

    def test_malformed_oversized_and_unexpected(self):
        bad = analyze(capture({"encrypt": False, "data1": "not-json", "data2": "", "data3": "", "data4": "", "unexpected": "safe"}))
        huge = analyze(capture({"encrypt": False, "data1": "x" * 4097}))
        self.assertEqual(bad["status"], "MALFORMED")
        self.assertEqual(huge["status"], "MALFORMED")

    def test_service_case_and_rejection(self):
        self.assertEqual(analyze(capture({"encrypt": False}, name="EWELINK-case"))["status"], "PARTIAL")
        self.assertEqual(analyze(capture({}, service_type="_http._tcp.local."))["classification"], "NOT_EWELINK")


if __name__ == "__main__":
    unittest.main()
