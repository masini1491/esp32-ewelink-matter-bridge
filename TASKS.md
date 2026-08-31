# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3A — Windows native DNS-SD observer adapter — BLOCKED / NOT AUTHORIZED

- [ ] **Deadline/TXT fix accepted**：commit `ed6b3e3c4d5e4b6f574d8785dfb39565f594fd7a` 已修正 browse→resolve overall deadline allocation，並將 TXT property overflow 改為 fail-closed。
- [ ] **BLOCKED — resolve lifetime authority gap**：current Microsoft authority不能證明 first success callback terminal，也不能支持 safe success-after-cancel/quiescence rule；不得使用 fixed sleep、推測性 cancel或 speculative late-callback handling。
- [ ] **D3B decision**：research found no released Windows-native route that both performs the required mDNS/DNS-SD observation and has an authoritative bounded completion/quiescence contract. See `docs/d3b-windows-dnssd-research.md`; unblock condition remains authoritative Microsoft lifecycle semantics or separately authorized non-LAN platform proof.
- [ ] D3A只可在 unblock condition已滿足後，另行取得明確 implementation/revalidation 授權。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] D3不得執行 live query，直到 observer lifecycle/alternative path完成 implementation與 revalidation。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 safe Windows observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard discovery/resolve，以取得可交給 D1 sanitizer的 evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local discovery/response scope。
