# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety Sandero i Sandero Stepway zintegrowane przez
Pull Requesty #3–#15. Aktualny punkt odniesienia to merge commit
`ee67670`.

PR #14 dodał obserwacje WLTP z jawnym kontekstem LPG i benzyny.
PR #15 zsynchronizował dokumentację projektu po pakietach technicznych
i decyzji D-014.

Bieżący pakiet analityczny jest rozwijany na gałęzi
`analysis/sandero-pdf-source-coverage`.

## Verified Quality Baseline

Zweryfikowany punkt odniesienia po PR #15:

```bash
python tools/dkb.py quality
```

Wynik:

- 149 testów automatycznych zakończonych powodzeniem,
- 32 pliki CSV w `data/master`,
- 762 rekordy danych,
- 30 relacji między tabelami,
- 18 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 168 obserwacji w `configuration_attribute_values.csv`,
- baza SQLite obejmująca 32 tabele i 762 rekordy,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8,
- GitHub Actions Quality, run #58, zakończony powodzeniem.

## Current Sprint

Sandero PDF Source Coverage Gap Analysis.

Zakres:

- ekstrakcja tekstu ze wszystkich siedmiu zarejestrowanych PDF,
- porównanie zawartości źródeł z obecnym modelem i danymi,
- potwierdzenie pokrycia głównych danych technicznych,
- identyfikacja wyposażenia seryjnego jako największej luki,
- porównanie wyposażenia konfiguracji manualnych i automatycznych,
- wykazanie potrzeby reprezentacji na poziomie konfiguracji,
- zapisanie zaakceptowanej decyzji D-015,
- brak implementacji schematu i brak importu wyposażenia.

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

## Next Development Package

Equipment Availability Schema Implementation.

Planowany przebieg:

1. Dodać kontrolowany słownik statusów dostępności wyposażenia.
2. Dodać `configuration_attribute_availability.csv` zgodnie z D-015.
3. Powiązać rekordy z konfiguracjami, atrybutami i źródłami.
4. Dodać walidację statusów, referencji i unikalności.
5. Dodać testy automatyczne dla nowego modelu.
6. Rozszerzyć budowę i weryfikację SQLite.
7. Zaktualizować dokumentację modelu oraz schematu.
8. Nie importować jeszcze wyposażenia z PDF; import pozostaje osobnym
   pakietem źródłowym.

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

Current package:

- siedem PDF zostało poprawnie odczytanych bez zmiany repozytorium,
- główne dane techniczne są już objęte wcześniejszymi pakietami,
- wyposażenie seryjne zostało wskazane jako największa luka,
- różnice manual–automatic potwierdziły poziom konfiguracji,
- zaakceptowano decyzję D-015,
- pakiet nie implementuje tabel ani nie importuje wyposażenia.

Next priority:

Implementacja schematu dostępności wyposażenia zgodnego z D-015, bez
importowania rekordów wyposażenia.
