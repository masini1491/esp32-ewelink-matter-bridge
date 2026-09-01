# Validation contract

## Evidence levels

| Level | Meaning | Does not establish |
| --- | --- | --- |
| Static/Test PASS | Formatting, document consistency, deterministic unit/vector or contract test passed. | Build, network, hardware or interoperability. |
| Host PASS | Portable code ran successfully against fake/mock inputs on a host. | ESP32 compile, live protocol or hardware. |
| Compile PASS | Intended target adapter participated in a successful target build. | Runtime, resource sufficiency, network or hardware. |
| Network PASS | Explicitly authorized live LAN observation/exchange succeeded. | Relay behavior, persistence or Matter controller interoperability. |
| Hardware PASS | Explicitly authorized evidence on the target ESP32 and CK-BL602 setup passed. | Matter ecosystem interoperability unless tested. |
| Matter interoperability PASS | Explicitly authorized commissioning/control evidence with a named controller and defined scenario passed. | General certification or all controllers. |

## S1 evidence

- Static/Test PASS: repository identity/sync, provenance dossier, architecture/authority consistency, secret scan and `git diff --check`.
- Host / Compile / Network / Hardware / Matter interoperability: not run in S1.
- Device claims are classified as `CONFIRMED_UPSTREAM`, `INFERRED`, `UNKNOWN` or `HARDWARE_TEST_PENDING`; no S1 claim is `CONFIRMED_LOCAL`.

## S2 software-first minimum

Before any hardware stage, S2 should validate protocol constants, serializer/parser boundaries, deterministic crypto vectors, fake transport/device behavior, unified-model state transitions, Matter mapping contract and host tests. S2C adds a C3 constrained target compile gate after the ESP-IDF/esp-matter release pair and reproducible C3 module/flash authority are recorded.

No validation level may be promoted across the table by inference.

## S2A build-authority evidence

- Static/Test PASS: released version/revision resolution, official compatibility/partition evidence, target/module/flash/PSRAM consistency, no-floating-branch audit, secret scan and scope review.
- Local toolchain / dependency resolver smoke: not run. No SDK was downloaded or installed.
- Compile / Network / Hardware / Matter interoperability: not run. S2C's required compile-gate evidence is frozen in `docs/build.md`.

## S2B portable-core evidence

- Static/Test PASS: deterministic envelope codec checks, malformed/missing/oversized/unsupported boundaries, synthetic CNG-backed MD5/AES-CBC/PKCS#7/Base64 vector, model transitions, four-channel isolation, stable binding keys, FakeTransport behavior, dependency-direction and secret/license audits.
- Host PASS: the MSVC x64 developer environment compiled `core/src/binding.cpp`, `core/src/device_model.cpp`, `core/src/envelope.cpp`, `tests/windows_cng_crypto_provider.cpp` and `tests/host_tests.cpp`; `bridge_host_tests.exe` passed all eight test groups.
- Toolchain note: CMake/Ninja was unavailable and the local Visual Studio CMake generator could not complete its ABI probe because no usable build program was configured. This did not prevent direct MSVC compilation of the same source list; it is a local `TOOLCHAIN` limitation, not a source failure.
- Network / Hardware / Matter interoperability: not run. No runtime participated.

Evidence lifecycle: the Windows/MSVC + CNG result above is `HISTORICAL`; the current Linux GitHub Actions host result is `CURRENT` and is recorded by run `33032450495`.

## S2C closure evidence

Verified run `33032450495` passed Host CI, pinned dependency installation, C3 build, evidence capture and artifact upload. Artifact `esp32c3-compile-evidence` is 727,923 bytes with SHA-256 `08e9bfe269877611e1950f4a01e5eec5819351faf7ecd1d99998bff83ccf9ab7`.

The S2C Host CI result is `CURRENT`; the compile/resource artifact remains current because M1 changes only governance text and a fail-fast metadata guard, not the target, source, dependency, partition or adapter contract.

