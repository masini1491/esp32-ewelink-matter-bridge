# TASKS

## Current Hot coordination

### B1-E1 — Sanitized device-evidence intake foundation

Status: `AWAITING_CHATGPT_RECONCILIATION`

Goal: add a strict local-only intake/validation tool for the minimum actual-device/app metadata needed by B1. The tool must normalize user-transcribed evidence into a bounded machine-readable record while failing closed on unknown or secret-bearing fields. It does not perform OCR, parse arbitrary app exports, connect to eWeLink, inspect the LAN, control a device, or automatically promote evidence into canonical project truth.

Current authority / baseline:
- Repository: `masini1491/esp32-ewelink-matter-bridge`
- Branch: `main`
- Project pre-stage HEAD: `424c87c2171fe11996439092f1e322427094d4bc`
- Playbook baseline: `main`
- Producer-observed Playbook revision at admission: `a51121996e348326e506353954e5844382378fd3`
- Project AI mode: `ChatGPT+Codex`
- Parent Cold commitment: `BACKLOG.md → B1 COMMITTED — Device-specific LAN contract evidence`.
- Existing B1 staging evidence: `evidence/inbox/B1-upstream-revisit-2026-09-20.md`.
- Canonical evidence boundary: actual target UIID/channel count/LAN behavior remain unresolved until device-specific evidence is reviewed and reconciled.

Actor split:
- ChatGPT owns Stage planning, evidence-schema/authority boundary, and later reconciliation.
- Codex owns only the implementation mutation / deterministic validation explicitly authorized below.
- Do not perform B1 factual reconciliation, live LAN/network observation, hardware work, C2 integration, or promotion of any actual-device claim.

Execution profile:
- Root model: `GPT-6 Luna`
- Root reasoning: `Medium`
- Agent: `1`
- Execution mode: focused local evidence-intake tooling + deterministic tests
- Cheap-model evidence pass: `No`
- Child Delegation Forecast: `NONE`

Evidence-intake contract:
1. Implement a repository-owned, host-only CLI under `tools/**` using the existing Python runtime/standard library only. Do not add package/runtime dependencies.
2. Input is a deliberately small structured JSON record supplied via file and/or stdin. Do not ingest screenshots, arbitrary eWeLink exports, raw captures, account dumps, network traces or free-form blobs in this Stage.
3. Use a strict top-level allowlist. Minimum accepted evidence fields:
   - `source_kind`: bounded enum identifying how the values were observed/transcribed (for example eWeLink app/device UI/manual transcription; exact enum is implementation-owned but must not imply stronger provenance than provided);
   - `product_model_variant`: exact visible product/model string, bounded text;
   - `uiid`: optional positive integer when actually shown/known;
   - `firmware_version`: optional bounded visible firmware string;
   - `lan_control`: bounded semantic state such as `enabled`, `disabled`, `not_shown`, or `unknown`;
   - `visible_channel_count`: optional positive integer representing channels visibly exposed by the source;
   - optional observation date/time only if explicitly supplied, preserving the input precision rather than inventing missing precision.
4. Unknown top-level fields must fail closed rather than being silently copied, dropped or heuristically redacted. The tool must never accept generic free-form `notes`, raw payload, nested arbitrary objects or catch-all metadata.
5. Explicitly reject known sensitive/private identifiers and secret-bearing keys, including at minimum device ID, deviceKey, Wi-Fi SSID/BSSID, MAC, private IP/address, account/user identifiers, tokens/authorization/cookies, passwords/keys, and Matter commissioning/fabric material. Error output must identify only the forbidden field category/key needed for correction; never echo the supplied secret value.
6. Output is a normalized, bounded JSON evidence candidate suitable for human/ChatGPT review. It must clearly label itself as `candidate` / `unreconciled` (or equivalent) and must not claim `CONFIRMED_LOCAL`, Network PASS, B1 closure, or canonical truth.
7. Preserve evidence precision and contradictions. Missing values remain missing/unknown. Do not infer UIID, firmware, LAN Control or channel count from product-family text.
8. For upstream-known CK-BL602 UIIDs 138/139/140/141, the tool may compute a separate non-authoritative consistency diagnostic against the known 1/2/3/4-channel upstream mapping, but a mismatch must be preserved as evidence and surfaced for review, not rejected or rewritten.
9. Output must omit secrets/private identifiers entirely. Do not hash secrets or identifiers into stable fingerprints; hashing is not sanitization for this Stage.
10. No automatic repository write of user evidence. Normal operation writes only stdout or an explicitly user-selected local output path. A later ChatGPT reconciliation may separately stage sanitized evidence under the existing `evidence/inbox/**` authority after reviewing actual input.
11. The tool must not require network access and must not send input to any external service.

Minimum deterministic validation:
- valid minimal record normalizes successfully;
- fully populated safe record normalizes successfully;
- unknown field is rejected;
- representative forbidden keys are rejected without echoing their values;
- nested/free-form payload is rejected;
- missing optional fields remain unknown/absent rather than inferred;
- UIID 141 + channel count 4 reports consistent without upgrading authority;
- an upstream-mapping contradiction (for example UIID 138 + visible count 4) remains present and is flagged for review rather than rejected/corrected;
- malformed type/range/oversized text is rejected;
- observation timestamp/date precision is preserved and not fabricated;
- output contains no forbidden secret/private fields or supplied secret values.

Authorized implementation mutation:
- new B1-E1 local intake tool under `tools/**`;
- new focused tests under `tests/**`;
- `docs/d1-offline-evidence.md` or a new narrowly scoped `docs/**` evidence-intake document only if needed to explain safe usage/schema;
- `VALIDATION.md` only for B1-E1 Static/Test / Host evidence and explicit non-promotion boundary;
- `CMakeLists.txt` only if needed to register deterministic host tests in the existing test path;
- `.gitignore` only if the tool creates a new local-only generated output/cache convention;
- `TASKS.md` only for this Stage's status bookkeeping.

Hard exclusions / STOP:
- No changes to `core/**`, `simulator/**`, `webui/**`, `platform/**`, firmware/runtime code, dependencies, or C2/C2A implementation.
- No live eWeLink API/cloud login, LAN/mDNS/network probing, device control, hardware I/O or Matter operations.
- No OCR/screenshot parsing or arbitrary export/capture parser.
- No storage of real secrets/private identifiers in Git, fixtures, docs, logs or normalized output.
- Do not update `BACKLOG.md` or declare B1 complete.
- Do not reconcile an actual unit's UIID/channel/LAN facts in this Stage; this Stage only creates the safe intake mechanism.
- If useful evidence cannot be represented without a broader/raw/private schema or an external dependency/service, STOP and return that requirement as a separate architecture/evidence-handling decision.

Validation / completion:
- standard-library-only local tool; no external/network dependency;
- deterministic tests cover the minimum validation matrix above;
- existing relevant Python tests remain passing;
- existing host/CMake test path remains passing if modified;
- `git diff --check` PASS;
- changed files stay within the authorized set;
- no evidence level is promoted by the tool itself;
- commit and push; confirm remote sync / HEAD according to current governance;
- after successful push, set only this Stage status to `AWAITING_CHATGPT_RECONCILIATION`, then STOP.
