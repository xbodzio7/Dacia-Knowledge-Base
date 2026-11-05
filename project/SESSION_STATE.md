# Session State

Ten dokument przechowuje trwały kontekst operacyjny potrzebny do rozpoczęcia kolejnej sesji. Nie przechowuje ręcznie aktualizowanych nazw bieżącego sprintu, gałęzi ani SHA.

## Canonical Current State

Jedynym źródłem bieżącego stanu jest:

- `project/state.json` — stan maszynowy,
- `project/STATE_SUMMARY.md` — generowane podsumowanie.

Przed rozpoczęciem pracy należy uruchomić:

```bash
python tools/dkb.py project-state --check
```

Bieżący SHA `main`, stan Pull Requestów i wyniki CI należy zawsze odczytywać dynamicznie z Git i GitHub. Nie są kopiowane do tego dokumentu. Historyczne zdania narracyjne nie mogą służyć do wyboru następnego pakietu.

## Verified Current Progress (2026-11-05)

Latest verified merged work on `main` is newer than the old 2026-10-27 narrative and must be considered before selecting or repeating any package:

- Package `bigster_brochure_grade_details_import_20261105_001`: 56 historical scalar observations from Bigster brochure printed pages 14–17 imported for parking-brake type, steering-wheel material, rear-seat folding and speaker count across 14 exact configurations.
- PR #759: 14 exact historical Bigster TPMS availability observations imported from the 2025-12-10 brochure.
- PR #760: 283 additional Bigster equipment availability observations imported; together with TPMS, 297 exact cells across 22 attributes and 14 configurations.
- PR #761: 14 exact historical Bigster overall-length observations imported.
- PR #762: six unresolved Bigster brochure facts explicitly deferred as `Do sprawdzenia`; this is a workflow status, not a master-data value.
- PR #767: source-page references added to those six deferred facts. This is traceability only and does not resolve them.
- PR #763: shortlist fuel-type filter and readable cargo context merged; this is a user-facing feature, not a data-completeness milestone.
- PR #766: consumer-guide example updated to published `data-products-v1.20.0`.

Current open PRs verified from GitHub:

- #754 — Bigster brochure page inventory/master reconciliation; Draft, not merged. Its remaining issue is exact candidate-to-configuration/evidence mapping and attribute contracts. CI green, if confirmed on current head, does not establish source-to-master completeness.
- #675 and #673 — Sandero Hybrid 155 configurator reporting/endpoint discovery; neither is a completed master-data import.
- #634 — old Draft Sandero residual full-modal import PR; do not rerun or treat as the current package without a fresh, current-main reconciliation.

Operational rule: before every continuation, inspect current main, recent merged PRs, open PR heads, and the canonical state. Do not repeat PR #752 source portfolio inventory, PR #767 page anchoring, or the same #754 crosswalk report. The next package must deliver a concrete, source-backed import batch or explicitly move to the highest-impact unblocked data gap for another model family. If no importable batch is possible, state the exact evidence boundary and switch scope; do not loop on a generic blocker.

## Recovered Work from ZIP Session (2026-11-02)

The repository ZIP used in the earlier portfolio-audit work was re-opened and its generated audit outputs were compared with current `main`. Recoverable report artifacts have been committed under `reports/recovered/`.

Recovered outputs include:

- portfolio audit snapshot dated 2026-10-01;
- model-family portfolio summary dated 2026-10-01;
- completeness audit;
- source coverage report;
- configuration inventory and field inventory audits (Markdown/CSV);
- peer-union candidate-gap CSV;
- completeness-spec diagnostics (Markdown/CSV);
- active configuration shortlist (Markdown/CSV);
- all-configuration comparison (Markdown/CSV);
- PDF candidate ledger, review, and residual-gap prioritization.

These are preserved as historical/generated analysis artifacts. They are not current master data, do not prove current completeness, and do not replace source-backed imports. The audit snapshot records 94 active configurations, 6 model families, 108 source records, 402 explicit source-to-configuration relationships, and 0 configurations without source links as of its stated scope/date. The 2026-10-01 snapshot is not to be substituted for current `main` counts. Repository quality tests were not rerun as part of this recovery.

## Current Main Reconciliation (2026-11-02)

