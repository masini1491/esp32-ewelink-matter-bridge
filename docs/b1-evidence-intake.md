# B1 device-evidence intake (B1-E1)

`tools/b1_device_evidence_intake.py` is an offline, standard-library-only normalizer for a small JSON record manually transcribed from a device/app UI. It emits a `candidate_unreconciled` record for human review; it does not establish local confirmation, canonical project truth, B1 closure or Network PASS, and it never writes to the repository automatically.

## Input contract

Read one UTF-8 JSON object from `--input PATH` or, when `--input` is omitted, from stdin. The maximum encoded input size is 16 KiB. Unknown top-level fields, nested values, duplicate keys, non-standard JSON numbers and free-form payloads are rejected. Supported top-level fields are:

| Field | Required | Accepted form |
| --- | --- | --- |
| `source_kind` | yes | `ewelink_app_ui`, `device_ui`, or `manual_transcription`; records how the submitter says the value was observed, not proof of provenance |
| `product_model_variant` | yes | Exact visible string `CK-BL602-4SW-HS` or `CK-BL602-4SW-HS-03` |
| `lan_control` | yes | `enabled`, `disabled`, `not_shown`, or `unknown` |
| `uiid` | no | Positive integer from 1 through 65535, only when actually shown/known |
| `firmware_version` | no | Bounded version token (up to 64 characters), not free text |
| `visible_channel_count` | no | Positive integer from 1 through 64 representing the count visible in the source |
| `observed_at` | no | Explicit ISO date or date/time; the exact supplied precision and spelling are preserved |

Example minimal input (a schema example only, not device evidence):

```json
{
  "source_kind": "manual_transcription",
  "product_model_variant": "CK-BL602-4SW-HS",
  "lan_control": "unknown"
}
```

Run from the repository root:

```powershell
python tools/b1_device_evidence_intake.py --input .\candidate-input.json
```

Or pipe one JSON object on stdin. Normalized JSON goes to stdout by default. An optional `--output PATH` writes only to a new, explicitly selected local file; an existing path is never overwritten. Do not place real secrets/private identifiers in input. Rejection output is generic or names only a static field category; it never echoes supplied values or input paths.

## Privacy, consistency and authority limits

The tool rejects unknown fields rather than preserving, silently dropping or trying to redact them. It explicitly refuses device identifiers/keys, Wi-Fi identifiers/credentials, MAC/private address fields, account/user identifiers, tokens/authorization/cookies, passwords/key material and Matter commissioning/fabric fields. Input is not hashed or sent to an external service. Optional values omitted from input remain absent; no values are inferred from the product string.

For UIID 138/139/140/141 plus an explicitly supplied visible channel count, output may include a separate non-authoritative consistency diagnostic against the known 1/2/3/4-channel upstream mapping. Both supplied evidence values remain unchanged on mismatch, which is flagged for review. This diagnostic is not device confirmation and cannot reconcile an actual unit's variant.

The tool only prepares a safe candidate. Human review and a separately authorized B1 reconciliation are required before any actual-device fact can enter canonical evidence. It performs no OCR, screenshot/export parsing, cloud/API access, network operation, device control, hardware operation or Matter work.
