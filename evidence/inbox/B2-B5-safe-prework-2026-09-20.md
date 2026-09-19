# B2–B5 safe prework — 2026-09-20

Status: `PREWORK_COMPLETE / NOT_RUN`

Purpose: bounded research / readiness preparation that can be completed without live LAN activity, hardware control, commissioning, production firmware, credentials, or source/tooling mutation. This record has no execution authority and is not a validation PASS. Canonical project evidence levels remain owned by `VALIDATION.md`.

## B2 — Physical target / carrier / pinout closure

### Current canonical project premise

The software-first constrained target is `ESP32-C3-MINI-1-N4X`, 4 MB flash, no PSRAM. The repository explicitly treats this as a reproducible module/build profile rather than proof of a specific physical carrier board.

### Official hardware reference reviewed

Espressif `ESP32-C3-DevKitM-1` is an official development board based on `ESP32-C3-MINI-1` / `MINI-1U` with 4 MB flash and breaks out the available GPIOs. It is therefore a suitable **reference carrier** for the project's selected module class, but it is not automatically the project's physical board.

Official sources:
- https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c3/esp32-c3-devkitm-1/user_guide.html
- https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html

Relevant official pin constraints:
- GPIO2, GPIO8, GPIO9 are boot strapping pins.
- GPIO18 / GPIO19 are USB D- / D+.
- GPIO20 / GPIO21 are UART0 RX / TX.
- EN must not be left floating.
- Module antenna keepout/layout requirements apply to a product carrier.

### Closure boundary

B2 cannot be closed from the module name alone. Before project pinout authority is promoted, the actual physical carrier/product board must be identified by an exact board model plus a reliable schematic/pinout (or equivalent board evidence).

For any third-party “SuperMini”/clone carrier, do not inherit `ESP32-C3-DevKitM-1` header numbering, regulator behavior, LEDs, buttons, USB wiring, or pin availability by inference.

Safe prework result: official reference carrier and pin-risk checklist are established; actual carrier identity is still required.

## B3 — Network PASS readiness

Official eWeLink CUBE documentation states that the presence of the **LAN Control** option in the eWeLink app indicates LAN-control support and instructs users to enable it:
- https://ewelink.cc/ewelink-cube/supported-device/wifi/
- https://ewelink.cc/ewelink-cube/add-on/ewelink-smart-home/

Combined with the B1 upstream revisit, the current lowest-cost decision tree is:

1. **LAN Control option absent** → record a variant/firmware capability discrepancy; do not infer LAN support for the actual target and do not proceed to active protocol work.
2. **LAN Control present but disabled** → enabling it is a device configuration mutation and requires explicit user choice before a new live observation.
3. **LAN Control present and enabled** → a separately authorized, bounded live LAN observation can be planned. Existing D2/D3 negative observations remain historical bounded negatives and are not Network PASS.
4. **Future service response observed** → sanitize/reconcile the minimum protocol evidence first; do not automatically escalate to HTTP/control.
5. **No service observed again** → keep the result negative/unknown and investigate timing/interface/multicast conditions before any stronger conclusion.

No network operation was executed in this prework.

## B4 — Hardware PASS readiness

Hardware evidence remains `NOT RUN`. A future hardware stage should not start until B1 establishes the actual CK-BL602 variant/channel capability and B2 establishes the ESP32 carrier/pinout.

Minimum future hardware evidence matrix, derived from the project contracts:

- target/carrier identity and power/boot condition;
- no unintended control action during boot/reset;
- exact logical-channel ↔ device-channel mapping;
- channel isolation: each intended channel can be acted on without changing the other channels;
- command intent versus observed state kept separate;
- transport acceptance does not count as observed state;
- valid observation establishes state/freshness;
- disconnect/staleness marks availability/freshness correctly without manufacturing on/off state;
- reconnect requires fresh observation;
- restart/power-cycle checks are recorded separately from Matter-controller interoperability.

This is a **PLAN_ONLY / NOT RUN** matrix. It authorizes no mains work, device opening, energized probing, relay actuation, or hardware modification.

## B5 — Matter interoperability readiness

Home Assistant's current official Matter documentation supports commissioning Matter devices and adding **Matter bridges** to Home Assistant. For Home Assistant OS, the official Matter Server app is the supported/recommended path.

Official source:
- https://www.home-assistant.io/integrations/matter

The current project target is Matter over Wi-Fi on ESP32-C3, so Thread is not a prerequisite for the baseline interoperability scenario.

A bounded candidate interoperability scenario is prepared, but the controller is not yet promoted to project authority:

- named controller candidate: Home Assistant Matter integration / Matter Server;
- commission the bridge as a Matter device;
- confirm four bridged On/Off endpoints only if B1 has first established four active target channels;
- exercise each endpoint independently;
- verify observed state updates rather than treating command acceptance as convergence;
- verify endpoint identity is stable across ordinary bridge reconnect/restart;
- record controller/software version and scenario boundaries;
- do not promote this to certification or all-controller support.

This is `PLAN_ONLY / NOT RUN`; no commissioning was performed.

## C1 — ESP32-C6 / Thread trigger check

No current trigger was found. The selected C3 baseline already supports the project's Matter-over-Wi-Fi direction, and the candidate Home Assistant interoperability route supports Wi-Fi Matter devices. ESP32-C6 / Thread therefore remains optional future capability pending an explicit product/architecture requirement.

## Actor / next-input reconciliation

Safe ChatGPT-side preparation is complete for the current blockers:

- B1 next input: sanitized actual-device/app variant, firmware, visible channel count, and LAN Control status.
- B2 next input: exact physical ESP32 carrier/product-board identity plus reliable schematic/pinout evidence.
- B3 next input: B1 LAN Control result plus explicit authorization for any new live LAN campaign.
- B4 next input: B1 + B2 closure and an explicitly authorized physical setup.
- B5 next input: bridge firmware/hardware readiness plus selection of a named Matter controller/scenario.

No Codex implementation mutation is justified by this prework alone.
