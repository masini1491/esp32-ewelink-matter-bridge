# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3B — Windows DNS-SD lifecycle / alternative observer research — NOT AUTHORIZED

- [ ] **Admission evidence**：D3A 已完成 deadline allocation、TXT overflow fail-closed與 privacy/local-synthetic validation，但 Microsoft `DnsServiceResolve` / `DnsServiceResolveCancel` 官方文件不足以建立 successful resolve callback 的 terminal/quiescence contract，因此 D3A 不能安全解除 callback/request/cancel lifetime。
- [ ] **Objective**：只做 bounded public read-only research，找出可權威證明安全 completion/lifetime 的 Windows native DNS-SD 路徑，或找出更適合 D3 的 Windows native alternative observer path；不得做 live LAN、不得修改 source、不得安裝第三方 network tooling。
- [ ] Authority優先順序：Microsoft Learn/API docs → Windows SDK headers/samples/metadata → Microsoft maintained source/sample；第三方 source僅可作 supporting implementation evidence，不得覆蓋官方 contract缺口。
- [ ] 至少比較 current `DnsServiceBrowse` + `DnsServiceResolve` route 與可能的 Windows native alternatives（例如官方 DNS query API / multicast-only capability，若有明確官方支持），評估：completion semantics、cancel/quiescence、bounded execution、raw evidence exposure、D2A direct-child compatibility、D1 conversion complexity、dependency成本。
- [ ] 不得自行實作 raw DNS/mDNS packet parser，不得引入 Bonjour/Avahi/dns-sd/第三方 Python package，不得因找到候選 route就直接改 code。
- [ ] 若能建立可審核的安全 route，產出最小 durable decision evidence並提出下一個 implementation Stage；若仍無法建立安全 route，記錄 blocker與最小必要外部條件。D3B本身不授權 D3A source patch或 D3 live query。

## D3A — Windows native DNS-SD observer adapter — BLOCKED / DEPENDS ON D3B / NOT AUTHORIZED

- [ ] **Deadline/TXT fix accepted**：commit `ed6b3e3c4d5e4b6f574d8785dfb39565f594fd7a` 已修正 browse→resolve overall deadline allocation，並將 TXT property overflow 改為 fail-closed。
- [ ] **BLOCKED — resolve lifetime authority gap**：current Microsoft authority不能證明 first success callback terminal，也不能支持 safe success-after-cancel/quiescence rule；不得使用 fixed sleep、推測性 cancel或 speculative late-callback handling。
- [ ] D3A只可在 D3B 找到足夠 authority / safer native route後另行明確授權 implementation/revalidation。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] D3不得執行 live query，直到 observer lifecycle/alternative path完成 implementation與 revalidation。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 safe Windows observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard discovery/resolve，以取得可交給 D1 sanitizer的 evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local discovery/response scope。
