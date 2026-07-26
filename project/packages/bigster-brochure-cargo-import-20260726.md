# Bigster Brochure Cargo Value Import

Date: 2026-07-26

## Scope

Import 68 unambiguous luggage-capacity observations from page 20 of the official
Polish Bigster brochure dated 10 December 2025. The package covers eleven exact
4x2 configurations:

- four mild hybrid-G 140 manual configurations;
- four mild hybrid 140 manual configurations;
- three hybrid 155 automatic configurations.

Each value receives a one-to-one cargo-context row preserving VDA/ISO 3832 versus
ordinary litres, rear-bench state, compartment meaning, repair-kit state and
spare-wheel state.

## Equipment states

The brochure lists the tyre-repair kit as standard. Its footnote says that the
optional spare wheel replaces the kit. Therefore:

- repair-kit observations use `tyre_repair_kit_state_code = present` and
  `spare_wheel_state_code = absent`;
- spare-wheel observations use `spare_wheel_state_code = present` and
  `tyre_repair_kit_state_code = absent`;
- Essential receives no spare-wheel observations;
- mild hybrid-G 140 receives no spare-wheel observations because the brochure
  explicitly marks the spare wheel unavailable for that powertrain.

The page-20 table does not state double-floor condition, so every imported
`double_floor_state_code` remains empty and means **not stated**.

## Deferred hybrid-G 150 4x4

The four values `444`, `1712`, `556` and `1856` are not imported. Their technical
column says there is no repair kit / spare wheel, while the equipment table in the
same brochure marks the repair kit as standard for every trim. Importing either a
present or absent equipment state would resolve a source contradiction by guess.

## Deferred dimensions-page values

Page 23 gives `667/702` and `1937/2002` with no double floor and no spare wheel.
It does not identify a powertrain. Although the numbers match the mild hybrid 140
technical column, numerical equality is not sufficient evidence for projecting the
additional double-floor qualifier into exact configurations.

## Follow-up

The next package will evaluate the official Duster mini-brochure cargo table with
exact 4x2/4x4 and repair-kit/spare-wheel boundaries. Manual brochure values will
not be inherited by current automatic Eco-G 120 stock configurations.
