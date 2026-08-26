# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`
- 預期 Branch：`main`
- Bootstrap、S1 Architecture / Contract Freeze、S2A Build Authority 與 S2B Portable Foundation 已完成。
- Build authority：ESP-IDF `v5.5.5` + Component Registry `espressif/esp_matter ==1.6.0`；target/module profile：`esp32s3` / ESP32-S3-WROOM-1-N16R8（16 MB flash / 8 MB Octal PSRAM）。詳見 `docs/build.md`。
- S2B portable core 已建立 Host PASS；其 API/contract authority 見 `docs/portable-core.md`。S2C 不得為了迎合 SDK 而破壞 portable dependency direction；platform/Matter adapter 必須依賴 portable core，而不是把 ESP-IDF/CHIP types滲入 core。
- 第一 consumer仍限定 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 的 4-channel binary-switch contract；其真實 UIID、wire schema、encryption applicability與 LAN behavior仍非 `CONFIRMED_LOCAL`。
- S2C 允許為 build/CI 目的下載、解析與編譯 **pinned official dependencies**；這不等於授權對 eWeLink device、Google Home/controller或一般 LAN 做 live runtime/network operation。
- 真實 credential / deviceKey / Wi-Fi password / Matter fabric secret不得進 Git、CI secret、fixture、log或文件；compile probe只使用 synthetic values。

# S2C — Minimum CI + Compile-only Matter/ESP32 Integration

**S2C 是目前唯一可執行 Stage。目標是完成 software-first foundation 的最低可重現 Host CI + selected ESP32-S3 Compile PASS；不執行任何 live runtime。**

建議執行順序：S2C1 host CI → S2C2 pinned ESP-IDF compile harness → S2C3 esp-matter bridge compile probe → S2C4 partition/resource baseline → S2C5 closure。若 dependency/toolchain下載或 SDK compatibility出現 blocker，保留 evidence並 STOP，不得切換 floating version、替代 framework或跳過 compile participation evidence。

- [ ] **S2C1 — Minimum host CI**：建立單一最低充分 GitHub Actions host job，重現 S2B portable build/tests。CI不得依賴 Windows CNG 專屬 test provider才能成立；若要讓 Linux runner重現 crypto vectors，應使用 lowest-sufficient、license-reviewed host-test provider或將 provider-independent deterministic contract tests拆分清楚。不得建立大矩陣、coverage service或多平台重複 job，除非 evidence證明必要。
- [ ] **S2C2 — ESP-IDF target compile harness**：依 `docs/build.md` 取得/使用 pinned ESP-IDF `v5.5.5` 與 Component Manager `espressif/esp_matter ==1.6.0`，建立最小 ESP-IDF compile-only project/component wiring，使 `esp32s3` target真正 compile/link S2B portable core。Target config必須對應 N16R8 authority：16 MB flash、8 MB Octal PSRAM；不得用 generic/default config假裝通過。
- [ ] **S2C3 — esp-matter bridge compile probe**：最小 adapter/probe必須實際 include/reference pinned `esp_matter_bridge` API，並以 synthetic 4-channel device descriptor / binding contract證明 bridge lifecycle / bridged On/Off endpoint integration boundary可 compile/link。Probe僅能是 compile/link participation evidence；不得啟動 Wi-Fi、BLE commissioning、Matter server/controller、fabric、NVS runtime或 endpoint runtime interaction。若 API semantics需要 upstream確認，只讀 pinned `esp-matter 1.6.0` relevant header/example，不重掃 upstream。
- [ ] **S2C4 — Custom partition + resource baseline**：基於 `docs/build.md` 與 pinned bridge_cli official baseline建立本專案最低充分 custom partition table。保留 Matter persistence / NVS / NVS-key / PHY / OTA roles，移除不屬本專案的 Zigbee-specific storage只能在有明確理由下進行；每個 deviation都要記錄。以 ESP-IDF partition validation通過為必要條件。記錄 app binary、partition usage、flash/static compile-time evidence等可取得 baseline；不得由此推論 runtime heap、PSRAM實際使用、RF coexistence、battery/power或production margin。
- [ ] **S2C5 — Minimum reproducible validation + closure**：記錄 exact commands、environment/toolchain、dependency resolution/lock evidence、target/sdkconfig evidence、portable-core compile/link participation、esp_matter_bridge compile/link participation、partition validation與artifact/resource baseline。更新 `VALIDATION.md`、`docs/build.md`、`docs/roadmap.md`、必要 README/architecture，完成 S2 closure；從 queue移除 S2C完成項目，下一 Stage只保留真實 eWeLink LAN diagnostic/evidence gate，不自行開始。

## S2C host CI portability rule

