# Commercial Options, Equipment Filters and Workbook v1.2

Date: 2026-07-21

## Purpose

Turn the four official Polish MY26 price lists effective 3 July 2026 into source-backed consumer features without weakening the repository's evidence rules.

## Commercial data

The package introduces three stable master tables:

- `commercial_items.csv` — named packages and individual options;
- `commercial_item_attributes.csv` — exact source wording and canonical equipment membership;
- `commercial_item_configurations.csv` — configuration-specific availability and gross catalogue price.

The first import contains:

- 27 named commercial items,
- 68 commercial-item-to-equipment relationships,
- 86 configuration-specific price mappings,
- 39 current catalogue-price observations dated 3 July 2026.

Sandero/Sandero Stepway, Duster and Jogger receive configuration mappings. Bigster commercial items are registered without invented versions or configurations because its catalogue foundation is not yet modeled.

## Evidence rules

Commercial package membership may establish that an equipment attribute is optional for a configuration. It never changes an already source-backed `standard` state to `optional`.

Every item, membership and price mapping retains:

- the original commercial name,
- exact Polish source wording for included equipment,
- observation or price date,
- official source code.

The interface may show normalized Polish labels, while source wording remains available in master data and provenance.

## Interactive shortlist v1.2

The native equipment multi-select remains as a hidden semantic control for the existing filter engine, but the user-facing surface is replaced by grouped click selection:

- equipment is grouped by category;
- one click selects or removes an item;
- selected items remain visible in a persistent tray outside the scrollable list;
- each selected chip can be removed directly;
- the tray includes a count, clear action and `show selected only` mode;
- list ordering stays stable;
- `required equipment` and `required as standard` remain separate filters.

Configuration cards use readable Polish labels and show all source-backed packages and options. The price breakdown chooses the cheapest deterministic set of commercial items that covers the selected optional equipment. Standard equipment is not charged, unrelated packages are not added, and uncovered optional equipment is shown as `price unknown` rather than guessed.

## Workbook v2

The deterministic workbook expands from six to eight sheets:

1. Overview,
2. Scopes,
3. Configurations,
4. Equipment,
5. Commercial Offers,
6. Comparisons,
7. Sources,
8. Artifacts.

`Equipment` and `Commercial Offers` are filterable consumer views with readable configuration names, Polish equipment labels, dates and source codes. Comparison semantics remain unchanged and the XLSX remains formula-free, macro-free and byte-deterministic.

## Validation

- repository CSV and reference validation covers all new tables;
- commercial import contracts verify exact counts and selected source facts;
- JavaScript v1.2 contract verifies deterministic minimum-cost package selection;
- browser catalogue tests retain Python/JavaScript filter parity;
- workbook tests verify the two new sheets, filters, source coverage and deterministic bytes;
- the complete repository quality gate is required before merge.

## Deferred scope

- Bigster versions and configurations;
- commercial financing and promotional prices;
- combinations, exclusions and dealer-specific package constraints not stated as deterministic catalogue rules;
- Python 3.10 retirement implementation.
