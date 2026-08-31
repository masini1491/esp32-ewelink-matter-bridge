# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`，branch `main`。
- Bootstrap、S1、S2A、S2B、S2C、M1 與 D1 offline evidence harness 已完成。
- Framework authority：ESP-IDF `v5.5.5` + `espressif/esp_matter ==1.6.0`；C3 `VIABLE_CONSTRAINED` 僅限 software-first compile/static resource evidence。
- Network、Hardware、Matter interoperability 均未驗證；CK-BL602 behavior 仍為 `UNKNOWN` / `HARDWARE_TEST_PENDING`，不得標為 `CONFIRMED_LOCAL`。
- 第一 consumer 仍限定 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03`；不得從其他 eWeLink/Sonoff device 推定其 UIID、wire schema、encryption applicability、channel numbering或 convergence semantics。
- 真實 credential、deviceKey、Wi-Fi password、Matter fabric material 不得進 Git、CI、fixture、log 或文件。

## D2 — Bounded live mDNS observation — BLOCKED / NOT AUTHORIZED

- [ ] **Previous attempt evidence — `INSUFFICIENT OBSERVABILITY`**：2026-08-31 已獲單次授權完成 repository／permission／passive-listen gate，執行 passive-only UDP/5353 mDNS multicast 30 秒；execution surface 未能把 observation summary 回傳，因此無法判定是否看見 `_ewelink._tcp.local.`，沒有可安全送入 D1 analyzer 的 observation summary，也沒有建立 `Network PASS` 或任何 `CONFIRMED_LOCAL` fact。該次未保存 raw capture、未修改 repository、未執行 standard mDNS query 或其他 protocol。
- [ ] **Playbook freshness guard**：前次 Codex 回報使用 `ai-development-playbook@84dec6d15c5d3057c865b11f8be7cefbb5d20440`，但後續 canonical GitHub review確認該 SHA 為 historical commit、不是當時 `main`。下一次 launch 必須先 fetch/sync 並確認 common Playbook 的 current `main` HEAD，不得沿用 cached / stale checkout。
- [ ] **Unblock condition**：下一次 live attempt 前，先確認 execution surface 能在 bounded observation 後提供最低必要 summary，或能把 observation 暫存於本機 temporary location供既有 D1 sanitizer/analyzer處理；仍不得為了繞過 observability缺口自行安裝新 network dependency、改用另一台 host、掃描、HTTP、cloud API或其他 workaround。若必須新增 live collector／adapter，另開 implementation Stage並取得明確授權。
- [ ] **Explicit user authorization required**：每次新的 live observation 都需新的明確使用者授權，才可在 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 所在 LAN 做一次 bounded、read-only `_ewelink._tcp.local.` observation。
- [ ] First contact 採最低充分 network activity：先 passive listen；只有在取得 service/TXT metadata 所必需時，才允許標準 mDNS browse/resolve query。不得把「read-only」誤解成可以升級到其他 protocol，亦不得宣稱整個流程完全零封包 transmit。
- [ ] Observation 必須 one-shot / bounded，使用固定短時間窗；不得 background monitor、infinite retry、LAN sweep、port scan 或 packet injection。
- [ ] Raw capture 不得 commit。若產生 raw observation/capture，只保留在本機工作區必要期間，先經 D1 sanitizer/analyzer，再人工 review 哪些 sanitized facts 具 durable evidence價值。
- [ ] 不得自動升級至 HTTP、`/zeroconf/*`、`getState`、deviceKey、decrypt、relay/channel control、Matter commissioning/control、firmware flash/boot 或其他 live mutation。若 mDNS evidence不足，保存目前可觀察 evidence並 STOP；下一層 evidence另開 Stage。
- [ ] 若 execution environment 無法存取同一 LAN、mDNS multicast或所需 read-only network capability，依 Playbook permission/environment規則 STOP並回報；不得改用 HTTP、掃描、另一台主機、proxy、cloud API或其他 workaround繞過。
- [ ] D2 成功最多可建立與**本次實際 mDNS observation**相符的 `Network PASS`，並將直接觀察到的 CK-BL602 service/TXT/discovery facts個別提升為 `CONFIRMED_LOCAL`。未直接觀察到的 UIID、wire schema、encryption applicability、channel numbering、HTTP/getState semantics與 convergence behavior仍保持 `UNKNOWN` / `HARDWARE_TEST_PENDING`。
- [ ] D2 不得宣告 `Hardware PASS` 或 `Matter interoperability PASS`；這兩層仍需各自明確授權且符合 `VALIDATION.md` 的真實 target/scenario evidence。
- [ ] 完成後依 Completion Evidence Guard檢查實際 observation、sanitized evidence、evidence classification與 TASKS state；D2本身不授權任何下一 Stage。
