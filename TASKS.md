# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`
- 預期 Branch：`main`
- Bootstrap 與 S1 Architecture / Contract Freeze 已完成；durable authority 見 `docs/architecture.md`、`docs/references/README.md`、`docs/references/sources/upstream-sources.md` 與 `VALIDATION.md`。
- Framework 已 freeze 為 **ESP-IDF + esp-matter**；primary target family 為 **ESP32-S3**。S2A 必須先 pin 官方相容 released version pair，並選定可重現的 PSRAM-capable ESP32-S3 build target/module profile，之後才可做 target-specific compile adapter。
- 專案目標：建立 ESP32-based、local-first 的 eWeLink LAN → Matter Bridge；第一個真實 consumer 為 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 類多路 Wi-Fi switch。
- 第一個 Matter mapping：4-channel binary switch → 4 × Matter On/Off bridged endpoints。
- 不預設 Home Assistant、Raspberry Pi、eWeLink Cloud 或 Internet 為日常控制依賴。
- 真實 CK-BL602 UIID、wire payload、encryption applicability、LAN 行為、ESP32 runtime 與 Google TV Streamer commissioning / interoperability 目前均非 `CONFIRMED_LOCAL`；涉及實機者維持 `UNKNOWN` / `INFERRED` / `HARDWARE_TEST_PENDING`。
- credential / deviceKey / Wi-Fi password / Matter fabric secret 不得提交 Git、測試 fixture、log 或文件。所有 software-first crypto fixture 必須使用明確標註的 synthetic/non-secret values。
- 現階段維持 monorepo 且 library-ready；不得為假想 reuse 提前拆多 repository、package 或 semantic versioning。

# S2 — Software-first foundation

S2 採 sequential gates。**先執行 S2A；S2A 完成並 review 前，不自行開始 S2B/S2C。** 這是為避免 dependency/version/target 尚未固定就產生需要重做的 source/build work。

## S2A — Build Authority / Reproducible Target Gate

- [ ] **S2A1 — Released dependency pair**：以 Espressif 官方 release / compatibility evidence pin 一組 released `ESP-IDF + esp-matter` version pair；不得使用 floating `main` 作正式 build authority。記錄 exact version/tag/commit、官方相容性來源與取得方式。
- [ ] **S2A2 — ESP32-S3 build target profile**：選定一個可重現、PSRAM-capable 的 ESP32-S3 module/board build profile，記錄 target、module/board identity、flash、PSRAM、最低 partition requirement、USB/power/pinout 是否屬於 build authority。若實際 PCB/板型尚未購買，允許 freeze「module/build profile」而不是實體開發板，但不得假裝 hardware 已選購或驗證。
- [ ] **S2A3 — Toolchain/bootstrap contract**：建立最低充分的 dependency/bootstrap/build authority 文件或 manifest；優先使用官方推薦方式，不 vendor 整份 esp-matter / ConnectedHomeIP。記錄 host prerequisites 與可重現 setup，但不需要在本 Stage 建 production firmware。
- [ ] **S2A4 — Compile-gate design**：定義 S2C 未來 compile-only harness 應如何證明 selected target + esp-matter bridge API 真正參與 compile/link。此 Stage 可做最小 dependency/toolchain smoke check；若 smoke check 需要新增 source，僅允許 build-probe 級別，不得開始 eWeLink/Matter application implementation。
- [ ] **S2A5 — Durable sync**：更新 build authority、architecture/roadmap/validation/reference revision（只有 upstream revisit 真有變化時）與 `AGENTS.md` 必要 project-specific contract。README 只需使用者可理解的最小狀態，不堆砌 setup 細節。

### S2A success / STOP

S2A 完成必須同時成立：

1. released ESP-IDF + esp-matter pair 已 pinned 且有官方 compatibility evidence；
2. ESP32-S3 PSRAM-capable build profile 已可重現，flash/PSRAM/partition 假設明確；
3. dependency/bootstrap authority 不依賴 floating branches；
4. 未建立 production eWeLink runtime 或 Matter app；
5. validation 清楚標記 build/toolchain evidence，不宣稱 network/hardware/interoperability；
6. commit / push 後 STOP，等待 ChatGPT review，再授權 S2B。

## S2B — Portable Protocol / Device-Model Foundation（S2A review 後才可執行）

