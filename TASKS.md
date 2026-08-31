# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3 — Bounded standard mDNS browse/resolve — NOT AUTHORIZED

- [ ] **Latest attempt evidence — capability gate STOP**：2026-08-31 在 project HEAD `53184b07a9258961e0e634b3053bcfaed3000918`、Playbook `6b898cb1610c6f7264e0e898d010b2456053829a` 下檢查；本機只有 `Resolve-DnsName`，沒有既有已知語意的 native mDNS DNS-SD browse/resolve observer，因此在 live operation前安全 STOP。D2A未啟動、live duration 0 秒、沒有 raw evidence、repo沒有 durable change、沒有 Network PASS。
- [ ] **Objective**：D3A完成後，在新的明確使用者授權下，使用 safe observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard mDNS browse/resolve query，以確認是否有 discovery/TXT response。只限 discovery layer，不得升級其他 protocol。
- [ ] Query 必須 one-shot / bounded；不得 LAN/ARP sweep、port scan、arbitrary DNS/UDP probe、background monitor或 retry loop。
- [ ] Raw observer output只可留在 Git-local temporary runtime，經既有 D1 sanitizer contract處理後只有 sanitized facts可 durable保存或進 model reasoning。
- [ ] 只有直接觀察且可靠 attribution到 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 的 facts才可標 `CONFIRMED_LOCAL`；generic eWeLink response不得自動提升為 CK-specific evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、另一台 host、proxy或 cloud API。
- [ ] `Network PASS` 最多只可建立為本次實際成功的 bounded local mDNS discovery/response scope；若 query後仍 `NO SERVICE OBSERVED`，D3可完成但 Network PASS不成立，也不得推論 protocol不存在或 hardware failure。
- [ ] 完成後依 Completion Evidence Guard更新最低必要 validation/evidence與 TASKS lifecycle；D3本身不授權 HTTP、decrypt、control或任何下一 Stage。
