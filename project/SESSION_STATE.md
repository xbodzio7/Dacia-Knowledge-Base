# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Etap budowy fundamentów i narzędzi został zakończony. Gałąź `dev/tools-improvements` została zintegrowana z `main` przez Pull Request #1.

Bieżący pakiet dokumentacyjny jest rozwijany na gałęzi `docs/project-state-sync`.

## Verified Quality Baseline

Ostatnia pełna lokalna kontrola:

```bash
python tools/dkb.py quality
```

Wynik:

- 148 testów automatycznych zakończonych powodzeniem,
- 23 pliki CSV w `data/master`,
- 546 rekordów danych,
- walidator repozytorium w wersji 0.10,
- baza SQLite obejmująca 23 tabele i 546 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Project State Synchronization.

Zakres:

- aktualizacja `ROADMAP.md`,
- aktualizacja `SESSION_STATE.md`,
- uzupełnienie `CHANGELOG.md`,
- usunięcie nieaktualnych informacji o planowanym tworzeniu narzędzi, które są już wdrożone,
- zapisanie następnego etapu rozwoju projektu.

## Current Phase

Aktualna faza to **Data Expansion**.

Priorytetem jest systematyczne rozwijanie danych merytorycznych na podstawie wiarygodnych źródeł. Nowa automatyzacja powinna powstawać tylko wtedy, gdy bezpośrednio wspiera jakość, import lub wykorzystanie danych.

## Next Development Package

Source-backed Data Expansion.

Planowany przebieg:

1. Wybrać pierwszą rodzinę modeli do opracowania.
2. Zebrać i sklasyfikować materiały źródłowe.
3. Rozszerzyć dane w `data/master`.
4. Zachować identyfikowalność pochodzenia informacji.
5. Uruchomić `python tools/dkb.py quality`.
6. Zintegrować mały, kompletny pakiet zmian przez osobną gałąź.

## Working Mode

Projekt jest rozwijany w małych, kontrolowanych pakietach.

Każdy pakiet:

- rozpoczyna się od sprawdzenia gałęzi i czystości katalogu roboczego,
- obejmuje wyłącznie pliki związane z bieżącym zadaniem,
- jest przeglądany przed commitem,
- przechodzi odpowiednie testy lub pełną bramkę `quality`,
- kończy się aktualizacją dokumentacji tylko wtedy, gdy zmienia stan projektu.

Git Bash służy do generowania zmian, testów i kontroli stanu. Git GUI może służyć do przeglądania różnic, stagingu, commitów i pushowania.

## Project Rules

- `data/master` zawiera źródłowe dane projektu.
- Raporty, eksporty wyszukiwania i lokalne bazy SQLite są artefaktami generowanymi.
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

Next priority:

Rozbudowa danych merytorycznych opartych na źródłach.
