# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`
- 預期 Branch：`main`
- Bootstrap、S1 Architecture / Contract Freeze、S2A Build Authority 與 S2B Portable Foundation 已完成。
- Framework/version authority **不變**：ESP-IDF `v5.5.5` + Component Registry `espressif/esp_matter ==1.6.0`。
- **Target strategy 修正**：resource profile 與 radio capability 分開建模；不得再把 C3 → C6 → S3 當成單純資源階梯。
- **Primary constrained target**：ESP32-C3 / ESP32-C3 SuperMini-class，Matter over Wi-Fi；以 4 MB 級資源限制優先驗證 v1 software footprint。S2C 必須先確認實際 compile profile / flash assumptions，不得把「SuperMini」型號名稱當成已驗證的 module/flash authority。
- **Development / high-margin fallback target**：ESP32-S3-WROOM-1-N16R8（16 MB flash / 8 MB Octal PSRAM）。S2A 原本建立的 S3 build authority保留為 development/fallback evidence，不再代表 v1 primary constrained target。
- **Optional capability target**：ESP32-C6。其主要價值是未來可選的 IEEE 802.15.4 / Matter over Thread 路徑；v1 eWeLink Bridge 仍以 Matter over Wi-Fi 為主，因此 C6 不因「資源比 C3 多」而自動成為 STANDARD target。若未來啟用 Thread，應以獨立 firmware/capability Stage 評估 Wi-Fi↔Thread coexistence與 resource budget。
- Board/resource profile只能改變 build-time resource/capability configuration；不得改變 portable protocol、security、state semantics、Matter mapping correctness或 secret handling。
- S2B portable core 已建立 Host PASS；其 API/contract authority見 `docs/portable-core.md`。Platform/Matter adapter依賴 portable core，不得把 ESP-IDF/CHIP types滲入 core。
- 第一 consumer仍限定 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 的 4-channel binary-switch contract；其真實 UIID、wire schema、encryption applicability與 LAN behavior仍非 `CONFIRMED_LOCAL`。
- S2C 允許為 build/CI目的下載、解析與編譯 pinned official dependencies；這不等於授權對 eWeLink device、Google Home/controller或一般 LAN做 live runtime/network operation。
- 真實 credential / deviceKey / Wi-Fi password / Matter fabric secret不得進 Git、CI secret、fixture、log或文件；compile probe只使用 synthetic values。

# S2C — Constrained-target CI + Compile-only Matter/ESP32 Integration

**S2C 是目前唯一可執行 Stage。目標是先以 ESP32-C3 constrained profile完成最低可重現 Host CI + Compile/Resource feasibility gate；只有 C3出現有證據的 resource/SDK blocker時，才使用既有 S3 N16R8 profile作 development/fallback comparison。不得因方便直接跳到 S3。**

建議執行順序：S2C0 authority correction → S2C1 host CI → S2C2 C3 compile harness → S2C3 esp-matter bridge compile probe → S2C4 partition/resource baseline → S2C5 bounded fallback decision / closure。若 dependency/toolchain下載或 SDK compatibility出現 blocker，保留 evidence並 STOP，不得切換 floating version、替代 framework或跳過 compile participation evidence。

