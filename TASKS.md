# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`
- 預期 Branch：`main`
- Bootstrap 與 S1 Architecture / Contract Freeze 已完成；durable authority 見 `docs/architecture.md`、`docs/references/README.md`、`docs/references/sources/upstream-sources.md` 與 `VALIDATION.md`。
- Framework/build authority 已 freeze 為 **ESP-IDF `v5.5.5` + esp-matter component `1.6.0`**；primary target/module profile 為 **ESP32-S3-WROOM-1-N16R8**（16 MB flash / 8 MB Octal PSRAM）。詳細 bootstrap、partition 與 S2C compile gate 見 `docs/build.md`；carrier/product board 仍未選定或驗證。
- 專案目標：建立 ESP32-based、local-first 的 eWeLink LAN → Matter Bridge；第一個真實 consumer 為 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03` 類多路 Wi-Fi switch。
- 第一個 Matter mapping：4-channel binary switch → 4 × Matter On/Off bridged endpoints。
- 不預設 Home Assistant、Raspberry Pi、eWeLink Cloud 或 Internet 為日常控制依賴。
- 真實 CK-BL602 UIID、wire payload、encryption applicability、LAN 行為、ESP32 runtime 與 Google TV Streamer commissioning / interoperability 目前均非 `CONFIRMED_LOCAL`；涉及實機者維持 `UNKNOWN` / `INFERRED` / `HARDWARE_TEST_PENDING`。
- credential / deviceKey / Wi-Fi password / Matter fabric secret 不得提交 Git、測試 fixture、log 或文件。所有 software-first crypto fixture 必須使用明確標註的 synthetic/non-secret values。
- 現階段維持 monorepo 且 library-ready；不得為假想 reuse 提前拆多 repository、package 或 semantic versioning。

# S2 — Software-first foundation

S2 採 sequential gates。**先執行 S2A；S2A 完成並 review 前，不自行開始 S2B/S2C。** 這是為避免 dependency/version/target 尚未固定就產生需要重做的 source/build work。

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
