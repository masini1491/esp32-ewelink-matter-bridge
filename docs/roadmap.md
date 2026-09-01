# Roadmap

## Completed scope

S1 froze the research provenance, ESP-IDF + esp-matter direction, portable layering, first 4-channel switch contract, secret ownership and validation taxonomy. S2A pinned ESP-IDF `v5.5.5` + esp-matter `1.6.0` and the ESP32-S3-WROOM-1-N16R8 profile. S2C repositions that S3 profile as development/high-margin fallback while C3/4 MB-class becomes the primary constrained Wi-Fi compile gate; C6 remains optional Thread capability. None of this is device, `Network PASS`, Matter-controller or hardware validation.

## S2 — Software-first foundation (complete)

S2 software-first scope is complete. Its evidence is limited to portable host validation and the authorized C3 compile/resource gate:

S2B portable foundation and S2C minimum CI plus compile-only C3 ESP-IDF/esp-matter integration/resource gate are complete. The C3 result is `VIABLE_CONSTRAINED`; S3 was not compiled as fallback and C6 remains optional Thread capability.

S2 does not authorize live mDNS, LAN control, real secrets, production credential persistence, hardware relay control, commissioning or Matter interoperability testing.

## Deferred evidence gates

- D2/D3 bounded mDNS evidence gates are complete as negative observations: no service response was observed. They do not establish `Network PASS`, CK-specific `CONFIRMED_LOCAL`, LAN feature absence or hardware failure.
- Device-specific UIID, channel wire schema, encryption applicability and state behavior: upstream revisit plus explicitly authorized hardware/network evidence.
- Physical carrier/product board and pinout: still required before hardware work. C3 constrained compile/resource evidence is S2C's primary gate; S3 N16R8 is retained only as development/fallback authority.
- Network, hardware and Matter-controller interoperability: not run. Any further live/network evidence requires separate explicit authorization.
