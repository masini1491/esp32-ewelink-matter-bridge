# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`，branch `main`。
- Bootstrap、S1 Architecture / Contract Freeze、S2A、S2B、S2C 與 M1 已完成。
- Framework authority：ESP-IDF `v5.5.5` + `espressif/esp_matter ==1.6.0`。
- Primary constrained target：ESP32-C3 / 4 MB-class，Matter over Wi-Fi；S2C classification：`VIABLE_CONSTRAINED`，僅限 software-first compile/static resource evidence。
- ESP32-S3-WROOM-1-N16R8 僅為 development/high-margin fallback；ESP32-C6 僅為 optional future Thread capability。
- Network、Hardware、Matter interoperability 均未驗證；CK-BL602 device behavior 仍為 `UNKNOWN` / `HARDWARE_TEST_PENDING`，不得標為 `CONFIRMED_LOCAL`。
- 第一 consumer仍限定 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03`；不得從其他 eWeLink/Sonoff device直接推定其 UIID、wire schema、encryption applicability、channel numbering或 convergence semantics。
- 真實 credential、deviceKey、Wi-Fi password、Matter fabric material不得進 Git、CI、fixture、log或文件。

# D1 — Offline eWeLink Discovery Evidence Harness

**D1 是目前唯一授權 Stage。目標是在完全不接觸真實 LAN/device 的前提下，建立第一接觸所需的離線 evidence contract、sanitization 與 deterministic analyzer。D1 不授權任何 live network、hardware、deviceKey 或 HTTP operation。**

## D1 authority / upstream boundary

- eWeLink LAN upstream baseline只讀既有 project dossier與 pinned `AlexxIT/SonoffLAN@5f17a0174e516e5aad17aaa4cb71da9bf0d3e79b` 的最低必要 discovery/TXT processing evidence。
- 已有 upstream evidence：`_ewelink._tcp.local.` browse；常見 service name以 `ewelink` 開頭；TXT可含 `id`、`type`、`seq`、`encrypt`、`iv`、`data1..data4`；`data1..data4`依序串接；encrypted case不應在沒有 deviceKey authority時假裝可解碼。
- 上述全部最多為 `CONFIRMED_UPSTREAM`；CK-BL602實際 service/TXT/UIID/data/encryption仍保持 `UNKNOWN / HARDWARE_TEST_PENDING`，直到後續明確授權的 live evidence成立。
- 不因 SonoffLAN存在 `getState` / `/zeroconf/{command}` 就在 D1實作或執行 HTTP；HTTP semantics與是否 truly read-only留待 live mDNS evidence後另行決定。

## D1.1 — Offline capture schema + sanitization contract

- [ ] 定義一個最小、human-reviewable 的**離線 mDNS capture input schema**，供後續 D2 將一次真實 observation轉成檔案後離線分析。Schema只描述 service metadata/TXT properties，不包含 packet-capture framework或 network API。
- [ ] 定義 sanitized evidence output contract：不得輸出/保存 Wi-Fi credential、deviceKey、Authorization/token、Matter secret；預設不得保存原始 local IP/host、完整 deviceId、IV、ciphertext/raw encrypted payload。需要識別同一裝置時使用 deterministic local alias/hash或等價 pseudonymous identity，不把 secret當 identity。
- [ ] 允許保存真正回答 protocol問題且非 secret的 evidence，例如 service type/name class、port presence、TXT key names、`type`、`seq` presence/shape、`encrypt` flag、fragment count/length、plaintext JSON key/type structure、可能出現的 UIID/field names；實際值是否保留應依最小必要 evidence原則逐欄決定。
- [ ] malformed/missing/oversized input必須 fail closed或標示 UNKNOWN，不得把缺欄位解讀成 false/off/unencrypted。

## D1.2 — Deterministic offline analyzer

- [ ] 建立最小 repository-owned analyzer，優先使用現有 host baseline可穩定執行且**不新增 network dependency**的方式；若 Python standard library足夠，優先用它，不為離線 JSON/TXT分析引入 zeroconf/aiohttp/pcap等 dependency。
- [ ] Analyzer只能讀已提供的離線 capture；不得開 socket、browse mDNS、發 HTTP、讀系統 Wi-Fi credential或自動掃 LAN。
- [ ] 支援 upstream已知的 `data1..data4`有序重組，並區分 plaintext vs encrypted metadata。Encrypted input只輸出 shape/presence/length等安全 evidence，不接受/要求 deviceKey，不做 live/decrypt流程。
- [ ] Plaintext raw若是 JSON，可輸出 deterministic sanitized structure（key/value type及最低必要非敏感 scalar evidence）；不得直接把未知 payload無界 dump進 log。
- [ ] 對 service name/deviceId/host/IP等 identifier做 deterministic redaction/pseudonymization；輸出需適合之後作為 durable evidence而不暴露本地網路細節。

## D1.3 — Synthetic fixtures + host validation

- [ ] 使用**純 synthetic、non-secret** fixtures涵蓋：plaintext fragmented TXT、encrypted fragmented TXT、missing fragment/field、invalid JSON、oversized field、unexpected extra key、service name case variant與非 eWeLink service rejection/ignore semantics。
- [ ] Fixtures不得聲稱是 CK-BL602 sample；只驗證 analyzer對 upstream-known envelope shape與未知欄位的保守處理。
- [ ] 最低充分 validation：deterministic analyzer tests、secret/redaction assertions、malformed boundary tests、`git diff --check`。若只新增 host-side script/docs/tests且未改 firmware/source/build contract，不得浪費成本重跑完整 ESP-IDF C3 compile。

## D1.4 — First-contact runbook boundary

- [ ] 建立/更新最小 durable diagnostic文件，明確寫出 D2第一次 live contact應只做**bounded passive mDNS observation**：固定短時間窗、`_ewelink._tcp.local.`、不發 `/zeroconf/*`、不控制 channel、不使用 deviceKey、不保存 Wi-Fi password、不持續 background monitor。
- [ ] D2 live observation的原始 capture不可直接 commit；先經 D1 analyzer/sanitization後，才依 evidence需要決定哪些 sanitized facts可進 repository。
- [ ] D2若觀察不到 service、或只得到 encrypted TXT，先保存可觀察 evidence並 STOP；不得自動升級 HTTP、deviceKey、packet injection、retry loop或控制 operation。
- [ ] 後續若確實需要 deviceKey-assisted decrypt、`getState`或其他 `/zeroconf` request，必須拆成新的明確 authority Stage，先判定 side effect/read-only semantics；不得由 D2 passive observation自動推導。

## D1 completion / validation ceiling

D1成功最多建立：

- analyzer Static/Test PASS；
- synthetic Host PASS（若實際執行）；
- first-contact evidence contract READY。

D1不得宣告：

- Network PASS；
- Hardware PASS；
- CK-BL602 `CONFIRMED_LOCAL`；
- encryption applicability confirmed；
- UIID/channel schema confirmed；
- HTTP/getState安全或支援已確認。

完成 D1後從 `TASKS.md` 移除 D1，只保留下方 D2 queue；Codex必須 STOP，不得自行開始 D2。

# D2 — Passive live mDNS observation — NOT AUTHORIZED BY D1

- [ ] **Explicit user authorization required**：在與 CK-BL602相同 LAN上，以 D1 runbook 做一次 bounded passive `_ewelink._tcp.local.` observation，取得最小 real-device discovery/TXT evidence，再離線 sanitization/review。
- [ ] D2只允許 discovery/listen/query mDNS service metadata所需的最低 read-only network activity；不發 eWeLink HTTP `/zeroconf/*`、不使用 deviceKey、不做 device control、不 commissioning Matter、不 flash/boot產品 firmware、不持續 background monitor。
- [ ] 任何 Wi-Fi/network credential只存在執行環境必要範圍，不進 Git/log/evidence；raw local IP/device identifier不直接 commit。
- [ ] D2完成與否依實際 observation決定；若 CK-BL602廣播不足以回答 protocol問題，下一步另開 evidence Stage，不在 D2自行擴張。
