# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety Sandero i Sandero Stepway zintegrowane przez
Pull Requesty #3–#19. Aktualny punkt odniesienia to merge commit
`44fd33c`.

PR #19 zaimportował 300 źródłowych rekordów funkcjonalnego wyposażenia,
dodał 25 kanonicznych atrybutów oraz zachował proweniencję stron PDF.

Bieżący pakiet źródłowy jest rozwijany na gałęzi
`data/sandero-passive-safety-availability`.

## Verified Quality Baseline

Zweryfikowany lokalnie punkt odniesienia dla bieżącego pakietu:

```bash
python tools/dkb.py quality
```

Wynik docelowy:

- 185 testów automatycznych zakończonych powodzeniem,
- 34 pliki CSV w `data/master`,
- 1227 rekordów danych,
- 34 relacje między tabelami,
- 19 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 168 obserwacji w `configuration_attribute_values.csv`,
- 419 rekordów w `configuration_attribute_availability.csv`,
- 389 rekordów `standard` i 30 rekordów `not_available`,
- 42 nowe kanoniczne atrybuty wyposażenia w dwóch pakietach,
- baza SQLite obejmująca 34 tabele i 1227 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Sandero Passive Safety Availability Import.

Zakres:

- ponowna weryfikacja siedmiu plików PDF przez SHA-256,
- import 119 datowanych rekordów dla siedmiu konfiguracji,
- mapowanie 17 funkcji bezpieczeństwa na nowe atrybuty boolean,
- 112 jawnych pozycji `standard`,
- 7 jawnych pozycji `not_available`,
- zachowanie strony i źródłowego brzmienia w `notes`,
- brak wnioskowania na podstawie nieobecności pozycji,
- odłożenie kół i tapicerki do osobnego modelowania wartościowego.

## Current Phase

Aktualna faza to **Data Expansion**.

Pięć pakietów źródłowych danych technicznych jest zakończonych.
Tabela `configuration_attribute_values.csv` zawiera 168 datowanych
obserwacji dla siedmiu konfiguracji Sandero i Sandero Stepway.

Pierwsze 140 obserwacji jest niezależnych od rodzaju paliwa i zachowuje
puste `fuel_type_code`. Obserwacje 141–168 zapisują zużycie paliwa oraz
emisję CO2 oddzielnie dla LPG i benzyny.

Zakres obejmuje:

- pojemność zbiornika paliwa,
- pojemność skokową i liczbę cylindrów,
- liczbę miejsc i przełożeń,
- prędkość maksymalną i średnicę zawracania,
- masę własną i dopuszczalną masę całkowitą,
- dopuszczalną masę całkowitą zespołu pojazdów,
- masy przyczepy z hamulcem i bez hamulca,
- długość, szerokość, rozstaw osi oraz zwisy,
- pojemność bagażnika VDA i w litrach,
- kontekst wariantu z zestawem naprawczym,
- zużycie paliwa w cyklu mieszanym WLTP,
- emisję CO2 w cyklu mieszanym WLTP.

Opcjonalne `fuel_type_code` wskazuje na
`data/master/enums/fuel_types.csv`. Decyzja D-014 zachowuje kontekst
paliwa na poziomie obserwacji bez tworzenia paliwowych duplikatów
definicji atrybutów.

Analiza siedmiu źródeł PDF wykazała, że główne obszary danych technicznych
są już reprezentowane, natomiast wyposażenie seryjne pozostaje największym
jednoznacznym obszarem niezaimportowanym.

Porównanie konfiguracji Stepway Expression i Extreme wykazało, że
wyposażenie może zależeć od rodzaju skrzyni biegów. Decyzja D-015 przyjmuje
więc dedykowaną relację dostępności wyposażenia na poziomie konfiguracji,
z ponownym użyciem istniejącego katalogu atrybutów.

Pierwszy import dostępności z PR #19 obejmuje 300 funkcjonalnych pozycji.
Bieżący pakiet dodaje wyłącznie jednoznaczne bezpieczeństwo pasywne, nie
zmieniając znaczenia istniejących rekordów. Jawne negacje źródłowe są
zapisywane jako `not_available`; brak wzmianki pozostaje brakiem rekordu.
Koła i tapicerka wymagają osobnego modelu wartości i pozostają poza zakresem.

## Next Development Package

Sandero Wheel and Upholstery Value Modeling.

Planowany przebieg:

1. Udokumentować model wartości dla kół i tapicerki.
2. Oddzielić rozmiar, materiał, wzór i wykończenie koła.
3. Rozstrzygnąć konflikt Stepway Essential: ERALIA kontra TAMIA BI-TON.
4. Zachować tapicerkę jako wariant lub wartość, nie jako prosty boolean.
5. Nie importować wewnętrznych kryteriów zamówieniowych jako wyposażenia.
6. Dopiero po decyzji przygotować osobny kontrolowany import źródłowy.

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

Current package:

- potwierdzono 17 jednoznacznych funkcji we wszystkich siedmiu PDF-ach,
- przygotowano 119 rekordów: 112 `standard` i 7 `not_available`,
- zachowano źródłowe brzmienie i numer strony,
- nie zmieniono znaczenia pierwszych 300 obserwacji,
- koła i tapicerka pozostają poza zakresem.

Next priority:

Wartościowe modelowanie kół i tapicerki po rozstrzygnięciu konfliktu
Stepway Essential oraz udokumentowaniu decyzji modelowej.
