# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`，branch `main`。
- Bootstrap、S1、S2A、S2B、S2C、M1 與 D1 offline evidence harness 已完成。
- Framework authority：ESP-IDF `v5.5.5` + `espressif/esp_matter ==1.6.0`；C3 `VIABLE_CONSTRAINED` 僅限 software-first compile/static resource evidence。
- Network、Hardware、Matter interoperability 均未驗證；CK-BL602 behavior 仍為 `UNKNOWN` / `HARDWARE_TEST_PENDING`，不得標為 `CONFIRMED_LOCAL`。
- 真實 credential、deviceKey、Wi-Fi password、Matter fabric material 不得進 Git、CI、fixture、log 或文件。

## D2 — Passive live mDNS observation — NOT AUTHORIZED

- [ ] 取得明確使用者授權後，才可在 CK-BL602 所在 LAN 做一次 bounded、passive/read-only `_ewelink._tcp.local.` observation。
- [ ] Raw capture 不得 commit；先經 D1 sanitizer/analyzer，再 review sanitized facts。
- [ ] 不自動升級至 HTTP、`/zeroconf/*`、`getState`、deviceKey、decrypt、relay/channel control、retry loop 或 background monitor。
- [ ] Network、Hardware、Matter interoperability 與 CK-BL602 local behavior 的 evidence classification 依實際 observation 決定；本 queue 不授權執行。
