# TASKS

## Current Hot coordination

### HC-002 — D1 malformed service type fails closed

Status: `AWAITING_CHATGPT_RECONCILIATION`
Priority: `P2`
Campaign: `HC-2026-10-11`
Repository: `masini1491/esp32-ewelink-matter-bridge`; branch: `main`; Project AI mode: `ChatGPT+Codex`.
Producer-observed target pre-promotion `main`: `87d69db24acb54f66f9d6f3c6144742757cf9ca9`.
Playbook baseline: `main`; producer-observed revision: `65b6f1546cf3412aaa79ee272a752cdb4ca48f45`.
Predecessor HC-001 passed ChatGPT remote reconciliation; exact-main GitHub Actions `validate` run `38113012284` concluded success. HC-001 completed history lives in Git history/`VALIDATION.md`, not active Hot.

Goal: ensure malformed `service` values in offline D1 captures fail closed instead of raising `AttributeError` from `service.get()` before its type is checked. Preserve existing valid D1 analyzer behavior, classifications and evidence boundary.

Current defect: `tools/ewelink_capture_analyzer.py` obtains `service = capture.get("service", {})`, then calls `service.get("txt", {})` and `service.get("name", "")` before verifying `service` is a dict. Input `service: null`, list, number or string crashes rather than returning `{"status":"MALFORMED","classification":"UNKNOWN"}`.

Actor / execution:
- ChatGPT owns planning, coordination and independent remote reconciliation. Codex owns only HC-002 authorized implementation and validation.
- Root model `GPT-6 Luna`; root reasoning `Medium`; one root agent; cheap-model evidence pass `No`; child delegation forecast `NONE`.
- Only HC-002 is executable. HC-003/004 remain queued until explicitly promoted by ChatGPT after HC-002 is reconciled.

Implementation contract:
1. Validate `service` as a mapping/dict **before** any `.get()` or other mapping operations. Keep `txt` / `name` type checks and existing analyzer output contract.
2. Invalid JSON-derived `service` types (`null`, array, number, string, boolean) must return `MALFORMED / UNKNOWN` as a structured result, without unhandled exceptions or raw input echo.
3. Do not broaden to unrelated capture semantics, introduce new identity inference, or change D1 evidence/Network PASS classifications.

Authorized mutation: `tools/ewelink_capture_analyzer.py`, `tests/test_capture_analyzer.py`, optional bounded `VALIDATION.md` HC-002 evidence, and `TASKS.md` HC-002 status only. No other tracked files.

Validation:
- Add deterministic tests for malformed service types and invalid `txt` while preserving valid D1 fixtures and privacy/redaction behavior.
- Run focused D1 tests plus relevant existing Python regression tests where feasible; `git diff --check` and changed-file scope.
- If tests unavailable or unexpected neighboring defect requires scope expansion, STOP and report evidence without silently patching additional files.
- No live eWeLink API/cloud, mDNS/LAN, device/hardware, firmware, Matter or commissioning operation; no inferred `CONFIRMED_LOCAL`, Network/Hardware/Matter PASS.
- Commit/push, verify canonical remote HEAD/scope, set only HC-002 status to `AWAITING_CHATGPT_RECONCILIATION`, report, and STOP. Do not start HC-003/004.

## Sequential follow-up checkpoints (not yet executable)

### HC-003 — B1 overlong JSON integer rejected safely

Status: `QUEUED_AFTER_HC-002_RECONCILIATION`
Priority: `P2`
Evidence: `tools/b1_device_evidence_intake.py` JSON parse of a 5,000-digit integer within the 16 KiB size cap can raise `ValueError` and produce traceback/exit 1, rather than safe structured `REJECTED`/exit 2.
Goal: preserve 16 KiB and all existing B1-E1 strict/sanitized input contracts; bound integer parsing or classify this exact JSON numeric parse failure safely without echoing input values.
Authorized implementation: `tools/b1_device_evidence_intake.py`, `tests/test_b1_device_evidence_intake.py`, optional bounded `VALIDATION.md` evidence, `TASKS.md` status bookkeeping. Tests cover overlong digits and safe output/exit code, ordinary valid JSON numbers, rejects, source precision, no secret echoes, existing suite and `git diff --check`. No acceptance of raw export, device evidence promotion, LAN, device or firmware work. Codex may act only after ChatGPT sets this Stage to `READY`; commit/push/status awaiting reconciliation, then STOP.

### HC-004 — Python unittest discovery compatibility

Status: `QUEUED_AFTER_HC-003_RECONCILIATION`
Priority: `P3`
Evidence: `tests/test_simulator_webui.py` parses required `--adapter` / `--web-root` arguments during module import, failing plain `unittest discover` even though CTest invokes it successfully.
Goal: make module import/discovery safe; keep actual simulator Web UI tests runnable with the intended built adapter and web-root fixture. If no adapter is available, mark the simulator suite as a clearly justified prerequisite skip (or provide an explicit uniform test entry point), never silently count unexecuted simulator tests as PASS.
Authorized implementation: `tests/test_simulator_webui.py`, and only if essential a minimal `tools/**` test-entry helper, optional bounded `VALIDATION.md` evidence, `TASKS.md` status bookkeeping. Validate plain `python -m unittest discover`, CTest-supplied adapter path and existing 3-suite CTest behavior, plus `git diff --check`. Preserve loopback-only synthetic semantics; no core, firmware, LAN, hardware or Matter work. Codex may act only after ChatGPT sets this Stage to `READY`; commit/push/status awaiting reconciliation, then STOP.

## Campaign execution gate

This is an explicitly user-authorized sequential correction campaign, not an invitation to perform all four mutations in a single coding-agent pass. Each Stage requires fresh safe-sync, current authority read, its own focused regression evidence, commit/push/read-back, independent ChatGPT reconciliation, then ChatGPT promotion of the next Stage. A blocked/failed Stage stops the campaign; next Stage is not automatically released. `BACKLOG.md` and B1/B2/B3/B4/B5/C2 candidate/committed evidence boundaries remain unchanged. No Static/Test or Host evidence is to be promoted to live Network/Hardware/Matter PASS.
