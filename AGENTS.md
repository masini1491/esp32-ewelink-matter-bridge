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

Authority hierarchy：user 當次明確指示 → 本 repository 最新正式 governance／technical source of truth → common playbook → `TASKS.md` → 舊 prompt、cached copy 或 memory。

## Git / permission / scope discipline

- 修改前確認 repository root、origin、branch、HEAD 與 working state。
- 遵守 common playbook 的 Permission-Gated Operation 與 Remote Git Permission Gate。
- 不得自行 `reset --hard`、force push、rewrite history、merge、rebase、stash，或刪除／丟棄來源不明的修改。
- 只執行使用者當次明確授權的 Stage；不得因 TASKS 或工具權限自行擴張 scope。
- 不提交 secrets、credentials、device keys、Wi-Fi passwords、tokens 或 private keys。

## Evidence and hardware boundary

文件、靜態檢查與 compile evidence 不等同於 runtime、device、bench 或 hardware validation。沒有實體 evidence 時，hardware validation 必須保持 Pending，不得推論為通過。

## Current bootstrap boundary

本 repository 目前仍處於 bootstrap；architecture、framework、target MCU（包含 C3、C6、S3 等選擇）與 protocol contract 尚未 freeze。不得由本檔案推導產品實作方向。
