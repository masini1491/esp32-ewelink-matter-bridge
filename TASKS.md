# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Project bootstrap boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`
- 預期 Branch：`main`
- 專案目標：建立 ESP32-based、local-first 的 eWeLink LAN → Matter Bridge；第一個真實 consumer 為 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 類多路 Wi-Fi switch。
- 第一個 Matter mapping：4-channel binary switch → 4 × Matter On/Off bridged endpoints。
- Matter stack baseline：優先採 Espressif `esp-matter` / upstream ConnectedHomeIP，不自行重做 Matter commissioning、fabric 或 bridge runtime。
- eWeLink LAN baseline：以合法可用的 upstream evidence 建立 embedded C/C++ implementation；SonoffLAN 可作 MIT provenance/reference，eWeLink CUBE 未確認 license 的 source 僅 `REFERENCE ONLY`，Tasmota GPL source 僅 architecture/reference，除非另有正式 license decision。
- Framework / concrete target 尚未因方便而永久 freeze；Stage 1 必須依 upstream support、host-testability、Matter integration cost 與 resource margin 作最低充分決策。ESP32-C6 / C3 / S3 皆可作候選，不以 compile success 推定硬體相容。
- 不預設 Home Assistant、Raspberry Pi、eWeLink Cloud 或 Internet 為日常控制依賴。
- 真實 CK-BL602 LAN 行為、ESP32 runtime 與 Google TV Streamer commissioning / interoperability 目前均為 `HARDWARE_TEST_PENDING`。
- credential / deviceKey / Wi-Fi password / Matter fabric secret 不得提交 Git、測試 fixture、log 或文件。
- 現階段維持 monorepo 且 library-ready；不得為假想 reuse 提前拆多 repository、package 或 semantic versioning。

## S1 — Repository Bootstrap + Architecture / Contract Freeze

- [ ] 依 `masini1491/ai-development-playbook` 與本專案需求建立最小 repository foundation：project-specific `AGENTS.md` routing/governance、README、reference/provenance routing、architecture/roadmap、validation baseline、必要的 `.gitignore` / `.gitattributes` 與最小 host-test skeleton；不要直接開始完整 eWeLink runtime 或 Matter production firmware。
- [ ] 先比較 `masini1491/esp32-wfrac-local-bridge`、`masini1491/esp32-yale-local-bridge`、`masini1491/esp32-vag-data-server` 的現行 repository conventions，只重用共通而仍適合本專案的治理／目錄／evidence pattern；不得機械複製 product-specific contract。
- [ ] 建立 topic-scoped upstream dossier / synthesis，至少覆蓋：`espressif/esp-matter`、`project-chip/connectedhomeip`、`AlexxIT/SonoffLAN`、`eWeLinkCUBE/CUBE-OS` / relevant add-on、`arendst/Tasmota`；記錄 revision、license、authority、可 reuse / reference-only 邊界與 unresolved gaps。
- [ ] Freeze 第一版 layering 與 ownership：`eWeLink Transport → eWeLink Protocol/Registry → Unified Device Model → Matter Adapter/Bridge → Matter over Wi-Fi`。Matter layer 不得直接處理 raw eWeLink HTTP/AES/mDNS；eWeLink layer 不得接管 Matter fabric/commissioning。
- [ ] Freeze 第一個 capability contract：4-channel switch 的 identity/state/command/availability semantics，以及 4 × Matter On/Off bridged endpoint mapping；未知欄位與硬體行為維持 `UNKNOWN` / `HARDWARE_TEST_PENDING`。
- [ ] 決定第一版正式 framework / target family 的最低充分 baseline；若 evidence 尚不足，保留候選並列明 Stage 2 前的決策 gate，不得為了開始 coding 猜一個 target。
- [ ] 建立 software-first validation 計畫：protocol constants、serializer/parser、crypto test vectors、transport interface、Fake/Mock、host tests、CI、compile-only adapter；不得把 host/compile PASS 宣稱為 hardware/network/Matter interoperability PASS。

## S1 success / STOP condition

S1 只在以下條件同時成立時完成：

1. repository governance / routing 與 architecture authority 已建立且不重複整份 common playbook；
2. upstream provenance / license / reuse boundary 已可審查；
3. 第一個 CK-BL602 4-channel capability contract 與 Matter mapping 已 freeze 到足以進入 software-first implementation；
4. framework / target decision 已有 evidence，或明確保留為下一 Stage 的 gated decision；
5. host-test / mock / hardware-pending validation boundary 已寫清楚；
6. 沒有真實 credential、沒有未授權 hardware/network execution、沒有把 reference-only source 機械 port 進 repository。

完成後更新 durable docs / validation evidence，從 `TASKS.md` 移除 S1 已完成項目；若仍有未解 blocker，只保留真正 unfinished / blocked / deferred 工作並 STOP。
