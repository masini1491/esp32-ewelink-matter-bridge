# B1 upstream revisit — 2026-09-20

Status: `COMPLETE_STAGING`

Purpose: sanitized public-upstream evidence for B1 (device-specific LAN contract evidence). This staging record has no execution authority and is not canonical validation/architecture truth. Formal conclusions still require reconciliation into project canonical owners.

## Source identities

- CoolKit official API repository: `CoolKit-Technologies/eWeLink-API`, `main` at `6ffbfd3d8e55122921ff5e4ccf3c3916c5593c00`; file `en/UIIDProtocol.md`.
- iHost / eWeLink Smart Home Home Assistant add-on repository: `iHost-Open-Source-Project/hassio-ihost-addon`, `master` at `5a8d7dec067f9196ada5879f31f71cbf6d595bff`; file `hassio-ihost-ewelink-smart-home/DOCS.md`.
- SonoffLAN: `AlexxIT/SonoffLAN`, `master` at `5721d2f24c6800617b280c015c9b0af987a99469`; files `DEVICES.md`, `custom_components/sonoff/core/ewelink/local.py`, `custom_components/sonoff/switch.py`.
- Public SonoffLAN issue evidence: issue #1494, exact model `CK-BL602-4SW-HS(138)`; used only for sanitized schema/variant observations, not as official protocol authority.
- Official eWeLink product/support pages reviewed on 2026-09-20:
  - https://ewelink.cc/ewelink-cube/supported-device/wifi/
  - https://ewelink.cc/ewelink-cube/add-on/ewelink-smart-home/
  - https://ewelink.cc/whats-new-in-ewelink-app-v5-22-2/
  - https://ewelink.cc/introducing-the-ewelink-pioneer-app/
  - https://help.ewelink.cc/hc/en-us/articles/34154618272921-What-s-New-in-eWeLink-App-V5-7

## Confirmed upstream observations

1. CoolKit's current UIID table defines the eWeLink-Remote plug family by channel count:
   - UIID 138 = single-channel plug;
   - UIID 139 = dual-channel plug;
   - UIID 140 = three-channel plug;
   - UIID 141 = four-channel plug.

2. Current SonoffLAN device evidence lists the same CK-BL602 family in multiple UIID/channel variants:
   - `CK-BL602-4SW-HS-03(138)-1` → UIID 138 / 1ch / local type `plug`;
   - `CK-BL602-4SW-HS(138)` → UIID 138 / 1ch / local type `plug`;
   - `CK-BL602-4SW-HS(141)` → UIID 141 / 4ch; SonoffLAN's table does not currently claim a verified local type for this row.

3. Current iHost/eWeLink Smart Home add-on documentation lists:
   - `CK-BL602-4SW-HS(138)` among Wi-Fi devices supported through `LAN&Cloud`;
   - the `CK-BL602-4SW-HS` / `CK-BL602-4SW-HS-03` family under multi-channel plugs with `LAN&Cloud` and channel control.

4. Official eWeLink app/support material also places `CK-BL602-4SW-HS` in dual-, three-, and four-channel eWeLink-Remote plug categories, and places `CK-BL602-4SW-HS-03(141)` in a four-channel category. Therefore the model-family string alone is not sufficient evidence for an exact active-channel count/UIID.

5. Sanitized SonoffLAN issue #1494 evidence for exact `CK-BL602-4SW-HS(138)` shows a cloud/device parameter payload containing a `switches` array with outlet values 0..3. The same snapshot had no active SonoffLAN local host/localtype observation for that device. Presence of four array entries therefore does not by itself prove four locally controllable channels.

6. SonoffLAN's current generic local implementation still browses `_ewelink._tcp.local.`, uses default port 8081 when no port is supplied, sends `/zeroconf/{command}`, and when the discovery payload advertises encryption derives an MD5 key from `devicekey` and applies AES-CBC / PKCS#7 / Base64 handling. This is generic upstream protocol evidence only; it does not prove that the target CK-BL602 variant advertises or requires encryption.

## Reconciliation impact

- Material trigger for B1 is satisfied: upstream evidence is newer/more specific than the project's 2026-08-26 provenance baseline.
- The project must no longer infer “four active channels” from the `CK-BL602-4SW-HS` / `-03` family string alone. Exact device UIID/capability evidence is required before implementation binds four Matter endpoints.
- Upstream evidence materially strengthens LAN-capability confidence for the family, including current `LAN&Cloud` documentation, but does not establish project `Network PASS` or `CONFIRMED_LOCAL`.
- Exact target-device encryption applicability, local discovery response, command/response semantics, state freshness/convergence, and actual active channel count remain unresolved pending device-specific evidence.

## Next lowest-cost discriminator

Obtain a sanitized observation from the actual target device/app that establishes, without exposing secrets/private identifiers:
- exact product/model variant shown by the app;
- UIID / hardware-firmware classification if shown;
- firmware version;
- whether the eWeLink app exposes and enables `LAN Control`;
- visible channel count.

Do not include device ID, deviceKey, Wi-Fi SSID/BSSID, MAC, private IP, tokens, account identifiers, or Matter credentials.

Reconciliation target: `docs/references/README.md` / source dossier, `docs/architecture.md`, `docs/portable-core.md`, and `VALIDATION.md` only after the remaining device-specific discriminator is evaluated.
