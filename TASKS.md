# TASKS

## Current Hot coordination

### HC-003 — B1 overlong JSON integer rejected safely

Status: `AWAITING_CHATGPT_RECONCILIATION`
Priority: `P2`
Campaign: `HC-2026-10-11`
Repository: `masini1491/esp32-ewelink-matter-bridge`; branch: `main`; Project AI mode: `ChatGPT+Codex`.
Producer-observed target pre-promotion `main`: `535b7ce1ec1892da079dd824c6207ecee11bd411`.
Playbook baseline: `main`; producer-observed revision: `65b6f1546cf3412aaa79ee272a752cdb4ca48f45`.
HC-001 and HC-002 completed independent ChatGPT remote reconciliation. HC-002 implementation commit `535b7ce1ec1892da079dd824c6207ecee11bd411`; associated Actions `host` job succeeded. Completion evidence remains in Git history and previous Stage contract, not an active Hot task.

Goal: ensure JSON input containing overlong integer tokens within the existing 16 KiB cap is rejected with structured `REJECTED` / exit 2, without traceback or user-input echo. Preserve B1-E1's strict allowlist, sanitization, and evidence-status invariants.

Current defect: `tools/b1_device_evidence_intake.py` calls `json.loads(...)` in `parse_input` but its catch list omits the `ValueError` that Python's integer digit limit can raise for a 5,000-digit JSON number. This bypasses `IntakeError` and breaks the CLI fail-closed outcome. Do not relax interpreter-global integer security limits.

Actor / execution:
- ChatGPT owns planning, coordination, and independent remote reconciliation. Codex owns only this Stage's authorized patch and validation.
- Root model `GPT-6 Luna`; root reasoning `Medium`; one root agent; cheap-model evidence pass `No`; child delegation forecast `NONE`.
- Only HC-003 is executable; HC-004 remains queued until ChatGPT separately reconciles HC-003 and promotes HC-004.

Implementation contract:
1. Restrict the fix to the JSON integer parsing failure boundary; use bounded integer token handling or convert the specific parse failure into a safe `IntakeError` without echoing user values. Do not catch arbitrary unrelated failures and mislabel them as invalid input.
2. Preserve the 16 KiB input size limit, all existing permitted fields, enum/type/range/precision checks, duplicate field rejection, and input/output non-overwrite semantics.
3. Keep `candidate_unreconciled` and non-authoritative UIID/channel consistency diagnostics; never introduce real device facts or expand the B1 schema.
4. Regression-test an overlong JSON integer (e.g., 5,000 digits) under the byte cap through both parser and CLI, explicitly asserting structured `REJECTED`, exit 2, no traceback/no input echo. Include ordinary JSON values, valid integer, existing malformed cases and secret redaction tests.

Authorized mutation:
- `tools/b1_device_evidence_intake.py`
- `tests/test_b1_device_evidence_intake.py`
- `VALIDATION.md` only for bounded HC-003 evidence, if necessary
- `TASKS.md` status bookkeeping only.
Do not edit any other tracked file.

Validation / STOP:
- Run focused B1 intake tests and relevant existing Python regression tests; run `git diff --check` and inspect scope. CMake/CTest or hardware/network/Matter tests are not required because this Stage does not touch the build or runtime contracts.
- No arbitrary app export, screenshot/OCR, device/cloud/LAN/mDNS, hardware, firmware, Matter or secret ingestion; no factual B1 reconciliation or evidence-level promotion.
- Commit and push, verify canonical remote HEAD/scope, update only HC-003 status to `AWAITING_CHATGPT_RECONCILIATION`, report exact validation, and STOP. Do not execute HC-004.

## Sequential follow-up checkpoints (not yet executable)

### HC-004 — Python unittest discovery compatibility

Status: `QUEUED_AFTER_HC-003_RECONCILIATION`
Priority: `P3`
Evidence: `tests/test_simulator_webui.py` parses required `--adapter` / `--web-root` arguments during module import, failing plain `unittest discover` even though CTest invokes it successfully.
Goal: make module import/discovery safe; keep actual simulator Web UI tests runnable with the intended built adapter and web-root fixture. If no adapter is available, mark the simulator suite as a clearly justified prerequisite skip (or provide an explicit uniform test entry point), never silently count unexecuted simulator tests as PASS.
Authorized implementation: `tests/test_simulator_webui.py`, and only if essential a minimal `tools/**` test-entry helper, optional bounded `VALIDATION.md` evidence, `TASKS.md` status bookkeeping. Validate plain `python -m unittest discover`, CTest-supplied adapter path and existing 3-suite CTest behavior, plus `git diff --check`. Preserve loopback-only synthetic semantics; no core, firmware, LAN, hardware or Matter work. Codex may act only after ChatGPT sets this Stage to `READY`; commit/push/status awaiting reconciliation, then STOP.

## Campaign execution gate

This is an explicitly user-authorized sequential correction campaign, not an invitation to perform all four mutations in a single coding-agent pass. Each Stage requires fresh safe-sync, current authority read, its own focused regression evidence, commit/push/read-back, independent ChatGPT reconciliation, then ChatGPT promotion of the next Stage. A blocked/failed Stage stops the campaign; next Stage is not automatically released. `BACKLOG.md` and B1/B2/B3/B4/B5/C2 candidate/committed evidence boundaries remain unchanged. No Static/Test or Host evidence is to be promoted to live Network/Hardware/Matter PASS.
