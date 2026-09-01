# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3 — Bounded standard mDNS browse/resolve — NOT AUTHORIZED

- [ ] D3A process-exit lifetime guard 已完成 local/synthetic revalidation；D3仍須新的明確使用者授權，D3A completion 不構成 live query authorization。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 safe Windows observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard discovery/resolve，以取得可交給 D1 sanitizer的 evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local discovery/response scope。
