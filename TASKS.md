# TASKS

## Current Hot coordination

### GOV-1 — Playbook adoption + coordination/evidence surface migration

Status: `AWAITING_CHATGPT_RECONCILIATION`

Goal: normalize this repository to the current AI Development Playbook adoption contract, persist `Project AI mode: ChatGPT+Codex`, and enable the selected coordination/evidence surfaces needed for upcoming work.

Current canonical pointers:
- Repository: `masini1491/esp32-ewelink-matter-bridge`
- Branch: `main`
- Project pre-stage HEAD: `78a2c405cfbd2bbea54a61b3194c6f3415586800`
- Playbook baseline: `main`
- Playbook HEAD observed at admission: `50c16aa7cf3c497ed7e0099a006f49acbd07956d`
- Playbook HEAD observed at reconciliation: `a5da45f7cc5229c1ee4b29f5105bce6370e54485`
- Project technical/validation authority remains in `docs/architecture.md`, `docs/portable-core.md`, `docs/build.md`, `VALIDATION.md`, and `docs/references/README.md`.

Execution profile:
- Root model: `Luna`
- Root reasoning: `Low`
- Agent: `1`
- Execution mode: `Focused governance / coordination migration`
- Cheaper pre-evidence: `No` — ChatGPT already completed the canonical audit.
- Child Routing Forecast: `NONE` — current scope is one tightly bounded governance migration with no material delegation benefit. Re-evaluate only if materially new runtime evidence changes the topology; do not create child delegation merely to change model/reasoning.

Authorized implementation mutation:
- `AGENTS.md`
- `BACKLOG.md`
- `evidence/inbox/README.md`
- `TASKS.md` only for this Stage's status bookkeeping; do not change the Stage contract or admit new work.

Required changes:
1. Normalize `AGENTS.md` to the current Playbook adoption contract:
   - exactly one `Playbook baseline: main`;
   - exactly one `Project AI mode: ChatGPT+Codex`;
   - new sessions route through selected Playbook baseline → `CHAT_INIT.md` → task-based minimum canonical routing, instead of mirroring the common Playbook file list;
   - preserve project-specific authority, hardware/evidence/security/secret/first-consumer boundaries and canonical project pointers;
   - selecting/adopting Playbook/mode/surfaces must not expand Current Write Target, Task/Stage, permission, credential, validation, hardware, release/deployment or external-service authority.
2. Set the project minimum contract in `AGENTS.md`:
   - `Canonical technical source(s): docs/architecture.md; docs/portable-core.md; docs/build.md; VALIDATION.md; docs/references/README.md`
   - `Current coordination surface: TASKS.md`
   - `Required validation: VALIDATION.md plus current Task/Stage-scoped validation`
   - `Project-specific exceptions or restrictions:` point to the existing Evidence and hardware boundary / Project-specific stable boundaries.
3. Declare the ChatGPT Coordination Write Allowlist as only:
   - `/TASKS.md`
   - `/BACKLOG.md`
   - `/evidence/inbox/*.md`
   All other paths remain read-only to ChatGPT unless higher project authority explicitly grants otherwise.
4. Define surface semantics:
   - `TASKS.md` = Hot coordination only; current executable / critical-path work; existence does not authorize execution.
   - `BACKLOG.md` = Cold Registry; not ordinary bootstrap/default Context; no execution authority; Candidate persistence does not imply commitment; Cold → Hot requires ChatGPT planning/reconciliation against current authority.
   - `evidence/inbox/*.md` = sanitized Evidence Staging Surface; not ordinary bootstrap/default Context; no execution authority; staging evidence is not canonical validation/architecture truth; formal conclusions require reconciliation into canonical owners such as `VALIDATION.md`.
   - Evidence must be sanitized before first Git write. Never commit raw `deviceKey`, Wi-Fi credentials, Matter secrets, MAC/private-network identifiers, private endpoints or personal data. Large sensitive/raw logs stay outside Git; Git may contain a safe digest/metadata/hash/pointer.
5. Create thin `BACKLOG.md` and seed only:
   - `B1 COMMITTED` — Device-specific LAN contract evidence. Trigger: materially new upstream evidence or separately authorized live/device evidence. Pointers: `docs/roadmap.md`, `VALIDATION.md`.
   - `B2 COMMITTED` — Physical target / carrier / pinout closure. Trigger: hardware target selection or preparation for hardware work. Pointers: `docs/roadmap.md`, `docs/build.md`.
   - `B3 COMMITTED` — Network PASS evidence. Trigger: separately authorized live LAN campaign with prerequisites ready. Existing D2/D3 negative observations are not Network PASS. Pointer: `VALIDATION.md`.
   - `B4 COMMITTED` — Hardware PASS evidence. Trigger: target ESP32 + CK-BL602 physical setup available and testing explicitly authorized. Pointer: `VALIDATION.md`.
   - `B5 COMMITTED` — Matter interoperability evidence. Trigger: bridge firmware/hardware ready and a named controller/scenario is available and explicitly authorized. Pointer: `VALIDATION.md`.
   - `C1 CANDIDATE` — ESP32-C6 / Thread capability. Trigger: explicit product requirement or architecture decision requiring Thread. Pointers: `docs/build.md`, `docs/roadmap.md`. Persistence does not make this committed work.
   Do not add completed S1/S2/D2/D3 history, CI-trigger optimization, or S3 fallback as standalone backlog work without its trigger.
