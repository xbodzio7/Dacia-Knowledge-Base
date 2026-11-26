# Duster Catalog Bootstrap Reporting-Scope Boundary

## Decision status

`ACTION_REQUIRED`

The accepted Duster source supports a bounded catalogue bootstrap, but the repository cannot currently add those configurations without making a new architecture decision about lifecycle and reporting scope.

## Source-backed catalogue candidate

Page 1 of the accepted price list contains 24 explicit non-empty version and powertrain combinations across five named versions:

- `essential`;
- `expression`;
- `extreme`;
- `journey`;
- `journey+` where explicitly priced.

The source names seven priced powertrain rows: Eco-G 100 4X2, mild hybrid 130 4X2, hybrid 140 4X2, mild hybrid 130 4X4, Eco-G 120 4X2, mild hybrid 140 4X2 and hybrid 155 4X2. Technical tables on pages 8 and 9 identify the corresponding manual or automatic transmission families.

The bootstrap package would create only versions, configurations and source relationships. Prices, promotions, technical observations and equipment availability remain separate packages.

## Current repository constraint

`versions.csv` and `configurations.csv` accept only the status `active`.

The configuration completeness and comparison tools then require the configuration mappings in `configuration_completeness.json` to equal the entire set of configurations with that status. This assumption was safe while the repository contained only the seven fully reviewed Sandero and Sandero Stepway configurations.

Adding 24 source-backed Duster configurations as `active` would therefore require one of the following before the catalogue commit can pass Quality:

1. add every Duster configuration to the current completeness scope and immediately classify all expected technical and equipment slots;
2. introduce a lifecycle status for source-backed catalogue entities that are not yet in reporting scope;
3. allow the reporting specification to select an explicit validated subset of active configurations.

Option 1 is rejected. It would manufacture a large operational gap set before the bounded Duster import packages exist and would mix catalogue creation with completeness evidence work.

## Option A — explicit reporting subset of active configurations

**Recommended.**

Keep source-backed Duster versions and configurations `active`, but change reporting contracts so that:

- every configuration named in the reporting spec must exist and be active;
- the spec may select a strict subset of active configurations;
- duplicate, missing or inactive mappings still fail;
- reports disclose both the selected count and the repository-wide active count;
- currently selected Sandero configuration codes and all existing output remain unchanged by default;
- adding an active configuration no longer silently expands completeness or comparison scope.

### Consequences

- preserves one clear entity status for source-backed current catalogue records;
- separates catalogue existence from readiness for a particular reporting portfolio;
- requires coordinated changes in completeness, source coverage, comparison contracts and their tests;
- requires careful field naming so `active_configurations` is not used for a selected subset without qualification.

## Option B — new catalogue lifecycle status

Introduce a controlled status such as `catalogued` for versions and configurations, and continue selecting only `active` configurations in current reports.

### Consequences

- smaller initial reporting change;
- makes promotion from `catalogued` to `active` an explicit later operation;
- adds a new lifecycle meaning that must be defined across validation, search, SQLite, user documentation and future imports;
- risks conflating source-backed existence with observation completeness unless promotion criteria are precisely specified.

## Recommendation

Select **Option A: explicit reporting subset**.

It matches the existing declarative completeness specification, keeps the source-backed catalogue truthful, and avoids creating a second lifecycle dimension solely to compensate for a reporting-scope assumption.

## Required action

The project owner must approve either:

- `A` — explicit reporting subset of active configurations; or
- `B` — a new catalogue lifecycle status.

No Duster version or configuration rows will be committed before that choice because the project autonomy contract lists a new architecture decision as a stop condition.

## Resume stage

`duster_catalog_reporting_scope_design`

After approval, the next implementation sequence is:

1. implement and test the chosen scope/lifecycle contract;
2. merge that architecture package;
3. create the five source-backed Duster versions;
4. create the 24 explicit Duster configurations and source relationships;
5. run Quality and merge the catalogue bootstrap;
6. proceed to the separate explicit catalogue-price package.
