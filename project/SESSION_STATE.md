# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety Sandero i Sandero Stepway zintegrowane przez
Pull Requesty #3–#23. Aktualny punkt odniesienia to merge commit
`431e4fb9`.

PR #23 zaakceptował decyzję D-017, potwierdził brak źródłowych pakietów
handlowych i odroczył dedykowany model do czasu uzyskania właściwych danych.
GitHub Actions Quality run #74 zakończył się powodzeniem.

Bieżący pakiet źródłowy jest rozwijany na gałęzi
`data/sandero-exterior-colour-values`.

## Verified Quality Baseline

Zweryfikowany lokalnie wynik docelowy bieżącego pakietu:

```bash
python tools/dkb.py quality
```

- 202 testy automatyczne zakończone powodzeniem,
- 34 pliki CSV w `data/master`,
- 1267 rekordów danych,
- 34 relacje między tabelami,
- 19 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 204 obserwacje w `configuration_attribute_values.csv`,
- 419 rekordów w `configuration_attribute_availability.csv`,
- 389 rekordów `standard` i 30 rekordów `not_available`,
- 347 kanonicznych atrybutów w 29 kategoriach,
- baza SQLite obejmująca 34 tabele i 1267 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Sandero Exterior Colour Value Import.

Zakres:

- weryfikacja siedmiu PDF przez SHA-256,
- dodanie kategorii `Exterior`,
- dodanie atrybutu string `exterior_color`,
- import siedmiu datowanych wartości `biel alpejska`,
- zachowanie strony 2, sekcji `Kolor` i zapisu `0 zł` w `notes`,
- brak zmian w dostępności wyposażenia i cenach konfiguracji,
- osiem nowych testów regresyjnych.

## Current Phase

Aktualna faza to **Data Expansion**.

Po bieżącym imporcie model obejmuje 204 datowane wartości konfiguracji.
Siedem nowych rekordów przechowuje wybrany kolor nadwozia `biel alpejska`
jako wartość string powiązaną z konfiguracją, datą i dokumentem źródłowym.

Zapis `0 zł` pozostaje wyłącznie w `notes`, ponieważ źródło przedstawia go
jako część podsumowania wybranego składnika. Nie jest to samodzielna wartość
koloru, rekord opcji ani cena składnika w istniejącym modelu.

Dostępność wyposażenia pozostaje bez zmian: 419 rekordów, w tym 389
`standard` i 30 `not_available`.

## Next Development Package

Sandero Remaining PDF Value Gap Analysis.

Planowany przebieg:

1. Porównać siedem PDF z aktualnymi 204 wartościami konfiguracji.
2. Porównać źródła z 419 rekordami dostępności wyposażenia.
3. Wskazać jednoznaczne fakty, które nadal nie mają rekordów.
4. Użyć istniejącego modelu wszędzie, gdzie zachowuje znaczenie źródła.
5. Wybrać jeden mały następny pakiet bez zgadywania danych.

## Working Mode

Projekt jest rozwijany w małych, kontrolowanych pakietach.

Każdy pakiet:

- rozpoczyna się od sprawdzenia gałęzi i czystości katalogu roboczego,
- obejmuje wyłącznie pliki związane z bieżącym zadaniem,
- jest przeglądany przed commitem,
- przechodzi odpowiednie testy lub pełną bramkę `quality`,
- kończy się aktualizacją dokumentacji tylko wtedy, gdy zmienia stan projektu.

Git Bash służy do generowania zmian, testów i kontroli stanu. Git GUI
może służyć do przeglądania różnic, stagingu, commitów i pushowania.

Powtarzalne kontrole pakietu są dostępne przez `package-start`,
`package-review` i `package-finish`. Commit, push, utworzenie Pull Requestu
oraz merge pozostają operacjami jawnymi.

## Project Rules

- `data/master` zawiera źródłowe dane projektu.
- Raporty, eksporty wyszukiwania i lokalne bazy SQLite są artefaktami generowanymi.
- Dane handlowe i techniczne muszą mieć datę i źródło.
- Nie należy zgadywać brakujących parametrów technicznych.
- Nie należy ponownie projektować stabilnej architektury bez wyraźnej potrzeby.
- Nie należy deklarować powodzenia CI bez sprawdzenia wyniku.
- `ROADMAP.md` definiuje fazę i kierunek rozwoju.
- `SESSION_STATE.md` opisuje bieżący kontekst roboczy i musi pozostawać
  zgodny z roadmapą.

## Sprint History

### Sprint 001 — Repository Startup Alignment

Completed:

- poprawiono lokalizację roadmapy wskazywaną przez `START_HERE`,
- procedurę rozpoczęcia pracy dopasowano do rzeczywistej struktury repozytorium.

### Tooling and Data Quality Phase

Completed:

- zunifikowany CLI,
- rozbudowany walidator danych,
- normalizacja kodowania CSV,
- wyszukiwanie, statystyki i raporty,
- bezpieczna budowa i pełna weryfikacja SQLite,
- testy regresyjne,
- lokalna bramka `quality`,
- automatyczna kontrola jakości w GitHub Actions.

### Sandero Source-backed Baseline

Completed:

- PR #3: rejestr siedmiu dokumentów i powiązania z modelami,
- PR #4: pięć wersji oraz powiązania źródło–wersja,
- PR #5: siedem konfiguracji oraz powiązania źródło–konfiguracja,
- PR #6: waluta PLN i siedem datowanych obserwacji cen,
- PR #7: synchronizacja dokumentacji bazowego pakietu danych,
- rozszerzenie walidacji referencji i statusów dla nowych tabel.

