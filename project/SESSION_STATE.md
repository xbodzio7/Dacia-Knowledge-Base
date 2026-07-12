# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety źródłowych danych Sandero i Sandero Stepway
zintegrowane przez Pull Requesty #3–#6. Aktualny punkt odniesienia to
merge commit `6d427bc`.

Bieżący pakiet dokumentacyjny jest rozwijany na gałęzi
`docs/sandero-data-sync`.

## Verified Quality Baseline

Ostatnia pełna lokalna kontrola:

```bash
python tools/dkb.py quality
```

Wynik:

- 148 testów automatycznych zakończonych powodzeniem,
- 31 plików CSV w `data/master`,
- 594 rekordy danych,
- 26 relacji między tabelami,
- 18 reguł statusów,
- walidator repozytorium w wersji 0.10,
- baza SQLite obejmująca 31 tabel i 594 rekordy,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Sandero Data Baseline Documentation Sync.

Zakres:

- aktualizacja `README.md`,
- aktualizacja `project/ROADMAP.md`,
- aktualizacja `project/SESSION_STATE.md`,
- uzupełnienie `CHANGELOG.md`,
- zapisanie bieżącego stanu po integracji PR-ów #3–#6.

## Current Phase

Aktualna faza to **Data Expansion**.

Pierwszy spójny pakiet źródłowy dla Sandero i Sandero Stepway jest
zakończony. Obejmuje dokumenty źródłowe, modele, wersje, konfiguracje
oraz datowane obserwacje cen.

## Next Development Package

Source-backed Technical Specifications.

Planowany przebieg:

1. Wybrać mały zestaw parametrów jednoznacznie widocznych w źródłach.
2. Sprawdzić, czy odpowiadają im istniejące atrybuty i jednostki.
3. Dodać wartości bez zgadywania brakujących danych.
4. Powiązać rekordy z dokumentami źródłowymi.
5. Uruchomić `python tools/dkb.py quality`.
6. Zintegrować pakiet przez osobną gałąź i Pull Request.

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
- Dane handlowe muszą mieć datę i źródło.
- Nie należy zgadywać brakujących parametrów technicznych.
- Nie należy ponownie projektować stabilnej architektury bez wyraźnej potrzeby.
- Nie należy deklarować powodzenia CI bez sprawdzenia wyniku.
- `ROADMAP.md` definiuje fazę i kierunek rozwoju.
- `SESSION_STATE.md` opisuje bieżący kontekst roboczy i musi pozostawać zgodny z roadmapą.

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
- rozszerzenie walidacji referencji i statusów dla nowych tabel.

Next priority:

Źródłowe dane techniczne dla zarejestrowanych konfiguracji.