- [ ] **S2C0 — Durable target-strategy correction**：先依 Yale 專案已採用的 target/resource-profile思想，修正本 repo `docs/architecture.md`、`docs/build.md`、`docs/roadmap.md`、`VALIDATION.md`與必要 README/AGENTS authority：`C3 = primary constrained Wi-Fi Matter target`、`S3 N16R8 = development/high-margin fallback`、`C6 = optional Thread-capability target`。保留 S2A pinned ESP-IDF/esp-matter版本 authority；不得把舊 S3 build evidence刪掉或誤寫成失敗。Resource profile不得改變核心 protocol/security semantics。
- [ ] **S2C1 — Minimum host CI**：建立單一最低充分 GitHub Actions host job，重現 S2B portable build/tests。CI不得依賴 Windows CNG專屬 provider才能成立；若 Linux runner需要新 host-test crypto provider，必須 lowest-sufficient、license-reviewed且不得滲入 portable public API。禁止大矩陣、coverage service或多平台重複 job，除非 evidence證明必要。
- [ ] **S2C2 — ESP32-C3 constrained compile harness**：依 pinned ESP-IDF `v5.5.5` + `espressif/esp_matter ==1.6.0` 建立最小 ESP-IDF compile-only project/component wiring，使 `esp32c3` target真正 compile/link S2B portable core。先以 ESP32-C3 SuperMini-class常見 4 MB 級限制作 constrained feasibility方向，但必須以實際可重現 target/module/flash config authority落地；不得猜板子 flash、partition或 PSRAM。C3不得因缺 Thread被判定失敗，因 v1只要求 Matter over Wi-Fi。
- [ ] **S2C3 — esp-matter bridge compile probe**：最小 adapter/probe必須實際 include/reference pinned `esp_matter_bridge` API，並以 synthetic 4-channel device descriptor / binding contract證明 bridge lifecycle / bridged On/Off endpoint integration boundary可在 C3 target compile/link。Probe只能是 compile/link participation evidence；不得啟動 Wi-Fi、BLE commissioning、Matter server/controller、fabric、NVS runtime或 endpoint runtime interaction。若 API semantics需要 upstream確認，只讀 pinned `esp-matter 1.6.0` relevant header/example，不重掃 upstream。
- [ ] **S2C4 — C3 partition + resource baseline**：建立 C3 constrained profile最低充分 custom partition table，保留 Matter persistence / NVS / NVS-key / PHY / OTA等必要 roles；以 ESP-IDF partition validation通過為必要條件。記錄 app binary、partition pressure、flash usage、static DRAM/IRAM等 compile-time可取得 evidence。目的不是「把 4 MB硬塞到能 build」，而是判定 v1核心在合理 OTA/persistence條件下是否 viable；不得犧牲 security/persistence/correctness只為讓 C3過關。
- [ ] **S2C5 — Bounded target decision + closure**：若 C3完整 Compile PASS且 partition/resource baseline仍合理，將 C3正式提升為 v1 constrained baseline；S3維持 development/fallback。若 C3明確因 flash/DRAM/SDK/bridge capability不足而失敗，先分類 root cause並保存 evidence，再允許用既有 S3 N16R8 authority做**一次 bounded fallback compile comparison**；不得把 C3 source failure與 toolchain/environment failure混為一談。C6不在此 Stage做額外 compile matrix，除非出現與 Thread capability無關、但會改變 v1 target decision的明確 evidence。
- [ ] **S2C6 — Minimum reproducible validation / S2 closure**：記錄 exact commands、environment/toolchain、dependency resolution/lock evidence、target/sdkconfig evidence、portable-core compile/link participation、esp_matter_bridge compile/link participation、partition validation與artifact/resource baseline。更新 durable docs與 queue。S2完成後下一 Stage只保留真實 eWeLink LAN diagnostic/evidence gate，不自行開始。

## Resource-profile invariant（由 Yale target strategy 移植）

Resource profile是 build-time resource/capability policy，不是新的 protocol layer：

- `CONSTRAINED / LIGHTWEIGHT`：ESP32-C3 SuperMini-class / 4 MB級方向；用來約束 v1 software footprint。
- `DEVELOPMENT / HIGH-MARGIN`：ESP32-S3 N16R8；供 debug、較大 build margin、未來功能實驗與 fallback。
- `OPTIONAL THREAD CAPABILITY`：ESP32-C6；是 radio/capability選項，不是單純的「中階資源 profile」。

所有 profile必須共享同一組不可降級 invariant：protocol correctness、secret handling、crypto semantics、state convergence、4-channel isolation與 Matter mapping correctness。高資源板子的存在不得成為無界增加 buffer、queue、logging、dependency或 feature footprint的理由。

## S2C ESP-IDF / Matter compile requirements

C3 Compile PASS只有在以下 evidence同時存在時才能成立：

1. exact ESP-IDF `v5.5.5` identity；
2. Component Manager resolved exact `espressif/esp_matter ==1.6.0`，有 dependency/lock evidence；
3. `idf.py set-target esp32c3` / sdkconfig evidence；
4. actual C3 flash/board/module build assumptions有可重現 authority，而不是只寫「SuperMini」；
5. portable core source真正出現在 target compile/link inputs；
6. platform adapter/probe真正 include/reference `esp_matter_bridge`，且 component參與 compile/link；
7. custom partition table被 ESP-IDF parser/build實際採用；
8. final target build/link成功；
9. OTA/persistence/security必要 roles未為了塞進 C3而被不當移除；
10. compile-time resource evidence足以判斷 constrained feasibility，而不是只證明空 image能產生。

只成功編譯空 `app_main`、只下載 SDK、只解析 manifest、只編 host core，都不得稱 S2C `Compile PASS`。

## C3 feasibility classification

C3結果必須落在下列之一：

