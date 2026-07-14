# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety Sandero i Sandero Stepway zintegrowane przez
Pull Requesty #3–#32. Aktualny punkt odniesienia to merge commit
`26b0a312`.

PR #32 zaimportował siedem datowanych wartości
`noise_level_at_50_kmh = 67`. GitHub Actions Quality run #93 zakończył
się powodzeniem.

Bieżący pakiet analityczny jest rozwijany na gałęzi
`analysis/sandero-remaining-technical-value-candidate-review`.

## Verified Quality Baseline

Zweryfikowany lokalnie wynik docelowy bieżącego pakietu:

```bash
python tools/dkb.py quality
```

- 249 testów automatycznych zakończonych powodzeniem,
- 34 pliki CSV w `data/master`,
- 1300 rekordów danych,
- 34 relacje między tabelami,
- 19 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 232 obserwacje w `configuration_attribute_values.csv`,
- 419 rekordów w `configuration_attribute_availability.csv`,
- 389 rekordów `standard` i 30 rekordów `not_available`,
- 349 kanonicznych atrybutów w 30 kategoriach,
- baza SQLite obejmująca 34 tabele i 1300 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Sandero Remaining Technical Value Candidate Review.

Zakres:

- weryfikacja siedmiu PDF przez SHA-256,
- porównanie z 232 wartościami konfiguracji, 419 rekordami dostępności i 7 cenami,
- klasyfikacja 1371 wystąpień kandydatów i 1010 niedopasowanych wystąpień,
- odrzucenie nagłówków, tekstu marketingowego, fragmentów tabel, wyposażenia i faktów już zaimportowanych pod innym brzmieniem,
- potwierdzenie wspólnego pola `Rodzaj Napędu przedni` na stronie 5,
- potwierdzenie aktywnego atrybutu enum `drive_type` i aktywnej wartości `fwd`,
- wybór osobnego małego importu bez zmian danych w bieżącym pakiecie.

## Current Phase

Aktualna faza to **Data Expansion**.

Model pozostaje na poziomie 232 datowanych wartości konfiguracji i 419 rekordów
dostępności wyposażenia. Raport pomocniczy wskazał 1371 wystąpień kandydatów,
z których 1010 nie dopasowało się tekstowo do proweniencji, a 62 podpisy
wystąpiły we wszystkich siedmiu źródłach.

Ręczna kontrola wykazała, że większość wyników to inne brzmienia już
zaimportowanych parametrów, wyposażenie, nagłówki, stopki i fragmenty tabel.
Obecne rekordy obejmują między innymi zbiornik paliwa, pojemność silnika,
cylindry, miejsca, biegi, prędkość maksymalną, średnicę zawracania, masy,
wymiary, pojemność bagażnika, WLTP, koła, tapicerkę, kolor, drzwi, normę
emisji i poziom hałasu przy 50 km/h.

Wszystkie siedem źródeł podaje na stronie 5 w sekcji `Układ napędowy` wartość
`Rodzaj Napędu przedni`. Katalog zawiera aktywny atrybut enum `drive_type`,
a słownik `drive_types.csv` zawiera aktywną wartość `fwd`. Tabela wartości
konfiguracji nie zawiera jeszcze `drive_type`. Nie jest potrzebna zmiana
schematu ani nowa decyzja architektoniczna.

Ogólniejsze atrybuty string `drive_layout` i `drivetrain_type` nie powinny
duplikować dokładnej wartości kontrolowanej. Kandydaci wymagający nowego modelu,
na przykład maksymalna ładowność, całkowita liczba zaworów oraz moc i moment z
kontekstem paliwa i zakresem obrotów, pozostają do późniejszych pakietów.

## Next Development Package

Sandero Front-Wheel Drive Value Import.

Planowany przebieg:

1. Zaimportować `drive_type = fwd` dla siedmiu konfiguracji.
2. Użyć istniejącego aktywnego atrybutu enum i kontrolowanej wartości.
3. Zachować datę, źródło, stronę 5, sekcję `Układ napędowy` i pełne brzmienie.
4. Pozostawić kontekst paliwa pusty.
5. Nie tworzyć wartości `drive_layout` ani `drivetrain_type`.
6. Nie zmieniać schematu, dostępności wyposażenia ani cen konfiguracji.
7. Dodać testy regresyjne i zakończyć pakiet pełną kontrolą jakości.

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

Completed:

- PR #24 zweryfikował siedem PDF przez SHA-256,
- dodano kategorię `Exterior` i atrybut `exterior_color`,
- zaimportowano 7 wartości `biel alpejska`,
- zachowano stronę, sekcję, źródłowe brzmienie i zapis `0 zł`,
- nie zmieniono dostępności wyposażenia ani cen konfiguracji,
- dodano osiem testów regresyjnych,
- GitHub Actions Quality run #76 zakończył się powodzeniem.

### Sandero Remaining PDF Value Gap Analysis

Completed:

- PR #25 zweryfikował siedem źródeł,
- porównano 204 wartości i 419 rekordów dostępności,
- potwierdzono wspólne pole `Opony Standardowe 205/60 R16 92H`,
- odrzucono nieuzasadnione przypisanie do osi i wartości maksymalnych,
- zaakceptowano decyzję D-018,
- nie zmieniono danych ani schematu,
- GitHub Actions Quality run #78 zakończył się powodzeniem.

