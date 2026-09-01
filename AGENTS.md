# Project Instructions

## Repository identity

- Repository：`masini1491/esp32-ewelink-matter-bridge`
- 正式 branch：`main`
- GitHub `main` 是 remote source of truth。

## Common playbook routing

本專案採用 `masini1491/ai-development-playbook` 作為 common development baseline。只依當次 task 讀取最低必要內容，不完整掃描 playbook：

- Git、repository identity、permission、remote sync：`REPOSITORY_EXECUTION.md`
- validation、debug、root cause：`DEBUG_VALIDATION.md`
- architecture、research、external authority：`RESEARCH_ARCHITECTURE.md`
- ESP32、embedded、hardware：`EMBEDDED_PROJECTS.md`
- Codex model、context、prompt discipline：`CODEX_PROMPT_RULES.md`
- UI/UX、human-facing interaction：`UI_UX.md`
- toolchain、runtime executable contract：`TOOLCHAIN.md`

Authority hierarchy：user 當次明確指示 → 本 repository 最新正式 governance／technical source of truth → common playbook → `TASKS.md` → 舊 prompt、cached copy 或 memory。

## Git / permission / scope discipline

- 修改前確認 repository root、origin、branch、HEAD 與 working state。
- 遵守 common playbook 的 Permission-Gated Operation 與 Remote Git Permission Gate。
- 不得自行 `reset --hard`、force push、rewrite history、merge、rebase、stash，或刪除／丟棄來源不明的修改。
- 只執行使用者當次明確授權的 Stage；不得因 TASKS 或工具權限自行擴張 scope。
- 不提交 secrets、credentials、device keys、Wi-Fi passwords、tokens 或 private keys。

## Evidence and hardware boundary

文件、靜態檢查與 compile evidence 不等同於 runtime、device、bench 或 hardware validation。沒有實體 evidence 時，hardware validation 必須保持 Pending，不得推論為通過。

Evidence levels and current Pending authority are defined in `VALIDATION.md`; upstream provenance routing is `docs/references/README.md`; project contracts are `docs/architecture.md`.

## S1 architecture / contract authority

- S1 originally selected ESP32-S3 as the primary target family. S2A resolved the released dependency pair and reproducible S3 module/flash/PSRAM build profile; S2C subsequently promoted ESP32-C3 / 4 MB-class to the primary constrained software/build baseline. ESP32-S3-WROOM-1-N16R8 remains development/high-margin fallback, and ESP32-C6 remains optional future Thread capability. C3 evidence is software-first compile/static-resource evidence only, not production-ready, a validated physical board, a minimum product target, Hardware PASS or runtime-resource PASS.
- Contract dependency direction is `eWeLink Transport → eWeLink Protocol / Registry → Unified Device Model → Matter Adapter / Bridge → Matter over Wi-Fi`. Platform/Matter adapters depend on portable core; portable core must not expose ESP-IDF, FreeRTOS or Matter types.
- The first consumer is limited to `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` as four binary channels mapped to four bridged Matter On/Off endpoints. Other device families/UIIDs are not authorized without a new Stage.
- Matter endpoint identity must bind stably to canonical device identity plus channel index, not discovery order. Exact device LAN behavior remains upstream/hardware-pending until separately evidenced.
- `deviceKey`, Wi-Fi credentials and Matter fabric/commissioning material are secrets. They do not enter Git, fixtures, logs, README or examples. Cloud account/App ID/token provisioning is FUTURE / separate authority and is not a v1 runtime dependency.

## Current scope boundary

`docs/build.md` freezes ESP-IDF `v5.5.5` and esp-matter component `1.6.0`. The primary constrained build direction is ESP32-C3 / ESP32-C3-MINI-1-N4X (4 MB flash, no PSRAM); ESP32-S3-WROOM-1-N16R8 (16 MB flash / 8 MB Octal PSRAM) is development/high-margin fallback authority, not a failure. ESP32-C6 remains an optional future Thread-capability target. No profile is a purchased/validated board or product pinout.

S2B portable core is governed by `docs/portable-core.md`; S2C added verified Host CI and a C3 compile/resource gate classified `VIABLE_CONSTRAINED`. The core remains independent of ESP-IDF/Matter. D2/D3 completed bounded mDNS observations without a service response; they do not establish `Network PASS` or CK-specific `CONFIRMED_LOCAL`. Current network/runtime evidence is summarized in `VALIDATION.md`.

Live LAN operations, hardware control, commissioning, production firmware and additional device families remain out of scope until separately and explicitly authorized.
