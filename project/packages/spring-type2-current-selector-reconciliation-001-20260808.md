# Spring Type 2 Current Selector Reconciliation 001

Date: 2026-08-08  
Baseline main: `167572418e839ce53d0252a2d04e23f9d00f803c`  
Package ID: `spring_type2_current_selector_reconciliation_001`

## Result

The current commercial-offer collector now reconciles the known Spring Type 2 source-history conflict without changing either source fact.

The three February 2026 brochure-backed `spring_type2_charging_cable_option` mappings remain preserved as historical `optional` observations. The later exact-current canonical `type2_charging_cable_supplied = standard` equipment-availability observations also remain unchanged for:

- Spring Essential electric 70 — 2026-07-31 official configurator observation;
- Spring Expression electric 70 — 2026-08-02 exact saved official configuration `7OO7LQ`;
- Spring Extreme electric 100 — 2026-08-02 exact saved official configuration `WKAWYV`.

For the current selector only, the Type 2 brochure option is suppressed when the same exact configuration has a later source-backed canonical `standard` observation for `type2_charging_cable_supplied`. Historical `as_of` views before those later observations still expose the brochure option.

## Deliberately bounded implementation

This package does **not** create a generic temporal-precedence rule between commercial items and component attributes.

The reconciliation is explicitly limited to:

- commercial item `spring_type2_charging_cable_option`;
- canonical attribute `type2_charging_cable_supplied`;
- exact same `configuration_code`;
- a later dated canonical availability row whose status is `standard`.

A future Type 2 optional commercial observation newer than the current standard observation would not be suppressed by this rule. No mapping is transferred between Spring grades or configurations.

This boundary is necessary because a generic rule such as “one component is standard, therefore the whole package is not selectable” would be invalid for many commercial packages. It also preserves the existing Duster contract where an `optional` commercial offer and a later commercial `standard` row represent an available package plus an exact selected-stock observation.

## Current selector impact

The previous commercial-readiness inventory contained 167 selector offers, 162 priced and 5 unpriced. Three of the five unpriced rows were the historical Type 2 brochure mappings.

After this reconciliation:

- selector offers: 164;
- priced selector offers: 162;
- unpriced selector offers: 2;
- Spring selector offers: 7;
- Spring priced selector offers: 5;
- Spring unpriced selector offers: 2.

The two remaining unpriced current questions are limited to Spring Expression electric 70:

- `spring_techno_package`;
- `spring_dc40_charging_option`.

Their historical MY2025 stock-list prices are not promoted to current MY26 values. They remain unknown until exact-current source evidence is captured.

## Preserved behavior

- all three historical Type 2 commercial mapping rows remain unchanged in `data/master`;
- all three exact-current Type 2 standard equipment rows remain unchanged in `data/master`;
- `spring_domestic_socket_charging_cable_option` remains a separate selector item and is not affected;
- Duster offer-plus-selected-state semantics remain unchanged;
- no compatibility, conflict, dependency or simultaneous-orderability rule is inferred;
- no source, master-data, schema or architecture mutation is introduced.

## Regression coverage

Direct regression coverage is embedded in the existing configuration-shortlist test method so the canonical discovery baseline remains 1885 tests. It verifies:

1. the historical Type 2 option is visible on 2026-02-19;
2. the Type 2 option is absent from the current selector for Essential, Expression and Extreme after the later exact standard observations;
3. the separate domestic-socket cable remains selectable;
4. only Techno and DC 40 kW remain unpriced in the bounded Spring fixture;
5. the existing offer-plus-selected-state behavior remains intact;
6. the deterministic reconciliation report records 164 current offers and 2 unpriced rows.

The first full CI pass correctly identified two older assertions that still treated the preserved historical Type 2 mappings as current selector rows. Those existing tests were updated in the same package to preserve their historical-master assertions while aligning current UI expectations with the exact chronology: Essential is suppressed from 2026-07-31, and Expression/Extreme from 2026-08-02.

The next full pass reached all 1885 discovered tests and exposed only the aggregate reviewed-state expectation. Runtime already suppressed all three Type 2 selector rows: the review ledger still preserves 29 historical commercial decisions, but only 26 attach to current selector components after this reconciliation. The three non-attached decisions are exactly the historical Type 2 rows: one `source-not-stated` and two `source-conflict`. The test now records that distinction explicitly without mutating the review ledger. No test method was added, so the discovery baseline remains unchanged.

## Delivery

This is a user-facing correction to the already published v1.19.0 configurator behavior. The public v1.19.0 release remains immutable.

The tag and release `data-products-v1.19.1` were confirmed absent on 2026-08-08. The next bounded package is therefore `data_products_v1_19_1_release_preparation_001`, which should prepare the established exact-source deterministic patch-release pipeline for this correction and stop before public publication.
