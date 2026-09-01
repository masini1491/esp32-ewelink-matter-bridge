# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3A — Windows native DNS-SD observer process-exit lifetime guard — REVALIDATION REQUIRED / NOT AUTHORIZED

- [ ] **Accepted from `874d9ca1d29250f61a415e1bc3a8f438565a9048`**：`ResolveOperation` + module-level registry已讓 callback/request/cancel/event/first-result在正常 observer execution期間保持強引用；first accepted result immutable，late/multiple/malformed與 timeout/cancel後 callback的 synthetic state handling成立。既有 deadline、TXT fail-closed、privacy、D1-compatible output與 D2A direct-child boundaries未被破壞。
- [ ] **Completion Evidence Guard blocker — Python interpreter finalization is still inside process lifetime**：目前 `PROCESS_LIFETIME_RESOLVES` 只是 module global。正常成功路徑由 `main()` return → `SystemExit` → Python interpreter shutdown；global/module objects可在 OS process真正終止前被 teardown。若 WinDNS resolve operation仍可能 late-callback，這段 finalization window仍可能讓 native callback命中已釋放/正在 teardown 的 ctypes callback/context。D2A的成功路徑只是 `process.wait()` 等 child自然退出，並不會把成功 child直接 terminate，因此不能把 D2A termination當成 normal-success 的 atomic ownership boundary。
- [ ] 現有 regression只證明 registry存在時是 strong reference；沒有實際覆蓋「結果已輸出 → interpreter finalization開始 → native operation仍可能 callback → OS process exit」的 lifetime boundary。因此不得把 current local tests解讀為 process-exit safety已完整證明。
- [ ] 修正需保持原本核心設計：memory safety不得依賴 undocumented resolve terminal/quiescence semantics。優先找最低複雜度的 **hard process-exit boundary**，使成功結果已可靠寫出/flush後，不再進入會逐步釋放 ctypes callback/context 的 Python normal finalization；或提出等價、可證明的 process-lifetime ownership方式。不得以固定 sleep或推測性 cancel取代。
- [ ] 若採 hard-exit設計，必須保證 machine result/stdout在 exit前可靠完成，錯誤 exit code語意不變，D2A仍能取得完整 raw stdout/result metadata；不得把 runtime artifact、identifier或secret寫入 Git。不要修改 D2A除非證據證明 observer端無法最低充分解決；若需要 material擴張先 STOP。
- [ ] 新增最低充分 regression/contract test覆蓋 normal-success shutdown path：證明 observer成功輸出完成後採用的 termination path不會先清空/釋放 process-lifetime resolve ownership；existing late/multiple callback、timeout/cancel、deadline/TXT/privacy tests仍須 PASS。
- [ ] D3A仍只授權 implementation/local-synthetic validation；不得實際呼叫 live `DnsServiceBrowse` / `DnsServiceResolve`。Network/Hardware/Matter全部 NOT RUN。
- [ ] Completion Evidence Guard成功後移除 D3A，D3恢復單純 `NOT AUTHORIZED`；不得自行執行 D3。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] D3不得執行 live query，直到 normal-success process-exit ownership完成 revalidation。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 safe Windows observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard discovery/resolve，以取得可交給 D1 sanitizer的 evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local discovery/response scope。
