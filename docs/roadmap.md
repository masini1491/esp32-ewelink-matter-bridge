# Roadmap

## Completed scope

S1 froze the research provenance, ESP-IDF + esp-matter / ESP32-S3-family direction, portable layering, first 4-channel switch contract, secret ownership and validation taxonomy. S2A then pinned ESP-IDF `v5.5.5` + esp-matter `1.6.0` and the ESP32-S3-WROOM-1-N16R8 build profile. Completion means documents and contracts are reviewable; it does not mean device, network, Matter or controller interoperability is validated.

## S2 — Software-first foundation (in progress)

S2 may begin only with explicit authorization. Its bounded goals are:

S2B portable foundation is complete with host evidence. The remaining authorized queue is S2C, which may add minimum CI and compile-only ESP-IDF/esp-matter integration only after a new explicit launch.

S2 does not authorize live mDNS, LAN control, real secrets, production credential persistence, hardware relay control, commissioning or Matter interoperability testing.

## Deferred evidence gates

- Device-specific UIID, channel wire schema, encryption applicability and state behavior: upstream revisit plus explicitly authorized hardware/network evidence.
- Physical carrier/product board, pinout and target-specific compile/resource evidence: required before target-specific adapter work. The reproducible ESP32-S3-WROOM-1-N16R8 module/flash/PSRAM build profile is already fixed by S2A; S2C owns its compile/partition baseline.
- Network, hardware and Matter-controller interoperability: separate authorized validation stages after software-first evidence.
