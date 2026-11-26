# Configurator Exact Appearance Status 001

Date: 2026-08-07  
Baseline main: `8153f916c7cabcdcb7d2064c8aa1d507a4098e9a`

## Purpose

Make configurator steps 4–6 (`Kolor`, `Koła`, `Tapicerka`) informative without turning exact saved manufacturer observations into a fabricated catalogue of available choices.

## Source boundary

The cross-model configurator evidence currently contains 18 saved states with colour, wheel and upholstery fields. Identity closure records 18 canonical matches and zero unresolved identity conflicts while preserving `no_cross_phase_promotion`, `no_cross_grade_transfer` and `no_cross_powertrain_transfer`.

That evidence supports displaying the value observed for one exact canonical configuration. It does not support claiming that all observed values are selectable alternatives for another configuration.

## Behaviour

The existing three appearance steps remain exact-observation steps. An additive status layer now derives their live text from the browser state:

- an explicitly selected exact-observation filter is shown directly;
- several explicit exact filters are summarized as `dokładne filtry: N`;
- zero visible configurations produce `brak wyniku`;
- more than one visible configuration with no explicit appearance filter produces `po wyborze 1 wariantu`;
- exactly one visible canonical configuration shows its saved exact colour, wheel or upholstery value when present;
- exactly one visible configuration without that exact observation produces `brak dokładnego zapisu`.

Long wheel and upholstery names are shortened only in the compact navigation label. The full value remains available in the status element `title` attribute.

## Integration contract

The layer:

- reuses the existing eight-step navigation shell;
- captures `configurator_observation` records from the embedded catalogue before the later equipment-group layer removes observation pseudo-components from browser pricing data;
- updates after `dkb:results-rendered`, exact-observation filter changes and reset;
- never creates a second selector or choice catalogue;
- never transfers appearance evidence between configurations, grades, powertrains or source phases;
- leaves existing exact-observation filtering semantics unchanged.

## Tests

The existing `test_unfiltered_shortlist_is_price_sorted_and_reports_unknowns` method is extended; no new discovered unittest method is introduced.

Static checks verify the appearance-status marker and exact control bindings. When Node.js is available, the test executes the exported pure helpers for:

- zero, one and multiple live results;
- one and multiple exact filters;
- exact observed value and missing observation states;
- compact rendering of long labels.

The canonical discovered unittest baseline remains 1885.

## Repository impact

Interface/reporting only:

- no master-data mutation;
- no schema change;
- no generic colour/wheel/upholstery catalogue;
- no cross-configuration inference;
- no pricing semantic change;
- no change to the deferred Spring retry package.

## Files

- `tools/reporting/configuration_shortlist_v12_pricing.js`
- `tests/test_configuration_shortlist.py`
- `project/packages/configurator-exact-appearance-status-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
