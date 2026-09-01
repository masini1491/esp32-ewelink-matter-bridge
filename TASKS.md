# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3A — Windows native DNS-SD observer process-lifetime revalidation — NOT AUTHORIZED

- [ ] **New implementation evidence after D3B**：Microsoft-maintained `microsoft/Xbox-GDK-Samples` 的 `Samples/Live/mDNS/mDNS.cpp` 直接使用 `DnsServiceResolve`，等待 resolve callback 後繼續，success path沒有額外的 success-after-cancel choreography。Mumble與OpenPrinting CUPS的 Windows DNS-SD implementations則把 resolve request/cancel/context保存於長生命週期 object，在 teardown時才 cancel/free。這些屬 implementation evidence，不取代 Microsoft Learn API contract，但足以支持新的 safer ownership design。
- [ ] **Reframed safety goal**：不再要求證明「first success callback = terminal callback」。改成讓 callback、request、cancel handle、query context與結果 state在 observer child process存活期間都保持有效，使 late/multiple callbacks即使發生也不會命中已釋放的 Python/ctypes object。
- [ ] **Preferred design**：建立 process-lifetime `ResolveOperation` / registry（名稱可調整），每個 operation持有 callback、`DNS_SERVICE_RESOLVE_REQUEST`、`DNS_SERVICE_CANCEL`、event/state/result。取得第一筆可接受 result後只標記 result accepted；不得立即釋放 operation。late/multiple callbacks必須 bounded、安全忽略或依明確 state machine處理。
- [ ] Memory safety不得依賴 undocumented resolve terminal/quiescence semantics。timeout/normal completion可依現有 bounded policy嘗試 `DnsServiceResolveCancel`，但即使 cancel無法證明 quiescence，operation objects仍保留到 process exit；D2A direct-child process termination是最終 hard ownership boundary。
- [ ] 保留既有 deadline/TXT fixes：overall browse/resolve deadline allocation、positive resolve budget、TXT property overflow fail-closed、multiple discovery只 resolve第一筆並以 `truncated: true`標記不完整集合、fixed `_ewelink._tcp.local.` scope、D1-compatible private raw contract與 privacy bounds。
- [ ] **Required synthetic regression**：模擬 first successful resolve callback後主流程已接受第一筆 result，但 native/fake backend再觸發第二／第三次 callback；必須證明 callback/context仍有效、沒有 use-after-free/invalid state、第一筆 durable result不被未授權覆寫。另測 timeout/cancel後 late callback與 process-shutdown ownership assumptions。
- [ ] D3A仍只授權 implementation + local/synthetic validation；不得實際呼叫 live `DnsServiceBrowse` / `DnsServiceResolve`。不得安裝第三方 mDNS/DNS-SD tooling，不得新增 raw DNS/mDNS packet parser。Network/Hardware/Matter全部 NOT RUN。
- [ ] 最低充分 Completion Evidence Guard：process-lifetime ownership清楚、callbacks強引用直到 child exit、late/multiple callback regression PASS、deadline/TXT/privacy regressions仍 PASS、D2A direct-child compatibility不變、targeted tests與 `git diff --check` PASS。成功後移除 D3A並將 D3恢復為單純 `NOT AUTHORIZED`；不得自行執行 D3。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] D3不得執行 live query，直到 process-lifetime observer design完成 implementation與 local/synthetic revalidation。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 safe Windows observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard discovery/resolve，以取得可交給 D1 sanitizer的 evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local discovery/response scope。
