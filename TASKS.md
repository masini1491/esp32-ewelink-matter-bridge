# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`，branch `main`。
- Bootstrap、S1 Architecture / Contract Freeze、S2A、S2B 與 S2C software-first compile/resource gate 已完成。
- Framework authority：ESP-IDF `v5.5.5` + `espressif/esp_matter ==1.6.0`。
- Primary constrained target：ESP32-C3 / 4 MB-class，Matter over Wi-Fi；S2C classification：`VIABLE_CONSTRAINED`，僅限 software-first compile/static resource evidence。
- ESP32-S3-WROOM-1-N16R8 僅為 development/high-margin fallback；ESP32-C6 僅為 optional future Thread capability。
- Network、Hardware、Matter interoperability 均未驗證；CK-BL602 device behavior 仍為 `UNKNOWN` / `HARDWARE_TEST_PENDING`，不得標為 `CONFIRMED_LOCAL`。
- 真實 credential、deviceKey、Wi-Fi password、Matter fabric material 不得進 Git、CI、fixture、log 或文件。
- S2 CURRENT evidence 應優先 reuse；本 maintenance 不因治理刷新而重跑或作廢既有 evidence，除非本 Stage 的實際 workflow change使對應 validation scope需要重新驗證。

# M1 — Governance Evidence Labels + Deterministic CI Preflight

**M1 是目前唯一授權 Stage。這是一個 bounded maintenance Stage，不重新開啟 S2C，也不授權下一個 LAN/network/hardware Stage。**

- [ ] **M1.1 — Evidence lifecycle clarity**：以最小文件 patch 讓 `VALIDATION.md` 清楚區分 S2B 的歷史 Windows CNG Host evidence與 S2C/current Linux Host CI evidence；優先使用最新版 Playbook 的 `CURRENT` / `HISTORICAL`（或等價但一致）語意。不得改寫既有測試事實、resource數字或 validation ceiling。
- [ ] **M1.2 — Target-history clarity**：在 `AGENTS.md` 以最小文字澄清「S1 原始 S3 primary selection」已被後續 S2C constrained-target authority更新為 C3 primary constrained baseline；保留 S3歷史與 development/fallback角色，不把 C3提升成 production/minimum-product hardware PASS。
- [ ] **M1.3 — Cheap deterministic build preflight**：在現有 `esp32c3-compile` workflow 的昂貴 ESP-IDF install/build之前，加入最低充分、repository-owned deterministic preflight，檢查 Matter OTA compile probe 後段必需且可事前確定的 project version metadata（至少 `PROJECT_VER` 與非空/有效 numeric `PROJECT_VER_NUMBER`，依目前 pinned build contract為準）。目的只避免再次發生「完整 build到最後 OTA packaging才因 version metadata缺失失敗」。不得建立大型 universal preflight framework，不得改 SDK/component/target/partition/source semantics。
- [ ] **M1.4 — Targeted validation + lifecycle closure**：執行最低充分 static/docs/workflow檢查與 `git diff --check`。若 push 到 `main` 因既有 workflow自然觸發 Host + C3 CI，視為本 workflow mutation 的 remote validation；不得額外手動重跑第二次完整 C3 build。Long-running CI 必須 bounded supervision，不串流整份 build log；成功只保存 job/run summary，失敗只抓 first fatal phase與 bounded log evidence。全部成立後更新 durable evidence（若必要）並從 `TASKS.md` 移除 M1；保留下一個 LAN diagnostic queue但不得自行開始。

## M1 explicit boundaries

- 不修改 portable core、Matter adapter semantics、partition layout、ESP-IDF/esp-matter版本或 target strategy。
- 不新增 S3/C6 matrix，不執行 S3 fallback/C6 build。
- 不因文件標示改動重跑已無 material change的舊 validation；Evidence reuse服從最新版 Playbook。
- 不執行 live Wi-Fi、mDNS、eWeLink HTTP/zeroconf、Matter runtime/commissioning、Google Home、CK-BL602 control、hardware/bench或真實 credential操作。
- 若 preflight 的可靠實作需要改變 version authority ownership、build architecture或額外 generator/framework，STOP；不要為了小 maintenance擴張 scope。
- 若 CI failure 出現在 preflight以外的 phase，依 Build / CI Phase Attribution找 first fatal evidence；不得把 overall workflow FAIL直接稱為 Compile FAIL。

## Next evidence-gated stage — not authorized by M1

- [ ] **Real eWeLink LAN diagnostic / evidence gate**：M1 完成後仍需另行取得明確授權，才建立 CK-BL602 LAN behavior 的 evidence／permission gate。不得從相似裝置推定 UIID、wire schema、encryption applicability、channel numbering或 convergence semantics；本 queue 本身不授權 live network、hardware或真實 credential操作。
