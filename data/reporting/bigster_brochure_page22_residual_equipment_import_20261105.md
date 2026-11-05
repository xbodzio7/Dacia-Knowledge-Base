# Bigster Brochure Page 22 — Historical Equipment Residual Import

## Goal

Import the remaining directly represented page-22 equipment facts from the official Polish Bigster brochure dated 2025-12-10, while preserving the exact grade and powertrain scope.

## Source and scope

- Source: `src_pl_bigster_brochure_20251210`
- PDF: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Printed page: 22 (PDF page 22)
- Configurations: 14 active configurations linked to the brochure (Essential 2; Expression, Journey and Extreme 4 each).

## Imported observations

Added **260 historical availability observations** across **20 existing boolean attributes**. The existing page-21/22 import now contains 557 brochure observations: 157 from page 21 and 400 from page 22. New master IDs: 10113–10372.

New attributes: `central_locking`, `keyless_entry`, `digital_instrument_cluster`, `youclip_phone_holder`, `rear_air_vents`, `steering_wheel_height_adjustment`, `steering_wheel_reach_adjustment`, `cargo_cover`, `wireless_charging`, `boot_12v_socket`, `rear_usb_c_ports`, `media_display_system`, `navigation_system`, `connected_services`, `remote_firmware_updates`, `touchscreen`, `wireless_smartphone_replication`, `bluetooth_connectivity`, `front_centre_armrest`, and `cooled_centre_armrest`.

The importer uses only existing active boolean attributes. The Hybrid 155-only high console with cooled storage is recorded for Journey/Extreme Hybrid 155 only; the armrest attribute is recorded only where the printed console row explicitly supports it. No value is projected to other Journey/Extreme powertrains.

## Reconciliation and exclusions

- Later 2026 price-list and configurator observations remain separate; no existing row is overwritten.
- Only the luggage-compartment 12 V socket is mapped; the front socket is not represented by the existing attribute.
- Rear USB-C presence is mapped; front/rear port distribution and total count are not inferred.
- Folding key, numeric USB-port count, 7/10-inch cluster-size attributes, 10.1-inch infotainment screen size, optional six-speaker Media Nav Live upgrade, package identities, YouClip 3-in-1 and floor/boot accessory items remain deferred.
- The brochure's 10.1-inch infotainment wording is kept separate from later configurator observations recorded as 10-inch.

## Acceptance

- 260 new observations, 20 existing attributes, 14 exact active source-linked configurations.
- Importer verifies source SHA-256, exact scope, existing attribute contracts, and the 557-row complete specification.
- No duplicate source/date/configuration/attribute slots and no overwrites.
- Focused tests: 33 passed. Full local pytest run exceeded the 300-second execution limit; final full Quality is required on the GitHub PR head.
