# TASKS

## Current Hot coordination

### GOV-2 — Project governance ownership slimming

Status: `AWAITING_CHATGPT_RECONCILIATION`

Goal: align this repository's `AGENTS.md` with the current AI Development Playbook ownership architecture by moving duplicated shared methodology back to its upstream canonical owners while preserving all project-specific governance, authority, technical boundaries, and enabled coordination/evidence surfaces. This is a subtractive governance-only Stage and must not change product/runtime behavior or technical truth.

Current authority / baseline:
- Repository: `masini1491/esp32-ewelink-matter-bridge`
- Branch: `main`
- Project pre-stage HEAD: `a14536c22e10edcfdcd28e0560e2917ea0870190`
- Playbook baseline: `main`
- Playbook HEAD observed at admission: `42fcd13205df8c351d41ff7df1a4ff51cede6c85`
- Project AI mode: `ChatGPT+Codex`

Execution profile:
- Root model: `Luna`
- Root reasoning: `Low`
- Agent: `1`
- Execution mode: `Focused docs/governance normalization`
- Cheap-model evidence pass: `No` — ChatGPT already completed the current ownership audit.
- Child Routing Forecast: `NONE` — one bounded `AGENTS.md` normalization has no material delegation benefit.

Authorized mutation:
- `AGENTS.md`
- `TASKS.md` only for this Stage's status bookkeeping.

Required normalization in `AGENTS.md`:
1. Preserve the thin adoption/bootstrap layer:
   - repository identity / branch / remote authority;
   - exactly one `Playbook baseline: main`;
   - exactly one `Project AI mode: ChatGPT+Codex`;
   - selected Playbook baseline → `CHAT_INIT.md` → task-based minimum canonical routing;
   - do not add a copied Playbook owner/file catalogue.
2. Preserve the project minimum contract exactly in substance:
   - canonical technical source mapping;
   - current coordination surface `TASKS.md`;
   - required validation routing;
   - project-specific exceptions/restrictions pointer.
3. Preserve project-specific authority and no-authority-expansion wording.
4. Preserve the exact enabled ChatGPT coordination/evidence write allowlist:
   - `/TASKS.md`
   - `/BACKLOG.md`
   - `/evidence/inbox/*.md`
   Paths outside the allowlist remain ChatGPT read-only unless higher project authority explicitly grants otherwise.
5. Slim duplicated shared methodology:
   - remove the project-local generic authority-hierarchy mirror when the existing project authority boundary + selected Playbook owner already covers it;
   - collapse generic Git / permission / safe-sync / scope-procedure wording into minimum routing to the selected Playbook canonical owner; do not keep a local copy of generic Git safety policy;
   - keep only project-specific secret/security deltas that are not already preserved more precisely below;
   - for `TASKS.md`, `BACKLOG.md`, and `evidence/inbox/*.md`, preserve which surfaces are enabled and the exact local write boundary, but route shared Hot / Cold / Candidate / Committed / Evidence Staging semantics, default-load policy, promotion lifecycle, and generic sanitization methodology to the selected Playbook canonical owners instead of redefining them locally;
   - retain any project-specific sanitization restrictions that are genuinely stricter/specific to this bridge.
6. Preserve all project-specific engineering truth unchanged:
   - Evidence / hardware boundary;
   - first-consumer restriction as currently written;
   - dependency direction / portable-core isolation;
   - stable Matter endpoint identity;
   - deviceKey / Wi-Fi / Matter secret boundaries;
   - live LAN / hardware / commissioning / production-firmware explicit-authorization boundary;
   - no promotion of static/compile evidence into network/runtime/hardware/Matter PASS;
   - canonical project technical routing.
7. Do **not** perform the separately identified B1 technical reconciliation in this Stage. In particular, do not alter the current CK-BL602 / four-channel project contract wording, `docs/architecture.md`, `docs/portable-core.md`, `VALIDATION.md`, or any B1 evidence. That technical reconciliation remains a separate evidence-driven decision.

Hard exclusions:
- Do not modify `BACKLOG.md`, `evidence/**`, `README.md`, `VALIDATION.md`, `docs/**`, source, tests, scripts/tooling, build files, CI/workflows, manifests, lockfiles, or any other path.
- Do not change Project AI mode, the ChatGPT allowlist, product scope, architecture, validation truth, hardware status, or B1 evidence state.
- Do not execute any BACKLOG item or live network/hardware/Matter work.
- If safe completion requires a technical-contract change or a path outside the authorized mutation list, STOP instead of expanding scope.

Validation / completion:
- implementation diff is limited to `AGENTS.md`; `TASKS.md` changes only Stage status/bookkeeping;
- exactly one Playbook baseline declaration and one Project AI mode declaration remain;
- bootstrap still routes through `CHAT_INIT.md` and no mirrored Playbook file list is introduced;
- project minimum contract, authority boundary, exact allowlist, hardware/evidence/security boundaries, and canonical project routing remain materially unchanged;
- generic shared methodology duplication is reduced rather than moved to a new local section;
- no technical/product/validation semantics change;
- `git diff --check` PASS;
- commit and push; confirm remote sync / HEAD according to project governance;
- after successful push, set only this Stage status to `AWAITING_CHATGPT_RECONCILIATION`, then STOP.
