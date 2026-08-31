# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3A — Windows native DNS-SD observer adapter — REVALIDATION REQUIRED / NOT AUTHORIZED

- [ ] **Deadline/TXT fix accepted**：commit `ed6b3e3c4d5e4b6f574d8785dfb39565f594fd7a` 已修正 browse→resolve overall deadline allocation，並將 TXT property overflow 改為 fail-closed；這部分可視為完成。
- [ ] **Remaining native async lifecycle blocker**：`NativeDnsSdBackend.resolve()` 在第一個 successful resolve callback 後立即返回，但 Windows `DnsServiceResolve` 官方 contract 為非同步且 callback 可能對每個 result 被呼叫；目前 success path 沒有明確 cancel/quiescence step。若後續仍有 callback，local ctypes callback／request／cancel lifetime 可能在 function return 後失效，與 D2A direct-child safety不相容。
- [ ] 修正前先依 Microsoft authority釐清成功 result後如何安全終止／確認 resolve operation quiescent。最低充分做法應保證 callback、request與 cancel handle存活到 operation確實結束；不得只靠固定 sleep猜測完成。
- [ ] 新增 regression test模擬 multi-callback / late-callback resolve：第一個 success callback後仍嘗試第二個 callback，證明 adapter不會在 callback lifetime結束後返回；若設計採 explicit cancel，測試 cancel path與 quiescence semantics。
- [ ] 保持 Windows native `dnsapi.dll` + Python stdlib/ctypes；不得新增 raw mDNS parser、第三方 network dependency或 live LAN validation。Network/Hardware/Matter仍 NOT RUN。
- [ ] Completion Evidence Guard需確認：deadline regression仍 PASS、TXT fail-closed仍 PASS、resolve success lifecycle bounded/quiescent、privacy/schema不變、targeted tests與 scoped diff完整。成功後移除 D3A並解除 D3 dependency。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] D3不得執行 live query，直到 D3A resolve async lifecycle完成 revalidation。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 Windows DNS-SD observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard browse/resolve，以取得可交給 D1 sanitizer的 discovery/TXT evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local mDNS discovery/response scope。
