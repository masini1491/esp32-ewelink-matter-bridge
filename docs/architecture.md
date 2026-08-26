# Architecture and contract freeze (S1)

## Decision record

### Platform → target → concrete board

| Level | S1 decision | Rationale / boundary |
| --- | --- | --- |
| Platform class | ESP32 Wi-Fi Matter Bridge | Local Wi-Fi bridge with BLE commissioning; no Thread requirement in v1. |
| Framework | ESP-IDF `v5.5.5` + esp-matter component `1.6.0` | Released official pair; esp-matter exposes bridge lifecycle APIs and bridge examples, unlike the higher-level Arduino Matter wrapper. See `docs/build.md`. |
| Primary constrained target family | ESP32-C3 | Matter over Wi-Fi, constrained by the C3's single core and 4 MB-class flash direction. S2C owns feasibility evidence; C3 has no Thread requirement in v1. |
| Constrained module/build profile | ESP32-C3-MINI-1-N4X | Official generic module with 4 MB Quad-SPI flash and no PSRAM. It is a reproducible compile/resource baseline, not a claim about a purchased SuperMini board. |
| Development/high-margin fallback | ESP32-S3-WROOM-1-N16R8 | 16 MB Quad-SPI flash + 8 MB Octal-SPI PSRAM, retained from S2A for debug, growth experiments and a bounded fallback comparison only if C3 is proven not viable. |
| Optional radio-capability target | ESP32-C6 | Its material difference is IEEE 802.15.4 / future Matter-over-Thread capability, not an automatic middle tier between C3 and S3. Thread/Wi-Fi coexistence needs a separate Stage. |

The selected dependency pair is released ESP-IDF `v5.5.5` plus esp-matter component `1.6.0`, not floating upstream `main`. Exact revisions, bootstrap and the S2C compile-only gate are in `docs/build.md`.

Resource profile and radio capability are independent policies. `CONSTRAINED / LIGHTWEIGHT` is C3/4 MB-class; `DEVELOPMENT / HIGH-MARGIN` is S3 N16R8; `OPTIONAL THREAD CAPABILITY` is C6. A profile may change build limits and optional capability, but never protocol correctness, crypto/secret handling, command convergence, four-channel isolation or Matter mapping correctness. More resource must not justify unbounded buffers, queues, logs, dependencies, tasks or features.

Official comparison evidence: ESP32-C3 provides Wi-Fi/BLE on a single core with 400 KB SRAM; ESP32-C6 adds Wi-Fi 6/BLE/802.15.4 on a single core with 512 KB HP SRAM; ESP32-S3 provides Wi-Fi/BLE, dual cores, 512 KB internal SRAM and modules with PSRAM support. These capabilities are selection evidence, not a compile or hardware pass.

## Dependency and ownership contract

```text
eWeLink Transport
        ↓
eWeLink Protocol / Registry
        ↓
Unified Device Model
        ↓
Matter Adapter / Bridge
        ↓
Matter over Wi-Fi
```

| Layer | Owns | Must not own / depend on |
| --- | --- | --- |
| eWeLink Transport | Future bounded LAN request/response mechanics behind a portable interface | Matter types, fabrics, commissioning, device capability policy |
| eWeLink Protocol / Registry | Future protocol serialization, discovery observations, registry metadata and protocol-to-model translation | Matter endpoint APIs, fabric material, controller lifecycle |
| Unified Device Model | Portable device identity, capabilities, channel state, availability, command intent and observed convergence | ESP-IDF, FreeRTOS, esp-matter, CHIP types, raw HTTP/AES/mDNS details |
| Matter Adapter / Bridge | Mapping portable model capabilities/states to Matter bridge and endpoint lifecycle; stable endpoint identity binding | Parsing raw eWeLink payloads or owning eWeLink secrets |
| Matter over Wi-Fi | Espressif/CHIP SDK integration, commissioning, fabric, persistence and network protocol lifecycle | eWeLink protocol interpretation |

Dependency direction is inward: platform/runtime adapters depend on the portable core; the portable core must not expose or depend on ESP-IDF, FreeRTOS or Matter implementation types. This is library-ready only: no package, separate repository or speculative generalization is created.

S2B implements this portable boundary in `core/`; its exact codec, crypto-provider, model and host-test contracts are in `docs/portable-core.md`.

## First consumer capability contract

Scope is only `CK-BL602-4SW-HS` and `CK-BL602-4SW-HS-03` as a 4-channel binary switch. Other device families and UIIDs are out of scope.

| Contract item | Frozen rule | Evidence status |
| --- | --- | --- |
| Canonical identity | Stable internal identity is `source namespace + deviceId`; deviceKey is never identity or a loggable value. | INFERRED |
| Product/UIID | Model names are first-consumer candidates. Exact UIID/capability response must be captured from upstream evidence or permitted hardware evidence before implementation. | UNKNOWN / HARDWARE_TEST_PENDING |
| Channels | Four logical channels, indexed `0..3` in the portable model. Any wire-field naming/index convention needs source confirmation and an adapter mapping. | INFERRED |
| State | Each channel is `on`, `off`, or `unknown`; device availability is separately `available` or `unavailable`. Unknown is not off. | Frozen project contract |
| Command intent | A command records requested channel state and a correlation/sequence when the protocol provides one. Transport acceptance is not observed state. | Frozen project contract |
| Convergence | Only a later valid device observation may set observed state. Until then the channel remains pending/last-known with explicit freshness, never claimed as confirmed. | Frozen project contract |
| Reconnect/staleness | A transport disconnect or expired freshness makes availability `unavailable`; it does not manufacture state changes. Reconnect requires a new observation before state is fresh. | Frozen project contract |
| Matter mapping | One bridge node with four bridged Matter On/Off endpoints, one per logical channel. Endpoint identity is stable across ordinary reconnect/restart by persisted binding to canonical device identity + channel index; it must not be derived from discovery order or transient address. | Frozen project contract; persistence behavior HARDWARE_TEST_PENDING |

The exact device LAN behavior, UIID, `switches` payload shape, encryption use and endpoint controller presentation remain `CONFIRMED_UPSTREAM` only where SonoffLAN evidence applies; they are not `CONFIRMED_LOCAL`.

## Security and secret ownership

| Material | Owner / rule |
| --- | --- |
| `deviceId` | Non-secret device identity; may be stored only when a later product persistence contract permits it. Logs should minimize it. |
| `deviceKey` | Secret owned by the eWeLink protocol/credential boundary. Future runtime storage must be secure, write-only and never expose it to logs, README, examples, fixtures or Matter layers. |
| Wi-Fi credentials | Matter/network provisioning boundary; never a core model or eWeLink protocol value, never committed or logged. |
| Matter commissioning/fabric material | esp-matter/ESP-IDF Matter persistence boundary. It is never owned, parsed or exported by eWeLink layers. |
| Cloud account/App ID/token | FUTURE / separate authority only. It is not required for v1 local runtime and is not authorized in S1/S2 absent an explicit Stage. |

S1 obtained no real secrets and defines no secret fixture format.
