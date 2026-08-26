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

# S2B — Portable Protocol / Device-Model Foundation

**S2B 是目前唯一可執行的 implementation Stage。S2C 在 S2B 完成、review 且另行明確授權前不得開始。**

建議實作順序：component boundary → generic protocol envelope / serializer-parser → crypto-provider contract與 synthetic vectors → Unified Device Model → Matter mapping contract → Fake/Mock → host validation。若中途 evidence 顯示某 wire/device-specific欄位仍不足，保留 typed unknown/adapter boundary；不要為了讓測試通過而猜 protocol。

- [ ] **S2B1 — Portable component boundaries**：建立最低充分 portable C/C++ foundation 與 host build/test skeleton；dependency direction 必須符合 `docs/architecture.md`。核心不得依賴 ESP-IDF、FreeRTOS、esp-matter/CHIP types、socket、Wi-Fi、mDNS、NVS 或 target-specific headers。優先維持簡單 component boundaries，不為未來假想 reuse 建 speculative HAL/package。
- [ ] **S2B2 — Generic eWeLink LAN protocol envelope**：只依 pinned SonoffLAN behavior evidence與 S1 contract 實作第一版必要 generic envelope/command value types，例如 sequence、canonical device identity reference、command/path、plain/encrypted envelope boundary與 bounded payload representation。不得宣稱 CK-BL602-specific UIID、`switches` wire schema、channel field naming或 encryption applicability 已確認；這些維持 adapter/evidence gate。
- [ ] **S2B3 — Crypto provider contract + deterministic vectors**：建立 devicekey-derived MD5 key → AES-CBC → PKCS#7 → Base64 的 contract、provider interface與 deterministic synthetic/non-secret vectors。不得自行實作 cryptographic primitive；host test provider如需第三方 crypto library，先完成 license/toolchain review並使其可替換。Production ESP-IDF crypto adapter不在本 Stage實作。真實 deviceKey不得出現於 repo、log、fixture或 final summary。
- [ ] **S2B4 — Serializer / parser boundaries**：建立 bounded、deterministic、host-testable serialization/parsing contract，覆蓋 valid、missing、malformed、oversized/unsupported input與 encrypted/plain envelope distinction。不得撰寫 ad-hoc unsafe JSON parser。若新增 JSON dependency，必須記錄 exact dependency、license、portable/resource理由；避免只為少量欄位引入過重 framework。
- [ ] **S2B5 — Unified Device Model**：實作 S1 freeze 的 portable semantics：canonical identity、4 logical channels `0..3`、每 channel `on/off/unknown`、device availability、freshness/staleness、pending command intent、transport acceptance 與 observed convergence 分離。unknown 不得等同 off；disconnect/stale 不製造假的 state change；reconnect需新 observation才恢復 fresh。
- [ ] **S2B6 — Matter mapping contract only**：建立完全不依賴 esp-matter/CHIP types 的 portable mapping descriptor/contract，能表達 `canonical device identity + channel index → stable bridged On/Off endpoint binding key`、四 channel isolation與 endpoint identity不得由 discovery order / transient IP 決定。不得在 S2B 建立真正 esp-matter endpoint或 persistence runtime。
- [ ] **S2B7 — Fake / Mock + orchestration contract**：建立 FakeTransport / synthetic device observations，使 host tests能驗證 command intent → transport request boundary、transport accepted ≠ observed state、observation → convergence、disconnect/reconnect/staleness、四 channel isolation與 malformed response handling。Fake不得偷偷實作 live socket/mDNS/HTTP。
- [ ] **S2B8 — Durable validation / docs sync**：建立最低充分 host validation command與 evidence；更新 `VALIDATION.md`、必要 architecture/reference notes、README/roadmap（只在狀態需要時）與 queue。若新增第三方 host-only dependency，將 license/provenance寫入正式 authority。完成後移除 S2B items，保留 S2C但不得開始。

## S2B validation minimum

至少需要：

- host-side deterministic unit tests；
- protocol envelope serializer/parser round-trip與 malformed/boundary tests；
- synthetic crypto vectors（含 key derivation、padding/block boundary、Base64/encrypted envelope deterministic checks）；
- Unified Device Model state-transition tests：unknown、pending、accepted、observed convergence、stale、disconnect/reconnect；
- four-channel isolation tests；
- stable identity / Matter binding-key contract tests；
- FakeTransport tests，證明沒有 live network dependency；
- dependency-direction audit；
- secret scan；
- third-party license/provenance audit；
- `git diff --check`。

S2B 成功最高只能宣告 `Host PASS` / `Static/Test PASS`。不得宣稱 `Compile PASS`、`Network PASS`、`Hardware PASS` 或 `Matter interoperability PASS`。

## S2B STOP / escalation conditions

遇到下列情況不得猜測式 implementation：

- 必須知道 CK-BL602-specific UIID、`switches` exact wire schema、encryption applicability或 response semantics才可繼續；
- pinned SonoffLAN behavior evidence互相矛盾或不足以定義 generic contract；
- 需要引入 license不明 / GPL / reference-only source 才能完成；
- portable core開始需要 ESP-IDF/FreeRTOS/Matter types才能成立；
- crypto design要求自行實作 primitive；
- task需要 live LAN/hardware才能驗證。

此時保留最小 evidence、將 blocker留在 `TASKS.md`、使用 `INSUFFICIENT OBSERVABILITY` / `UNKNOWN` 等正確分類並 STOP；不要自行擴張成 S2C或 hardware Stage。

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
