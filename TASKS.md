# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3 — Bounded standard mDNS browse/resolve — NOT AUTHORIZED

- [ ] **Admission evidence**：D2 已完成一次 30 秒 passive-only `_ewelink._tcp.local.` observation，D2A cross-command handoff與 cleanup均通過；結果為 `NO SERVICE OBSERVED`，未建立 `Network PASS` 或任何 CK-specific `CONFIRMED_LOCAL`。Passive miss 不代表 CK-BL602 不支援 LAN/mDNS。
- [ ] **Objective**：在新的明確使用者授權下，使用既有 safe observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard mDNS browse/resolve query，以確認是否有 discovery/TXT response。只限 discovery layer，不得升級其他 protocol。
- [ ] Query 必須 one-shot / bounded；整體 live window固定短時間。不得 LAN/ARP sweep、port scan、arbitrary DNS/UDP probe、background monitor或 retry loop。
- [ ] 重用既有 `tools/bounded_result_runner.py` 與 D1 sanitizer contract。Raw stdout/stderr只留在 Git-local temporary runtime，不得進 model context、Git、fixture、docs或 final report；只有 sanitized facts可 durable保存。
- [ ] 若 observer output需要新增 substantive mDNS parser/collector、network dependency或下載新工具才能轉成 D1 input，STOP；另開 Stage，不得在 D3內實作。
- [ ] 只有直接觀察且可靠 attribution到 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 的 facts才可標 `CONFIRMED_LOCAL`。generic eWeLink response不得自動提升為 CK-specific evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、另一台 host、proxy或 cloud API。
- [ ] `Network PASS` 最多只可建立為本次實際成功的 bounded local mDNS discovery/response scope；不得推廣為 eWeLink LAN protocol、relay、hardware或 Matter PASS。
- [ ] 若 query後仍 `NO SERVICE OBSERVED`，記錄 bounded negative observation即可，不得推論 protocol不存在或 hardware failure；D3可完成但 Network PASS不成立。
- [ ] 完成後依 Completion Evidence Guard更新最低必要 `VALIDATION.md` / D3 evidence docs與 TASKS lifecycle；D3本身不授權 HTTP、decrypt、control或任何下一 Stage。