After recovering ZIP-session artifacts, current main and the canonical source coverage report were checked against previously recorded Spring follow-up plans. The following review-document "next package" items have already been implemented on main and must not be repeated:

- Spring Essential Biel Alpejska default-colour migration (direct `exterior_color` value and standard 0 PLN mapping).
- Spring Essential Lichen Khaki exact-current price (2300 PLN).
- Spring charging cable semantic migration and exact stock-price-list states, including Type 2 cable standard and domestic-socket cable 1500 PLN mappings.

Current official brochure portfolio reconciliation records six registered brochures, zero fully assimilated at the source-wide coverage level, and all six as `partial_review`. This does not mean previously imported individual observations are missing; the status describes source-wide page/master reconciliation.

The Duster mini brochure was previously selected as a source-gap package, but current-main reconciliation confirmed that page 20 has already been imported exactly (35 observations), page 21's ambiguity/unresolved reviews are closed with no import approvals, and pages 22–23 have completed review-only ambiguity packages. The selected Duster scope was therefore too broad/stale to justify a repeat. Do not repeat those page reviews.

No master data was changed in this state-reconciliation step. Tests/Quality were not rerun.

## Verified Quality Baseline

<!-- dkb:documentation-baseline:session:start -->
- 1959 testów automatycznych zakończonych powodzeniem,
- 48 pliki CSV w `data/master`,
- 21802 rekordów danych,
- 51 relacje między tabelami,
- 27 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 8399 obserwacji w `configuration_attribute_values.csv`,
- 189 wersjonowanych specyfikacji w `data/imports/configuration_values`,
- 451 obserwacji w `configuration_attribute_value_ranges.csv`,
- 25 wersjonowanych specyfikacji w `data/imports/configuration_value_ranges`,
- 10112 rekordów w `configuration_attribute_availability.csv`,
- 8148 rekordów `standard`, 688 `optional`, 1276 `not_available` i 0 `unknown`,
- 417 kanonicznych atrybutów w 30 kategoriach,
- baza SQLite obejmująca 48 tabele i 21802 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.
<!-- dkb:documentation-baseline:session:end -->

Dodatkowe kontrakty stanu projektu i autonomii są uruchamiane jawnie w CI poza historycznym licznikiem discovery `test_*.py`.

## Verified PDF Residual Review Boundary

Kanoniczna kolejka przeglądu PDF jest zamknięta: 52/52 paczki oraz 1 266/1 266 kandydatów zostały rozliczone. Decyzje pozostają w sześciu jawnych kategoriach: `context_only_non_import`, `covered`, `covered_by_selected_evidence`, `deferred_source_conflict`, `partially_covered` i `unresolved_signature_mismatch`. Nie należy zastępować ich zbiorczym statusem `ignore` ani traktować jako automatycznej zgody na import.

Strona 21 minibroszury Dustera została rozliczona w dwóch paczkach:

- `residual_gap_018`: 40 kandydatów — 14 `context_only_non_import` i 26 `unresolved_signature_mismatch`;
- `residual_gap_019`: 21 kandydatów — 19 `context_only_non_import` i 2 `unresolved_signature_mismatch`.

Łącznie są to 61 kandydatów, zero wybranych sygnatur dowodowych, zero wybranych rekordów, zero zatwierdzeń importu i brak zmian w `data/master`. Identyfikatory `000P-27614`, `000P-27615` i `000P-27616` nie są kanonicznymi identyfikatorami tej kolejki i nie mogą być używane do ponownego otwarcia strony bez nowego, bezpośredniego dowodu źródłowego.

## Working Mode

Projekt jest rozwijany w małych, kontrolowanych pakietach.

Każdy pakiet:

- wynika z kanonicznej kolejki w `project/state.json`,
- rozpoczyna się od aktualnego `main`,
- obejmuje wyłącznie jawnie określony zakres,
- przechodzi odpowiednie testy i pełną bramkę jakości,
- jest publikowany przez Pull Request,
- jest scalany po zielonym CI i potwierdzeniu aktualnego head,
- kończy się aktualizacją stanu oraz wymaganej dokumentacji.

Zwykłe etapy implementacji, PR, CI, naprawy należącej do zakresu i merge nie wymagają polecenia `kontynuuj`.

