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


## Supersession Notice (2026-11-25)

The cennik-only priority recorded below was completed and superseded on 2026-11-25. Official Polish cennik reconciliation is complete across the represented model families, including Striker. The canonical active package is now Official Bigster Brochure Full Assimilation, as recorded in `project/state.json`. Older statements below about cennik-only priority, Striker follow-up work or brochure deferral are historical records and must not override the canonical state.

## Historical User Priority — Cennik-only (2026-11-06; superseded 2026-11-25)

The user explicitly narrowed active work to official Polish Dacia price lists (cenniki) only. Defer all brochure, catalogue and non-price-list assimilation until the cennik backlog has been reconciled. This instruction was active only until cennik reconciliation was completed on 2026-11-25; it is now superseded by canonical state.

Official Polish price-list sources:
- Duster: https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/f07ca0a87f.pdf — reconciled in the Duster MY26 2026-11-02 price-list package.
- Sandero/Sandero Stepway: https://cdn.group.renault.com/dac/pl/pdf/cenniki/sandero-price.pdf.asset.pdf/3b4618d7da.pdf — reconciled in the current package.
- Jogger: https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/f5cdbd7878.pdf — the 2026-10-01 page-1 price matrix and its commercial matrix have been reconciled; the 02.11.2026 date belongs to the technical-data table, not a separate seven-seat price table.
- Bigster: https://cdn.group.renault.com/dac/pl/pdf/cenniki/bigster-price.pdf.asset.pdf/2fe688def9.pdf — current catalogue/commercial price-list work is already reconciled.

Latest completed package before the current correction: `sandero_stepway_price_my26_20261102_commercial_reconciliation_20261106_001`. It registered the 2026-11-02 source, linked 19 configurations and six grades, added 15 catalogue-price observations (+500 PLN each), confirmed four unchanged Hybrid 155 prices, added three commercial items and 209 dated option/package mappings, and reconciled all nine pages with 24 scalar equipment observations, 27 availability observations, 42 technical observations and 27 Sandero dimension observations. No brochure data was imported; the raw PDF binary is archived at `owner_supplied/2026-11-02/3b4618d7da.pdf` and its SHA-256 is verified.

Current completed package: `jogger_price_matrix_correction_20261001_20261106_001`. Corrected the seven-seat Eco-G 120 manual price alignment: Essential has no catalogue price in the printed matrix, Expression is 86,550 PLN and Extreme is 94,400 PLN. Added source relationships for the 12 printed configurations and three grades. Preserved April/July historical prices. The 01.10.2026 date applies to the page-1 price matrix; 02.11.2026 is the technical-data status date. The source PDF was already archived with SHA-256. No brochure or configurator data imported.

The Sandero/Sandero Stepway catalogue-price history has been implemented and merged in PR #798. The Duster MY26 catalogue-price history was implemented and merged in PR #799. The Jogger MY26 catalogue-price history is also present in the repository. The next reporting gap selected on 2026-11-12 is the Bigster MY26 comparison between the 2026-10-01 and 2026-11-02 official cenniks. At the time of this 2026-11-06 note, the Striker cennik was unavailable. This was superseded on 2026-11-21 when the Project Owner supplied the exact official 2026-11-02 MY26 PDF and approved adding Striker. Source registration/model bootstrap was merged in PR #877; the 11 catalogue prices are tracked in PR #878.

## Historical Quality Gate Before Further Model Data (2026-11-22; completed 2026-11-25)

The Project Owner explicitly requires completion of all portfolio-wide, historical-scope, report-dependency and test-isolation safeguards before any further model-data assimilation. The next Striker priced-options/packages package is blocked in `project/state.json`; do not start it or any other model-data package until the guardrail closure is documented and all required CI checks pass. Historical completeness reports also fail closed when a scope has no `effective_from` but references a source document dated after the report's as-of cutoff.

## Historical Progress — Bigster MY26 Price List Archive (2026-11-15; cennik phase superseded)

The Bigster MY26 Polish price-list binary effective 2026-11-02 is now archived in `main` through PR #825. The source PDF was downloaded from the official Dacia/Renault Group CDN by the post-merge GitHub Actions workflow and passed exact identity checks:

- SHA-256: `592f28852118b57fe6bdef75864ea479d9e01bb9af9a166108014eff4ae85b5b`
- Size: 1,995,398 bytes; PDF page count: 8.
- First-page markers include model year 2026, effective date 02.11.2026 and all 13 catalogue-price cells.
- Manifest: `data/source_intake/bigster_my26_20261102_capture.json`.
- Sidecar: `data/source_intake/bigster_my26_20261102.sha256`.
- Archived PDF: `PDF/Cenniki/DACIA BIGSTER cennik MY26 20261102.pdf`.
- `data/master/sources.csv` now points to the archived binary and records the verified provenance.

No prices were re-imported. The Bigster MY26 catalogue-price comparison between the official 2026-10-01 and 2026-11-02 price lists is already implemented in `tools/bigster_catalogue_price_history.py` and its JSON/Markdown reports; do not repeat it. This was the next task at the time of writing. It was superseded after cennik reconciliation was completed; the current next package is Bigster brochure assimilation.

## Vehicle Change History Plan (2026-11-06)

The implementation plan is recorded in `project/CHANGE_HISTORY_PLAN.md` and merged through PR #789. The proposed first stage is the Sandero/Sandero Stepway catalogue-price timeline. It is a derived reporting layer, not a second manually maintained master table. Implementation begins after the current cennik reconciliation packages are closed.

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

Historical open-PR snapshot (2026-11-05; verify GitHub dynamically):

