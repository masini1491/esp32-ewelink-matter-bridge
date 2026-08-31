# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`，branch `main`。
- Bootstrap、S1、S2A、S2B、S2C、M1 與 D1 offline evidence harness 已完成。
- Framework authority：ESP-IDF `v5.5.5` + `espressif/esp_matter ==1.6.0`；C3 `VIABLE_CONSTRAINED` 僅限 software-first compile/static resource evidence。
- Network、Hardware、Matter interoperability 均未驗證；CK-BL602 behavior 仍為 `UNKNOWN` / `HARDWARE_TEST_PENDING`，不得標為 `CONFIRMED_LOCAL`。
- 第一 consumer 仍限定 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03`；不得從其他 eWeLink/Sonoff device 推定其 UIID、wire schema、encryption applicability、channel numbering或 convergence semantics。
- 真實 credential、deviceKey、Wi-Fi password、Matter fabric material 不得進 Git、CI、fixture、log 或文件。

## D2A — Bounded observation runner / result-handoff adapter — NOT AUTHORIZED

- [ ] **Admission evidence**：2026-08-31 第二次 D2 retry 已確認同一 execution surface 的短命令 stdout round-trip 與 temporary-file round-trip 均可正常回傳，且 temporary file 可刪除；common Playbook 也已確認使用 current `main`。但在一次 30 秒 passive-only UDP/5353 mDNS observation 後，execution surface 再次未能回傳 temporary-file sanitized summary。故 blocker 已縮小為「long-running live observation → bounded result handoff」而非一般 stdout／temporary filesystem 不可用。
- [ ] **Stage objective**：建立最低充分、非 production 的 local runner / handoff adapter，使既有 observation capability 能被 bounded supervision，結束後留下可由後續短命令讀取的 sanitizer-safe result；優先包裝既有 observation tool，不新增 protocol feature、不修改 D1 sanitizer contract。
- [ ] D2A implementation / validation 預設 **local-only / synthetic-only**；不得因這個 Stage 自行進行 live LAN observation。可用 synthetic child process 模擬「固定等待 → bounded output → cleanup」以驗證 timeout、termination、result handoff 與 no-orphan semantics。
- [ ] Runner 必須 fail-closed、固定 hard timeout、沒有 infinite retry/background orphan；raw/temporary path 必須 repository 外或 ignored temporary location，且只允許將 D1-safe / bounded summary交給 caller。不得把 local IP、hostname、full deviceId、raw TXT、IV、ciphertext、deviceKey、token、Wi-Fi 或 Matter secret寫入 durable output。
- [ ] **Prefer wrapper, not parser**：若既有 observation capability 無法在不新增 substantive mDNS parser/collector、network dependency或下載新工具的前提下被安全包裝，D2A 必須 STOP並回報需要另一個明確設計／implementation Stage；不得在 D2A 內擴張成新的通用 mDNS stack。
- [ ] D2A 只解決 execution/observability boundary，不得宣告 Network PASS、Hardware PASS、Matter interoperability PASS，也不得把任何 CK-BL602 behavior提升為 `CONFIRMED_LOCAL`。
- [ ] 完成後依 Completion Evidence Guard檢查 runner behavior、bounded termination、result handoff、cleanup、secret boundary、scoped diff與 TASKS state；D2A 本身不授權重新執行 D2 live observation。

## D2 — Bounded live mDNS observation — BLOCKED / DEPENDS ON D2A / NOT AUTHORIZED

- [ ] **Latest retry evidence — `INSUFFICIENT OBSERVABILITY`**：以 project baseline `ae28fa7a09eae4f233b907235f80144b39225fd5`、common Playbook `6b898cb1610c6f7264e0e898d010b2456053829a` 執行；stdout preflight PASS、temporary-file round-trip PASS，之後進行一次 passive-only UDP/5353 mDNS 30 秒 observation，未執行 standard query。long-running command 完成後仍無可用 sanitized summary，因此無法判定是否見到 `_ewelink._tcp.local.`、無 target attribution、無 D1 classification、無 `CONFIRMED_LOCAL`、無 `Network PASS`。raw capture 未保存，temporary summary 未殘留，repository 未修改。
- [ ] D2 目前依賴 D2A 解決 bounded result handoff。D2A 完成也**不會自動授權**新的 live attempt；每次 D2 live observation仍需新的明確 user launch authorization。
- [ ] 下一次 D2 first contact 仍採最低充分 network activity：先 passive listen；只有在取得 service/TXT metadata 所必需且既有 tool semantics明確時，才允許一次標準 mDNS browse/resolve query。不得升級至其他 protocol或宣稱整個流程完全零 transmit。
- [ ] Observation 必須 one-shot / bounded；不得 background monitor、infinite retry、LAN sweep、port scan 或 arbitrary packet injection。
- [ ] Raw capture 不得 commit。若產生 raw observation，只可存在 temporary local storage必要期間，先經既有 D1 sanitizer/analyzer，再人工 review sanitized facts；raw identifier／secret不得進 model final report、Git、fixture、CI或 durable docs。
- [ ] 不得自動升級至 HTTP、`/zeroconf/*`、`getState`、deviceKey、decrypt、relay/channel control、Matter commissioning/control、BLE、firmware flash/boot、另一台 host、proxy或 cloud API。若 D2 evidence不足，保存最低有效 evidence並 STOP；下一層另開 Stage。
- [ ] D2 成功最多建立與**實際 mDNS observation**相符的 `Network PASS`；只有直接觀察且可靠 attribution 到 CK 的 facts 才能提升為 `CONFIRMED_LOCAL`。UIID、wire schema、encryption applicability、channel numbering、HTTP/getState semantics、convergence與 relay behavior未直接觀察時仍保持 `UNKNOWN` / `HARDWARE_TEST_PENDING`。
- [ ] D2 不得宣告 `Hardware PASS` 或 `Matter interoperability PASS`；完成後依 Completion Evidence Guard檢查 observation、sanitized evidence、classification與 TASKS lifecycle，且不得自行啟動下一 Stage。
