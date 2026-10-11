# TASKS

## Current Hot coordination

### HC-001 — Bound simulator Web UI child IPC and shutdown

Status: `READY`
Priority: `P1`
Campaign: `HC-2026-10-11` (four confirmed repository health-check corrections; sequential checkpoints)
Repository: `masini1491/esp32-ewelink-matter-bridge`; branch: `main`; Project AI mode: `ChatGPT+Codex`.
Producer-observed target pre-admission `main`: `40e6db0df492289ff7b8ce099d4654ccf36dc6d5`.
Playbook baseline: `main`; producer-observed revision: `65b6f1546cf3412aaa79ee272a752cdb4ca48f45`.

Goal: eliminate indefinite waits caused by `tools/simulator_webui.py` reading a nonresponsive simulator child through blocking `readline()`, including its `close() → request("quit")` path. Preserve the existing simulator-backed, loopback-only synthetic UI and machine contract.

Actor and execution:
- ChatGPT owns planning, coordination, and independent remote reconciliation; Codex owns only this Stage's authorized implementation/validation.
- Root model: `GPT-6 Luna`; root reasoning: `High`; one root agent; cheap-model evidence pass: `No`; child delegation forecast: `NONE`.
- Only HC-001 is executable. HC-002/003/004 below are admitted follow-up checkpoints, **not** executable until ChatGPT separately promotes each after successful prior reconciliation. Do not continue automatically.

Required behavior / acceptance:
1. Make **every** adapter request/response wait, including ordinary `/api/state`, `/api/actions`, and graceful shutdown, explicitly time-bounded on Windows/MSVC/Python host and other supported hosts. A byte/line bound does not replace a wall-time bound.
2. On nonresponsive, partial-output, exited, malformed or oversized child response, return an honest bounded unavailable/error outcome to callers. Ensure failed IPC cannot leave an HTTP handler waiting forever; distinguish simulator unavailable/timeout from malformed user input.
3. Graceful shutdown may attempt `quit`, but must not block access to terminate/kill/reap fallback. Stop only the child process this server owns. Bound shutdown, clean up pipe handles/worker resources and prevent orphan child/thread/HTTP listener.
4. Keep state-machine ownership in C++ `SyntheticDevice`; do not duplicate convergence/freshness logic in Python or JavaScript. Preserve loopback-only binding, local-only assets, synthetic-only evidence, current endpoint semantics for healthy child.
5. Deterministic regression tests must exercise healthy normal response and close, child never writes output, child emits incomplete response but does not exit, child ignores `quit`, process unexpectedly exits, and timeout cleanup. Verify tests complete in bounded time and owned process is reaped.
6. Run focused Python UI tests, existing relevant Python tests, host CMake/CTest suites (where locally available), `git diff --check`, and inspect modified-file scope. Mark unavailable validation honestly; no invented PASS.

Authorized mutation: `tools/simulator_webui.py`, `tests/test_simulator_webui.py`, narrowly needed host-focused tests under `tests/**`, `VALIDATION.md` for HC-001 evidence, and `TASKS.md` for status only. If a new support helper is unavoidable, STOP with a narrowly scoped architecture proposal instead of silently expanding paths/dependencies.

STOP / exclusions:
- No changes to `core/**`, `simulator/**`, `webui/**`, `platform/**`, `CMakeLists.txt`, dependency versions, firmware, real LAN/device, hardware, Matter or Cloud behavior.
- No global process kill, indefinite retry, network listener beyond IPv4 loopback, external runtime/package install, or secret exposure.
- If fixing bounded IPC requires changing existing adapter protocol or public semantics beyond this Stage, STOP for architecture review.
- After implementing and testing HC-001 only: commit/push, confirm remote HEAD and scope, update **only HC-001** status to `AWAITING_CHATGPT_RECONCILIATION`, report concrete evidence, then STOP. ChatGPT reviews and unlocks HC-002 separately.

## Sequential follow-up checkpoints (not yet executable)

### HC-002 — D1 malformed service type fails closed

Status: `QUEUED_AFTER_HC-001_RECONCILIATION`
Priority: `P2`
Evidence: `tools/ewelink_capture_analyzer.py` calls `service.get(...)` before validating `service` is a dict. JSON `service: null`, array, number or string can cause `AttributeError`.
Goal: validate container/type before dereferencing, consistently classify malformed JSON-derived service values as `MALFORMED / UNKNOWN` without exception/traceback and preserve valid D1 evidence behavior.
Authorized implementation: `tools/ewelink_capture_analyzer.py`, `tests/test_capture_analyzer.py`, optional bounded `VALIDATION.md` evidence, `TASKS.md` status bookkeeping. Tests include null/list/number/string service, valid/invalid txt, existing capture cases and `git diff --check`. Do not modify D1 real observation authority, network/hardware behavior or other tools. Codex may act only after ChatGPT sets this Stage to `READY`; commit/push/status awaiting reconciliation, then STOP.

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
