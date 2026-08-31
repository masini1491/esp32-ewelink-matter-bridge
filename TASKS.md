# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3A — Windows native DNS-SD observer adapter — REVALIDATION REQUIRED / NOT AUTHORIZED

- [ ] **Deadline/TXT fix accepted**：commit `ed6b3e3c4d5e4b6f574d8785dfb39565f594fd7a` 已修正 browse→resolve overall deadline allocation，並將 TXT property overflow 改為 fail-closed；這部分可視為完成。
- [ ] **BLOCKED — official resolve lifetime contract insufficient**：Microsoft documents `DnsServiceResolve` as asynchronous and says that, upon completion, its callback is invoked “for each result”; the callback status is only for “this particular set of results”. The official `DnsServiceResolveCancel` page says it cancels a *running* query but does not specify whether cancellation after a successful callback is required/valid, whether it yields a terminal callback, or when callbacks can no longer occur. Therefore the current authority cannot establish that the first success callback is terminal, nor support a safe cancel/quiescence rule for releasing ctypes callback/request/cancel objects.
- [ ] **Unblock condition**：obtain authoritative Microsoft SDK/API completion and callback-lifetime semantics for successful `DnsServiceResolve`, or separately authorize a bounded platform proof that can establish the contract without live LAN evidence. Do not use fixed sleeps, inferred cancellation behavior, or a speculative late-callback implementation.
- [ ] No source patch or synthetic multi-callback regression is authorized until that authority gap is resolved; current deadline/TXT/privacy tests remain valid but do not close the lifecycle question.
- [ ] 保持 Windows native `dnsapi.dll` + Python stdlib/ctypes；不得新增 raw mDNS parser、第三方 network dependency或 live LAN validation。Network/Hardware/Matter仍 NOT RUN。
- [ ] Completion Evidence Guard需確認：deadline regression仍 PASS、TXT fail-closed仍 PASS、resolve success lifecycle bounded/quiescent、privacy/schema不變、targeted tests與 scoped diff完整。成功後移除 D3A並解除 D3 dependency。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] D3不得執行 live query，直到 D3A resolve async lifecycle authority gap解除。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 Windows DNS-SD observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard browse/resolve，以取得可交給 D1 sanitizer的 discovery/TXT evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local mDNS discovery/response scope。
