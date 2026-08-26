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

Before any hardware stage, S2 should validate protocol constants, serializer/parser boundaries, deterministic crypto vectors, fake transport/device behavior, unified-model state transitions, Matter mapping contract and host tests. A target compile-only adapter is optional only after the ESP-IDF/esp-matter release pair and concrete ESP32-S3 module gate are recorded.

No validation level may be promoted across the table by inference.

## S2A build-authority evidence

- Static/Test PASS: released version/revision resolution, official compatibility/partition evidence, target/module/flash/PSRAM consistency, no-floating-branch audit, secret scan and scope review.
- Local toolchain / dependency resolver smoke: not run. No SDK was downloaded or installed.
- Compile / Network / Hardware / Matter interoperability: not run. S2C's required compile-gate evidence is frozen in `docs/build.md`.
