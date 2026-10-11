# TASKS

## Current Hot coordination

### HC-004 — Python unittest discovery compatibility

Status: `AWAITING_CHATGPT_RECONCILIATION`
Priority: `P3`
Revision: `HC-004-R1` — minimal discovery-package-marker allowance after read-only STOP; no prior implementation or validation PASS claimed.
Campaign: `HC-2026-10-11` (final checkpoint)
Repository: `masini1491/esp32-ewelink-matter-bridge`; branch: `main`; Project AI mode: `ChatGPT+Codex`.
Producer-observed target pre-promotion `main`: `142f64d85c6075e1c5c1182b0ae63fbde3ba29dc`.
Playbook baseline: `main`; producer-observed admission revision: `65b6f1546cf3412aaa79ee272a752cdb4ca48f45`; current scope-review revision: `bc43725aeda50c3540ab7ef320e31076843b9c1e`.
Predecessors HC-001, HC-002, HC-003 passed ChatGPT remote reconciliation. HC-003 implementation commit `142f64d85c6075e1c5c1182b0ae63fbde3ba29dc`; exact-commit Actions host job success and local 12/12 B1 intake, 8/8 D1 regression claims were reviewed. Completed Stage histories live in Git, not active queue.

Goal: remove `tests/test_simulator_webui.py` import-time required `--adapter` / `--web-root` parsing so conventional Python unittest discovery can import/discover test modules without failing, while preserving real simulator-backed tests in the CTest invocation that supplies a built adapter.

Current defect: the test module declares required CLI parameters and parses arguments at module import, resulting in `SystemExit` when Python unittest discovery imports it without those arguments. The existing CTest invocation explicitly passes these arguments and succeeds; that success does not establish general discovery compatibility.

STOP/revision evidence: Codex performed read-only HC-004 preflight at target `dba5482ef17f4ea54395896f6869e44afead2c8c` and correctly STOPPED with no mutation. Root `python -m unittest discover` reported `Ran 0 tests` / exit 5 because `tests/` lacks `__init__.py`, while `python -m unittest discover -s tests -p "test_*.py"` discovered 44 tests but hit import-time required-argument failure. ChatGPT confirmed the absent `tests/__init__.py` and retained the original test coverage/completion contract. This is a minimum same-Stage scope revision, not a new feature or blanket package-layout authority.

Actor / execution:
- ChatGPT owns planning, coordination, and independent remote reconciliation; Codex owns only this Stage's authorized test harness implementation and validation.
- Root model `GPT-6 Luna`; root reasoning `Medium`; one root agent; cheap-model evidence pass `No`; child delegation forecast `NONE`.
- Only HC-004 is executable. Do not invent next stages or execute adjacent work.

Implementation contract:
1. Make module import and normal `unittest` discovery safe without required side-effecting CLI argument parsing. Preserve the existing `--adapter` / `--web-root` supported standalone/CTest execution path or provide a clearly defined compatible explicit test entry point.
2. Use a bounded, explicit fixture/setup prerequisite for tests that require a compiled `bridge_simulator_adapter` and web assets. When no adapter exists, tests depending on it may report an honest explanatory `skip` or prerequisite outcome; missing adapter must never be reported as an executed PASS.
3. Preserve all existing simulator/IPC tests, including HC-001's timeout/no-response/process-reaping regressions; do not weaken coverage, state machine semantics, loopback-only networking, or existing CTest contract.
4. Ensure test runner exit/error/skip reporting is unambiguous: discovery must not silently report `Ran 0 tests` as evidence of full compatibility, and CTest must still execute the actual built-adapter tests rather than skipping them.
5. Test both `python -m unittest discover -s tests -p "test_*.py"` and conventional repository-root `python -m unittest discover`, with explicit test totals, skips and failures. The newly authorized empty `tests/__init__.py` package marker permits root recursive discovery; it must not contain test loading logic or cause another package/layout restructure. Both discovery modes must discover nonzero tests and must not fail on import-time CLI parsing. Missing adapter may skip only adapter-dependent tests, with explicit reason; complete simulator Web UI verification requires the built adapter through the unchanged CTest invocation, which must run its actual tests rather than skip them. Validate CTest with the built adapter in the existing host build if available.
6. Run relevant Python suites and `git diff --check`; report test count, skips, failures and environment/toolchain limits truthfully.

Authorized mutation:
- `tests/test_simulator_webui.py`;
- **New empty file only**: `tests/__init__.py`, to allow repository-root `unittest discover` traversal; no other package/layout changes;
- only if essential, a minimal test-entry helper under `tools/**`;
- `VALIDATION.md` for a bounded HC-004 evidence entry if appropriate;
- `TASKS.md` for HC-004 status bookkeeping.
No other tracked-file modifications.

STOP / exclusions:
- No modifications to `core/**`, `simulator/**`, `webui/**`, production `tools/simulator_webui.py`, `CMakeLists.txt`, `platform/**`, dependency versions, firmware, real LAN/device/hardware, cloud or Matter code.
- The missing `tests/__init__.py` prerequisite is now explicitly reviewed and admitted for this Stage **only as an empty package marker**. Further package restructuring, adding a nonempty test loader or changing CMake/other paths still requires STOP and a separate scope decision.
- No live network, device, hardware, firmware runtime, commissioning or Matter operation. A loopback-only synthetic host test remains Host/Test evidence, never Network/Hardware/Matter PASS.
- Commit/push, verify canonical remote HEAD and scope, set HC-004 to `AWAITING_CHATGPT_RECONCILIATION`, report execution/testing evidence, and STOP. ChatGPT will independently reconcile and then close this four-item campaign.

## Campaign execution gate

HC-004 is the only active checkpoint. After it has been independently accepted, ChatGPT may restore the minimum `TASKS.md` EMPTY Hot template. Do not fabricate or auto-admit follow-up items merely because this campaign completed. Existing `BACKLOG.md` commitments/candidates and all actual-device evidence gates remain unchanged.
