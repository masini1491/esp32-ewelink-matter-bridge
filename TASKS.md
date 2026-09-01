# TASKS

本檔是 ChatGPT／Codex 共用的 active unfinished-work / executable scoped Prompt queue。Completed 不保留，完成事實以 Git history 為準；本檔存在不代表授權任何 Stage。本 repository 採 persistent TASKS mode，queue 清空後保留最小 `EMPTY` state。

## G1 — Reconcile project governance with current common playbook — NOT AUTHORIZED

**Recommended execution:** Luna / Low；Context L0→L2；Agent 1；docs-only governance synchronization。

- [ ] 以 project `main` 與 `masini1491/ai-development-playbook@8d50c077434c3cfb106c88f1b0bf60c239fb5320` 為 baseline；playbook 與所有其他 repositories 唯讀。先依最新 `AGENTS.md` 與 common routing 完成必要 preflight。
- [ ] 僅更新 `AGENTS.md`、`docs/roadmap.md` 與本 `TASKS.md`。不得修改 README、VALIDATION、source、tests、tooling、workflow、build/protocol/security/runtime/product behavior。
- [ ] `AGENTS.md`：保留 project-specific authority/stricter rules；補齊 common routing 至 `UI_UX.md`、`TOOLCHAIN.md`；明確宣告本 repository 採 persistent TASKS mode／EMPTY lifecycle；移除或改寫已被 common baseline取代或已過期的 current-state wording，尤其不得再宣稱「沒有 live LAN evidence」或把已完成的 real eWeLink LAN diagnostic gate寫成 next candidate。Current network/runtime evidence 只做最低充分摘要並 route 至 `VALIDATION.md`：D2/D3 已有 bounded mDNS observations，但沒有 service response、Network PASS 或 CK-specific `CONFIRMED_LOCAL`。
- [ ] `docs/roadmap.md`：只修正 material stale status。記錄 D2/D3 bounded mDNS evidence gate已完成且為 negative observation；不得把它誤寫成 Network PASS，不自動指定或授權下一個 live/network Stage。其餘 S1/S2/build/hardware pending contract保持不變。
- [ ] 不做 cosmetic rewrite，不因文件長度拆檔，不複製 common Playbook全文；遵守 `Reference, don’t repeat`。若發現需改動上述 allowed paths以外的 material governance file，STOP並回報，不擴張 scope。
- [ ] Validation：檢查 routing/authority 無 contradiction、project-specific stricter rules仍保留、D3 current evidence與 `VALIDATION.md` 一致、persistent TASKS contract成立、`git diff --check` PASS；確認 changed files 僅限允許範圍。
- [ ] 完成並驗證後移除 G1，將 `TASKS.md` 收斂為最小 `Queue status: EMPTY` template；commit/push後 STOP，不啟動任何下一 Stage。
