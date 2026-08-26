# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`
- 預期 Branch：`main`
- Bootstrap、S1 Architecture / Contract Freeze 與 S2A Build Authority 已完成；durable authority 見 `docs/architecture.md`、`docs/build.md`、`docs/references/README.md`、`docs/references/sources/upstream-sources.md` 與 `VALIDATION.md`。
- Framework/build authority 已 freeze 為 **ESP-IDF `v5.5.5` + esp-matter component `1.6.0`**；primary target/module profile 為 **ESP32-S3-WROOM-1-N16R8**（16 MB flash / 8 MB Octal PSRAM）。carrier/product board 仍未選定或驗證；S2B 不得重新打開這個 build decision，除非發現正式 evidence conflict。
- 專案目標：建立 ESP32-based、local-first 的 eWeLink LAN → Matter Bridge；第一個真實 consumer 為 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 類多路 Wi-Fi switch。
- 第一個 Matter mapping：4-channel binary switch → 4 × Matter On/Off bridged endpoints。
- 不預設 Home Assistant、Raspberry Pi、eWeLink Cloud 或 Internet 為日常控制依賴。
- 真實 CK-BL602 UIID、wire payload、encryption applicability、LAN 行為、ESP32 runtime 與 Google TV Streamer commissioning / interoperability 目前均非 `CONFIRMED_LOCAL`；涉及實機者維持 `UNKNOWN` / `INFERRED` / `HARDWARE_TEST_PENDING`。
- credential / deviceKey / Wi-Fi password / Matter fabric secret 不得提交 Git、測試 fixture、log 或文件。所有 software-first crypto fixture 必須使用明確標註的 synthetic/non-secret values。
- 現階段維持 monorepo 且 library-ready；不得為假想 reuse 提前拆多 repository、package 或 semantic versioning。

# S2C — Minimum CI + Compile-only Matter/ESP32 Integration（S2B 完成並 review 後才可執行）

- [ ] **S2C1 — Minimum host CI**：只建立能重現 S2B portable tests 的最低必要 GitHub Actions / host build；避免大矩陣與重複 validation。
- [ ] **S2C2 — ESP-IDF target compile harness**：使用 `docs/build.md` pinned build authority，讓 `esp32s3` / N16R8 profile 真正 compile/link portable core與最小 platform adapter，證明 intended backend 沒被 conditional build 排除。
- [ ] **S2C3 — esp-matter bridge compile probe**：只做 compile-only integration，驗證 pinned `esp_matter_bridge` API 能建立/描述本專案所需的 bridged On/Off endpoint lifecycle boundary；可使用 synthetic/fake device descriptor，不做 commissioning、Wi-Fi runtime或 controller interaction。
- [ ] **S2C4 — Partition + resource baseline**：依 `docs/build.md` frozen gate，建立/驗證最低充分 custom partition table，並記錄 build artifact / flash / static memory 等 compile-time 初始資源 evidence；只作 baseline，不推論 runtime heap、radio coexistence或production margin。
- [ ] **S2C5 — Durable sync / closure**：更新 `VALIDATION.md`、roadmap、README/architecture（僅需要時）與 queue。S2完成後下一階段應是實際 eWeLink LAN transport / diagnostic harness 前的 evidence gate，而不是直接宣稱 Matter Bridge 可用。

# Explicitly NOT authorized in S2

- 不執行真實 mDNS browse、HTTP request、LAN discovery或 CK-BL602 command。
- 不執行 relay switching、hardware test、Google TV Streamer / Google Home commissioning或 Matter interoperability。
- 不實作 production credential provisioning、deviceKey persistent storage、eWeLink Cloud login/App ID/token flow。
- 不建立 Home Assistant / Raspberry Pi dependency。
- 不把 CUBE-OS/add-on 或 Tasmota reference-only source搬入本 repo。
- 不為「未來支援所有 eWeLink」提前加入其他 UIID、light、sensor、curtain、climate families。
- 不建立 speculative scheduler、polling engine、retry subsystem、web UI、MQTT、OTA或多 gateway topology。

# S2 overall completion condition

只有 S2A → S2B → S2C 都經個別 explicit launch / review且完成後，才可宣告 **Software-first foundation complete**。此狀態最高只代表 Host PASS + selected target Compile PASS（若 S2C成功）；Network、Hardware、Matter interoperability仍必須保持未驗證。
