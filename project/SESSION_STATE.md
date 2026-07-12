# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera źródłowe pakiety Sandero i Sandero Stepway
zintegrowane przez Pull Requesty #3–#12. Aktualny punkt odniesienia to
merge commit `17d075d`.

Bieżący pakiet dokumentacyjny jest rozwijany na gałęzi
`docs/sandero-dimensions-capacities-sync`.

## Verified Quality Baseline

Ostatnia pełna lokalna kontrola:

```bash
python tools/dkb.py quality
```

Wynik:

- 148 testów automatycznych zakończonych powodzeniem,
- 32 pliki CSV w `data/master`,
- 734 rekordy danych,
- 29 relacji między tabelami,
- 18 reguł statusów,
- walidator repozytorium w wersji 0.10,
- baza SQLite obejmująca 32 tabele i 734 rekordy,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Sandero Dimensions and Capacities Documentation Sync.

Zakres:

- aktualizacja `README.md`,
- aktualizacja `project/ROADMAP.md`,
- aktualizacja `project/SESSION_STATE.md`,
- uzupełnienie `CHANGELOG.md`,
- zapisanie bieżącego stanu po integracji PR-ów #11 i #12.

## Current Phase

Aktualna faza to **Data Expansion**.

Cztery pakiety źródłowych danych technicznych są zakończone.
Tabela `configuration_attribute_values.csv` zawiera 140 datowanych
obserwacji dla siedmiu konfiguracji Sandero i Sandero Stepway.

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
- kontekst wariantu z zestawem naprawczym.

## Next Development Package

Fuel-mode-aware WLTP Observation Analysis.

Planowany przebieg:

1. Zidentyfikować w źródłach wartości zużycia paliwa i emisji CO2
   rozdzielone na LPG oraz benzynę.
2. Sprawdzić, czy aktualny model obserwacji potrafi zachować kontekst
   rodzaju paliwa bez utraty znaczenia.
3. Zaprojektować najmniejsze rozszerzenie schematu i walidacji.
4. Dodać testy modelu przed importem nowych obserwacji.
5. Powiązać każdy rekord z konfiguracją, datą i dokumentem źródłowym.
6. Uruchomić `python tools/dkb.py quality`.
7. Zintegrować pakiet przez osobną gałąź i Pull Request.

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
- 140 obserwacji technicznych dla siedmiu konfiguracji,
- pełna kontrola jakości: 32 pliki CSV, 734 rekordy i 32 tabele SQLite.

Next priority:

Analiza modelu obserwacji WLTP z jawnym kontekstem LPG i benzyny.
