# TASKS

本檔只保存 active unfinished-work / executable scoped Prompt queue。完成並驗證的 Stage 應移除；永久紀錄以 Git history 與 durable project docs 為準。

## Current execution boundary

- 目標 Repository：`masini1491/esp32-ewelink-matter-bridge`，branch `main`。
- Bootstrap、S1 Architecture / Contract Freeze、S2A、S2B 與 S2C software-first compile/resource gate 已完成。
- Framework authority：ESP-IDF `v5.5.5` + `espressif/esp_matter ==1.6.0`。
- Primary constrained target：ESP32-C3 / 4 MB-class，Matter over Wi-Fi；S2C classification：`VIABLE_CONSTRAINED`，僅限 software-first compile/static resource evidence。
- ESP32-S3-WROOM-1-N16R8 僅為 development/high-margin fallback；ESP32-C6 僅為 optional future Thread capability。
- Network、Hardware、Matter interoperability 均未驗證；CK-BL602 device behavior 仍為 `UNKNOWN` / `HARDWARE_TEST_PENDING`，不得標為 `CONFIRMED_LOCAL`。
- 真實 credential、deviceKey、Wi-Fi password、Matter fabric material 不得進 Git、CI、fixture、log 或文件。
## Next evidence-gated stage — not authorized

- [ ] **Real eWeLink LAN diagnostic / evidence gate**：M1 完成後仍需另行取得明確授權，才建立 CK-BL602 LAN behavior 的 evidence／permission gate。不得從相似裝置推定 UIID、wire schema、encryption applicability、channel numbering或 convergence semantics；本 queue 本身不授權 live network、hardware或真實 credential操作。
