# Official Dacia Brochure Source Registration and Gap Review

Date: 2026-07-25

## Purpose

Archive and register five official Polish Dacia brochures supplied by the project owner, verify their immutable binary identities and classify useful technical candidates without importing context-poor observations.

## Registered sources

| Source | Publication date | Pages | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| Bigster brochure | 2025-12-10 | 24 | 10,359,318 | `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74` |
| Jogger brochure | 2025-12-17 | 23 | 3,636,538 | `eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6` |
| Sandero brochure | 2026-02-02 | 21 | 8,358,370 | `adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97` |
| Sandero Stepway brochure | 2026-02-02 | 21 | 8,541,016 | `800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48` |
| Duster mini brochure | 2025-10-20 | 25 | 9,712,859 | `84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8` |

The original Renault CDN addresses, repository paths, sizes, page counts, publication markers and hashes are retained in `project/sources/official-dacia-brochures-20260725.json`.

## Master-data registration

The package adds five active `brochure_pdf` records to `data/master/sources.csv` and five model-level `brochure_for` relationships to `data/master/source_models.csv`.

The sources are linked only to their model ranges:

- Bigster,
- Jogger,
- Sandero III,
- Sandero Stepway III,
- Duster III.

No source-to-version or source-to-configuration relationship is created because the brochures describe model ranges and contain tables with multiple powertrain, layout or equipment contexts.

## Evidence boundary

Source registration does not create, replace or supersede:

- configuration attribute values,
- configuration value ranges,
- equipment availability,
- configuration prices,
- commercial package observations.

Ordinary scalar technical values that duplicate current price-list or exact-card evidence remain unimported. A future import may use a brochure only after proving an exact source-level difference and preserving its complete context.

## Gap review

`data/reporting/official_dacia_brochure_gap_review.json` records three durable classifications.

### Duplicate existing evidence

The ordinary engine, performance, mass, towing, WLTP and dimension tables largely repeat already registered price-list or exact-card evidence. They are not duplicated merely because a second official source exists.

### Deferred context modeling

The brochures contain valuable facts that cannot be represented safely as one context-free scalar:

- Sandero and Sandero Stepway elasticity from 80 to 120 km/h separated by gear and fuel;
- Sandero and Sandero Stepway cargo values separated by VDA, ordinary litres, seat state and underfloor compartment;
- Jogger cargo values separated by five- or seven-seat layout and second- or third-row state;
- Bigster cargo values separated by spare wheel or repair kit, double floor and folded bench;
- Duster cargo values separated by 4x2 or 4x4, spare wheel or repair kit and folded rear seats.

These candidates remain deferred until a minimal, reusable context model is accepted.

### Explicit non-imports

- Country-adjustment placeholder wording in the Sandero brochure is not a numeric Polish CO2 or consumption observation.
- The Duster mini brochure's Eco-G 120 technical table describes the manual powertrain and must not populate exact automatic configurations.

## Deterministic implementation

`tools/register_official_dacia_brochures_20260725.py`:

- verifies the immutable receipt and all five archived binaries;
- applies fixed source IDs 23–27 and source-model IDs 30–34;
- owns only the five brochure source codes;
- rejects ID collisions and inactive model targets;
- verifies that no registered brochure source has materialized observations elsewhere in `data/master`;
- supports reproducible `--apply` and `--check` modes.

## Acceptance criteria

- five original PDFs are archived and match the pinned sizes and SHA-256 values;
- five active source rows and five model relationships match the deterministic contract;
- no version, configuration or observation-level projection is introduced;
- the machine-readable gap review retains the context and explicit non-import boundaries;
- canonical state and generated documentation are synchronized;
- the complete quality gate passes before merge.
