# Project Instructions

## Repository identity

- Repository：`masini1491/esp32-ewelink-matter-bridge`
- 正式 branch：`main`
- GitHub `main` 是 remote source of truth。

## Common playbook routing

本專案採用 `masini1491/ai-development-playbook` 作為 common development baseline。只依當次 task 讀取最低必要內容，不完整掃描 playbook：

- Playbook baseline：`main`
- Project AI mode：`ChatGPT+Codex`
- 新 session 入口：selected Playbook baseline → `CHAT_INIT.md` → task-based minimum canonical routing。
- 依 task 需要讀取 `REPOSITORY_EXECUTION.md`、`CHATGPT_WORKFLOW.md`、`CODEX_EXECUTION.md`、`AI_CONTEXT.md`、`DEBUG_VALIDATION.md`、`RESEARCH_ARCHITECTURE.md`、`EMBEDDED_PROJECTS.md`、`UI_UX.md` 或 `TOOLCHAIN.md`；不在此重複保存 Playbook file list。

Authority hierarchy：user 當次明確指示 → 本 repository 最新正式 governance／technical source of truth → common playbook → `TASKS.md` → 舊 prompt、cached copy 或 memory。

## Git / permission / scope discipline

- 修改前確認 repository root、origin、branch、HEAD 與 working state。
- 遵守 common playbook 的 Permission-Gated Operation 與 Remote Git Permission Gate。
- 不得自行 `reset --hard`、force push、rewrite history、merge、rebase、stash，或刪除／丟棄來源不明的修改。
- 只執行使用者當次明確授權的 Stage；不得因 TASKS 或工具權限自行擴張 scope。
- 不提交 secrets、credentials、device keys、Wi-Fi passwords、tokens 或 private keys。

## Project minimum contract

- Canonical technical source(s): `docs/architecture.md`; `docs/portable-core.md`; `docs/build.md`; `VALIDATION.md`; `docs/references/README.md`
- Current coordination surface: `TASKS.md`
- Required validation: `VALIDATION.md` plus current Task/Stage-scoped validation
- Project-specific exceptions or restrictions: existing Evidence and hardware boundary plus Project-specific stable boundaries below。

## Coordination and evidence write boundary

- ChatGPT Coordination Write Allowlist：`/TASKS.md`、`/BACKLOG.md`、`/evidence/inbox/*.md`。
- `TASKS.md` 是 Hot coordination only；存在本身不授權執行。
- `BACKLOG.md` 是 Cold Registry；不屬於 ordinary bootstrap/default Context，沒有 execution authority；Candidate persistence 不代表 commitment，Cold → Hot 需依 current authority 經 ChatGPT planning/reconciliation。
- `evidence/inbox/*.md` 是 sanitized Evidence Staging Surface；不屬於 ordinary bootstrap/default Context，沒有 execution authority，也不是 canonical validation/architecture truth；正式結論須 reconciliation 至 `VALIDATION.md` 等 canonical owner。
- Evidence 在第一次 Git write 前必須 sanitized；不得提交 raw `deviceKey`、Wi-Fi credentials、Matter secrets、MAC/private-network identifiers、private endpoints 或 personal data。大型敏感/raw logs 留在 Git 外；Git 僅可保存安全 digest／metadata／hash／pointer。

## Evidence and hardware boundary

文件、靜態檢查與 compile evidence 不等同於 runtime、device、bench 或 hardware validation。沒有實體 evidence 時，hardware validation 必須保持 Pending，不得推論為通過。

Evidence levels and current Pending authority are defined in `VALIDATION.md`; upstream provenance routing is `docs/references/README.md`; project contracts are `docs/architecture.md`.

## Project-specific stable boundaries

- The first consumer is limited to `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` as four binary channels mapped to four bridged Matter On/Off endpoints. Other device families/UIIDs require a new Stage and explicit authorization.
- Contract dependency direction is `eWeLink Transport → eWeLink Protocol / Registry → Unified Device Model → Matter Adapter / Bridge → Matter over Wi-Fi`. Platform/Matter adapters depend on portable core; portable core must not expose ESP-IDF, FreeRTOS or Matter types.
- Matter endpoint identity must bind stably to canonical device identity plus channel index, never discovery order. Exact device LAN behavior remains upstream/hardware-pending until separately evidenced.
- `deviceKey`, Wi-Fi credentials and Matter fabric/commissioning material are secrets; they do not enter Git, fixtures, logs, README or examples. Cloud account/App ID/token provisioning is FUTURE / separate authority and is not a v1 runtime dependency.
- Live LAN operations, hardware control, commissioning, production firmware and additional device families remain out of scope until separately and explicitly authorized. Static or compile evidence must not be promoted to network, runtime, hardware or Matter interoperability PASS.

## Canonical project authority routing

- Current build, dependency, target and resource profile: `docs/build.md`.
- Architecture and portable-core contracts: `docs/architecture.md` and `docs/portable-core.md`.
- Current validation and D2/D3 observation evidence: `VALIDATION.md`.
- Upstream provenance and reference boundaries: `docs/references/README.md` and its linked source dossiers.
