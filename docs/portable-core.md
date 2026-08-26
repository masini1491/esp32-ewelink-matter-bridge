# Portable core contract (S2B)

## Scope and structure

```text
core/include/bridge_core/  portable public value types and contracts
core/src/                 portable implementation
tests/                    host-only tests and Windows CNG test provider
```

`bridge_core` uses only C++17 standard-library types. Its public API has no ESP-IDF, FreeRTOS, CHIP/esp-matter, socket, Wi-Fi, mDNS or NVS type. It is built and tested independently of the ESP-IDF authority in `docs/build.md`.

## Generic envelope boundary

`ProtocolEnvelope` expresses only the confirmed generic boundary: sequence, canonical identity, command, `/zeroconf/{command}` path, `selfApikey`, and either a plain or encrypted payload.

- `PlainPayload::data_json` is an opaque, bounded data document. S2B does not parse it as a CK-BL602 schema.
- `EncryptedPayload` contains Base64 ciphertext and IV as distinct values.
- `EWB1` is an internal, deterministic length-prefixed contract codec used for portable round-trip validation. It is **not** the live eWeLink HTTP/JSON wire format and must not be sent to a device.
- The codec rejects missing, malformed, oversized and unsupported records. It does not include a general JSON parser, so no JSON dependency or ad-hoc JSON parser was added.

The known JSON field names establish future adapter vocabulary only. CK-BL602 UIID, `switches` schema, outlet numbering, encryption applicability and response behavior remain `UNKNOWN` / `HARDWARE_TEST_PENDING`.

## Crypto provider boundary

`CryptoProvider` owns MD5 derivation, AES-CBC with PKCS#7 padding and Base64 encoding. Portable code orchestrates these steps but implements no cryptographic primitive.

The host test provider is `WindowsCngCryptoProvider`, backed by the Windows CNG (`bcrypt`) and Crypt32 system APIs. It is test-only and replaceable; no production ESP-IDF crypto provider exists in S2B. No third-party source or package was added, so there is no third-party dependency/license addition in this stage.

Synthetic vector values are deliberately non-secret. The fixed IV exists only in deterministic tests; it is not a runtime IV-generation policy. The tests check a fixed key/ciphertext/Base64 vector and the full-block PKCS#7 boundary.

## Unified Device Model and mapping

- A model has canonical `source_namespace + device_id`, separate availability, and four channels `0..3`.
- `FindChannel()` returns `nullptr` for an out-of-range channel; the portable API does not use C++ exceptions, so it remains valid for ESP-IDF's exception-disabled target build.
- Each channel has observed `on` / `off` / `unknown`, freshness, optional pending intent, transport disposition and convergence outcome.
- Creating or accepting a command does not mutate observed state. Only a valid `on`/`off` observation changes it.
- Disconnect/staleness makes availability unavailable and freshness false without manufacturing an on/off value. Reconnect restores availability only; a new observation is required for freshness.
- `StableBindingKey(identity, channel)` produces four distinct portable `on_off` binding keys. IP address and discovery order are not inputs. Persistence and actual Matter endpoint allocation remain outside S2B.

## Fake transport and host validation

`CommandTransport` is a portable request boundary. `CommandOrchestrator` preserves the original transport failure for its caller while recording rejected model state. The test-only `FakeTransport` records intents and returns configured accept/reject outcomes. It contains no socket, HTTP, Wi-Fi or mDNS behavior.

The normal runner is CMake/CTest with `BRIDGE_BUILD_HOST_TESTS=ON` on a host that has a C++ generator and the Windows CNG provider. S2B local evidence used the MSVC x64 developer environment to compile the exact sources declared in `CMakeLists.txt`, then ran `build/host-direct/bridge_host_tests.exe`.

This establishes Host PASS only. S2C may compile the core as an inward dependency of a target-only adapter, but must not change this portable contract or make its public API platform-dependent.
