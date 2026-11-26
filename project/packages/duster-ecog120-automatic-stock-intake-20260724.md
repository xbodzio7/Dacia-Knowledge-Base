# Duster Eco-G 120 Automatic Stock Intake — 2026-07-24

Status: complete

## Goal

Register exact 2026 Duster Eco-G 120 automatic configurations proven by official Dacia Poland stock cards without treating promotional prices, missing text or conflicting dealer-card descriptions as canonical factory availability.

## Imported configurations

The package adds three active configurations:

- `duster_iii_expression_ecog120_4x2_automatic`;
- `duster_iii_extreme_ecog120_4x2_automatic`;
- `duster_iii_journey_ecog120_4x2_automatic`.

Every source card explicitly identifies Duster, the exact version, Eco-G 120, model year 2026 and an automatic transmission.

## Catalogue prices

Only amounts explicitly labelled `Cena katalogowa` are imported:

- Expression — 96,900 PLN gross;
- Extreme — 110,300 PLN gross;
- Journey — 107,600 PLN gross.

Displayed promotional, financing, cash and monthly-payment amounts are excluded.

## Equipment evidence

Power-folding mirrors are imported as standard for:

- Extreme automatic;
- Journey automatic.

Expression receives no folding-mirror state. One exact official Expression card lists electrically adjustable and heated mirrors without folding, while another official Expression stock description conflicts. The package preserves that conflict as a non-import rather than choosing either `standard` or `not_available`.

No shark-fin antenna state is imported for any of the three configurations because the exact current cards do not state the factory antenna type.

## Source volatility

Official stock-card URLs are dynamic and may later expire or redirect after a vehicle is sold or the listing changes. The registered normalized snapshot preserves the exact observed identity, catalogue-price statement, equipment evidence and non-import boundaries with a fixed SHA-256.

## Intrinsic technical boundary

A second official-web snapshot contributes only three intrinsic Eco-G 120 engine values to each exact automatic configuration: 1199 cm³ displacement, three cylinders and 12 valves. The current Dacia engine page explicitly offers Eco-G 120 with the dual-clutch automatic transmission. Manual towing weight, VDA cargo volume, WLTP and performance values are not projected onto the automatic variants.

The three configurations form a new independent comparison scope containing these nine exact technical observations. Equipment remains available to the buyer-facing browser, while the source-completeness scope intentionally avoids claiming a complete stock-card equipment denominator.

## Consumer validation focus

The generated shortlist and comparison products must show all three automatic configurations with their exact catalogue prices. Extreme and Journey must show power-folding mirrors as standard; Expression must remain unknown. None of the three may show a factory shark-fin antenna state.

The comparison scope may show 1199 cm³, three cylinders and 12 valves. Towing weight, VDA cargo volume, WLTP and performance rows must remain missing until an automatic-specific homologation source proves them; values from the manual configuration must never appear by inheritance.

## Determinism

`tools/import_duster_ecog120_automatic_stock_20260724.py` verifies:

- the exact snapshot hash;
- three active Duster versions;
- explicit 2026 Eco-G 120, 90 kW/122 KM and automatic-transmission evidence;
- three positive catalogue prices;
- exactly two standard folding-mirror observations;
- absence of an inferred Expression mirror state and all antenna records.

`--apply` replaces only records owned by this source or the three exact configuration codes. `--check` reproduces the normalized contract without mutation.

## Verification

- exact source registration and relationships;
- three active automatic configurations;
- exact catalogue-price separation from promotions;
- two positive mirror observations and no negative inference;
- browser catalogue count and rendered current prices;
- full repository quality gate and canonical project-state check.
