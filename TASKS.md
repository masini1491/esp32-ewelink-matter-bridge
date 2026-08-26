# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`
- 預期 Branch：`main`
- Bootstrap 已完成；目前 repository 已有最小 `AGENTS.md`、`README.md`、`.gitignore`。下一步不是 production implementation，而是 **S1 Architecture / Contract Freeze**。
- 專案目標：建立 ESP32-based、local-first 的 eWeLink LAN → Matter Bridge；第一個真實 consumer 為 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 類多路 Wi-Fi switch。
- 第一個 Matter mapping：4-channel binary switch → 4 × Matter On/Off bridged endpoints。
- 不預設 Home Assistant、Raspberry Pi、eWeLink Cloud 或 Internet 為日常控制依賴。
- 真實 CK-BL602 LAN 行為、ESP32 runtime 與 Google TV Streamer commissioning / interoperability 目前均為 `HARDWARE_TEST_PENDING`。
- credential / deviceKey / Wi-Fi password / Matter fabric secret 不得提交 Git、測試 fixture、log 或文件。
- 現階段維持 monorepo 且 library-ready；不得為假想 reuse 提前拆多 repository、package 或 semantic versioning。

## Stage 0 evidence handoff（供 S1 驗證，不等於可直接複製）

目前已取得的外部 evidence 應由 S1 以最小必要 GitHub / upstream read 驗證並寫成 repository-local provenance：

- `espressif/esp-matter`：Matter on ESP32 / bridge implementation 的主要 upstream；repository license 已確認為 Apache-2.0。優先 reuse upstream Matter runtime / bridge capability，不自行重做 commissioning、fabric 或 CHIP core。
- `project-chip/connectedhomeip`：Matter/CHIP upstream reference；license 已確認為 Apache-2.0。
- `AlexxIT/SonoffLAN`：MIT；可作 eWeLink LAN protocol / behavior / implementation reference。已觀察其 local implementation 包含 `_ewelink._tcp.local.` discovery、devicekey-derived AES-CBC、PKCS#7、Base64、`/zeroconf/{command}`、預設 8081，以及 `switch` / `switches` 等 local command behavior。S1 必須記錄 revision 與哪些部分可 reuse/port、哪些只是 behavior evidence。
- `eWeLinkCUBE/CUBE-OS` 與 relevant eWeLink CUBE add-on：官方/第一方 evidence 顯示 eWeLink Wi-Fi → Matter bridge 架構成立；目前 repository metadata 未確認 license，預設 `REFERENCE ONLY`，不得 mechanical port / line-by-line translation / rename-and-claim。
- `arendst/Tasmota`：ESP32 / Matter bridge architecture 可供比較，但 repository 為 GPL-3.0；在本專案未有正式 GPL decision 前只作 reference，不把其 source 直接帶入專案。

若 S1 發現上述 license、revision、authority 或 protocol observation 已變更，以最新 upstream evidence 為準並明確記錄差異；不要默默沿用舊聊天室結論。

## S1 — Architecture / Contract Freeze

