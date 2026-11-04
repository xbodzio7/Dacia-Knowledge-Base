# Sandero Stepway page 17 — max power RPM gap closure

Reviewed: 2026-11-04

## Result

- Compared completeness specifications covering 94 active configurations.
- Found 10 absent fuel-specific `max_power_rpm` ranges across five Stepway Eco-G 120 configurations.
- Added all 10 ranges from the registered Dacia brochure source.
- This closes these 10 slots; the audit's technical gap total falls from 80 to 70. Equipment gaps remain 292.

## Evidence

Official Dacia Sandero Stepway brochure, source `src_pl_sandero_stepway_brochure_20260202`, page 17, section SILNIKI. The table gives LPG as 90 kW from 4500 to 5000 rpm and petrol as 84 kW from 4500 to 5000 rpm, for both manual and automatic Eco-G 120 powertrains. The matching source SHA-256 is `800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48`.

## Imported scope

- `sandero_stepway_iii_essential_ecog120_manual`, lpg: 4500–5000 rpm
- `sandero_stepway_iii_essential_ecog120_manual`, petrol: 4500–5000 rpm
- `sandero_stepway_iii_expression_ecog120_manual`, lpg: 4500–5000 rpm
- `sandero_stepway_iii_expression_ecog120_manual`, petrol: 4500–5000 rpm
- `sandero_stepway_iii_expression_ecog120_automatic`, lpg: 4500–5000 rpm
- `sandero_stepway_iii_expression_ecog120_automatic`, petrol: 4500–5000 rpm
- `sandero_stepway_iii_extreme_ecog120_manual`, lpg: 4500–5000 rpm
- `sandero_stepway_iii_extreme_ecog120_manual`, petrol: 4500–5000 rpm
- `sandero_stepway_iii_extreme_ecog120_automatic`, lpg: 4500–5000 rpm
- `sandero_stepway_iii_extreme_ecog120_automatic`, petrol: 4500–5000 rpm

No other technical values or equipment availability statuses were changed. Remaining technical and equipment gaps require separate source-level review.

Import specification: `data/imports/configuration_value_ranges/sandero-stepway-page17-max-power-rpm-ranges-20260202.json`. Master rows added: IDs 442–451.
