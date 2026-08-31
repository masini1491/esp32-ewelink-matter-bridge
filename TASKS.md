# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3A — Windows native DNS-SD observer adapter — NOT AUTHORIZED

- [ ] **Admission evidence**：D3 capability gate 已安全 STOP，未執行 live query。Current Windows environment僅確認有 `Resolve-DnsName`，沒有已知語意的 `dns-sd` / Avahi 類 DNS-SD browse/resolve observer；既有 project tooling也不是 mDNS collector，因此 D3無法在不新增 observer capability的前提下安全執行。
- [ ] **Preferred implementation direction**：優先使用 Windows 10+ 原生 DNS-SD API（`DnsServiceBrowse` / `DnsServiceResolve`，`dnsapi.dll` / `windns.h`）建立一個 bounded evidence-only adapter，而不是自行實作 DNS packet parser、引入第三方 mDNS stack或下載外部工具。
- [ ] D3A 預設只授權 implementation + local/synthetic validation；不得因完成 adapter就自行發出 live mDNS query。Live use仍由後續 D3取得新的明確授權。
- [ ] Adapter scope僅 `_ewelink._tcp.local.` DNS-SD browse/resolve。輸出應可 deterministic轉成既有 D1 input contract；不得輸出/保存不必要的 local IP、hostname、完整 deviceId、raw TXT、IV、ciphertext、credential或 Matter secret到 durable evidence/model context。
- [ ] 必須 one-shot / bounded、可取消、無 background monitor、無 retry loop，且能作為 D2A runner 的 direct child；若 Windows API callback/worker semantics無法符合 direct-child cleanup contract，STOP並記錄 limitation，不得假稱已解決。
- [ ] 優先沿用現有 host tooling / compiler；不得為 D3A 安裝第三方 network package。若 native Windows API route不可行，STOP並另提明確替代設計，不得自行降級成 custom raw mDNS packet parser。
- [ ] 最低充分 validation：compile/static、synthetic callback/result shaping、timeout/cancel/cleanup、D1-compatible output contract、secret/raw-field audit、targeted tests與 scoped diff。Network/Hardware/Matter一律 NOT RUN。
- [ ] 完成後依 Completion Evidence Guard移除 D3A，並將 D3由 `DEPENDS ON D3A` 恢復為單純 `NOT AUTHORIZED`。D3A 本身不授權 live D3。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] **Latest attempt evidence — capability gate STOP**：2026-08-31 在 project HEAD `53184b07a9258961e0e634b3053bcfaed3000918`、Playbook `6b898cb1610c6f7264e0e898d010b2456053829a` 下檢查；本機只有 `Resolve-DnsName`，沒有既有已知語意的 native mDNS DNS-SD browse/resolve observer，因此在 live operation前安全 STOP。D2A未啟動、live duration 0 秒、沒有 raw evidence、repo沒有 durable change、沒有 Network PASS。
- [ ] **Objective**：D3A完成後，在新的明確使用者授權下，使用 safe observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard mDNS browse/resolve query，以確認是否有 discovery/TXT response。只限 discovery layer，不得升級其他 protocol。
- [ ] Query 必須 one-shot / bounded；不得 LAN/ARP sweep、port scan、arbitrary DNS/UDP probe、background monitor或 retry loop。
- [ ] Raw observer output只可留在 Git-local temporary runtime，經既有 D1 sanitizer contract處理後只有 sanitized facts可 durable保存或進 model reasoning。
- [ ] 只有直接觀察且可靠 attribution到 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 的 facts才可標 `CONFIRMED_LOCAL`；generic eWeLink response不得自動提升為 CK-specific evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、另一台 host、proxy或 cloud API。
- [ ] `Network PASS` 最多只可建立為本次實際成功的 bounded local mDNS discovery/response scope；若 query後仍 `NO SERVICE OBSERVED`，D3可完成但 Network PASS不成立，也不得推論 protocol不存在或 hardware failure。
- [ ] 完成後依 Completion Evidence Guard更新最低必要 validation/evidence與 TASKS lifecycle；D3本身不授權 HTTP、decrypt、control或任何下一 Stage。
