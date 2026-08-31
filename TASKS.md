# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`，branch `main`。
- Bootstrap、S1、S2A、S2B、S2C、M1 與 D1 offline evidence harness 已完成。
- Framework authority：ESP-IDF `v5.5.5` + `espressif/esp_matter ==1.6.0`；C3 `VIABLE_CONSTRAINED` 僅限 software-first compile/static resource evidence。
- Network、Hardware、Matter interoperability 均未驗證；CK-BL602 behavior 仍為 `UNKNOWN` / `HARDWARE_TEST_PENDING`，不得標為 `CONFIRMED_LOCAL`。
- 第一 consumer 仍限定 `CK-BL602-4SW-HS / CK-BL602-4SW-HS-03`；不得從其他 eWeLink/Sonoff device 推定其 UIID、wire schema、encryption applicability、channel numbering或 convergence semantics。
- 真實 credential、deviceKey、Wi-Fi password、Matter fabric material 不得進 Git、CI、fixture、log 或文件。

## D2 — Bounded live mDNS observation — NOT AUTHORIZED

- [ ] **Latest retry evidence — `INSUFFICIENT OBSERVABILITY`**：以 project baseline `ae28fa7a09eae4f233b907235f80144b39225fd5`、common Playbook `6b898cb1610c6f7264e0e898d010b2456053829a` 執行；stdout preflight PASS、temporary-file round-trip PASS，之後進行一次 passive-only UDP/5353 mDNS 30 秒 observation，未執行 standard query。long-running command 完成後仍無可用 sanitized summary，因此無法判定是否見到 `_ewelink._tcp.local.`、無 target attribution、無 D1 classification、無 `CONFIRMED_LOCAL`、無 `Network PASS`。raw capture 未保存，temporary summary 未殘留，repository 未修改。
- [ ] D2A 已完成 synthetic cross-command result handoff validation。這只解除 observation-result handoff dependency，**不會自動授權**新的 live attempt；每次 D2 live observation仍需新的明確 user launch authorization。
- [ ] 下一次 D2 first contact 仍採最低充分 network activity：先 passive listen；只有在取得 service/TXT metadata 所必需且既有 tool semantics明確時，才允許一次標準 mDNS browse/resolve query。不得升級至其他 protocol或宣稱整個流程完全零 transmit。
- [ ] Observation 必須 one-shot / bounded；不得 background monitor、infinite retry、LAN sweep、port scan 或 arbitrary packet injection。
- [ ] Raw capture 不得 commit。若產生 raw observation，只可存在 temporary local storage必要期間，先經既有 D1 sanitizer/analyzer，再人工 review sanitized facts；raw identifier／secret不得進 model final report、Git、fixture、CI或 durable docs。
- [ ] 不得自動升級至 HTTP、`/zeroconf/*`、`getState`、deviceKey、decrypt、relay/channel control、Matter commissioning/control、BLE、firmware flash/boot、另一台 host、proxy或 cloud API。若 D2 evidence不足，保存最低有效 evidence並 STOP；下一層另開 Stage。
- [ ] D2 成功最多建立與**實際 mDNS observation**相符的 `Network PASS`；只有直接觀察且可靠 attribution 到 CK 的 facts 才能提升為 `CONFIRMED_LOCAL`。UIID、wire schema、encryption applicability、channel numbering、HTTP/getState semantics、convergence與 relay behavior未直接觀察時仍保持 `UNKNOWN` / `HARDWARE_TEST_PENDING`。
- [ ] D2 不得宣告 `Hardware PASS` 或 `Matter interoperability PASS`；完成後依 Completion Evidence Guard檢查 observation、sanitized evidence、classification與 TASKS lifecycle，且不得自行啟動下一 Stage。
