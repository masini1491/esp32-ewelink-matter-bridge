#!/usr/bin/env python3
"""Normalize a small, manually transcribed CK-BL602 evidence candidate offline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 16 * 1024
MAX_FIRMWARE_CHARS = 64
MAX_VISIBLE_CHANNEL_COUNT = 64
MAX_TIMESTAMP_CHARS = 40

SOURCE_KINDS = frozenset({"ewelink_app_ui", "device_ui", "manual_transcription"})
PRODUCT_VARIANTS = frozenset({"CK-BL602-4SW-HS", "CK-BL602-4SW-HS-03"})
LAN_CONTROL_STATES = frozenset({"enabled", "disabled", "not_shown", "unknown"})
ALLOWED_FIELDS = frozenset(
    {
        "source_kind",
        "product_model_variant",
        "uiid",
        "firmware_version",
        "lan_control",
        "visible_channel_count",
        "observed_at",
    }
)

FORBIDDEN_FIELD_CATEGORIES = {
    "deviceid": "device identifier",
    "devicekey": "device credential",
    "devicesecret": "device credential",
    "localkey": "device credential",
    "wifissid": "Wi-Fi network identifier",
    "ssid": "Wi-Fi network identifier",
    "bssid": "Wi-Fi network identifier",
    "mac": "hardware address",
    "macaddress": "hardware address",
    "ip": "private network address",
    "ipv4": "private network address",
    "ipv6": "private network address",
    "ipaddress": "private network address",
    "ipaddressv4": "private network address",
    "localip": "private network address",
    "privateip": "private network address",
    "privateipaddress": "private network address",
    "privateaddress": "private network address",
    "address": "private network address",
    "account": "account identifier",
    "accountid": "account identifier",
    "userid": "user identifier",
    "username": "user identifier",
    "token": "token or authorization material",
    "accesstoken": "token or authorization material",
    "refreshtoken": "token or authorization material",
    "authorization": "token or authorization material",
    "cookie": "token or authorization material",
    "password": "password or key material",
    "passwd": "password or key material",
    "wifipassword": "password or key material",
    "wifikey": "password or key material",
    "wificredential": "password or key material",
    "wifipassphrase": "password or key material",
    "apikey": "password or key material",
    "appkey": "password or key material",
    "appsecret": "password or key material",
    "key": "password or key material",
    "privatekey": "password or key material",
    "secret": "password or key material",
    "secretkey": "password or key material",
    "matterfabric": "Matter commissioning/fabric material",
    "fabric": "Matter commissioning/fabric material",
    "fabrics": "Matter commissioning/fabric material",
    "fabricid": "Matter commissioning/fabric material",
    "commissioning": "Matter commissioning/fabric material",
    "commissioningdata": "Matter commissioning/fabric material",
    "mattersetupcode": "Matter commissioning/fabric material",
    "setupcode": "Matter commissioning/fabric material",
    "manualcode": "Matter commissioning/fabric material",
    "discriminator": "Matter commissioning/fabric material",
}

FIRMWARE_PATTERN = re.compile(r"v?\d{1,8}(?:\.\d{1,8}){0,3}(?:[-+][A-Za-z0-9][A-Za-z0-9.\-]{0,23})?\Z", re.IGNORECASE)
TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?(?:Z|[+-]\d{2}:\d{2})?)?\Z"
)
UPSTREAM_CHANNEL_COUNTS = {138: 1, 139: 2, 140: 3, 141: 4}


class IntakeError(ValueError):
    """A safe-to-display validation failure with no user-supplied value."""


def _field_category(field: str) -> str | None:
    normalized = "".join(character.lower() for character in field if character.isalnum())
    return FORBIDDEN_FIELD_CATEGORIES.get(normalized)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IntakeError("duplicate JSON field")
        result[key] = value
    return result


def _reject_nonstandard_constant(_value: str) -> None:
    raise IntakeError("non-standard JSON number")


def parse_input(raw: bytes) -> Any:
    if len(raw) > MAX_INPUT_BYTES:
        raise IntakeError("input exceeds size limit")
    try:
        text = raw.decode("utf-8", errors="strict")
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        raise IntakeError("input is not valid UTF-8 JSON") from None


def _validate_timestamp(value: object) -> str:
    if not isinstance(value, str) or len(value) > MAX_TIMESTAMP_CHARS or not TIMESTAMP_PATTERN.fullmatch(value):
        raise IntakeError("observed_at must be an ISO date or date/time")
    try:
        if "T" in value:
            datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
        else:
            date.fromisoformat(value)
    except ValueError:
        raise IntakeError("observed_at must be a valid ISO date or date/time") from None
    return value


def normalize_record(record: object) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise IntakeError("top-level JSON value must be an object")

    if any(not isinstance(field, str) for field in record):
        raise IntakeError("field names must be strings")
    for field in record:
        category = _field_category(field)
        if category is not None:
            raise IntakeError(f"forbidden field category: {category}")
    if any(field not in ALLOWED_FIELDS for field in record):
        raise IntakeError("unknown top-level field; input was not copied")
    if any(isinstance(value, (dict, list)) for value in record.values()):
        raise IntakeError("nested or free-form values are not accepted")

    required = {"source_kind", "product_model_variant", "lan_control"}
    if not required.issubset(record):
        raise IntakeError("required evidence field is missing")

    source_kind = record["source_kind"]
    if not isinstance(source_kind, str) or source_kind not in SOURCE_KINDS:
        raise IntakeError("source_kind is not a supported source category")

    product = record["product_model_variant"]
    if not isinstance(product, str) or product not in PRODUCT_VARIANTS:
        raise IntakeError("product_model_variant is not an in-scope visible model string")

    lan_control = record["lan_control"]
    if not isinstance(lan_control, str) or lan_control not in LAN_CONTROL_STATES:
        raise IntakeError("lan_control is not a supported semantic state")

    normalized: dict[str, Any] = {
        "schema": "b1-device-evidence-candidate/v1",
        "record_status": "candidate_unreconciled",
        "source_kind": source_kind,
        "product_model_variant": product,
        "lan_control": lan_control,
    }

    if "uiid" in record:
        uiid = record["uiid"]
        if type(uiid) is not int or not 1 <= uiid <= 65535:
            raise IntakeError("uiid must be a positive integer when supplied")
        normalized["uiid"] = uiid

    if "firmware_version" in record:
        firmware = record["firmware_version"]
        if (
            not isinstance(firmware, str)
            or len(firmware) > MAX_FIRMWARE_CHARS
            or not FIRMWARE_PATTERN.fullmatch(firmware)
        ):
            raise IntakeError("firmware_version must be a bounded visible version token")
        normalized["firmware_version"] = firmware

    if "visible_channel_count" in record:
        count = record["visible_channel_count"]
        if type(count) is not int or not 1 <= count <= MAX_VISIBLE_CHANNEL_COUNT:
            raise IntakeError("visible_channel_count is outside the accepted positive range")
        normalized["visible_channel_count"] = count

    if "observed_at" in record:
        normalized["observed_at"] = _validate_timestamp(record["observed_at"])

    uiid = normalized.get("uiid")
    visible_count = normalized.get("visible_channel_count")
    if uiid in UPSTREAM_CHANNEL_COUNTS and visible_count is not None:
        expected_count = UPSTREAM_CHANNEL_COUNTS[uiid]
        consistent = visible_count == expected_count
        normalized["upstream_consistency_diagnostic"] = {
            "authority": "non_authoritative_upstream_mapping_only",
            "status": "consistent" if consistent else "mismatch_review_required",
            "expected_visible_channel_count": expected_count,
            "reported_visible_channel_count": visible_count,
        }

    return normalized


def _read_bounded_input(path: Path | None) -> bytes:
    stream = sys.stdin.buffer if path is None else path.open("rb")
    try:
        return stream.read(MAX_INPUT_BYTES + 1)
    finally:
        if path is not None:
            stream.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="input JSON file; omit to read stdin")
    parser.add_argument("--output", type=Path, help="new output file; omit to write normalized JSON to stdout")
    args = parser.parse_args(argv)

    try:
        if args.input is not None and args.output is not None:
            if args.input.resolve() == args.output.resolve():
                raise IntakeError("input and output paths must differ")
        if args.output is not None and args.output.exists():
            raise IntakeError("output file already exists; refusing to overwrite")
        candidate = normalize_record(parse_input(_read_bounded_input(args.input)))
        serialized = json.dumps(candidate, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        if args.output is None:
            sys.stdout.write(serialized)
            sys.stdout.flush()
        else:
            with args.output.open("x", encoding="utf-8", newline="\n") as output:
                output.write(serialized)
    except IntakeError as error:
        sys.stderr.write(json.dumps({"status": "REJECTED", "reason": str(error)}, sort_keys=True) + "\n")
        return 2
    except (OSError, UnicodeError):
        sys.stderr.write('{"status":"ERROR","reason":"local file or stream operation failed"}\n')
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