- **VIABLE_CONSTRAINED**：完整 compile/link +必要 partition roles成立，resource baseline仍有合理後續 runtime驗證空間；C3成為 v1 constrained baseline。
- **COMPILE_ONLY_TIGHT**：能 build但 partition/static resource margin已明顯過緊；不得直接當 production-ready，下一 Stage前需明確 resource gate。
- **NOT_VIABLE_BY_EVIDENCE**：在不犧牲必要 security/persistence/correctness下，C3因已確認的 resource或 SDK/bridge limitation無法成立；可啟動一次 S3 fallback comparison。
- **INCONCLUSIVE_TOOLCHAIN**：toolchain/environment/dependency failure使 source feasibility無法判定；不得因此把 C3判死或直接升級 S3。

## Toolchain / execution environment rule

- 使用 Espressif官方 install/export / Component Manager flow；不 vendor esp-matter或 ConnectedHomeIP。
- 允許取得 pinned SDK/component/toolchain dependencies，屬 build provisioning，不屬 live device/network test。
- Windows native環境若不適合 Matter build，優先 WSL2/Linux或 GitHub Actions Linux；不要為不受支持的 native Windows path無界 debug。
- 若 local缺 SDK/WSL2/權限，但 GitHub Actions可用官方可重現 Linux build完成 target Compile PASS，允許以 CI作 compile authority並保存 run/job evidence。
- 不得為解決 toolchain問題更換 ESP-IDF/esp-matter版本、改回 Arduino或使用 floating branch。

## S2C explicit runtime prohibition

即使 firmware image可 build，本 Stage不得執行：

- flash / boot ESP32；
- Wi-Fi connect / provisioning；
- BLE advertising / commissioning；
- Matter server startup / fabric creation；
- mDNS browse/advertise；
- eWeLink HTTP / zeroconf request；
- CK-BL602 discovery/control；
- NVS真實 credential persistence；
- Google TV Streamer / Google Home controller interaction；
- relay switching、hardware test或 bench test。

Compile/link symbol participation ≠ runtime authorization。

## CI cost discipline

保持最低充分：理想為 1個 host job + 1個 C3 ESP-IDF compile job。**不要建立 C3/C6/S3 matrix。** S3只有在 C3落入 `NOT_VIABLE_BY_EVIDENCE` 且 root cause已確認後，才允許一次 bounded fallback comparison。C6的 Thread選配路徑留給未來獨立 Stage。

## S2C validation minimum

至少：

- S2B host tests在正式 CI或可重現host path通過；
- GitHub Actions workflow最小化 / no redundant matrix audit；
- dependency/version/no-floating audit；
- exact component resolution evidence；
- C3 target/sdkconfig/flash assumptions audit；
- portable-core target compile/link participation audit；
- esp_matter_bridge compile/link participation audit；
- partition parser/build validation；
- flash/static resource baseline capture；
- required OTA/persistence/security-role audit；
- secret scan；
- license/provenance audit；
- dependency-direction audit；
- scope audit（無 runtime/live network）；
- `git diff --check`。

成功可宣告 `Static/Test PASS`、`Host PASS`、以及只針對實際成功 target/profile的 `Compile PASS`。仍必須保持 `Network PASS = NOT RUN`、`Hardware PASS = NOT RUN`、`Matter interoperability PASS = NOT RUN`；CK-BL602仍不得標 `CONFIRMED_LOCAL`。

## S2C STOP conditions

遇到以下情況先保存 evidence並 STOP：

- pinned SDK pair無法依官方方式 resolve/build且 root cause未確認；
- 只能改 floating version才 build；
- `esp_matter_bridge` API與既有 architecture contract衝突；
- C3 module/flash/partition只能靠猜測；
- 為塞進 C3必須犧牲必要 OTA/persistence/security/correctness；
- portable core必須污染 ESP-IDF/CHIP types；
- compile probe必須跑 runtime才可證明 API；
- toolchain/environment failure與 source/resource failure無法區分。

不得無界 retry；不得因 C3遇到單純 toolchain問題就直接改 S3。

# S2 overall completion condition

S2C全部完成後才可宣告 **Software-first foundation complete**。此 milestone最高代表 portable Host PASS + 已驗證 target的 Compile PASS；Network、Hardware、Matter interoperability仍未驗證。

完成後 `TASKS.md` 不保留已完成 S2A/S2B/S2C歷史；只保留下一個真正 unfinished / deferred / evidence-gated工作。不得自行開始下一 Stage。