- #754 — Bigster brochure page inventory/master reconciliation; Draft, not merged. Its remaining issue is exact candidate-to-configuration/evidence mapping and attribute contracts. CI green, if confirmed on current head, does not establish source-to-master completeness.
- #675 and #673 — Sandero Hybrid 155 configurator reporting/endpoint discovery; neither is a completed master-data import.
- #634 — old Draft Sandero residual full-modal import PR; do not rerun or treat as the current package without a fresh, current-main reconciliation.

Operational rule: before every continuation, inspect current main, recent merged PRs, open PR heads, and the canonical state. Do not repeat PR #752 source portfolio inventory, PR #767 page anchoring, or the same #754 crosswalk report. The next package must deliver a concrete, source-backed import batch or explicitly move to the highest-impact unblocked data gap for another model family. If no importable batch is possible, state the exact evidence boundary and switch scope; do not loop on a generic blocker.

## Deferred Bigster Brochure Continuation (paused 2026-11-06)

This work is paused under the cennik-only priority above. PR #782 is merged into `main` (merge commit `13c58b86d9652ff127516b1d45924b8ca66005b0`). The page-22 residual equipment import added 260 historical availability observations across 20 existing boolean attributes and 14 exact active source-linked configurations. Full Quality passed on Python 3.10, 3.13 and 3.14; Windows validation and the remaining PR checks passed. The temporary Bigster snapshot check was skipped by workflow design.

- Combined page-21/page-22 brochure equipment availability coverage: 557 observations (157 page 21, 400 page 22).
- Page-22 IDs: 10113–10399.
- The Hybrid 155-only cooled-console qualifier is preserved; composite/package and unsupported facts remain deferred.
- Do not repeat page 14–17 grade details, page 20 technical/RPM reconciliation, page 21 YouClip/equipment imports, or page 23 dimensions.

## Bigster MY26 Commercial Price Matrix (2026-11-05)

The 2026-10-01 and 2026-11-02 official Bigster MY26 price lists have now been reconciled for printed pages 4–5.

