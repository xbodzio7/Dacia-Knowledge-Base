# Interface and Source Coverage Repair

Status: complete

Package ID: `interface_source_coverage_repair_001`

## Scope

This bounded maintenance package implements direct user feedback for the interactive configuration shortlist without adding models, versions, configurations, domains or attributes.

## Interface repairs

- Spring receives a current official Dacia Polska model image; the generated vehicle artwork remains the offline/error fallback.
- The `Wybór do porównania` panel stops being sticky while the comparison table is open, so it cannot cover the table headers during vertical scrolling.
- Comparison parameter groups can be collapsed individually by selecting their headings or globally with `Ukryj wszystkie grupy` and `Pokaż wszystkie grupy`.
- Collapsed-group state is retained for the current browser session.
- Technical and equipment cells expose recorded source/date provenance through an information marker.

## Data and wording repairs

The official Polish Sandero/Sandero Stepway MY26 price matrix effective 2026-07-03 supplies 19 exact missing commercial mappings. They cover source-stated combinations of the rear-view camera, Media Nav Live, glass sunroof and the Comfort Auto, Thermo, Winter, Media Nav Live and Easy packages. Applicability is recorded only for the exact grade and powertrain columns shown by the source.

The interface no longer uses one ambiguous message for distinct states:

- `brak wpisu w bazie` means no matching technical/equipment record is currently present;
- `brak powiązania z cennikiem` means optional equipment exists but no commercial item covers it for that configuration;
- `cena niepodana w źródle` means the mapped item exists but the registered source does not state an amount.

## Sandero TCe 100 injection type

The existing `direct_injection` observations for Sandero Essential, Expression and Journey TCe 100 remain unchanged. The official MY26 technical table explicitly labels the TCe 100 injection type as direct injection, so changing it to multi-point or port injection would contradict the registered source.

## Missing-data boundary

The current completeness analysis retains 97 missing technical slots and 36 missing equipment slots, but has 0 eligible source-backed candidates and 7 exhausted-source candidates under its current exact-source scopes. This package therefore repairs verified commercial mappings and improves status transparency; it does not copy values from sibling trims or powertrains.

The next bounded review is `registered_source_completeness_reconciliation_001`. It will test the user's broader observation against all registered exact sources and classify each remaining active comparison or optional-price gap as importable, source-not-stated, source-conflict or context-unmodeled. It adds no models or domains.

## Result

- official Spring image source registered;
- comparison-header overlap removed;
- collapsible parameter groups added;
- 19 exact commercial mappings imported;
- Sandero TCe 100 direct-injection state verified and preserved;
- ambiguous missing-data and missing-price messages separated;
- a bounded registered-source reconciliation selected as the next package.