S2B 的 Windows CNG/Crypt32 provider是有效 Host PASS evidence，但 GitHub Actions不應因此被迫採用昂貴或脆弱的 Windows-only pipeline。S2C1應優先保持 portable core/test contract不變，選擇最低成本 Linux host CI。若 crypto vector測試需要新的 host-only provider：

- 優先使用 runner/system既有、成熟、permissive/compatible-license provider；
- 必須記 license/provenance；
- 不得自行實作 MD5/AES cryptographic primitive；
- 不得改變 production crypto ownership；
- 不得讓 test-only provider滲入 portable public API。

若無法在不增加高成本/高風險 dependency下重現完整 crypto vector，可把 CI分成 provider-independent portable tests + clearly documented crypto-provider limitation，而不是宣稱完整 CI PASS。此時 S2C1是否完成必須依 evidence誠實判定。

## S2C ESP-IDF / Matter compile requirements

Compile PASS只有在以下 evidence同時存在時才能成立：

1. exact ESP-IDF `v5.5.5` identity；
2. Component Manager resolved exact `espressif/esp_matter ==1.6.0`，有 dependency/lock evidence；
3. `idf.py set-target esp32s3` / sdkconfig evidence；
4. 16 MB flash + Octal PSRAM config與 N16R8 build authority一致；
5. portable core source真正出現在 target compile/link inputs；
6. platform adapter/probe真正 include/reference `esp_matter_bridge`，且 component參與 compile/link；
7. custom partition table被 ESP-IDF parser/build實際採用；
8. final target build/link成功。

只成功編譯一個空 `app_main`、只下載 SDK、只解析 manifest、只編 host core，都不得稱 S2C `Compile PASS`。

## Toolchain / execution environment rule

- 依 `docs/build.md` 使用 Espressif 官方 install/export / Component Manager flow；不 vendor esp-matter或 ConnectedHomeIP。
- 允許為本 Stage取得 pinned SDK/component/toolchain dependencies，屬 build provisioning，不屬 live device/network test。
- Windows native環境若不適合 Matter build，優先依 pinned官方支援方式使用 WSL2/Linux或 CI Linux environment；不要花大量成本修補不受支持的 native Windows path。
- 若 local environment缺少 SDK/WSL2/必要權限，但 GitHub Actions可用官方可重現 Linux build完成 target Compile PASS，允許以 CI作 compile authority；需保存 run/job evidence。
- 不得為解決 toolchain問題更換 ESP-IDF/esp-matter版本、改回 Arduino、使用 floating branch或降低 target profile。

## S2C explicit runtime prohibition

即使 compile probe包含 Matter API，也不得在本 Stage執行：

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

## S2C validation minimum

至少：

- S2B host tests在正式 CI或可重現host path通過；
- GitHub Actions workflow最小化 / no redundant matrix audit；
- dependency/version/no-floating audit；
- exact component resolution evidence；
- target/sdkconfig flash/PSRAM audit；
- portable-core target compile/link participation audit；
- esp_matter_bridge compile/link participation audit；
- partition parser/build validation；
- artifact/resource baseline capture；
- secret scan；
- license/provenance audit；
- dependency-direction audit；
- scope audit（無 runtime/live network）；
- `git diff --check`。

S2C成功可宣告：

- `Static/Test PASS`
- `Host PASS`
- `Compile PASS`（selected pinned ESP32-S3 build only）

仍必須保持未驗證：

- `Network PASS`
- `Hardware PASS`
- `Matter interoperability PASS`
- CK-BL602 `CONFIRMED_LOCAL`

## S2C STOP conditions

若遇到以下任一情況，先保留 evidence並 STOP，不做猜測式 workaround：

- pinned ESP-IDF `v5.5.5` + esp-matter `1.6.0`無法依官方方式 resolve/build，且原因尚未確認；
- 必須改 floating branch或非 pinned dependency才能 build；
- `esp_matter_bridge` API與 S1/S2A authority衝突，需要 architecture重新判定；
- N16R8 flash/PSRAM config無法在 selected target被可靠表達；
- partition需求只能靠猜測或需刪除 Matter必需 persistence role；
- portable core必須引入 ESP-IDF/CHIP types才能 compile；
- compile probe開始需要 live runtime才能證明 API；
- toolchain/environment failure無法和 source failure區分。

依 playbook分類 operational/toolchain/source blocker；不得反覆無界 retry。

# S2 overall completion condition

S2C全部完成後，才可宣告 **Software-first foundation complete**。此 milestone最高只代表 portable Host PASS + pinned ESP32-S3 Compile PASS；Network、Hardware、Matter interoperability仍未驗證。

完成後 `TASKS.md` 不保留已完成 S2A/S2B/S2C歷史；只保留下一個真正 unfinished / deferred / evidence-gated工作。不得自行開始下一 Stage。