Praca zatrzymuje się wyłącznie na granicy opisanej przez `ACTION_REQUIRED` w `project/AUTONOMOUS_MAINTAINER.md` i `project/AUTONOMY_EVENTS.md`.

## Project Rules

- `data/master` zawiera źródłowe dane projektu.
- Raporty, eksporty wyszukiwania i lokalne bazy SQLite są artefaktami generowanymi.
- Dane handlowe i techniczne muszą mieć datę i źródło.
- Nie należy zgadywać brakujących parametrów technicznych.
- Brak stwierdzenia w źródle nie oznacza wartości negatywnej.
- Nie należy ponownie projektować stabilnej architektury bez wyraźnej potrzeby.
- Nie należy deklarować powodzenia CI bez sprawdzenia wyniku.
- `project/state.json` definiuje bieżący pakiet, następny pakiet, fazę i politykę zatrzymania.
- `project/ROADMAP.md` definiuje trwały kierunek i backlog, nie chwilowy stan.
- Dokumentacja operacyjna musi być synchronizowana w tym samym pakiecie, w którym zmienia się sposób pracy.

## Package Workflow

Powtarzalne kontrole są dostępne przez:

```bash
python tools/dkb.py package-start <branch>
python tools/dkb.py package-review --manifest ../package.json --quality
python tools/dkb.py package-publish --manifest ../package.json --push
python tools/dkb.py package-finish --manifest ../package.json
```

Decyzję o kolejnym kroku workflow może rozstrzygnąć:

```bash
python tools/dkb.py autonomy-decision --event ../event.json
```

## Documentation Synchronization

Liczniki oraz generowane powierzchnie stanu są kontrolowane przez:

```bash
python tools/dkb.py project-state --check
python tools/dkb.py project-state --apply
```

Szczegóły kontraktu znajdują się w `project/DOCUMENTATION_SYNC.md`.

## Historical Record

Dawna wersja tego dokumentu zawierała setki linii historii sprintów oraz nieaktualne odwołania do gałęzi, PR-ów i commitów. Pełny stan sprzed migracji pozostaje dostępny w Git pod commitem:

```text
bceab5405a294b0b785b4fd206f3af37e164e85c
```

Granica migracji i lokalizacja pozostałych zapisów historycznych są opisane w:

- `project/history/legacy-narrative-migration-2026-07-17.md`,
- `project/reviews/`,
- `CHANGELOG.md`,
- historii commitów i scalonych Pull Requestów.


## Current Main Residual Reconciliation (2026-11-02)

The stable residual queue had selected Sandero brochure page 17 (packages `residual_gap_004`, `026`, `027`) because no later current-main reconciliation was recorded. This page is now reconciled:

- 46 candidates reviewed: 5 ambiguous and 41 unresolved.
- The ambiguity review selected 8 exact signatures / 16 records. All 16 already exist in `data/master/configuration_attribute_values.csv` under exact source `src_pl_sandero_brochure_20260202`: engine power 4, engine torque 4, maximum kerb weight 4, gross vehicle weight 2, gross train weight 2.
- The remaining 41 candidates have no selected evidence: 27 context-only and 14 signature mismatches.
- No import-ready gap, master-data change, or new import spec.

Durable package receipts:
- `data/reporting/sandero_brochure_page17_current_main_reconciliation_20261102.json`
- `project/reviews/sandero-brochure-page17-current-main-reconciliation-2026-11-02.md`

The next package is now a bounded **current-main residual queue re-entry**: reconcile completed reviews against later imports and closure receipts before selecting another boundary. Do not repeat Sandero page 17, Bigster equipment page 21 (packages `028`–`030` are already reviewed), Bigster PR #754 crosswalk, or PR #634. If the queue yields no exact import, switch to a non-Bigster family with the highest-impact actionable source gap.


## Jogger Equipment Page 20 — Current Main Reconciliation (2026-11-02)

The completed ambiguity review selected 154 record references (110 unique codes) across 3 partially covered candidates. All 110 unique codes already exist in current-main `configuration_attribute_availability.csv`. The other two ambiguity outcomes are context-only and deferred source conflict. Three unresolved chunks cover 107 candidates and have no selected evidence signatures. No new import spec or master row is warranted.

Durable receipts:
- `data/reporting/jogger_equipment_page20_current_main_reconciliation_20261102.json`
- `project/reviews/jogger-equipment-page20-current-main-reconciliation-2026-11-02.md`

