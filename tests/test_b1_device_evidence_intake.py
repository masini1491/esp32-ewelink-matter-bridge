"""Deterministic, offline tests for the B1-E1 evidence-intake boundary."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from b1_device_evidence_intake import (  # noqa: E402
    MAX_INPUT_BYTES,
    IntakeError,
    normalize_record,
    parse_input,
)

TOOL = ROOT / "tools" / "b1_device_evidence_intake.py"


def minimal_record() -> dict:
    return {
        "source_kind": "manual_transcription",
        "product_model_variant": "CK-BL602-4SW-HS",
        "lan_control": "unknown",
    }


class B1DeviceEvidenceIntakeTests(unittest.TestCase):
    def test_minimal_record_is_candidate_and_missing_optionals_stay_absent(self) -> None:
        result = normalize_record(minimal_record())
        self.assertEqual(result["record_status"], "candidate_unreconciled")
        self.assertEqual(result["lan_control"], "unknown")
        for field in ("uiid", "firmware_version", "visible_channel_count", "observed_at"):
            self.assertNotIn(field, result)
        serialized = json.dumps(result)
        self.assertNotIn("CONFIRMED_LOCAL", serialized)
        self.assertNotIn("Network PASS", serialized)

    def test_fully_populated_record_preserves_exact_values_and_precision(self) -> None:
        record = {
            "source_kind": "ewelink_app_ui",
            "product_model_variant": "CK-BL602-4SW-HS-03",
            "uiid": 141,
            "firmware_version": "1.2.3-beta2",
            "lan_control": "enabled",
            "visible_channel_count": 4,
            "observed_at": "2026-10-05T14:07",
        }
        result = normalize_record(record)
        self.assertEqual(result["observed_at"], "2026-10-05T14:07")
        self.assertEqual(result["firmware_version"], record["firmware_version"])
        self.assertEqual(result["upstream_consistency_diagnostic"]["status"], "consistent")
        self.assertEqual(
            result["upstream_consistency_diagnostic"]["authority"],
            "non_authoritative_upstream_mapping_only",
        )
        serialized = json.dumps(result).lower()
        for private_field in ("deviceid", "devicekey", "ssid", "bssid", "mac", "ipaddress", "token", "password", "matterfabric"):
            self.assertNotIn(private_field, serialized)

    def test_uiid_mapping_mismatch_is_preserved_for_review(self) -> None:
        record = {**minimal_record(), "uiid": 138, "visible_channel_count": 4}
        result = normalize_record(record)
        self.assertEqual(result["uiid"], 138)
        self.assertEqual(result["visible_channel_count"], 4)
        diagnostic = result["upstream_consistency_diagnostic"]
        self.assertEqual(diagnostic["status"], "mismatch_review_required")
        self.assertEqual(diagnostic["expected_visible_channel_count"], 1)
        self.assertEqual(diagnostic["reported_visible_channel_count"], 4)

    def test_all_upstream_mapping_entries_are_advisory(self) -> None:
        for uiid, channel_count in ((138, 1), (139, 2), (140, 3), (141, 4)):
            with self.subTest(uiid=uiid):
                record = {**minimal_record(), "uiid": uiid, "visible_channel_count": channel_count}
                self.assertEqual(normalize_record(record)["upstream_consistency_diagnostic"]["status"], "consistent")

    def test_unknown_and_free_form_fields_fail_without_echo(self) -> None:
        marker = "SYNTHETIC_UNKNOWN_VALUE_MUST_NOT_ECHO"
        for record in (
            {**minimal_record(), "notes": marker},
            {**minimal_record(), "raw_payload": marker},
            {**minimal_record(), "metadata": {"anything": marker}},
            {**minimal_record(), "source_kind": {"nested": marker}},
        ):
            with self.subTest(record_keys=list(record)):
                with self.assertRaises(IntakeError) as raised:
                    normalize_record(record)
                self.assertNotIn(marker, str(raised.exception))

    def test_forbidden_private_and_secret_fields_are_rejected_without_value_echo(self) -> None:
        forbidden = (
            "deviceId",
            "device_key",
            "wifi_ssid",
            "bssid",
            "mac_address",
            "private_ip",
            "local_ip",
            "address",
            "account_id",
            "user_id",
            "access_token",
            "authorization",
            "cookie",
            "password",
            "wifi_password",
            "local_key",
            "app_secret",
            "private_key",
            "matter_fabric",
            "commissioning_data",
        )
        marker = "SYNTHETIC_SECRET_VALUE_MUST_NOT_ECHO"
        for field in forbidden:
            with self.subTest(field=field):
                with self.assertRaises(IntakeError) as raised:
                    normalize_record({**minimal_record(), field: marker})
                self.assertIn("forbidden field category", str(raised.exception))
                self.assertNotIn(marker, str(raised.exception))

    def test_malformed_types_ranges_and_oversized_values_fail_closed(self) -> None:
        invalid_records = (
            {**minimal_record(), "uiid": True},
            {**minimal_record(), "uiid": 0},
            {**minimal_record(), "uiid": 1.5},
            {**minimal_record(), "visible_channel_count": 0},
            {**minimal_record(), "visible_channel_count": 65},
            {**minimal_record(), "firmware_version": "x" * 65},
            {**minimal_record(), "firmware_version": "SYNTHETIC-NOT-A-VERSION"},
            {**minimal_record(), "product_model_variant": "Other-Family"},
            {**minimal_record(), "lan_control": False},
            [minimal_record()],
        )
        for record in invalid_records:
            with self.subTest(value_type=type(record).__name__):
                with self.assertRaises(IntakeError):
                    normalize_record(record)
        with self.assertRaises(IntakeError):
            parse_input(b" " * (MAX_INPUT_BYTES + 1))
        with self.assertRaises(IntakeError):
            parse_input(b"{not-json}")
        deeply_nested = (
            b'{"source_kind":'
            + b"[" * 5000
            + b"0"
            + b"]" * 5000
            + b',"product_model_variant":"CK-BL602-4SW-HS","lan_control":"unknown"}'
        )
        with self.assertRaises(IntakeError):
            normalize_record(parse_input(deeply_nested))
        with self.assertRaises(IntakeError):
            parse_input(b'{"uiid":1,"uiid":2}')

    def test_timestamp_validation_does_not_round_or_fabricate_precision(self) -> None:
        for timestamp in ("2026-10-05", "2026-10-05T14:07", "2026-10-05T14:07:08.123456789+08:00"):
            with self.subTest(timestamp=timestamp):
                result = normalize_record({**minimal_record(), "observed_at": timestamp})
                self.assertEqual(result["observed_at"], timestamp)
        for timestamp in ("2026-02-30", "2026-10-05T25:00", "yesterday"):
            with self.subTest(timestamp=timestamp):
                with self.assertRaises(IntakeError):
                    normalize_record({**minimal_record(), "observed_at": timestamp})

    def test_cli_supports_file_stdin_and_explicit_new_output_only(self) -> None:
        payload = json.dumps(minimal_record())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.json"
            output_path = root / "candidate.json"
            input_path.write_text(payload, encoding="utf-8")

            file_result = subprocess.run(
                [sys.executable, str(TOOL), "--input", str(input_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            stdin_result = subprocess.run(
                [sys.executable, str(TOOL)],
                input=payload,
                capture_output=True,
                text=True,
                check=False,
            )
            output_file_result = subprocess.run(
                [sys.executable, str(TOOL), "--input", str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(file_result.returncode, 0, file_result.stderr)
            self.assertEqual(stdin_result.returncode, 0, stdin_result.stderr)
            self.assertEqual(output_file_result.returncode, 0, output_file_result.stderr)
            self.assertEqual(json.loads(file_result.stdout), json.loads(stdin_result.stdout))
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), json.loads(file_result.stdout))

            overwrite_result = subprocess.run(
                [sys.executable, str(TOOL), "--input", str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(overwrite_result.returncode, 2)
            self.assertIn("output file already exists", overwrite_result.stderr)

    def test_cli_rejection_never_echoes_synthetic_secret_value(self) -> None:
        marker = "SYNTHETIC_DEVICE_SECRET_DO_NOT_ECHO"
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps({**minimal_record(), "deviceKey": marker}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(TOOL), "--input", str(input_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("forbidden field category", result.stderr)
        self.assertNotIn(marker, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
