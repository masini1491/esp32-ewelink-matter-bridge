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
- 依 task-based minimum canonical routing 選取 Playbook owner；不在此重複保存 Playbook file list。

## Git / permission / scope discipline

Git、permission、scope 與 remote sync 遵循 selected Playbook canonical owner；本檔不重複保存 generic procedure。

## Project minimum contract

- Canonical technical source(s): `docs/architecture.md`; `docs/portable-core.md`; `docs/build.md`; `VALIDATION.md`; `docs/references/README.md`
- Current coordination surface: `TASKS.md`
- Required validation: `VALIDATION.md` plus current Task/Stage-scoped validation
- Project-specific exceptions or restrictions: existing Evidence and hardware boundary plus Project-specific stable boundaries below。

## Coordination and evidence write boundary

- ChatGPT Coordination Write Allowlist：`/TASKS.md`、`/BACKLOG.md`、`/evidence/inbox/*.md`。
- Allowlist 以外的 path 對 ChatGPT 保持 read-only，除非更高層 project authority 明確授權。
`TASKS.md`、`BACKLOG.md` 與 `evidence/inbox/*.md` 的 Hot／Cold／Evidence Staging semantics、default-load policy、promotion lifecycle 與 generic sanitization methodology 遵循 selected Playbook canonical owners；本檔僅宣告上述 enabled surfaces 與 local write boundary。

## Authority boundary

本檔與本 repository 的正式 technical/governance source of truth 保留 project-specific authority。Adopting the Playbook or selecting Project AI mode does not grant additional write/execution/deployment/secret authority，亦不新增或擴張 Current Write Target、Task/Stage、repository write、permission/credential、hardware、validation、external-service 或 data-egress authority。

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
