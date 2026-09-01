# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## D3A — Windows native DNS-SD observer error-path hard-exit guard — REVALIDATION REQUIRED / NOT AUTHORIZED

- [ ] **Accepted from `20241f22dcf0011dffbd51e3db68f1f3bda38807`**：normal-success path 已在完整 JSON 寫入並 `flush()` 後使用 `os._exit(0)`，subprocess / D2A synthetic handoff證明 stdout可解析、exit `0` 且不執行一般 Python finalization。`ResolveOperation` registry、first-result immutability、late/multiple/malformed callback、deadline/TXT/privacy/D1 boundaries維持成立。
- [ ] **Remaining Completion Evidence Guard blocker — error path can still finalize Python while a native resolve remains live**：`NativeDnsSdBackend.resolve()` timeout時會保留 `ResolveOperation`、嘗試 `DnsServiceResolveCancel`後丟出 `TimeoutError`；cancel仍不被視為 quiescence。`main()`目前 catch後 `print(OBSERVER_ERROR)` + `return 2`，因此會走 `SystemExit` / normal interpreter finalization。若 timeout/cancel後仍有 late callback，module/global/ctypes objects仍可能在 OS process exit前被 teardown。
- [ ] 同一風險亦涵蓋任何「resolve已啟動／registry非空後」才發生的 error，例如 resolve cancel failure、resolve完成後 overall deadline exceeded或後續 validation error；不得只用 synthetic pre-resolve failure證明 error path安全。
- [ ] 修正目標：所有可能持有 live `ResolveOperation` 的 CLI terminal path都必須在完整 error JSON寫入並可靠 `flush()` 後，以不進入 Python normal finalization的 hard process-exit boundary結束，同時維持 error exit code `2`。可採共用 `write/flush/hard-exit(payload, code)` helper或等價最低複雜度設計。
- [ ] 新增最低充分 regression：模擬 registry已有 operation／timeout-cancel後進 error terminal path，註冊 `atexit` marker，證明 error JSON完整可 parse、exit code `2`、normal finalization marker未執行、registry未先被清空；D2A synthetic handoff仍能取得完整 stdout/result metadata。
- [ ] 保留既有 success hard-exit、late/multiple callback、timeout/cancel late callback、strong registry ownership、deadline/TXT/privacy與D2A tests。不得以固定 sleep或 undocumented cancel/quiescence語意替代 hard-exit ownership。
- [ ] D3A仍只授權 implementation/local-synthetic validation；不得實際呼叫 live `DnsServiceBrowse` / `DnsServiceResolve`。Network/Hardware/Matter全部 NOT RUN。
- [ ] Completion Evidence Guard成功後移除 D3A，D3恢復單純 `NOT AUTHORIZED`；不得自行執行 D3。

## D3 — Bounded standard mDNS browse/resolve — BLOCKED / DEPENDS ON D3A / NOT AUTHORIZED

- [ ] D3不得執行 live query，直到 success與error terminal paths都完成 hard process-exit ownership revalidation。
- [ ] D3 objective維持：在新的明確使用者授權下，使用 safe Windows observer + D2A runner，對 `_ewelink._tcp.local.` 做一次 bounded standard discovery/resolve，以取得可交給 D1 sanitizer的 evidence。
- [ ] D3禁止 HTTP、`/zeroconf/*`、getState、deviceKey、decrypt、relay/channel control、BLE、Matter、firmware、LAN/ARP sweep、port scan、另一台 host、proxy或 cloud API。
- [ ] 只有直接觀察且可靠 attribution到目標 CK的 facts才可標 `CONFIRMED_LOCAL`；`Network PASS` 最多只限實際成功的 bounded local discovery/response scope。
