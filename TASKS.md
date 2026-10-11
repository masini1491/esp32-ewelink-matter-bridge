# TASKS

## Current Hot coordination

### HC-004 — Python unittest discovery compatibility

Status: `READY`
Priority: `P3`
Campaign: `HC-2026-10-11` (final checkpoint)
Repository: `masini1491/esp32-ewelink-matter-bridge`; branch: `main`; Project AI mode: `ChatGPT+Codex`.
Producer-observed target pre-promotion `main`: `142f64d85c6075e1c5c1182b0ae63fbde3ba29dc`.
Playbook baseline: `main`; producer-observed revision: `65b6f1546cf3412aaa79ee272a752cdb4ca48f45`.
Predecessors HC-001, HC-002, HC-003 passed ChatGPT remote reconciliation. HC-003 implementation commit `142f64d85c6075e1c5c1182b0ae63fbde3ba29dc`; exact-commit Actions host job success and local 12/12 B1 intake, 8/8 D1 regression claims were reviewed. Completed Stage histories live in Git, not active queue.

Goal: remove `tests/test_simulator_webui.py` import-time required `--adapter` / `--web-root` parsing so conventional Python unittest discovery can import/discover test modules without failing, while preserving real simulator-backed tests in the CTest invocation that supplies a built adapter.

Current defect: the test module declares required CLI parameters and parses arguments at module import, resulting in `SystemExit` when Python unittest discovery imports it without those arguments. The existing CTest invocation explicitly passes these arguments and succeeds; that success does not establish general discovery compatibility.

Actor / execution:
- ChatGPT owns planning, coordination, and independent remote reconciliation; Codex owns only this Stage's authorized test harness implementation and validation.
- Root model `GPT-6 Luna`; root reasoning `Medium`; one root agent; cheap-model evidence pass `No`; child delegation forecast `NONE`.
- Only HC-004 is executable. Do not invent next stages or execute adjacent work.

Implementation contract:
1. Make module import and normal `unittest` discovery safe without required side-effecting CLI argument parsing. Preserve the existing `--adapter` / `--web-root` supported standalone/CTest execution path or provide a clearly defined compatible explicit test entry point.
2. Use a bounded, explicit fixture/setup prerequisite for tests that require a compiled `bridge_simulator_adapter` and web assets. When no adapter exists, tests depending on it may report an honest explanatory `skip` or prerequisite outcome; missing adapter must never be reported as an executed PASS.
3. Preserve all existing simulator/IPC tests, including HC-001's timeout/no-response/process-reaping regressions; do not weaken coverage, state machine semantics, loopback-only networking, or existing CTest contract.
4. Ensure test runner exit/error/skip reporting is unambiguous: discovery must not silently report `Ran 0 tests` as evidence of full compatibility, and CTest must still execute the actual built-adapter tests rather than skipping them.
5. Test standard discovery from the repository root using `python -m unittest discover -s tests -p "test_*.py"`, as well as the conventional `python -m unittest discover` command, with explicit attention to test count and skipped prerequisites. The latter may require explicit discovery guidance rather than added package/layout changes outside the allowlist. Validate CTest with the built adapter in the existing host build if available. Avoid source/package restructure unrelated to this task.
6. Run relevant Python suites and `git diff --check`; report test count, skips, failures and environment/toolchain limits truthfully.

Authorized mutation:
- `tests/test_simulator_webui.py`;
- only if essential, a minimal test-entry helper under `tools/**`;
- `VALIDATION.md` for a bounded HC-004 evidence entry if appropriate;
- `TASKS.md` for HC-004 status bookkeeping.
No other tracked-file modifications.

STOP / exclusions:
- No modifications to `core/**`, `simulator/**`, `webui/**`, production `tools/simulator_webui.py`, `CMakeLists.txt`, `platform/**`, dependency versions, firmware, real LAN/device/hardware, cloud or Matter code.
- If the standard discovery contract requires modifying `tests/__init__.py`, packaging or CMake outside the above allowlist, STOP and return the minimum architecture/scope decision instead of silently expanding mutation scope.
- No live network, device, hardware, firmware runtime, commissioning or Matter operation. A loopback-only synthetic host test remains Host/Test evidence, never Network/Hardware/Matter PASS.
- Commit/push, verify canonical remote HEAD and scope, set HC-004 to `AWAITING_CHATGPT_RECONCILIATION`, report execution/testing evidence, and STOP. ChatGPT will independently reconcile and then close this four-item campaign.

## Campaign execution gate

HC-004 is the only active checkpoint. After it has been independently accepted, ChatGPT may restore the minimum `TASKS.md` EMPTY Hot template. Do not fabricate or auto-admit follow-up items merely because this campaign completed. Existing `BACKLOG.md` commitments/candidates and all actual-device evidence gates remain unchanged.
