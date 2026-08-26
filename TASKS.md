# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`
- 預期 Branch：`main`
- Bootstrap 與 S1 Architecture / Contract Freeze 已完成；durable authority 見 `docs/architecture.md`、`docs/references/README.md` 與 `VALIDATION.md`。
- 專案目標：建立 ESP32-based、local-first 的 eWeLink LAN → Matter Bridge；第一個真實 consumer 為 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 類多路 Wi-Fi switch。
- 第一個 Matter mapping：4-channel binary switch → 4 × Matter On/Off bridged endpoints。
- 不預設 Home Assistant、Raspberry Pi、eWeLink Cloud 或 Internet 為日常控制依賴。
- 真實 CK-BL602 LAN 行為、ESP32 runtime 與 Google TV Streamer commissioning / interoperability 目前均為 `HARDWARE_TEST_PENDING`。
- credential / deviceKey / Wi-Fi password / Matter fabric secret 不得提交 Git、測試 fixture、log 或文件。
- 現階段維持 monorepo 且 library-ready；不得為假想 reuse 提前拆多 repository、package 或 semantic versioning。

## S2 — Software-first foundation (not started)

- [ ] **S2A — Build decision gate**：pin 官方相容的 released ESP-IDF + esp-matter pair，選定具 PSRAM 的 ESP32-S3 module/board，並記錄 flash、partition 與 target build authority。
- [ ] **S2B — Portable contract foundation**：只實作 protocol constants、serializer/parser boundary、deterministic crypto vectors、transport interface/Fake、Unified Device Model 與 four-channel Matter mapping contract 的 host tests。
- [ ] **S2C — Minimum validation foundation**：為 S2 contract 增加最低必要 host test/CI；只在 S2A 完成後評估 compile-only ESP32/Matter adapter。

## Explicitly NOT authorized in S2 unless a later Stage explicitly changes scope

- 不寫完整 eWeLink runtime、實際 mDNS browse loop、production HTTP transport 或 polling/retry runtime。
- 不寫 production AES/deviceKey storage/provisioning flow；只允許為 contract/test-vector 需要做的研究與 deterministic software design。
- 不建立完整 Matter production firmware、commissioning product flow 或 Google Home pairing implementation。
- 不執行真實 CK-BL602 network command、relay switching、hardware test 或 Google TV Streamer commissioning。
- 不建立 Home Assistant / Raspberry Pi requirement。
- 不因「未來可能支援所有 eWeLink」就提前實作大量 UIID/device families；第一個 consumer 僅 freeze 4-channel switch contract，通用化只做到 library-ready boundary。

S2 is not authorized by this completed S1 task. Do not start it without a new explicit launch.
