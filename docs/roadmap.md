# Roadmap

## Completed scope

S1 froze the research provenance, ESP-IDF + esp-matter / ESP32-S3-family direction, portable layering, first 4-channel switch contract, secret ownership and validation taxonomy. S2A then pinned ESP-IDF `v5.5.5` + esp-matter `1.6.0` and the ESP32-S3-WROOM-1-N16R8 build profile. Completion means documents and contracts are reviewable; it does not mean device, network, Matter or controller interoperability is validated.

## S2 — Software-first foundation (not started)

S2 may begin only with explicit authorization. Its bounded goals are:

1. Implement only portable contract-driven types/interfaces: protocol constants, serializer/parser boundaries, deterministic crypto vectors, fake transport/device, unified model and Matter mapping contract tests.
2. Add only the minimum host test and CI evidence needed for those contracts; S2C may later create the compile-only adapter using the pinned build authority.

S2 does not authorize live mDNS, LAN control, real secrets, production credential persistence, hardware relay control, commissioning or Matter interoperability testing.

## Deferred evidence gates

- Device-specific UIID, channel wire schema, encryption applicability and state behavior: upstream revisit plus explicitly authorized hardware/network evidence.
- Board/module, flash/PSRAM and partition selection: required before target-specific adapter work.
- Network, hardware and Matter-controller interoperability: separate authorized validation stages after software-first evidence.