It records ESP-IDF `5.5.5`, `esp32c3`, `espressif/esp_matter` `1.6.0`, the 4 MB custom partition table at offset `0xC000`, dual OTA app roles, generated binary and resolved CSV partition evidence. Firmware is `0x136DF0` with `0x99210` (33%) free in the smallest app slot; static DRAM is 50.15% used and bootloader free space is 57%.

The probe compiled/linked portable-core sources and referenced `esp_matter_bridge`. Classification: `VIABLE_CONSTRAINED` (software-first compile/resource evidence only). Network, Hardware and Matter interoperability remain `NOT RUN`; CK-BL602 remains `UNKNOWN` / `HARDWARE_TEST_PENDING`.

## D2 bounded mDNS observation evidence

At project HEAD `850674c8a90419f798527f81dfb0542dbfd3f905`, an explicitly authorized, passive-only `_ewelink._tcp.local.` mDNS observation ran for 30 seconds through the D2A bounded-result handoff runner. The separate short-command handoff and runtime cleanup passed; no standard mDNS query, HTTP request, deviceKey, decryption or device control occurred.

Result: `NO SERVICE OBSERVED`. This records only the bounded observation outcome; it does not establish that the CK-BL602 lacks LAN/mDNS support, and it does not establish `Network PASS`. No CK-specific fact reached `CONFIRMED_LOCAL`; UIID, encryption applicability, channel/wire schema, HTTP semantics and convergence remain `UNKNOWN` / `HARDWARE_TEST_PENDING`. Hardware and Matter interoperability remain `NOT RUN`.

## D3A Windows DNS-SD adapter evidence

Static/Test PASS: Windows `dnsapi.dll` exported `DnsServiceBrowse`, `DnsServiceBrowseCancel`, `DnsServiceResolve`, and `DnsServiceResolveCancel` on the Windows 10+ 64-bit host. Deterministic synthetic tests validate ctypes declarations, fixed `_ewelink._tcp.local.` scope, an overall deadline split between browse/cancel and a positive resolve/cancel budget, fail-closed full-budget behavior, single-resolve handling of multiple discovery names, TXT property-count fail-closed behavior, D1-compatible capture conversion, and raw host/address omission from the machine-result schema.

Host/local synthetic PASS: every native resolve operation retains callback/request/cancel/event/result ownership for the observer child process lifetime. Synthetic late/multiple callbacks after first acceptance, and late callback after timeout/cancel, remained valid and could not overwrite the accepted first result. Every terminal path serializes and flushes its complete machine payload before using Python's hard process-exit path, avoiding normal interpreter teardown of ctypes state before OS child exit. Synthetic success and timeout-after-registry subprocess/D2A handoff checks confirmed parseable stdout, completed runner metadata, exit `0` or `2` as applicable, and no normal-finalization marker. The adapter uses no shell, socket, packet parser, background monitor, or third-party dependency. Native API calls were deliberately not invoked. Network, Hardware, and Matter interoperability remain `NOT RUN`; no CK-specific fact is `CONFIRMED_LOCAL`.

## D3B Windows observer research decision

Static/Test PASS: public Microsoft API/SDK research compared the existing DNS-SD API, `DnsQueryEx`, `DnsStartMulticastQuery`, `DnsQueryRaw`, and `Resolve-DnsName`. No live operation occurred. `DnsQueryEx` has a documented completion callback lifetime but its multicast-only option is LLMNR, not mDNS. `DnsStartMulticastQuery` is mDNS but runs indefinitely and its published stop contract does not establish callback quiescence. The existing DNS-SD resolve route retains the same unresolved terminal-success lifetime gap.

Historical classification: D3B found no alternate route with a documented terminal/quiescence contract. Subsequent D3A process-lifetime ownership revalidation is `CURRENT`: it prevents ctypes lifetime from depending on undocumented resolve terminality by retaining each resolve operation until direct-child process exit. Network, Hardware, and Matter interoperability remain `NOT RUN`.