### Sandero Source-backed Technical Data

Completed:

- PR #8: 35 podstawowych obserwacji technicznych i trzy nowe relacje,
- PR #9: 49 obserwacji osiągów, mas pojazdu i mas przyczep,
- PR #10: synchronizacja dokumentacji po pierwszych dwóch pakietach,
- PR #11: 35 obserwacji długości, szerokości, rozstawu osi i zwisów,
- PR #12: 21 obserwacji pojemności bagażnika i wariantu naprawczego,
- PR #13: synchronizacja dokumentacji po pakietach wymiarów i pojemności,
- PR #14: 28 obserwacji WLTP z jawnym kontekstem LPG i benzyny,
- opcjonalne `fuel_type_code` i decyzja D-014,
- PR #15: synchronizacja dokumentacji po pakietach technicznych i WLTP,
- 168 obserwacji technicznych dla siedmiu konfiguracji,
- pełna kontrola jakości: 149 testów, 32 pliki CSV, 762 rekordy,
  30 relacji oraz 32 tabele SQLite.

### Sandero PDF Source Coverage Analysis

Completed:

- PR #16: przeanalizowano siedem zarejestrowanych źródeł PDF,
- główne dane techniczne potwierdzono jako objęte wcześniejszymi pakietami,
- wyposażenie seryjne wskazano jako największą lukę,
- różnice manual–automatic potwierdziły poziom konfiguracji,
- zaakceptowano decyzję D-015,
- oddzielono implementację schematu od importu danych.

### Package Workflow Automation

Completed:

- PR #17: dodano `package-start`, `package-review` i `package-finish`,
- zachowano jawne commit, push, PR i merge,
- dodano testy workflow izolowane od konfiguracji Git i zakończeń linii,
- wymuszono UTF-8 dla procesów lokalnej bramki jakości na Windows,
- GitHub Actions Quality run #62 zakończył się powodzeniem.

### Equipment Availability Schema

Completed:

- PR #18: dodano kontrolowany słownik czterech statusów,
- dodano pusty schemat relacji zgodny z D-015,
- zadeklarowano cztery referencje i walidację statusów,
- dodano testy schematu oraz automatyczne pokrycie SQLite,
- GitHub Actions Quality run #64 zakończył się powodzeniem.

### Sandero Core Equipment Availability

Completed:

- PR #19: zweryfikowano siedem dokumentów PDF przez SHA-256,
- zaimportowano 300 rekordów dostępności dla siedmiu konfiguracji,
- wykorzystano 27 istniejących i 25 nowych atrybutów kanonicznych,
- zachowano 277 statusów `standard` i 23 jawne `not_available`,
- GitHub Actions Quality run #66 zakończył się powodzeniem.

### Sandero Passive Safety Availability

Completed:

- potwierdzono 17 jednoznacznych funkcji we wszystkich siedmiu PDF-ach,
- PR #20 zaimportował 119 rekordów: 112 `standard` i 7 `not_available`,
- zachowano źródłowe brzmienie i numer strony,
- nie zmieniono znaczenia pierwszych 300 obserwacji,
- koła i tapicerka pozostają poza zakresem.

### Sandero Wheel and Upholstery Value Modeling

Completed:

- PR #21 zaakceptował decyzję D-016,
- wskazano `configuration_attribute_values.csv` jako właściwą relację,
- rozdzielono rozmiar, materiał, wzór i wykończenie koła,
- zachowano tapicerkę jako wartość wariantu,
- konflikt ERALIA/TAMIA sklasyfikowano jako nierozstrzygnięty,
- import danych pozostawiono do osobnego pakietu.

### Sandero Wheel and Upholstery Value Import

Completed:

- PR #22 zweryfikował siedem PDF przez SHA-256,
- dodano `wheel_design` i `upholstery_variant`,
- zaimportowano 29 wartości dla siedmiu konfiguracji,
- zachowano proweniencję strony, sekcji i źródłowego brzmienia,
- Stepway Essential otrzymał wyłącznie wspólną wartość materiału `steel`,
- wzór ERALIA/TAMIA BI-TON i wykończenie pozostają celowo bez rekordu,
- GitHub Actions Quality run #72 zakończył się powodzeniem.

### Sandero Packages and Options Gap Analysis

Completed:

- PR #23 przejrzał komplet siedmiu bieżących źródeł,
- nie znaleziono nazwanej sekcji pakietów ani opcji handlowych,
- wyposażenie seryjne pozostało wyposażeniem, a nie pakietem,
- `Bez Opcji` sklasyfikowano jako kwalifikator technicznej masy,
- zaakceptowano decyzję D-017,
- GitHub Actions Quality run #74 zakończył się powodzeniem.

### Sandero Exterior Colour Value Import

Current package:

- zweryfikowano siedem PDF przez SHA-256,
- dodano kategorię `Exterior` i atrybut `exterior_color`,
- przygotowano 7 wartości `biel alpejska`,
- zachowano stronę, sekcję, źródłowe brzmienie i zapis `0 zł`,
- nie zmieniono dostępności wyposażenia ani cen konfiguracji,
- dodano osiem testów regresyjnych.

Next priority:

Analiza pozostałych luk wartości w siedmiu źródłach PDF i wybór jednego
następnego kontrolowanego pakietu.
