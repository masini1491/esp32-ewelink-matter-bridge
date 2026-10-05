# TASKS

## Current Hot coordination

### C2A — Simulator-backed diagnostic Web UI foundation

Status: `AWAITING_CHATGPT_RECONCILIATION`

Goal: add a self-contained host/PC diagnostic Web UI that is driven by the existing `bridge_simulator` synthetic device rather than duplicating device-model semantics in browser or Python code. This Stage is synthetic-only and exists to exercise operator flows, channel state, pending intent and convergence without B1 live-device evidence, live LAN, hardware, firmware runtime or Matter commissioning.

Current authority / baseline:
- Repository: `masini1491/esp32-ewelink-matter-bridge`
- Branch: `main`
- Project pre-stage HEAD: `601bfc5c08b32c47e1ad73f48e1ddecd2ce4422d`
- Playbook baseline: `main`
- Producer-observed Playbook revision at admission: `90e3b3fe692276c872e0eeb396751e6deb5c3e9d`
- Project AI mode: `ChatGPT+Codex`
- Existing implementation/evidence: `simulator/**`, `docs/portable-core.md`, `VALIDATION.md`.
- Related Cold item: `BACKLOG.md → C2` remains future live/device integration and is not executed by this Stage.

Actor split:
- ChatGPT owns planning, UI/machine-boundary contract, coordination, and later result reconciliation.
- Codex owns only the implementation mutation / validation explicitly authorized below.
- Do not perform B1/B3 evidence collection, live device integration, hardware, firmware runtime, Matter commissioning/interoperability, or backlog promotion.

Execution profile:
- Root model: `GPT-6 Luna`
- Root reasoning: `Medium`
- Agent: `1`
- Execution mode: focused host-only UI + simulator adapter implementation
- Cheap-model evidence pass: `No`
- Child Delegation Forecast: `NONE`

Architecture / machine-boundary contract:
1. The authoritative synthetic state machine remains `bridge_simulator::SyntheticDevice` / `bridge_core`. Browser JavaScript and any host adapter may present/transport state, but must not reimplement convergence, freshness, transport disposition, pending-intent, or four-channel model semantics.
2. Use a host-only adapter boundary between the browser and `bridge_simulator`. The adapter may expose a small local diagnostic API/protocol required by this UI, but it must remain synthetic-only and must not become a live eWeLink protocol/API contract.
3. The Web UI/server must bind to loopback only by default (`127.0.0.1` / equivalent localhost scope) and must not expose a LAN listener in this Stage.
4. Core UI assets must be self-contained in the repository. No CDN, remote font, analytics, cloud runtime, package registry dependency at runtime, or external web service.
5. Prefer existing toolchains/standard-library capabilities and keep dependencies minimal. Do not add a frontend framework/package manager unless implementation evidence shows the bounded UI cannot reasonably be delivered without one; if such a dependency becomes necessary, STOP and return it as a separate dependency/architecture decision.
6. Synthetic identity/status must be visibly labeled as synthetic/simulator data. The UI must never imply that a CK-BL602 device, LAN session, relay, Matter endpoint, or controller has been observed.
7. Human-facing status must distinguish at least availability, observed state, freshness, pending intent, transport disposition and convergence where applicable; unknown/pending/error states must not be represented as success.
8. Status semantics must not rely on color alone. Buttons/actions need clear text labels and disabled/unavailable explanation where applicable.
9. Secrets are out of scope. No `deviceKey`, Wi-Fi credentials, cloud token/App ID, Matter fabric/commissioning material, secret input, persistence, logs or examples.

Minimum operator flow:
- start the local diagnostic UI with a synthetic four-channel device;
- show that the surface is simulator-only / not connected to hardware;
- connect / disconnect / mark stale / reconnect;
- choose the next synthetic transport result (accepted or rejected);
- submit ON/OFF intent independently for CH1–CH4;
- inject explicit synthetic ON/OFF observations independently for CH1–CH4;
- display per-channel observed state, freshness, pending intent, transport disposition and convergence;
- show submitted synthetic command/event diagnostics sufficient to explain the current state without exposing raw secrets or pretending that UI feedback is lower-level validation evidence.

Implementation guidance:
- Prefer a small repository-owned host executable/adapter that directly owns a `SyntheticDevice` instance and a thin loopback-only Web-serving layer.
- A lightweight helper runtime already available in the repository/host may be used only if it remains host-only, self-contained for the project workflow, and does not duplicate simulator semantics.
- Keep the browser contract narrow and diagnostic-specific. It is not the future live-device API and must not constrain B1 protocol decisions.
- Keep C2A visually functional and readable rather than building a design-system project. One coherent diagnostic page is sufficient.

Authorized implementation mutation:
- new C2A host/UI paths under `tools/**`, `simulator/**`, or a new clearly host-only `webui/**` directory;
- new C2A-focused tests under `tests/**`;
- `CMakeLists.txt` only as needed to build/test a host executable/adapter;
- `docs/portable-core.md` only for simulator/UI boundary documentation;
- `VALIDATION.md` only for C2A Static/Test / Host evidence and explicit non-promotion boundary;
- `.gitignore` only if a new host-only C2A-generated cache/output needs a minimal ignore rule;
- `TASKS.md` only for this Stage's status bookkeeping.

Hard exclusions / STOP:
- No changes to `core/include/**`, `core/src/**`, `platform/**`, production firmware, ESP-IDF/esp-matter configuration, partition/build authority, or dependency versions.
- No live eWeLink LAN/mDNS/discovery/control, real device address, real relay action, external network service, hardware I/O, Matter commissioning/controller interaction, or cloud integration.
- No binding beyond loopback and no remote-access/security model in this Stage.
- No database/persistence/authentication system; synthetic diagnostic state may remain process-local and reset on restart.
- Do not implement C2 live/device integration or rewrite `BACKLOG.md`.
- No new claim of `CONFIRMED_LOCAL`, Network PASS, Hardware PASS, or Matter interoperability PASS.
- If implementation requires changing portable-core/simulator semantics, adding a material external dependency, or defining a live-device API, STOP and return the requirement as a separate architecture candidate.

Validation / completion:
- UI actions are backed by the real `bridge_simulator` implementation, not a duplicate JS/Python state machine;
- loopback-only binding is deterministic and tested or otherwise directly verifiable;
- core assets load without Internet/CDN dependency;
- focused tests cover browser/adapter machine contract enough to prove connect/disconnect/stale/reconnect, accept/reject, per-channel intent/observation and rendered state mapping;
- existing `bridge_simulator_tests` and `bridge_host_tests` remain passing;
- normal host build/test path passes in the available environment;
- `git diff --check` PASS;
- changed files stay within the authorized set;
- no live/network/hardware/Matter evidence level is promoted;
- commit and push; confirm remote sync / HEAD according to current governance;
- after successful push, set only this Stage status to `AWAITING_CHATGPT_RECONCILIATION`, then STOP.
