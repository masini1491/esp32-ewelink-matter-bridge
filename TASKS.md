# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3A — Windows native DNS-SD observer adapter — REVALIDATION REQUIRED / NOT AUTHORIZED

- [ ] **Completion Evidence Guard finding**：commit `31aed282aba466b331d103deffee37b1b4538a3a` 已加入 Windows native DNS-SD adapter，但 current implementation 的 overall timeout budget 有 blocking defect：`observe()` 先以完整 `timeout` 呼叫 `backend.browse()`；native `browse()` 會等待該完整 timeout 後才 cancel/return，因此只要實際發現任何 service，回到 `observe()` 時計算出的 remaining resolve budget 幾乎必然 `<= 0`，隨即 `TimeoutError("resolve budget exhausted")`。這表示 future D3 live run 無法在同一 overall budget內完成 browse → resolve/TXT evidence。
- [ ] 修正應保持 Windows native DNS-SD route；不得新增 raw mDNS parser或第三方 network dependency。需要把 browse phase與 overall observation deadline分離，例如 early-stop browse、明確 browse sub-budget或其他 bounded設計，並保證 resolve仍有正的 bounded budget。
- [ ] 新增 regression test，必須能模擬「browse實際耗時但仍在 overall deadline內發現 service」並證明後續 resolve取得正 remaining budget；現有 immediate fake browse不足以覆蓋此 defect。
- [ ] **TXT fail-closed review**：native resolve目前以 `min(dwPropertyCount, MAX_TXT_PROPERTIES)` 靜默截斷 properties；修正時應確認是否需要在超過 bound時 fail-closed或明確標記 truncation，避免把不完整 TXT當完整 D1 evidence。
- [ ] D3A revalidation仍只授權 implementation/local-synthetic validation；不得自行呼叫 live `DnsServiceBrowse` / `DnsServiceResolve`。Network/Hardware/Matter均保持 NOT RUN。
- [ ] 完成後依 Completion Evidence Guard確認 timeout/deadline、cancel lifecycle、D1-compatible output、TXT bounds/privacy、targeted tests與 scoped diff；成功後再移除 D3A並解除 D3 dependency。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] D3仍不得執行 live query，直到 D3A timeout-budget defect完成修正與 revalidation。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 Windows DNS-SD observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard browse/resolve，以取得可交給 D1 sanitizer的 discovery/TXT evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local mDNS discovery/response scope。