Next: reconcile Jogger equipment page 21's completed review against current main. Preserve the deferred heated steering wheel conflict; do not infer availability.


## Jogger Equipment Page 21 — Current Main Reconciliation (2026-11-04)

The completed page-21 ambiguity review selected 30 availability record codes across two competing signatures. All 30 unique codes are present exactly once in `data/master/configuration_attribute_availability.csv` using the canonical identifier column `code`. The two unresolved review chunks contain 72 candidates with zero selected evidence signatures or records. The heated-steering-wheel Journey state remains deferred because the 2025-12-17 brochure says standard while the later 2026-07-03 price list says unavailable. No import spec or master-data change is warranted.

Durable receipt: `data/reporting/jogger_equipment_page21_current_main_reconciliation_20261104.json`.

Next: review the registered Duster mini brochure against current imports and completeness gaps; import only exact source-backed values not already present.


## Duster Mini Equipment Pages 21–22 Gap Closure (2026-11-04)

Reviewed the registered official Duster Mini brochure, printed pages 21–22, against current availability records. Added 12 missing source-backed cells across nine exact configurations: Multiview camera (5 unavailable, 4 optional) and passenger-seat height adjustment (2 optional, 1 standard). Existing cells were not overwritten. Brochure scope was kept to its listed powertrains; newer or unlisted powertrains were not projected.

Durable receipts:
- `data/imports/configuration_attribute_availability/duster_mini_equipment_page21_22_20251020.json`
- `data/reporting/duster_mini_equipment_page21_22_gap_import_20261104.json`
- `data/reporting/duster_mini_equipment_page21_22_gap_import_20261104.md`

Next: re-enter the verified PDF residual gap queue and select the next exact source-backed package.


## Duster Mini Equipment Pages 21–22 Gap Closure (2026-11-05)

PR #773 was rebuilt on current `main` after the earlier stacked branch diverged, then merged after all required checks passed. Merge commit: `5adfa817a391cdb1e423320d1ab8921c105b048f`. The package adds 12 exact availability observations across nine configurations for Multiview camera and passenger-seat height adjustment. Quality passed on Python 3.10, 3.13, 3.14 and Windows package workflow; all reporting workflows passed.

The state handoff is now the current-main verified PDF residual queue re-entry. Historical candidate priorities must be reconciled against all later review, import and closure receipts before selecting a new package.


## Verified PDF Residual Queue Re-entry Review (2026-11-05)

Re-entered the historical 52-package / 1,266-candidate queue against current main and later closure receipts. Sandero technical page 17 is already reconciled; Stepway page 17 and Duster Mini pages 21–22 have exact import closures; Jogger equipment pages 20–21 have current-main reconciliation receipts.

Exact selected-evidence checks found no missing or duplicate codes in the reviewed boundaries: Duster Mini equipment page 23 (393 unique codes), Bigster equipment pages 21–22 (14 and 126), Sandero equipment pages 18–19 (4 each), Sandero Stepway equipment page 18 (1), and Duster Mini technical page 21 (3, checked against the values table). Partial and deferred decisions remain unpromoted. No master data changed in this re-entry review.

The next package is **Official Bigster Brochure Full Assimilation**. It will inventory all 24 pages, reuse existing page 20–22 reviews, reconcile against the 2026-10-01 official price list, preserve conflicts and import only exact unsuperseded gaps.

PR #775 corrected the generated state summary and merged as `d457774820839acf58c0b87920587a710e8e4ace`; its PR Quality run passed all four jobs. The post-merge main Quality run #41937756472 was still in progress at this handoff.


## Bigster page 21 — YouClip mount points import (2026-11-05)

Captured the exact numeric row from the official Bigster brochure: 4 YouClip mounting points for Essential and 5 for Expression, Journey and Extreme. Added the canonical integer attribute `youclip_mount_points` in the existing Infotainment category and 14 source-linked scalar observations for the 14 active Bigster configurations linked to the brochure (2 Essential, 4 per other grade).

Source page 21, SHA-256 `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`. Observation IDs 8217–8230. Three focused tests verify the source receipt, exact manifest, active source-linked configuration set and grade mapping. No existing observations were overwritten.

The broader **Official Bigster Brochure Full Assimilation** package remains active.
