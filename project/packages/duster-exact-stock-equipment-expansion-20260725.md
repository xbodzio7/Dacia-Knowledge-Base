# Duster Exact Stock Equipment Expansion — 2026-07-25

Status: complete

## Goal

Expand the three exact 2026 Duster Eco-G 120 automatic stock configurations with source-backed equipment and selected-package evidence without projecting manual-version data or converting missing text into negative availability.

## Exact equipment

The package adds 203 new dated configuration-level equipment observations:

- Expression automatic — 54 records;
- Extreme automatic — 75 new records;
- Journey automatic — 74 new records.

The distribution is 199 `standard` and four explicit `not_available` states. Two standard folding-mirror observations for Extreme and Journey are reused from the immediately preceding exact-stock intake instead of being duplicated on the same observation date. The negative states are limited to source wording that explicitly removes driver seat-belt height adjustment from all three cards and the configured Extreme card's explicit absence of the two-level boot floor.

Compound source statements are decomposed only where every capability is explicit, for example ESC/HSA, automatic lights/rain-sensing wipers, electric/heated/folding mirrors and front/rear pyrotechnic pretensioners.

## Commercial packages

The existing commercial model is reused without schema changes. The official Duster MY26 price list supplies package names, component membership and gross prices, while exact stock cards prove applicability and selection.

Four optional offer mappings are added:

- Extreme — Pakiet PARKING, 2,200 PLN;
- Extreme — Pakiet ZIMOWY PLUS, 2,300 PLN;
- Journey — Pakiet PARKING, 2,200 PLN;
- Journey — Pakiet ZIMOWY PLUS, 2,300 PLN.

Four later `standard` rows record that those packages are selected in the exact stock vehicles. Their amount is deliberately empty: the stock card proves inclusion but does not restate a standalone package price. The earlier optional price-list row remains the price observation.

## Source lifecycle

Stock card 121540 expired after the first observation. Its normalized snapshot preserves the explicit Extreme PARKING and ZIMOWY PLUS descriptions. Current card 127567 is retained as supporting evidence but does not replace the dated primary card; its shortened dealer-authored `Pakiet ZIMOWY` heading is documented rather than allowed to erase the original exact-card evidence.

## Boundaries

- no equipment is copied from manual configurations;
- Expression power-folding mirrors remain unresolved;
- factory antenna type remains unimported for all three configurations;
- wheel, upholstery and paint wording is not converted into boolean equipment;
- rubber mats, luggage-compartment liners, warranty and dealer accessories remain outside factory-configuration equipment;
- missing rows are not interpreted as `not_available`.

## Determinism

`tools/import_duster_exact_stock_equipment_20260725.py` verifies the snapshot SHA-256, exact configuration coverage, active supported equipment attributes, 203-row distribution, reuse of the two prior exact folding-mirror observations, four package offers, four selected-package states and non-inference boundaries. `--apply` replaces only records owned by this source and the exact generated commercial mapping codes; `--check` reproduces the contract without mutation.