- [ ] **S1A — Reference / provenance foundation**：建立 topic-scoped reference routing 與最小 synthesis/dossier，至少覆蓋 `esp-matter`、ConnectedHomeIP、SonoffLAN、eWeLink CUBE、Tasmota。每個來源記錄 repository、實際 revision/commit、license、authority、relevant files/topics、可 reuse / reference-only 邊界、limitations、do-not-assume 與 unresolved gaps。不得完整 vendor/copy upstream source 進 repo。
- [ ] **S1B — Technology stack / target decision**：依官方 Matter support、bridge API maturity、host-testability、integration cost、RAM/flash/resource margin、BLE commissioning 與未來 growth，比較 ESP-IDF / Arduino-ESP32 及 ESP32-C3 / C6 / S3 等候選。選「最低充分 target + 合理成長空間」；若 evidence 不足以 freeze concrete board，至少 freeze framework + target family，並建立下一 Stage 前的 decision gate。不得只因其他 sibling repo 使用 ESP-IDF/C6 就機械沿用。
- [ ] **S1C — Layering / ownership contract**：freeze 第一版 dependency direction：`eWeLink Transport → eWeLink Protocol/Registry → Unified Device Model → Matter Adapter/Bridge → Matter over Wi-Fi`。Matter layer 不得直接 parse raw eWeLink HTTP/AES/mDNS；eWeLink layer 不得接管 Matter fabric/commissioning；portable core 不得無理由洩漏 ESP-IDF / FreeRTOS / Matter-specific types。
- [ ] **S1D — First capability contract**：freeze `CK-BL602-4SW-HS / HS-03` 第一個 consumer 的最小 machine contract：device identity、UIID/capability evidence、channel numbering、4-channel state representation、command intent、availability/unknown semantics、state convergence / confirmation semantics，以及 4 × Matter On/Off bridged endpoint mapping。任何未被 upstream 或實機證實的 device-specific behavior 維持 `INFERRED` / `UNKNOWN` / `HARDWARE_TEST_PENDING`。
- [ ] **S1E — Security / secret ownership boundary**：freeze `deviceId`、`deviceKey`、Wi-Fi credential、Matter fabric/commissioning secret 的 ownership/storage/logging rules。S1 不需要取得任何真實 secret；不得把 eWeLink account/password 或真實 deviceKey 寫入 repository。若未來 provisioning 需要 cloud login / App ID / token，先列 FUTURE / separate authority，不納入第一版 local runtime。
- [ ] **S1F — Software-first validation contract**：定義 Stage 2 可在無硬體下完成的範圍：protocol constants、serializer/parser、crypto deterministic vectors、transport interface、Fake/Mock eWeLink device/transport、unified state model、Matter mapping contract、host tests、CI，以及必要時 compile-only ESP32/Matter adapter。明確區分 Host/Test PASS、Compile PASS、Network PASS、Hardware PASS、Matter interoperability PASS。
- [ ] **S1G — Durable project docs / governance sync**：依 freeze 結果更新 project-specific `AGENTS.md`、README 與必要的 architecture / roadmap / validation / reference-routing docs。只放本專案 authority；common playbook 用 routing，不複製全文。README 可以維持精簡，不要把研究假設寫成產品已支援能力。

## Explicitly NOT authorized in S1

- 不寫完整 eWeLink runtime、實際 mDNS browse loop、production HTTP transport 或 polling/retry runtime。
- 不寫 production AES/deviceKey storage/provisioning flow；只允許為 contract/test-vector 需要做的研究與 deterministic software design。
- 不建立完整 Matter production firmware、commissioning product flow 或 Google Home pairing implementation。
- 不執行真實 CK-BL602 network command、relay switching、hardware test 或 Google TV Streamer commissioning。
- 不建立 Home Assistant / Raspberry Pi requirement。
- 不因「未來可能支援所有 eWeLink」就提前實作大量 UIID/device families；第一個 consumer 僅 freeze 4-channel switch contract，通用化只做到 library-ready boundary。

## S1 success / STOP condition

S1 只在以下條件同時成立時完成：

1. upstream provenance / license / reuse boundary 已可審查，且 relevant revision 已 pinned；
2. framework / target decision 有 evidence，或留下明確且 bounded 的下一 Stage decision gate；
3. layering、ownership、secret boundary 與第一個 4-channel capability contract 已 freeze 到足以進入 software-first implementation；
4. Stage 2 host-test / mock / compile-only scope 與 validation taxonomy 已明確；
5. durable docs / `AGENTS.md` 已同步且沒有把 common playbook 大量複製進 project repo；
6. 沒有真實 credential、沒有未授權 hardware/network execution、沒有把 GPL / unlicensed reference source 機械 port 進 repository。

完成後：

- 將已完成 S1 item 從 `TASKS.md` 移除；
- 只有真正 Blocked / Deferred / Pending-validation / 下一個可執行 Stage 才留在 queue；
- 不自行啟動 Stage 2；
- commit / push 後 STOP，等待使用者與 ChatGPT review。