### Sandero Standard Tyre Specification Import

Completed:

- PR #26 zweryfikował siedem PDF przez SHA-256,
- dodano `standard_tyre_specification`,
- zaimportowano 7 wartości `205/60 R16 92H`,
- zachowano stronę 5, sekcję i pełne źródłowe brzmienie,
- nie zmieniono dostępności wyposażenia ani cen konfiguracji,
- dodano dziewięć testów regresyjnych,
- test koloru ograniczono do własnego pakietu zamiast globalnego rozmiaru tabeli,
- GitHub Actions Quality run #81 zakończył się powodzeniem.

### Sandero Remaining PDF Value Gap Reassessment

Completed:

- PR #27 zweryfikował siedem PDF przez SHA-256,
- porównano 211 wartości, 419 rekordów dostępności i 7 cen,
- przeanalizowano raport kandydatów oraz odrzucono fałszywie dodatnie luki,
- potwierdzono `Liczba Drzwi 5` na stronie 5 we wszystkich źródłach,
- potwierdzono aktywny atrybut `number_of_doors` i brak odpowiadających rekordów,
- wybrano osobny import bez zmian danych ani schematu,
- GitHub Actions Quality run #83 zakończył się powodzeniem.

### Sandero Number of Doors Value Import

Completed:

- PR #28 zweryfikował siedem PDF przez SHA-256,
- zaimportowano 7 wartości `number_of_doors = 5`,
- zachowano stronę 5, sekcję `Typ nadwozia` i pełne brzmienie źródła,
- użyto istniejącego atrybutu integer bez zmiany schematu,
- nie zmieniono dostępności wyposażenia ani cen konfiguracji,
- dodano osiem testów regresyjnych,
- GitHub Actions Quality run #85 zakończył się powodzeniem.

### Sandero Euro 6e BIS Emission Standard Modeling

Completed:

- PR #29 zweryfikował siedem PDF przez SHA-256,
- potwierdzono `Norma Emisji Spalin Euro 6e BIS` na stronie 6,
- dodano kontrolowaną wartość `euro_6e_bis`,
- zachowano odrębność od `euro_6e`,
- zaakceptowano decyzję D-019,
- nie zaimportowano wartości konfiguracji,
- dodano siedem testów regresyjnych,
- GitHub Actions Quality run #87 zakończył się powodzeniem.

### Sandero Euro 6e BIS Emission Standard Value Import

Completed:

- PR #30 zweryfikował siedem PDF przez SHA-256,
- zaimportowano 7 wartości `emission_standard = euro_6e_bis`,
- zachowano datę, stronę 6 i dokładne brzmienie źródła,
- nie użyto ogólniejszej wartości `euro_6e`,
- nie zmieniono dostępności wyposażenia ani cen konfiguracji,
- pozostawiono poziom hałasu 67 dB poza pakietem,
- dodano osiem testów regresyjnych,
- GitHub Actions Quality run #89 zakończył się powodzeniem.

### Sandero 50 km/h Noise Level Modeling

Completed:

- PR #31 zweryfikował siedem PDF przez SHA-256,
- potwierdzono `Poziom Hałasu Przy 50 Km/H (DB) 67`,
- dodano kategorię `Acoustics` i jednostkę `dB`,
- dodano atrybut decimal `noise_level_at_50_kmh`,
- zachowano warunek pomiaru przy 50 km/h,
- nie przyjęto niepotwierdzonej lokalizacji ani procedury pomiaru,
- nie zaimportowano wartości konfiguracji,
- dodano siedem testów regresyjnych,
- GitHub Actions Quality run #91 zakończył się powodzeniem.

### Sandero 50 km/h Noise Level Value Import

Completed:

- PR #32 zweryfikował siedem PDF przez SHA-256,
- zaimportowano 7 wartości `noise_level_at_50_kmh = 67`,
- zachowano datę, stronę 6 i dokładne brzmienie źródła,
- pozostawiono kontekst paliwa pusty,
- nie utworzono wartości ogólnego, wewnętrznego ani zewnętrznego hałasu,
- nie zmieniono dostępności wyposażenia ani cen konfiguracji,
- zaktualizowano trwałą granicę model/import,
- dodano osiem testów regresyjnych,
- GitHub Actions Quality run #93 zakończył się powodzeniem.

### Sandero Remaining Technical Value Candidate Review

Current package:

- zweryfikowano siedem PDF przez SHA-256,
- porównano 232 wartości, 419 rekordów dostępności i 7 cen,
- sklasyfikowano 1371 wystąpień kandydatów i odrzucono fałszywie dodatnie luki,
- potwierdzono `Rodzaj Napędu przedni` na stronie 5 we wszystkich źródłach,
- potwierdzono aktywny enum `drive_type`, wartość `fwd` i brak odpowiadających rekordów,
- zachowano granicę względem `drive_layout` i `drivetrain_type`,
- wybrano osobny import bez zmian danych ani schematu.

Next priority:

Kontrolowany import `drive_type = fwd` dla siedmiu konfiguracji.
