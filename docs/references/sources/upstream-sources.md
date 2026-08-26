# Upstream provenance dossier

研究日期：2026-08-26。每筆 revision 是該 repository default branch 當日的 Git commit；後續工作不得把它誤認為已驗證的 local runtime 行為。

## espressif/esp-matter

- Repository：<https://github.com/espressif/esp-matter>
- Pinned revision：`c2cd0cb60c63e35530b5e4125169bd054cabeba3` (`main`)
- License：Apache-2.0。
- Authority：Espressif 官方 Matter SDK；本專案 Matter runtime、bridge API、commissioning/fabric integration 的主要 authority。
- Relevant files/topics：`components/esp_matter_bridge/esp_matter_bridge.h`；`examples/bridge_apps/README.md`、`bridge_cli`、`zigbee_bridge`。
- Observations：bridge component exposes create/resume/remove bridged device APIs，並保存 parent endpoint、device endpoint 與 device type 的 persistent info；bridge examples 明確包含 runtime add/remove 的 `bridge_cli`。
- Reuse boundary：可依 Apache-2.0 與後續 dependency/version decision 使用官方 SDK/API；不要 copy example application wholesale。Matter data model、commissioning、fabric 與 bridged endpoint lifecycle 應交給此 SDK。
- Limitations / do-not-assume：SDK API 存在不代表本專案的 eWeLink device discovery、crypto、state convergence 或 controller interoperability 已被證實；`main` 不是未來 implementation 可直接浮動採用的 version pin。

## project-chip/connectedhomeip

- Repository：<https://github.com/project-chip/connectedhomeip>
- Pinned revision：`f8dc7b9f20b34f6cab940bf8ec2a9ca3331cb195` (`master`)
- License：Apache-2.0。
- Authority：Matter/CHIP upstream reference；`examples/bridge-app/` 是 bridge data-model/lifecycle 的 reference，不是本 ESP32 app 的 implementation base。
- Relevant files/topics：`examples/bridge-app/`（含 `bridge-common`、`esp32`、`linux` variants）。
- Observations：upstream maintains a bridge-app family with shared bridge material and platform variants, so it is useful for checking Matter bridge concepts beneath Espressif's integration.
- Reuse boundary：只透過 selected Espressif integration 間接採用；若日後直接 reuse，須在 exact file/attribution/release compatibility 下再審查。
- Limitations / do-not-assume：不把 generic bridge example 視為 ESP32 resource profile、eWeLink protocol contract 或 Google controller interoperability evidence。

## AlexxIT/SonoffLAN

- Repository：<https://github.com/AlexxIT/SonoffLAN>
- Pinned revision：`5f17a0174e516e5aad17aaa4cb71da9bf0d3e79b` (`master`)
- License：MIT。
- Authority：third-party eWeLink/Sonoff LAN behavior evidence；不是官方 protocol specification。
- Relevant files/topics：`custom_components/sonoff/core/ewelink/local.py`。
- Observations：該 revision implements `_ewelink._tcp.local.` discovery, devicekey-derived MD5 key with AES-CBC/PKCS#7/Base64 payload handling, default port 8081, `/zeroconf/{command}` and `switch` / `switches` command paths. These are `CONFIRMED_UPSTREAM` only.
- Reuse boundary：MIT permits carefully attributed reuse after a future file-level review. S2 should prefer independently designed portable code plus deterministic vectors; no mechanical port, line-by-line translation, or copied retry/logging policy.
- Limitations / do-not-assume：CK-BL602 variants may differ; service records, HTTP response details, channel semantics, encryption applicability and retry behavior are not `CONFIRMED_LOCAL`.

## eWeLinkCUBE/CUBE-OS

- Repository：<https://github.com/eWeLinkCUBE/CUBE-OS>
- Pinned revision：`1e7db1eaf2288b9a3c01b575829b83210b58f4b6` (`master`)
- License：NONE/UNKNOWN in GitHub metadata; no repository license was established during S1.
- Authority：first-party product evidence that local eWeLink Wi-Fi to Matter bridging exists; not a protocol or reuse authority.
- Relevant files/topics：root `README.md` describes self-hosted local eWeLink Wi-Fi / Zigbee to Matter bridging.
- Reuse boundary：REFERENCE ONLY. No source, asset, configuration or implementation pattern may be copied or translated.
- Limitations / do-not-assume：its Linux/VM/Raspberry Pi topology, supported device matrix, cloud behavior, Matter implementation, security model and licenses do not apply to this ESP32 project.

## eWeLinkCUBE/cc.ewelink.smart.home.addon

- Repository：<https://github.com/eWeLinkCUBE/cc.ewelink.smart.home.addon>
- Pinned revision：`c66a0151e70363131715cbcec69430f442fb009a` (`main`)
- License：NONE/UNKNOWN in GitHub metadata.
- Authority：first-party add-on evidence that LAN discovery and cloud-assisted account syncing are separate product concerns.
- Relevant files/topics：root `README.md`; it describes LAN and cloud discovery, and documents App ID/App Secret setup.
- Reuse boundary：REFERENCE ONLY.
- Limitations / do-not-assume：this does not authorize cloud login, App ID/App Secret, token handling, host networking, Docker or CUBE dependency in this project. Cloud provisioning remains FUTURE / separate authority.

## arendst/Tasmota

- Repository：<https://github.com/arendst/Tasmota>
- Pinned revision：`d3cadb4cd7749816a96c77261d8bd4e3b263a326` (`development`)
- License：GPL-3.0.
- Authority：comparative ESP32/Matter bridge architecture evidence only.
- Relevant files/topics：`tasmota/tasmota_xdrv_driver/xdrv_52_3_berry_matter.ino` and Matter-related build architecture.
- Observations：the tracked tree contains an ESP32 Matter driver, confirming that its Matter-related architecture is a relevant comparison point.
- Reuse boundary：REFERENCE ONLY unless a separate GPL licensing decision explicitly changes this rule. No source, translation, header, build fragment or derived implementation may enter this repository.
- Limitations / do-not-assume：Tasmota architecture, feature set and controller behavior are not requirements for this narrower local-first bridge.

## espressif/arduino-esp32 (comparison only)

- Repository：<https://github.com/espressif/arduino-esp32>
- Pinned revision：`8e54570aba75937c33baa9343f7576b210fe85b0` (`master`)
- License：LGPL-2.1.
- Authority：comparison evidence for the Arduino Matter wrapper, not the selected framework.
- Relevant files/topics：`libraries/Matter/README.md`, Matter endpoint examples.
- Observations：the wrapper exposes common static endpoint classes and callback/attribute-store patterns; its documentation does not present an equivalent official dynamic bridged-device lifecycle API to `esp_matter_bridge`.
- Reuse boundary：REFERENCE ONLY in S1. No Arduino dependency is selected.
- Limitations / do-not-assume：multi-endpoint examples do not establish dynamic bridge maturity, persistent endpoint identity or suitable resource margin for this project.