6. Create thin `evidence/inbox/README.md` describing the evidence-staging contract/template. A record should preserve, when applicable: evidence identity; safe target/board/device identity; source/firmware/build/revision identity; measurement/test conditions; authorized action/scenario; observed result; timestamp meaning/precision; evidence classification/pending status; sanitization/provenance; completeness state; reconciliation target/status. Do not define a second validation taxonomy; point to `VALIDATION.md`.

Exclusions / STOP:
- Do not modify `README.md`, `VALIDATION.md`, `docs/*`, source, tests, scripts/tooling, build files, workflow/CI or any other path.
- Do not execute any BACKLOG item.
- Do not perform live network/hardware/Matter work.
- Do not run or modify Playbook-owned Adoption Doctor/tests; ChatGPT handles post-push canonical read-back and any ChatGPT-side adoption verification.
- If safe completion requires any path outside the authorized list, STOP rather than expanding scope.

Validation / completion:
- changed files for implementation are exactly `AGENTS.md`, `BACKLOG.md`, `evidence/inbox/README.md`, plus `TASKS.md` only for Stage status bookkeeping;
- `TASKS.md` keeps this same Stage identity and contract; after successful commit/push, set only `Status: AWAITING_CHATGPT_RECONCILIATION`;
- one Playbook baseline declaration, one Project AI mode declaration (`ChatGPT+Codex`), `Current coordination surface: TASKS.md`;
- bootstrap uses `CHAT_INIT.md`, no mirrored common Playbook file list;
- allowlist exactly TASKS/BACKLOG/evidence inbox;
- BACKLOG/evidence staging have no execution authority;
- existing project-specific hardware/security/evidence boundaries remain intact;
- no template placeholders remain in `AGENTS.md`;
- `git diff --check` PASS;
- commit and push; confirm remote sync/HEAD according to project governance; then STOP for ChatGPT reconciliation.


## Reconciliation delta — 2026-09-20

Remote read-back at project HEAD `6b294ebcc7edab174c15170e8e62c43919b0ddf4` confirmed the intended files and Cold/Evidence content, but GOV-1 is not yet complete. Fix only these closure gaps within the same Stage identity:

1. `AGENTS.md` still mirrors the common Playbook filenames in one consolidated bullet. Remove that filename list; keep only the thin `Playbook baseline → CHAT_INIT.md → task-based minimum canonical routing` bootstrap plus project-owned pointers.
2. Add a clear `## Authority boundary` (or semantically equivalent explicit boundary) stating that Playbook adoption, Project AI mode selection, and coordination/evidence surface enablement do not grant or expand Current Write Target, Task/Stage, repository write, execution, permission/credential, hardware, validation, release/deployment, external-service, secret, or data-egress authority.
3. Make the coordination write boundary explicit that paths outside `/TASKS.md`, `/BACKLOG.md`, and `/evidence/inbox/*.md` remain ChatGPT read-only unless higher project authority explicitly grants otherwise.

The Playbook advanced from the admission SHA to `a5da45f7cc5229c1ee4b29f5105bce6370e54485`. The intervening changes add untrusted-content instruction/data authority separation, BEH-022 routing, and a cloud deterministic-validation example; they do not change GOV-1's selected mode or coordination-surface semantics.

For this reconciliation-fix pass:
- implementation mutation: `AGENTS.md` only;
- `TASKS.md` may change only GOV-1 status/bookkeeping and this reconciliation delta;
- leave `BACKLOG.md` and `evidence/inbox/README.md` unchanged;
- after successful commit/push, set GOV-1 back to `AWAITING_CHATGPT_RECONCILIATION`;
- run `git diff --check` and STOP for ChatGPT reconciliation.


## Reconciliation delta — adoption-doctor marker closure

Remote semantic read-back at project HEAD `6d3a6f15e25d9cc9121d5ff6222204e13a984868` confirms the prior three reconciliation gaps are closed. One final deterministic-adoption compatibility pass remains.

Current Playbook `tools/adoption_doctor.py` at Playbook HEAD `a5da45f7cc5229c1ee4b29f5105bce6370e54485` would still emit WARN findings for the current `AGENTS.md` because:
1. `PROJECT_AUTHORITY_MARKER` requires the `## Authority boundary` section to also contain an explicit project-specific authority marker; the current wording does not contain the detector's expected project-authority semantics.
2. `NO_AUTHORITY_EXPANSION_MARKER` recognizes explicit wording such as `adoption does not grant` / `採用 Playbook 本身不會新增`; the current semantic equivalent `不授予或擴張` is clear to a human but is not recognized by the current deterministic doctor.

Fix only `AGENTS.md` wording so the existing semantic contract remains unchanged but is machine-detectable by the current adoption doctor. Prefer the current minimal-project wording pattern:
- under `## Authority boundary`, explicitly state that this file and this repository's formal technical/governance source of truth preserve project-specific authority;
- explicitly state that adopting the Playbook or selecting Project AI mode does not grant additional write/execution/deployment/secret authority (or use the current canonical equivalent recognized by the doctor).

Do not change mode, allowlist, coordination/evidence semantics, technical boundaries, BACKLOG, evidence staging, source/docs/tests/tooling/CI, or any other project behavior.

For this final closure pass:
- implementation mutation: `AGENTS.md` only;
- `TASKS.md` may change only GOV-1 status/bookkeeping;
- after successful commit/push and `git diff --check`, set GOV-1 back to `AWAITING_CHATGPT_RECONCILIATION`;
- STOP for ChatGPT reconciliation.
