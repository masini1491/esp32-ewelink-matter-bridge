# Build authority (S2A)

This document is the sole build/version authority for the project. It pins released artifacts; branch names and upstream `main`/`master` are research routing only.

## Released dependency pair

| Dependency | Pinned release | Exact revision | Official compatibility evidence |
| --- | --- | --- | --- |
| ESP-IDF | `v5.5.5` | `b774170ff46c393eeb5e495ea37936038d3f4f4f` | The esp-matter 1.6.0 source README recommends ESP-IDF `v5.5.5` for Matter development. |
| esp-matter | Component Registry `espressif/esp_matter` `1.6.0` | `81e4abe329deaef3e316b32e6768858c8f41e000` | The component manifest declares version `1.6.0`; the same source README identifies `release/v1.6` as Matter 1.6 support and recommends the pinned ESP-IDF release. |
| ConnectedHomeIP | transitive through esp-matter 1.6.0 | `93abd8e68` (upstream short revision stated by Espressif) | esp-matter's README identifies this as its compatible CHIP revision. Do not clone or add it as a separate project dependency. |

The Component Registry entry is a released immutable version. Future S2C project metadata must use `espressif/esp_matter: "==1.6.0"`, not `^1.6.0`, a Git branch, URL or floating commit.

## Target profiles

| Profile | Target / module authority | Resource/radio meaning | Status |
| --- | --- | --- | --- |
| Constrained / lightweight | `esp32c3` + ESP32-C3-MINI-1-N4X | 4 MB Quad-SPI flash, no PSRAM; Matter over Wi-Fi baseline. This is the reproducible module profile behind a SuperMini-class direction, not an assertion about a physical board. | S2C compile/resource gate |
| Development / high-margin | `esp32s3` + ESP32-S3-WROOM-1-N16R8 | 16 MB Quad-SPI flash + 8 MB Octal-SPI PSRAM. | S2A build authority; fallback only after confirmed C3 non-viability |
| Optional Thread capability | ESP32-C6 | Future IEEE 802.15.4 / Matter-over-Thread path. | Not compiled in S2C |

The profiles cannot change portable protocol, cryptographic semantics, secret ownership, state convergence, four-channel isolation or Matter mapping semantics. C6 is not a resource-derived standard target; S3 is not permission to increase footprint without a bounded reason.

## Reproducible ESP32-S3 profile (development/fallback)

| Layer | S2A selection | Status |
| --- | --- | --- |
| Target family | `esp32s3` | Build authority |
| Module/build profile | `ESP32-S3-WROOM-1-N16R8` | Build authority; not hardware validation |
| Flash | 16 MB Quad SPI | Build authority |
| PSRAM | 8 MB Octal SPI | Build authority |
| Development carrier | Optional official `ESP32-S3-DevKitC-1` carrying the same N16R8 module, or an equivalent carrier | Not selected/purchased/validated by S2A |
| Product PCB / pinout / power circuit | Not selected | Outside S2A |

The selected module is a generic Espressif module profile, rather than a small third-party board assumption. Its flash/PSRAM capacity is a resource allowance for Wi-Fi Matter, BLE commissioning, local bridge state and future four-endpoint growth; it is not an observed runtime memory budget.

## C3 constrained partition contract

`platform/esp32c3_probe/partitions.csv` is the S2C 4 MB compile baseline. It retains the official bridge example's roles that matter to this project: `esp_secure_cert`, `nvs`, encrypted `nvs_keys`, `otadata`, `phy_init`, two OTA app slots and `fctry`. It deliberately removes only Zigbee-specific storage from the official bridge CLI table; Zigbee is not in this project's v1 scope.

Each app slot is `0x1D0000` (1,900,544 bytes). The table ends at `0x3D6000`, leaving `0x2A000` (172,032 bytes) of the 4 MB address space unallocated. This is a partition-layout allowance, not an application-size or runtime-memory pass. The S2C build record must determine whether the actual image fits with meaningful margin.

## S3 partition contract

- A custom partition table is required for the future S3 fallback build; it must set 16 MB flash explicitly and make the partition table explicit.
- The official esp-matter 1.6.0 `examples/bridge_apps/bridge_cli/partitions.csv` is the baseline authority: it demonstrates secure-cert, NVS/NVS-key, OTA data, PHY and dual OTA application partitions with a custom table.
- S2A deliberately does not copy or invent a project `partitions.csv`. That example is sized for its own 4 MB/bridge configuration and includes Zigbee-specific storage that is not this project's requirement.
- S2C may create a project table only after its compile harness has a real app size/configuration. It must retain the required Matter/persistence/OTA roles, document every deviation from the official baseline, and pass ESP-IDF partition validation. No oversized or product-final layout is frozen now.

## Bootstrap contract

1. Install ESP-IDF exactly at `v5.5.5` using Espressif's official installer or a clone checked out to the exact tag, then use the SDK's own install/export flow.
2. Use the ESP-IDF Component Manager to resolve the exact `espressif/esp_matter ==1.6.0` component in the future S2C project. It retrieves the released component and its declared transitive dependencies; this repository does not vendor esp-matter or ConnectedHomeIP.
3. Commit the generated dependency lock only when a future build project exists and its resolver has produced it. The lock must resolve to the version above and must not replace it with a branch/URL dependency.
4. On Windows, use the officially supported Matter host environment (WSL2/Linux as applicable to the selected Espressif release). If a repository-owned Windows helper is later necessary, its formal runtime is PowerShell 7 `pwsh`; S2A creates no script.

No SDK download, toolchain installation or target build was performed in S2A. This is a deterministic bootstrap authority, not a local toolchain PASS.

## S2C compile-only gate

S2C must produce `Compile PASS` only if all conditions below are evidenced by the selected build:

1. `idf.py set-target esp32c3` and generated configuration identify `esp32c3`, 4 MB flash and the C3-MINI-1-N4X no-PSRAM compile profile; no generic/default target may substitute.
2. The portable-core component is registered as a build target and appears in compile commands/link inputs; conditional configuration must not silently omit it.
3. A minimal compile probe includes and references the pinned `esp_matter_bridge` API so compilation and linking prove the selected esp-matter bridge component participated. It may use only synthetic descriptors and no runtime commissioning/network activity.
4. The configured custom partition table is parsed by ESP-IDF and build output reports its flash/static-resource baseline. This is a compile-time baseline, not runtime/heap/headroom evidence.

The S2C record must include command, dependency-lock evidence, target/config evidence, relevant compile/link evidence and artifact/resource baseline. It must not claim Network, Hardware or Matter interoperability PASS.

## S2A evidence links

- [esp-matter 1.6.0 source README](https://github.com/espressif/esp-matter/blob/81e4abe329deaef3e316b32e6768858c8f41e000/README.md)
- [esp-matter 1.6.0 component manifest](https://github.com/espressif/esp-matter/blob/81e4abe329deaef3e316b32e6768858c8f41e000/idf_component.yml)
- [official bridge CLI partition baseline](https://github.com/espressif/esp-matter/blob/81e4abe329deaef3e316b32e6768858c8f41e000/examples/bridge_apps/bridge_cli/partitions.csv)
- [ESP32-S3-WROOM-1 datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