- [ ] **S2B1 — Portable component boundaries**：建立 portable C/C++ foundation，dependency direction 必須符合 `docs/architecture.md`。核心不得依賴 ESP-IDF、FreeRTOS、esp-matter/CHIP types、socket、Wi-Fi、mDNS 或 NVS。
- [ ] **S2B2 — Generic eWeLink LAN protocol envelope**：只依 pinned SonoffLAN behavior evidence實作／freeze與第一版必要的 generic envelope/command contracts，例如 sequence、device identity、command/path、plain/encrypted envelope boundary；不得猜 CK-BL602-specific UIID 或 `switches` wire schema。若 exact field behavior evidence 不足，保留 typed `Unknown/Unsupported` 或 adapter boundary，不以猜測補齊。
- [ ] **S2B3 — Crypto contract / deterministic vectors**：建立 devicekey-derived MD5 key、AES-CBC、PKCS#7、Base64 envelope semantics 的 deterministic synthetic test vectors與 crypto-provider boundary。**不得自行發明/手刻 cryptographic primitive**；若 portable host implementation 需要 crypto library，先做 license/toolchain review並保持 production crypto 可由 ESP-IDF-supported provider adapter 實作。真實 deviceKey 永不進 repo。
- [ ] **S2B4 — Serializer/parser boundaries**：建立 bounded、deterministic、host-testable serializer/parser contract；不得因方便而寫 ad-hoc unsafe JSON parser。JSON dependency若新增，必須說明 license、resource/portability理由與是否屬 portable core或adapter。
- [ ] **S2B5 — Unified Device Model**：實作 S1 freeze 的 portable state semantics：canonical identity、4 logical channels `0..3`、`on/off/unknown`、availability、freshness/staleness、pending command intent、transport acceptance ≠ observed convergence。不得把 unknown 當 off。
- [ ] **S2B6 — Matter mapping contract only**：建立不依賴 esp-matter types 的 portable mapping descriptor/contract，能表達 canonical device + channel → stable bridged On/Off endpoint identity requirement；不在 S2B 建真正 Matter endpoint runtime。
- [ ] **S2B7 — Fake/Mock**：建立 FakeTransport / synthetic device observations，使 command → transport request boundary、observation → model convergence、disconnect/reconnect/staleness等 contract 可在 host 測試；禁止 live LAN。

### S2B validation minimum

- deterministic host unit tests；
- malformed/boundary input tests；
- crypto synthetic vectors；
- state transition / pending-vs-observed / stale availability tests；
- four-channel isolation與 stable identity mapping tests；
- secret scan / license audit / dependency-direction review；
- 不得將 Host PASS 宣稱為 Compile/Network/Hardware/Matter interoperability PASS。

## S2C — Minimum CI + Compile-only Matter/ESP32 Integration（S2B 完成並 review 後才可執行）

- [ ] **S2C1 — Minimum host CI**：只建立能重現 S2B portable tests 的最低必要 GitHub Actions / host build；避免大矩陣與重複 validation。
- [ ] **S2C2 — ESP-IDF target compile harness**：使用 S2A pinned build authority，讓 selected ESP32-S3 target 真正 compile/link portable core與最小 platform adapter，證明 intended backend 沒被 conditional build 排除。
- [ ] **S2C3 — esp-matter bridge compile probe**：只做 compile-only integration，驗證 pinned `esp_matter_bridge` API 能建立/描述本專案所需的 bridged On/Off endpoint lifecycle boundary；可使用 synthetic/fake device descriptor，不做 commissioning、Wi-Fi runtime或 controller interaction。
- [ ] **S2C4 — Resource baseline**：記錄 build artifact / flash / static memory 等 compile-time 可取得的初始資源 evidence；只作 baseline，不推論 runtime heap、radio coexistence或production margin。
- [ ] **S2C5 — Durable sync / closure**：更新 `VALIDATION.md`、roadmap、README/architecture（僅需要時）與 queue。S2完成後下一階段應是實際 eWeLink LAN transport / diagnostic harness 前的 evidence gate，而不是直接宣稱 Matter Bridge 可用。

# Explicitly NOT authorized in S2

- 不執行真實 mDNS browse、HTTP request、LAN discovery或 CK-BL602 command。
- 不執行 relay switching、hardware test、Google TV Streamer / Google Home commissioning或 Matter interoperability。
- 不實作 production credential provisioning、deviceKey persistent storage、eWeLink Cloud login/App ID/token flow。
- 不建立 Home Assistant / Raspberry Pi dependency。
- 不把 CUBE-OS/add-on 或 Tasmota reference-only source 搬入本 repo。
- 不為「未來支援所有 eWeLink」提前加入其他 UIID、light、sensor、curtain、climate families。
- 不建立 speculative scheduler、polling engine、retry subsystem、web UI、MQTT、OTA或多 gateway topology。

# S2 overall completion condition

只有 S2A → S2B → S2C 都經個別 explicit launch / review 且完成後，才可宣告 **Software-first foundation complete**。此狀態最高只代表 Host PASS + selected target Compile PASS（若 S2C 成功）；Network、Hardware、Matter interoperability 仍必須保持未驗證。
