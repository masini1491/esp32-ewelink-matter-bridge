# TASKS

## Current Hot coordination

### SIM-1 — Host-side synthetic device simulator foundation

Status: `READY`

Goal: add a deterministic, reusable host-only synthetic device simulator around the existing portable `bridge_core` contracts so command/state/convergence behavior can be exercised without live LAN, hardware, Matter commissioning, or assumptions about unresolved CK-BL602 wire behavior. The simulator is intended to become a safe test backend for later diagnostics such as C2, but this Stage does not implement a Web UI.

Current authority / baseline:
- Repository: `masini1491/esp32-ewelink-matter-bridge`
- Branch: `main`
- Project pre-stage HEAD: `849a4c4e7db1f28cb82ceacc2f4620d84df8c536`
- Playbook baseline: `main`
- Producer-observed Playbook revision at admission: `3772e7e60213c99482dc201c064757075a8a48a9`
- Project AI mode: `ChatGPT+Codex`
- Existing contracts: `core/include/bridge_core/transport.hpp`, `core/include/bridge_core/device_model.hpp`, `docs/portable-core.md`, `VALIDATION.md`.

Actor split:
- ChatGPT owns this Stage's planning, contract freeze, coordination, and later result reconciliation.
- Codex owns only the implementation mutation / validation explicitly authorized below.
- Do not broaden into B1/B3 live evidence collection, protocol research, Web UI implementation, firmware runtime, or hardware work.

Execution profile:
- Root model: `GPT-6 Luna`
- Root reasoning: `Medium`
- Agent: `1`
- Execution mode: focused host-side implementation with deterministic tests
- Cheap-model evidence pass: `No`
- Child Delegation Forecast: `NONE`

Execution prerequisite recovery:
- The previous launch stopped before Stage execution because the local worktree contained only untracked Python bytecode caches under `tests/__pycache__/` and `tools/__pycache__/` while local `main` was behind `origin/main` with no local-only commit.
- Before safe-sync, Codex may remove only untracked `*.pyc` files contained under those two `__pycache__/` directories, and only after re-checking that no other dirty path is present. Any additional modified/untracked path, unfinished Git operation, local ahead/divergence, or ambiguity remains a STOP.
- After the permitted cleanup, require a clean tree, perform the normal fetch + fast-forward-only sync, then re-read latest governance and this current Hot Stage before implementation.
- This Stage also authorizes the minimum repository hygiene fix in `.gitignore` to ignore Python bytecode/cache output (`__pycache__/` and `*.py[cod]`, or an equivalent minimal rule) so host-side Python tooling does not recreate the same safe-sync blocker. Do not broaden `.gitignore` cleanup beyond this Python-cache purpose.

Implementation contract:
1. Add a host-only synthetic simulator layer outside `bridge_core`; preferred structure is a small `bridge_simulator` library under a dedicated simulator directory, built only for host/test use.
2. The simulator must use the existing `bridge_core::CommandTransport`, `CommandOrchestrator`, `UnifiedDeviceModel`, and current four-channel project target contract rather than duplicating production model semantics.
3. Keep execution deterministic and event-driven: no sockets, HTTP, mDNS, background threads, wall-clock sleeps, ESP-IDF, FreeRTOS, CHIP/esp-matter runtime, real credentials, or external services.
4. Minimum simulator capabilities:
   - connect / disconnect / stale / reconnect lifecycle against the portable model;
   - record submitted `CommandIntent` values;
   - configure the next synthetic transport result as accepted or rejected through the existing transport contract;
   - inject explicit synthetic on/off observations;
   - preserve the existing rule that transport acceptance does not itself mutate observed state;
   - expose enough read-only state for deterministic host tests and a future diagnostic adapter without creating a Web or network API in this Stage.
5. Minimum deterministic scenarios:
   - accepted command with no observation remains pending and does not manufacture observed state;
   - accepted + matching observation converges `Matched`;
   - accepted + opposite observation converges `Conflicted`;
   - rejected transport converges `Rejected`;
   - disconnect/stale preserves last observed value but clears freshness as defined by the current model;
   - reconnect alone does not restore freshness;
   - channel operations remain isolated across all four project-target channels.
6. The simulator is synthetic test infrastructure only. Do not encode UIID 138/139/140/141 as actual-device identities, do not claim exact CK-BL602 LAN behavior, and do not model unresolved encryption/wire schema as fact.
7. Keep the current `bridge_core` public API and four-channel semantics unchanged. If the simulator cannot be implemented cleanly without changing portable-core behavior/API, STOP and return the required change as a separate architecture candidate instead of modifying the core contract in this Stage.
8. Document only the minimum simulator boundary and validation evidence needed to prevent synthetic results from being confused with Network/Hardware/Matter evidence.

Authorized implementation mutation:
- `.gitignore` only for the minimum Python bytecode/cache ignore rule described above;
- new host-only simulator source/header paths under `simulator/**`;
- new simulator-focused host test source under `tests/**`;
- `CMakeLists.txt` only as needed to build/test the host-only simulator;
- `docs/portable-core.md` only for the simulator boundary;
- `VALIDATION.md` only for this Stage's Static/Test or Host evidence and explicit non-promotion boundary;
- `TASKS.md` only for this Stage's status bookkeeping.

Hard exclusions / STOP:
- No changes to `core/include/**`, `core/src/**`, `platform/**`, `.github/workflows/**`, dependency versions, partition/build target authority, or production firmware.
- No Web UI, HTTP API, browser assets, CLI protocol, persistence/database, live LAN/mDNS, hardware I/O, Matter commissioning/controller interaction, or external-service operation.
- No real `deviceKey`, Wi-Fi credential, cloud token/App ID, Matter fabric/commissioning material, or unsanitized capture.
- No new claim of `CONFIRMED_LOCAL`, Network PASS, Hardware PASS, or Matter interoperability PASS.
- Do not implement other CK-BL602 family variants or dynamic-channel production behavior in this Stage.
- If implementation reveals a portable-core defect or required semantic change, STOP with evidence; do not silently repair or redesign the core.

Validation / completion:
- simulator code is host-only and depends inward on `bridge_core`; `bridge_core` remains independent of simulator types;
- existing `bridge_host_tests` remain passing;
- new deterministic simulator tests cover the minimum scenarios above;
- normal CMake/CTest host path builds and passes on the available host environment;
- existing C3 compile probe contract remains unchanged; do not run or modify hardware/network/Matter validation for this Stage;
- `.gitignore` prevents repository-local Python `__pycache__` / `.pyc` output from reappearing as untracked safe-sync blockers;
- `git diff --check` PASS;
- changed files stay inside the authorized set;
- commit and push; confirm remote sync / HEAD according to current governance;
- after successful push, set only this Stage status to `AWAITING_CHATGPT_RECONCILIATION`, then STOP.
