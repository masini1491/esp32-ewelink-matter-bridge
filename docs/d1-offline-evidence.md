# D1 Offline eWeLink Discovery Evidence

This document defines a bounded, offline input and sanitized output contract. D1 does not open sockets, browse mDNS, send HTTP, read credentials, decrypt payloads, or operate a device.

## Input

The JSON capture contains `synthetic`, `service.name`, `service.type`, optional `service.port`, and a `service.txt` object. D1 recognizes the upstream vocabulary `_ewelink._tcp.local.`, case-insensitive names beginning with `ewelink`, and optional TXT keys `id`, `type`, `seq`, `encrypt`, `iv`, `data1` through `data4`. Fixtures are `SYNTHETIC / NON-SECRET` and are not CK-BL602 captures.

## Sanitized output

The analyzer emits service class, port presence, sorted TXT key names, sequence shape, fragment indices/count/length, a deterministic non-secret device alias, and plaintext JSON keys/types. Missing or ambiguous fields remain `UNKNOWN`; partial or malformed input fails closed. Encrypted input is shape-only: no deviceKey is accepted, no decryption occurs, and raw IV, ciphertext or payload is not emitted. Full local IP/host, complete deviceId, Wi-Fi credential, token and Matter secret are never output.

Processing is deterministic and bounded to 64 KiB input and 4 KiB per fragment. `data1..data4` are joined only in numeric order for a complete plaintext JSON structural check. This does not establish CK-BL602 UIID, channel numbering, encryption applicability or convergence behavior.

## D2 boundary

D2 requires separate user authorization. Its first contact may be a short, passive/read-only observation of `_ewelink._tcp.local.` only. Raw capture must not be committed; it must first pass this sanitizer and offline review. D2 must not automatically escalate to `/zeroconf/*`, `getState`, deviceKey, decryption, relay/channel control, retries or background monitoring. If no service is observed, or only encrypted metadata is seen, preserve the bounded sanitized result and stop.