- Added two commercial items: metallic paint and two-tone body.
- Added 172 dated commercial item/configuration mappings: 86 from 2026-10-01 and 86 from 2026-11-02.
- Metallic paint: 3000 PLN → 3100 PLN; two-tone body: 1400 PLN → 1500 PLN.
- Other priced options/packages retain their published prices: 19-inch wheels 1200 PLN, panoramic roof 4300 PLN, powered tailgate 1300 PLN, Media Nav Live 2400 PLN, EASY 2700 PLN, PARKING 2200 PLN, WINTER 1200 PLN, WINTER PLUS 2300 PLN.
- Spare wheel price is recorded as 800 PLN in October and 900 PLN in November for Hybrid 155 only. Nonmatching powertrains are recorded as `unknown`, not `not_available`, so older generic prices are not presented as current.
- The legacy 215/70 R16 row labelled for mild hybrid 130 4x4 is not mapped to tribrid 150 4x4. The source's 135/80 R17 row is not projected from non-G mild hybrid 140 to mild hybrid-G 140.
- The October source PDF hash is verified against the archived repository file. The November source remains in the user's Library; its raw bytes could not be materialized, so no SHA-256 is asserted.
- The 2026-11-02 price-list page-6 technical table states its data are current as of 01.10.2026. The matching 2026-10-01 source has 22 specifications and 150 observations, including the three Tribrid 150 engine_power rows (103 kW, IDs 8231–8233; PR #778). Do not duplicate. Next: resolve page-22 semantic/identity gaps and page-19 accessory-to-catalog links in the 24-page brochure.

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


## Quality-guardrail closure — 2026-11-24

The Project Owner’s temporary block on model-data assimilation is technically satisfied. PRs #879–#889 are merged to `main`. The closure covers portfolio-wide and transitive report regression checks, explicit analytical-report dependency declarations and input closure, fail-closed historical effective-date/future-source rules, source/master-data change-impact matrices, trusted read-only canonical baseline repair with an explicit six-file allowlist, and import-time source archive path/SHA-256 verification. All six required checks passed on the exact heads of the safeguard PRs; after PR #889, the push-triggered Quality and Repository Baselines workflows also passed on main commit `f44544a0038173d9789db137c69bd0d552a66734`.

The next package is unblocked in principle: Striker MY26 priced options and packages, using only the archived official Polish price list and preserving every P/package marker and unresolved applicability. No model-data assimilation has started in this closure step. Canonical counters and generated state documentation must still be refreshed through the trusted Baseline Repair workflow before the next package begins.

## Verified Quality Baseline

<!-- dkb:documentation-baseline:session:start -->
- 2055 testów automatycznych zakończonych powodzeniem,
- 48 pliki CSV w `data/master`,
- 23490 rekordów danych,
- 51 relacje między tabelami,
- 27 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 8953 obserwacji w `configuration_attribute_values.csv`,
- 235 wersjonowanych specyfikacji w `data/imports/configuration_values`,
- 472 obserwacji w `configuration_attribute_value_ranges.csv`,
- 28 wersjonowanych specyfikacji w `data/imports/configuration_value_ranges`,
- 10399 rekordów w `configuration_attribute_availability.csv`,
- 8382 rekordów `standard`, 704 `optional`, 1313 `not_available` i 0 `unknown`,
- 417 kanonicznych atrybutów w 30 kategoriach,
- baza SQLite obejmująca 48 tabele i 23490 rekordów,
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


## Bigster MY26 Catalogue Price History (2026-11-12)

The new bounded report compares the 13 exact canonical configurations priced in both official Polish Bigster MY26 cenniks dated 2026-10-01 and 2026-11-02. All 13 prices are unchanged. The report is derived from existing master observations and the source registry; it does not add duplicate master price rows. The 2026-07-03 source is not used as the direct baseline because several engine/configuration identifiers were subsequently renamed or restructured; no cross-identifier equivalence is inferred.

The 2026-11-02 Bigster source has a verified SHA-256 in the source registry, but its raw PDF remains outside the repository archive. Promotions, financing, leasing, accessories and dealer offers are excluded. Striker is explicitly deferred while its cennik is unavailable. The next planned work is a cross-model residual coverage review of official Polish cenniks only; brochures and configurator sources remain out of scope.

## PDF Extraction Toolchain Regression (2026-11-12)

PR #804 exposed a non-deterministic CI environment: the committed official PDF candidate ledger was generated with Poppler 24.02.0, while the moving `ubuntu-latest` runner supplied Poppler 26.01.0. The resulting candidate JSON/Markdown differed even though the registered source PDFs and their hashes were unchanged. This was an environment/toolchain mismatch, not a Bigster price-history defect.

The corrective changes in the PR:
- pin the Linux quality matrix to `ubuntu-24.04`;
- verify both `pdftotext` and `pdfinfo` are version 24.02.0 before the PDF quality check;
- make the candidate-ledger generator reject a different `pdftotext` version rather than silently creating a different canonical artifact;
- make the existing repository-artifact test report backend-version drift explicitly;
- record the permanent policy in `project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md`.

The PDF artifact test remains enabled. Do not update the committed candidate ledger to a newer Poppler version without a separately reviewed extraction-difference package. Re-run the full quality matrix on the exact final PR head before considering PR #804 ready or mergeable.


## PR #804 Follow-up — Historical PDF CI Contract Alignment (2026-11-12)

The first CI rerun after pinning Poppler exposed a stale assertion in the historical post-cross-model workspace review verifier. It required the former Quality workflow step name and therefore failed on Python 3.10, Python 3.13 and the Windows package-contract suite before the full Quality gate could run. This was a test-contract drift, not a PDF extraction or Bigster data failure. The verifier now requires the current step name and explicitly checks that both `pdftotext` and `pdfinfo` are pinned to 24.02.0. The checks remain strict; no test was removed or skipped. Re-run all required CI checks on the new exact PR head before considering the change ready.


## Cennik-only Follow-up — Bigster and Spring (2026-11-12)

- PR #804 merged: Bigster MY26 catalogue-price history compares 13 exact configurations between official Polish cenniks dated 2026-10-01 and 2026-11-02; all 13 prices are unchanged. The PR also pins the PDF extraction toolchain and aligns the historical review contract with the pinned CI step.
- Current cennik-only follow-up: Spring MY25 stock price list dated 2026-07-08. The exact 85,900 PLN Extreme Electric 100 catalogue-price cell on printed page 1 was missing from the source-linked master price observations; a bounded source-price observation and source-configuration link are proposed in PR #805.
- The 17,000 PLN dealer-stock promotion is not allocated to individual configurations. The 2026-07-08 MY25 stock value is not generalized to MY26. Existing 2026-07-31 configurator observation remains a distinct dated source.
- First PR #805 CI attempt caught a CSV quoting defect: the thousands separator in the source note had not been enclosed in quotes. The note was corrected; all controls must be re-run on the corrected final HEAD. The failure was not a data-value disagreement.


## D-017 — Fail-fast package data integrity gates (2026-11-12)

Added a dedicated package-preflight command and automated Quality workflow step. The command scans all repository CSV and JSON files under `data/`, reusing the strict canonical CSV validator and standard JSON parser. It catches malformed quoting, CSV column-count drift and invalid JSON before the full test matrix. CSV-producing code must use a standards-compliant serializer; dependent reports and generated documentation remain subject to their canonical generators and checks. The existing semantic repository validator, source-fidelity review and exact-HEAD CI remain mandatory.


## Cennik-only State Reconciliation — 2026-11-12

- PR #805 is merged (merge commit `8cf8bfc29345ea10e3742ce8708a4fc20181003c`); the Spring MY25 stock Extreme Electric 100 price gap is closed.
- PR #804's Bigster MY26 catalogue-price history and the existing Jogger MY26 2026-10-01 full-document reconciliation are already present in current `main`; neither is a valid next package.
- The canonical next package is now a cross-model residual coverage review of official Polish Dacia price lists only. It must reuse existing source-backed reconciliations, isolate exact remaining gaps, and avoid duplicate or historical re-imports.
- Brochures and configurator evidence remain deferred under the user's cennik-only priority.
- This is a state/documentation reconciliation only; no master data, source records, or baseline counters are changed.


## Duster MY26 Cennik Residual Review — 2026-11-12

The official Duster MY26 cennik effective 2026-11-02 was rechecked against the exact ten-page archived PDF and repository source inventory. Printed pages 2 and 7 were inspected: page 2 contains narrative technology/comfort claims; page 7 contains accessory descriptions and QR links but no priced configuration options. Page 8 is a separate complete-winter-wheel accessory list, page 9 contains the dimensions diagram, and page 10 contains legal/commercial terms. No configuration price or option import was identified on pages 2 or 7.

The first text-extraction pass incorrectly reported 280 V on page 6 and incorrectly claimed that the source hash was not registered. A later visual review of the exact archived ten-page PDF confirms that printed page 6 states 230 V for all three Hybrid 155 configurations, matching the 2026-09-01 technical table; printed page 2 separately states 260 V in narrative text. The registered source SHA-256 is `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`. No three 280 V observations are missing, no 280 V values should be imported, and existing 230 V master observations must not be overwritten. The JSON reconciliation report is correct; its stale Markdown companion is the remaining documentation defect selected for the next package.

No master data changed in this review. The exact gap and page inventory are recorded in `data/reporting/duster_price_list_20261102_commercial_reconciliation.json` and its Markdown companion. Brochures and configurator evidence remain out of scope.


## Jogger MY26 Cennik Commercial Matrix — 2026-11-14

- PR #814 merged: official Polish cennik cross-model residual review covers six source/date entries and identified the then-open Jogger commercial matrix gap, which is now closed by the package recorded below.
- Jogger package `jogger_price_list_20261001_commercial_matrix_import_20261114_001`: one special non-metallic paint item and 54 exact dated mappings imported from pages 3–4 (38 optional, 16 not_available) across 12 source-linked configurations.
- Existing 48 July 2026 Jogger commercial mappings and all catalogue price history remain unchanged. The 7-seat Eco-G 120 manual matrix remains Essential dash, Expression 86,550 PLN, Extreme 94,400 PLN.
- Extreme heated seats marked `P` are not mapped as a standalone option. The metallic paint 2,800/3,000 PLN pair remains deferred because no exact colour/grade mapping is established.
- The official PDF source row now uses the direct official asset URL; original PDF remains archived at `owner_supplied/2026-10-01/f5cdbd7878.pdf` with SHA-256 `12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46`.
- Next cennik-only package: capture and hash the live official Spring MY26 PDF as a distinct source version; preserve the owner-supplied MY25 Library PDF and do not import MY26 prices until the exact binary is archived.


## Spring MY26 Official Cennik Binary Intake — 2026-11-14

- PR #815 merged successfully; Jogger MY26 2026-10-01 commercial matrix is complete (1 item, 54 mappings; 38 optional, 16 not_available).
- The owner-supplied Library PDF `2e0588c888.pdf` remains MY25/effective 2026-03-03. The same live official CDN URL returns a different MY26 PDF/effective 2026-02-06. These are distinct content versions and must never overwrite one another.
- Current package `spring_my26_current_official_cennik_binary_intake_20261114_001` updates the existing Spring source-assimilation audit workflow to download and verify the live MY26 PDF, record its SHA-256, upload a short-lived audit artifact, and push the verified binary/manifest to a dedicated source branch.
- After binary capture, next package is the MY26 Spring price and commercial matrix import; the three price cells are Essential Electric 70 73,500 PLN, Expression Electric 70 81,500 PLN, Extreme Electric 100 85,900 PLN. The printed catalogue-price heading/footer and `Cena promocyjna` row labels must both be preserved.


## Spring MY26 Live Asset Identity Verification — 2026-11-14

- PR #816 merged and extended the source-audit workflow. Its first direct GitHub Actions download (run #43534970475) retrieved a 1.35 MB PDF but the extracted first page did not contain the expected `ROCZNIK 2026` marker. No PDF binary was committed.
- Do not assume the web-extracted MY26 PDF is the same content currently served to GitHub Actions. The CDN URL may resolve differently by cache/location, or text extraction may differ.
- PR #817 changes the workflow to always retain a diagnostic artifact, print the first-page text, page count, file size and SHA-256, compare the digest with the registered MY25 hash, and commit nothing unless the MY26 identity is verified.

## Next Cennik-only package — Duster MY26 Hybrid 155 voltage reconciliation

The Bigster MY26 2026-11-02 source archive is closed. The next cennik-only task is documentation consistency correction for the Duster MY26 2026-11-02 Hybrid 155 voltage evidence. The exact source SHA-256 is already registered as `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`; page 6 states 230 V for all three Hybrid 155 configurations and page 2 separately states 260 V in narrative text. The former 280 V reading was a text-extraction error. Do not import 280 V or overwrite 230 V; correct the stale Markdown report and align notes only.

## Single-maintainer Pull Request review policy — 2026-11-15

The project owner confirmed that independent approving GitHub reviews are not required for this single-maintainer repository. The AI maintainer must still perform a documented technical review of every PR before merge. The six required status checks remain mandatory on the exact current PR head: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, Generated documentation / documentation-baseline --check, and Repository state / project-state --check. Stale heads, conflicts, failed or missing checks, unresolved source evidence, and policy blocks continue to prevent merge. See D-026, AI_WORKING_AGREEMENT.md and AUTONOMOUS_MAINTAINER.md.

## Duster MY26 2026-11-02 voltage evidence correction — 2026-11-15

A later visual review of the archived ten-page official PDF and the completed Duster commercial-reconciliation package supersedes the earlier 280 V statement above. Printed page 6 states 230 V for all three Hybrid 155 configurations, matching the 2026-09-01 technical table; printed page 2 separately states 260 V in narrative text. The earlier 280 V reading was a text-extraction error, and the claim that the registered source lacked a SHA-256 was stale: the source register records SHA-256 `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`. No 280 V observations should be imported, and no existing 230 V observation should be overwritten. A follow-up documentation-consistency package is planned to correct the stale Markdown reconciliation report and align all remaining notes.


## Duster MY26 Hybrid 155 voltage evidence correction — 2026-11-15

The Duster MY26 2026-11-02 Markdown reconciliation report has been corrected in the current documentation package. The exact archived ten-page official PDF is registered at SHA-256 `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`. Visual inspection confirms printed page 6 states 230 V for all three Hybrid 155 configurations, matching the 2026-09-01 technical table; printed page 2 separately states 260 V in narrative text. The earlier 280 V reading was a text-extraction error. The Markdown report now has the correct 10-page inventory (page 9 dimensions; page 10 legal/commercial terms) and no longer proposes a 280 V import. The JSON reconciliation report and master data were already correct and remain unchanged. No voltage observation was imported, modified or overwritten.


## Duster MY26 Voltage Evidence Correction — PR #830 merged (2026-11-15)

PR #830 is merged in current `main` (merge commit `0ad4a78c9d051116f20d288ef6cffaccb5e7f2ac`). All six mandatory exact-head checks passed on `fa5f25e766fda5e6a211bb35a1b6a99d428d36a4`. The Duster MY26 2026-11-02 Markdown reconciliation report now agrees with the archived ten-page PDF and the already-correct JSON report: printed page 6 states 230 V for all three Hybrid 155 configurations; printed page 2 separately states 260 V in narrative text. The earlier 280 V reading was a text-extraction error. No master data, source registry records, or voltage observations changed. This closure supersedes the earlier planned Duster documentation-correction handoff.

## Next Cennik-only Package — Spring MY26 Price and Commercial Matrix

The next package is `spring_my26_price_and_commercial_matrix_import_20261115_001`. The exact seven-page Dacia-branded MY26 price list hosted by PGD is archived at `PDF/Cenniki/DACIA SPRING cennik MY26 20260206.pdf`, source `src_pl_spring_price_my26_20260206`, SHA-256 `ab36fba1106ca4929c42330df7896cea8fe56e8774353f6cbb5a7a94cfc18055`. Its full page review is complete. Import scope is limited to the three exact price cells and explicit page-3/page-4 commercial mappings. Preserve the catalogue-price header/footer versus “Cena promocyjna” row-label ambiguity, keep MY26 distinct from MY25 stock and existing dated configurator observations, and retain the page-2/page-5 technical conflict without importing technical or dimension values. Reuse the three exact existing Spring configurations; do not infer grade applicability or duplicate historical rows.


## Unified package consistency gate — 2026-11-16

D-027 adds a fail-closed sequence to the existing required `Repository state / project-state --check` status context. For every PR it now runs, on the same candidate commit: (1) `package-preflight` for CSV/JSON and source-capture manifest integrity, (2) `project-state --check` for canonical counters, references and generated state summary, and (3) `documentation-baseline --check` for managed documentation. The CI gate is read-only; corrections must use canonical generators and all three checks must be rerun after the final edit. The separately required generated-documentation status and all six existing required status names remain unchanged. See D-027, `project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md`, `project/AUTONOMOUS_MAINTAINER.md` and `project/AI_WORKING_AGREEMENT.md`.


## Spring MY26 price and commercial matrix — PR #832 merged (2026-11-16)

PR #832 was merged into `main` with squash commit `d48a22262d5127108bd139474a8905011a849343`. The archived seven-page Dacia-branded PGD-hosted Spring MY26 price list (source `src_pl_spring_price_my26_20260206`, SHA-256 `ab36fba1106ca4929c42330df7896cea8fe56e8774353f6cbb5a7a94cfc18055`) was independently checked against the imported values and grade applicability. All three page-1 prices and all ten priced page-3/page-4 commercial mappings matched the rendered source. The page-1 catalogue-price header/footer versus “Cena promocyjna” row-label ambiguity remains explicit; the Extreme DC 40 kW “P” cell was not interpreted; the page-2 narrative/page-5 technical conflict remains unresolved and no technical values were imported.

The importer verifies the archived PDF SHA-256, exact configuration/grade scope, uniqueness and master/specification consistency. The six mandatory exact-head CI checks passed on PR head `01788e61bd104232e77001af901f938712ac00bc`; source-fidelity review also passed. No independent approval was available or required under D-026. PR #832 is closed and merged.

Post-merge master baseline: 48 CSV files, 22,791 master rows, 8,492 configuration values, 189 configuration import specifications, 451 value ranges, 25 range import specifications, 10,399 availability records, 417 attributes and 30 attribute categories; test baseline 1,988. The canonical state and generated summary are synchronized in the follow-up state-closure package.

Next: audit current registered Polish MY26 price lists against master price and commercial mappings, keeping the owner's cennik-first priority. Brochures remain deferred; do not use configurator inference to fill price-list gaps.

## Sandero Eco-G 120 Fuel Capacity — PR #845 merged; state closure (2026-11-19)

PR #845 was merged into `main` with squash commit `4cd0d14be0665dce393889d673ad64c615d85147`. It imported 18 source-backed fuel-tank-capacity observations from the official 2026-11-02 Sandero/Sandero Stepway cennik page 5: petrol 50 L and LPG 40 L across nine exact Eco-G 120 configurations. The existing `fuel_tank_capacity` attribute and explicit `fuel_type_code` are used. Older undifferentiated observations remain unchanged; the source does not distinguish total LPG vessel capacity from filling capacity, so no such classification was inferred.

The PR updated the live baseline to 1,994 tests, 48 master CSV files, 22,809 rows, 8,510 configuration values and 190 import specifications, but did not transition `current_package` / `next_package`. The follow-up state-closure PR synchronizes `project/state.json` and the generated `project/STATE_SUMMARY.md`: Sandero Eco-G 120 is recorded as complete with PR #845 and its exact merge commit. The next cennik-only package is a bounded residual coverage assessment of technical/equipment values in the latest official Polish MY26 price lists. The five-model catalogue-price/commercial-matrix audit found no confirmed missing current price or commercial mapping records. Brochures and configurator inference remain deferred.

The post-merge Quality workflow for PR #846 is run #44417134605 on exact main commit `89f205ed4c214d56ca8d79fab218c6391679ba79`; at this checkpoint, Python 3.10, Python 3.13 and Windows have passed, while Python 3.14 is still running the full quality gate. Repository Baselines run #44417134619 completed successfully, including project-state and generated-documentation checks.

## Bigster MY26 2026-10-01 Cennik Equipment Evidence Note Synchronization — 2026-11-19

The official eight-page Bigster MY26 cennik effective 2026-10-01 is archived at `owner_supplied/2026-10-01/d477c604e8.pdf` with registered SHA-256 `0964b3a3311708698ef3cee6bd28244f76c1db36d0d9452e128e5113384dac97`. PR #733 imported 564 equipment-availability observations for six exact automatic configurations (94 attributes each). PR #758 later corrected the canonical source import specification's evidence notes, but the already-imported master rows were not synchronized.

A direct master/spec comparison found 538 exact rows and 26 note-only mismatches. All 564 rows, IDs 8720–9283, configuration/attribute keys, availability statuses, observation dates and source codes were already present and correct. This package updates only the 26 stale `notes` fields to the exact generated text from `data/imports/bigster_equipment_availability_20261001.csv`; no observation is added, removed or reclassified. Status distribution remains 465 standard, 46 optional and 53 not_available. A regression test checks the archived source hash and exact master/spec parity for all 564 rows.

This is a note-synchronization closure only. The full row-by-row PDF value comparison for pages 4–5 remains open, as do the 147 page-6 technical observations and page-7 paired-dimension mapping. Do not treat this package as approval to infer technical values or dimension semantics.

## Bigster MY26 2026-10-01 Equipment Evidence Note Synchronization — merged 2026-11-19

PR #849 was merged to main as `bafdfb20a5f4a029dfef2a1ce7d552c4bb86fbbf`. The package synchronized exactly 26 master evidence notes to the corrected canonical import specification for 564 existing page-4/5 equipment observations. All IDs 8720–9283, source codes, dates and availability statuses were preserved; no observations were re-imported. Six required checks passed on the exact PR head.

## Bigster MY26 2026-10-01 Cennik Equipment Matrix Reconciliation — PR #850 merged (2026-11-19)

The official archived eight-page cennik has SHA-256 `0964b3a3311708698ef3cee6bd28244f76c1db36d0d9452e128e5113384dac97`. Pages 4–5 were independently reviewed against the 564 existing observations (six exact configurations × 94 attributes). 93 attribute groups are consistent with the printed matrix. The HDC row remains unresolved: the grade-level matrix marks Expression, Extreme and Journey standard, while its qualifier says "wyłącznie dla wersji Extreme oraz 4x4". The source does not explicitly define whether that is a strict Extreme-4x4 conjunction or a union of Extreme grade and 4x4 drivetrain. Preserve the current six master statuses until this is clarified.

The existing 86 dated commercial mappings across 11 items were checked. Spare-wheel applicability remains unknown where the October source qualifier does not exactly match the registered configuration label; do not project the Hybrid 155 or older mild-hybrid 130 4x4 price to other powertrains.

Source-link drift was also detected: the registered CDN URL currently returns a PDF marked effective 2026-11-02, while a separate official Dacia CDN URL returns the 2026-10-01 edition. Do not replace the registered URL until the candidate binary is verified against the archived SHA-256. The archived PDF remains canonical.


PR #850 was merged to `main` as `07e3d38d678e9d5af75d089f9c3f6050257c672d`. The six mandatory exact-head checks passed: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, Repository state / project-state --check, and Generated documentation / documentation-baseline --check. The Temporary Bigster Repository Snapshot workflow was skipped and is not a required check.

The canonical state-closure follow-up records this package as complete with PR #850 and its exact merge commit. It selects `dacia_my26_cennik_residual_technical_coverage_assessment_20261119_001` as the next planned package: a bounded reconciliation of remaining technical/equipment gaps in the latest registered official Polish MY26 cenniks across Sandero/Sandero Stepway, Duster, Bigster, Jogger and Spring. Continue cennik-only; brochures and configurator inference remain deferred. No master data, source identity, HDC status or Bigster observation was changed by this state closure.

## Spring MY26 Dimension Diagram and DC 40 kW Package Marker Review — PR #870 merged (2026-11-21)

PR #870 was merged into `main` as `285cf33151a489dafdce53b45434b22ad76717e1` from exact reviewed head `7d3210639c5a6aa8cc3409b16aeab940c27d819c`. All six mandatory exact-head checks passed: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, Repository state / project-state --check, and Generated documentation / documentation-baseline --check.

The Spring MY26 2026-02-06 cennik review resolved the Extreme DC 40 kW P marker as part of the POWER package, not a standalone option. It added exactly two source-specific 155 mm ground-clearance observations for Expression Electric 70 and Extreme Electric 100. Essential remains explicitly `not_stated` because its 14-inch wheels do not meet the source's 15-inch qualifier. Other dimension callouts remain excluded where applicability or measurement semantics are not explicit. The source-scoped technical comparison logic ensures that a slot bound to one source is not treated as a missing observation for unrelated source editions.

Final baseline: 2,018 tests, 48 master CSV files, 22,857 master rows, 8,530 configuration values, 193 configuration import specifications, 451 value ranges, 25 range import specifications, 10,399 availability records, 417 attributes and 30 attribute categories.

## PR portfolio cleanup — 2026-11-21

PR #769 (Jogger page-21 reconciliation), #770 (recovered CSV headers) and #772 (Duster Mini availability plus Stepway ranges) were closed as superseded after exact Git blob comparisons confirmed that their substantive data/artifacts are already present on current `main`. No stale branches were merged and no remote branches were deleted. PR #754 and #634 remain drafts; PRs #673 and #675 retain unique historical configurator research and remain unmerged/deferred.

## Jogger MY26 2026-11-02 — source capture, archive and registration

PR #872 introduced the guarded source-capture workflow and was merged as `dc98fd015af7142a8e30644e0ff480415435dc76`. Post-merge workflow run #44948446147 captured the official nine-page PDF. PR #873 archived the PDF and SHA-256 sidecar and was merged as `1b1ff883d713a5aab4d182b9f7d0172425e1ba3c`. The source SHA-256 is `94324e97d00e825ed537b525052dacfc436b57984880585e087852411b65a5da`; file size 2,119,710 bytes. All 11 catalogue price cells match the 2026-10-01 edition, so no duplicate catalogue-price rows are added.

PR #874 registers the new source, 12 exact configuration links, three grade links and 12 dated special non-metallic paint mappings at 2,800 PLN. The metallic 2,800/3,000 PLN pair remains unmapped because the cennik gives no exact colour/configuration crosswalk. The old 2026-10-01 mapping remains unchanged pending visual re-verification: archived PDF text extraction returns 2,700/2,900 PLN, conflicting with the prior visual review and current master mapping at 2,800/3,000 PLN. The archived page-3 image could not be retrieved through the Library reader in this session; classify the historical delta as `Do sprawdzenia`.

The old CDN URL ending in `f5cdbd7878.pdf` now resolves to the newer 02.11.2026 document. The archived binary and SHA-256 remain authoritative for the historical 01.10.2026 source. The source assimilation standard now explicitly guards against mutable external URLs.

Striker remains deferred until price-list reconciliation is complete for all model families already represented in the master data.


## Jogger MY26 2026-11-02 — source registration and paint reconciliation closed

PR #874 was merged into `main` as `6e6a73882c7e46d6993f177532b3c3e099ccbf30` from the exact reviewed head `f56a9b63279bdfaf270e11f0d472d12b10814ed4`. All six required checks passed on that head: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, generated documentation baseline and repository state.

The official nine-page Jogger MY26 cennik effective 2026-11-02 is archived and registered as `src_pl_jogger_price_my26_20261102`. Twelve exact configuration links and three grade links were added. The 12 special non-metallic paint mappings at 2,800 PLN were added using the existing commercial item. All 11 catalogue vehicle-price cells match the previous edition, so no duplicate catalogue price rows were created. No technical or equipment rows were added.

Two matters remain explicitly unresolved: the 2026-10-01 archived page-3 text extraction conflicts with the prior visual review/master mapping (2,700/2,900 PLN versus 2,800/3,000 PLN), so the historical mapping remains unchanged and the delta is `Do sprawdzenia` pending visual re-verification; the 2026-11-02 metallic-paint pair 2,800/3,000 PLN remains unmapped because the cennik does not provide an exact colour/configuration crosswalk.

The source assimilation standard now guards against mutable CDN URLs: archived binary and SHA-256, not the current response from a historical URL, define the source edition. Striker remains deferred until price-list reconciliation is complete for all model families already represented in the master data.

## Verified Cennik Residual Coverage Closure (2026-11-21)

The official Polish MY26 cennik reconciliation is complete for the five model families already represented in the master data: Sandero/Sandero Stepway, Duster, Jogger, Bigster and Spring.

The current assessment covers seven source/date entries, 75 source-configuration links (the Bigster 2026-11-02 price/commercial-only source intentionally has zero configuration links), 82 catalogue price cells, 55 source-specific price rows, 521 commercial mappings, 281 technical scalar observations and 591 equipment-availability observations.

The Duster page-9 review added 18 exact 4x2/4x4 dimension observations. The Spring review added two 155 mm ground-clearance observations for the two exact 15-inch-wheel configurations and resolved the Extreme DC 40 kW P marker as part of the POWER package. The Jogger 2026-11-02 source is registered and adds 12 special non-metallic paint mappings without duplicating its 11 unchanged catalogue prices.

No additional technical/equipment facts are both missing and safely importable from the reviewed cenniks. Remaining evidence boundaries are preserved: Sandero Eco-G injection/LPG semantics and interior/trim meanings; Duster interior/seat callouts; Jogger historical 2026-10-01 paint amount and metallic-paint applicability; Bigster HDC applicability and extra dimensions; Spring power/battery conflict and ambiguous dimension callouts. Do not infer missing values or reopen resolved mappings without new source evidence.

Historical note superseded on 2026-11-21: after all five existing model families' cennik reconciliation was closed, the Project Owner explicitly approved Striker and supplied the official MY26 cennik effective 2026-11-02. PR #877 registers the exact PDF/source and model family; price/configuration imports remain separate follow-up packages.

## Next scope — Striker (owner approval required)

The Striker source-registration/model-family package is active in PR #877 following explicit owner approval. The exact 2026-11-02 official PDF is archived and SHA-256 verified; its 11 catalogue price cells are identified. No Striker price observations or configurations have yet been imported.


## Striker MY26 priced options and packages — PR #892 merged (2026-11-24)

PR #892 was merged into `main` as squash commit `6682f2323fcb1a7650c61a4848aa7f078a247635`. The exact post-merge Quality workflow run #45467006201 passed on main: Python 3.10, Python 3.13, Python 3.14 and Package workflow / Windows. Repository Baselines run #45467006375 also passed: generated documentation baseline and canonical project-state check. All six required checks are green.

The official Polish Striker MY26 cennik effective 2026-11-02 is archived at `PDF/Cenniki/striker-price.pdf`, SHA-256 `d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35`, size 1,615,585 bytes, eight pages. PR #892 imported the 11 printed option/package rows on page 5 as 11 commercial items and 121 dated grade/configuration mappings across the 11 exact source-linked configurations: 60 optional, three standard, 51 explicit dashes (`not_available`) and seven literal `P` markers (`unknown`). The heated washer nozzles/windscreen P marker remains unresolved; no standalone price or package membership was inferred. Package descriptions remain source labels/notes and were not expanded into equipment attributes.

The canonical state now records this package as complete. The next cennik-only package is `striker_my26_p_marker_and_package_composition_evidence_review_20261124_001`: inspect the same archived cennik's legends, notes and cross-references for explicit definitions of P and package contents. Do not infer unresolved applicability and do not use brochure or configurator sources.


## Striker MY26 P Marker and Package Composition Evidence Review — complete (2026-11-24)

The review of all eight pages of the archived official Polish Striker MY26 cennik effective 2026-11-02 is complete. The page-5 descriptions explicitly state the components of six packages: Zimowy, Zimowy Plus, Techno, Techno 2, City and City 2. The page-4/5 equipment matrix separately confirms the panoramic roof as standard in Extreme and optional in Journey.

The literal `P` marker on the heated washer nozzles/windscreen row is not defined by any legend, footnote, note or cross-reference in this cennik. All seven existing P mappings remain `unknown`; no package membership, standard/optional status or standalone price was inferred. Package descriptions were documented, but no component-level equipment observations or other master-data rows were created.

Durable receipts:
- `data/reporting/striker_my26_p_marker_and_package_composition_evidence_review_20261124_001.json`
- `project/reviews/striker-my26-p-marker-and-package-composition-evidence-review-2026-11-24.md`

No master data changed. Next: review the Spring MY26 2026-02-06 dimension diagram and Extreme DC 40 kW P marker against current master data, using only the cennik and preserving unresolved evidence.

## Next-package correction after Striker evidence review — 2026-11-24

The next-package pointer written after PR #894 incorrectly selected the Spring MY26 dimension diagram and DC 40 kW P-marker review. That work was already completed in PR #870 (squash merge `285cf33151a489dafdce53b45434b22ad76717e1`): the Extreme DC 40 kW P cells were identified as POWER-package components, and two source-specific 155 mm ground-clearance observations were added for Expression Electric 70 and Extreme Electric 100. Do not repeat that package.

The Striker MY26 page-1 catalogue prices are already imported in PR #878 (11 dated rows across 11 exact configurations). PR #892 completed the page-5 commercial matrix (11 items and 121 mappings), and PR #894 completed the P-marker/package-composition review. The seven P mappings remain unknown; the six package descriptions remain documented without inferred equipment-component rows.

The corrected next package is `striker_my26_technical_equipment_residual_review_20261124_001`: review only the remaining technical, equipment and dimension evidence in the archived official Striker MY26 cennik against current master data. Exclude completed page-1 prices, page-5 priced options/packages, and the P/package-composition review. Use only the cennik; preserve unresolved applicability and source conflicts. No master data changes are made by this planning correction.


## Striker MY26 matrix symbol clarification — 2026-11-24

The Project Owner explicitly defined the Striker MY26 2026-11-02 matrix symbols under D-035: `●` = standard, `-` = not available, `o` = paid option, and `P` = package. This owner-supplied interpretation supersedes the provisional P-as-unknown handling described in PR #894. The seven P mappings for the heated washer nozzles/windscreen commercial item are now `package`, not `unknown`; their amounts remain empty and the specific package identity remains unspecified. The three Journey rows remain paid optional at 1,000 PLN and Essential remains unavailable. The shared status enum, importer, import specification, master data, regression tests and successor evidence report are updated. No package-component equipment attributes are inferred. The next package remains the Striker MY26 remaining technical/equipment/dimension evidence review.


## Striker MY26 Technical Data and Dimension Import — 2026-11-24

The official Polish MY26 cennik dated 2026-11-02 has now been reviewed on printed pages 6–7. The package adds 423 scalar observations and 21 bounded ranges across the 11 exact source-linked configurations, backed by 42 scalar and 3 range import specifications. Page-6 text evidence and the archived PDF SHA-256 are verified; page 7 is a vector-only dimension diagram, so its text-layer check is skipped while binary identity remains mandatory. Petrol/LPG splits and range semantics are preserved. Hybrid 155 CO2 `95/96`, minimum running-order mass semantics, maximum folded-seat luggage volume, trim-level tyre fitment, 1000 m standing-start time and unexplained interior measurements remain explicitly excluded or unresolved. No price, commercial mapping, equipment-availability, configuration or attribute rows were changed.

## Automated report dependency impact and publication safeguards — PR #905 merged (2026-11-25)

PR #905 was merged to `main` as `f983db5e86b3df8567ca5e00c5d3eb0bf7a3fafe`.

- Added `python tools/dkb.py report-impact --base-ref <target-ref> --head-ref HEAD` to identify direct and transitive registered analytical-report consumers of changed inputs and upstream reports.
- The Quality workflow runs the new report-impact gate on the exact PR head before report-freshness validation. Affected current reports must be refreshed as matching JSON/Markdown outputs or explicitly remain `needs_review`; the existing fingerprint and dependency-freshness gate remains independent.
- Added regression coverage for direct and transitive impacts and the `needs_review` disposition without changing the generated test-count baseline.
- Codified the automated publication controls in `project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md` and `project/AUTONOMOUS_MAINTAINER.md`: change-impact matrix, data/package preflight, canonical state transition, generated documentation, exact-head freshness, package allowlists, duplicate-work review and failure classification.
- Required PR checks passed on the exact tested head: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, Generated documentation / documentation-baseline --check, and Repository state / project-state --check.
- The merge did not alter master data, source evidence, package selection or canonical baseline counters. The current Dacia source-assimilation package remains governed by `project/state.json`.

## Official Bigster Brochure Full Assimilation — package candidate (2026-11-25)

The 24-page Polish Bigster brochure dated 2025-12-10 was reviewed in full against rendered pages, extracted text, the archived PDF identity and existing source-linked master observations. The package records six page-14 colour palette items and their finish/two-tone labels without inventing grade applicability or paint prices, adds the page-19 roof-rack/panoramic-roof incompatibility note, and reconciles page-20 payload values against the later 2026-07-03 cennik. Ten identical payload observations are not duplicated; four 2025 mild-hybrid-G 140 ranges remain as dated historical observations alongside the later 451/540 kg values.

Existing source coverage was reconciled: 14 active source-linked configurations, 458 scalar observations, 557 equipment-availability observations, 34 source-specific ranges, 68 cargo-context values, 56 grade-detail scalar observations and 126 exterior-dimension observations. Explicit unresolved items remain in the deferral ledger; no configurator evidence or unsupported cross-configuration projection was used.

The candidate adds six commercial items and six exterior-colour attributes only. The Sandero/Stepway catalogue-price history report is explicitly marked needs_review because the shared sources.csv file changed; its original input fingerprints are preserved rather than silently rebased. Both report outputs are updated together.

