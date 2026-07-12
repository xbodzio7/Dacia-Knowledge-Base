# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety Sandero i Sandero Stepway zintegrowane przez
Pull Requesty #3–#14. Aktualny punkt odniesienia to merge commit `6224875`.

PR #13 zsynchronizował dokumentację po pakietach wymiarów i pojemności.
PR #14 dodał obserwacje WLTP z jawnym kontekstem LPG i benzyny.

Bieżący pakiet dokumentacyjny jest rozwijany na gałęzi
`docs/sandero-wltp-sync`.

## Verified Quality Baseline

Zweryfikowany punkt odniesienia po PR #14:

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
- GitHub Actions Quality, run #56, zakończony powodzeniem.

## Current Sprint

Sandero Fuel-aware WLTP Documentation Sync.

Zakres:

- aktualizacja `README.md`,
- aktualizacja `project/ROADMAP.md`,
- aktualizacja `project/SESSION_STATE.md`,
- uzupełnienie `CHANGELOG.md`,
- zapisanie integracji PR-ów #13 i #14,
- zapisanie merge commitu `6224875`,
- zamknięcie pakietu Fuel-mode-aware WLTP Observation Analysis.

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

## Next Development Package

Sandero PDF Source Coverage Gap Analysis.

Planowany przebieg:

1. Przejrzeć siedem zarejestrowanych źródeł PDF konfiguracji.
2. Porównać zawartość PDF z aktualnym pokryciem danych.
3. Wskazać niezaimportowane lub niekompletne obszary.
4. Powiązać kandydatów z istniejącym modelem danych.
5. Wykazać rzeczywistą lukę modelu tylko wtedy, gdy istniejące tabele
   nie mogą zachować znaczenia źródła.
6. Wybrać jeden mały następny pakiet na podstawie jednoznacznych danych.
7. Nie importować danych ani nie zgadywać wartości w pakiecie analitycznym.

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
- 168 obserwacji technicznych dla siedmiu konfiguracji,
- pełna kontrola jakości: 149 testów, 32 pliki CSV, 762 rekordy,
  30 relacji oraz 32 tabele SQLite.

Next priority:

Analiza pokrycia siedmiu źródeł PDF i wybór jednego następnego pakietu
na podstawie jednoznacznych danych źródłowych.
