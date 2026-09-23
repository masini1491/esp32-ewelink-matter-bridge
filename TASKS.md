# TASKS

## Current Hot coordination

### B1-R — Canonicalize CK-BL602 variant evidence

Status: `AWAITING_CHATGPT_RECONCILIATION`

Goal: reconcile the already-staged 2026-09-20 B1 upstream evidence into the project's canonical technical owners so the repository no longer implies that the `CK-BL602-4SW-HS / -03` family name by itself proves a four-channel target. Preserve the product direction as a four-channel bridge target, but make exact target variant/UIID/capability confirmation a prerequisite before any live adapter or Matter endpoint binding claim.

Current authority / baseline:
- Repository: `masini1491/esp32-ewelink-matter-bridge`
- Branch: `main`
- Project pre-stage HEAD: `ab8caf81293b182a840b2b7d98ef2c37150807ce`
- Playbook baseline: `main`
- Producer-observed Playbook revision at admission: `64a7d63dd8f92fd41a45c218f8eb930e65bc970a`
- Project AI mode: `ChatGPT+Codex`
- Evidence input: `evidence/inbox/B1-upstream-revisit-2026-09-20.md` at current project main; treat it as staged evidence, not canonical truth by itself.

Actor split:
- ChatGPT has already completed upstream retrieval/provenance/synthesis and task admission.
- Codex owns only the residual repository mutation / validation described below.
- Do not redo upstream research unless current canonical evidence is internally inconsistent or a required exact source identity cannot be established from the staged record.

Execution profile:
- Root model: `GPT-6 Luna`.
- Root reasoning: `Medium`
- Agent: `1`
- Execution mode: focused cross-document technical reconciliation
- Cheap-model evidence pass: `No`
- Child Delegation Forecast: `NONE`

Authorized implementation mutation:
- `AGENTS.md`
- `docs/architecture.md`
- `docs/portable-core.md`
- `docs/references/sources/upstream-sources.md`
- `docs/roadmap.md`
- `VALIDATION.md`
- `TASKS.md` only for this Stage's status bookkeeping.

Required reconciliation:
1. Preserve the current product direction: the bridge's first supported consumer remains the **four-channel variant** within the `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` family, mapped to four logical channels / four Matter On/Off endpoints.
2. Remove or qualify any wording that treats the family string alone as evidence that an arbitrary unit is four-channel.
3. Canonicalize the staged upstream fact that the family appears in multiple channel/UIID variants; exact target variant/UIID/capability evidence is required before the project claims the attached device has four active channels or binds live protocol/Matter behavior to that assumption.
4. In `docs/architecture.md`, distinguish:
   - **project target contract**: four logical channels for the intended four-channel consumer;
   - **upstream device fact**: family is multi-variant;
   - **actual target-device fact**: exact UIID/channel capability remains unresolved until device-specific evidence.
   Do not collapse these into one status.
5. In `docs/portable-core.md`, keep the existing four-channel portable model/API unchanged, but explicitly state that this is the project target model for the intended four-channel variant and is not evidence that every CK-BL602 family unit is four-channel.
6. In `docs/references/sources/upstream-sources.md`, preserve the historical S1 pinned entries and append/record the 2026-09-20 revisit as a later evidence update rather than rewriting history. Preserve exact source identities/revisions from the staging record, including:
   - CoolKit official API revision `6ffbfd3d8e55122921ff5e4ccf3c3916c5593c00`;
   - iHost/eWeLink Smart Home evidence revision `5a8d7dec067f9196ada5879f31f71cbf6d595bff`;
   - SonoffLAN revision `5721d2f24c6800617b280c015c9b0af987a99469`.
   Keep official/first-party versus third-party authority boundaries explicit.
7. In `VALIDATION.md`, add the minimum current B1 reconciliation needed to state:
   - multi-variant/channel-family evidence is `CONFIRMED_UPSTREAM` only;
   - actual target UIID/channel count, encryption applicability, local discovery/control semantics and convergence remain `UNKNOWN / HARDWARE_TEST_PENDING` unless separately evidenced;
   - no `Network PASS`, `Hardware PASS`, or Matter interoperability PASS is created by this docs reconciliation.
8. In `docs/roadmap.md`, update only the deferred B1 evidence-gate wording so it reflects that upstream revisit/reconciliation is complete while actual-device discrimination remains pending.
9. Keep the B1 next discriminator unchanged in substance: sanitized actual-device/app evidence for exact variant/UIID/firmware/LAN Control/visible channel count.

Hard exclusions / STOP:
- No source, tests, build/tooling, CI/workflow, dependency, generated artifact, runtime, network, hardware, commissioning or external-service changes.
- Do not make the portable model dynamic-channel in this Stage.
- Do not change the four-endpoint product direction merely because the family is multi-variant.
- Do not claim that UIID 138/139/140/141 identifies the user's actual unit without actual-device evidence.
- Do not promote generic SonoffLAN behavior to `CONFIRMED_LOCAL`.
- Do not execute live LAN/hardware/Matter work.
- Do not modify `BACKLOG.md` or `evidence/**`; ChatGPT owns coordination/evidence bookkeeping outside this implementation pass.
- If reconciliation reveals that current source/API behavior must change rather than only canonical docs/evidence truth, STOP and return that as a separate implementation candidate.

Validation / completion:
- changed implementation files are limited to the six canonical/project-governance files listed above; `TASKS.md` may change only Stage status/bookkeeping;
- project first-consumer wording consistently says intended four-channel **variant**, not family-name-implies-four-channel;
- portable-core four-channel behavior/API is unchanged;
- S1 historical provenance remains historical; the 2026-09-20 revisit is additive/current evidence;
- validation taxonomy is not expanded or redefined;
- no PASS is promoted across evidence levels;
- `git diff --check` PASS;
- perform the project-required docs/governance validation that is actually applicable; do not run unrelated full hardware/network work;
- commit and push; confirm remote sync / HEAD according to current governance;
- after successful push, set only this Stage status to `AWAITING_CHATGPT_RECONCILIATION`, then STOP.
