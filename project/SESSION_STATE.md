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

Bieżący SHA `main`, stan Pull Requestów i wyniki CI należy zawsze odczytywać dynamicznie z Git i GitHub. Nie są kopiowane do tego dokumentu.

## Verified Quality Baseline

<!-- dkb:documentation-baseline:session:start -->
- 1267 testów automatycznych zakończonych powodzeniem,
- 46 pliki CSV w `data/master`,
- 11092 rekordów danych,
- 51 relacje między tabelami,
- 25 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 3267 obserwacji w `configuration_attribute_values.csv`,
- 117 wersjonowanych specyfikacji w `data/imports/configuration_values`,
- 244 obserwacji w `configuration_attribute_value_ranges.csv`,
- 20 wersjonowanych specyfikacji w `data/imports/configuration_value_ranges`,
- 5770 rekordów w `configuration_attribute_availability.csv`,
- 4482 rekordów `standard`, 507 `optional`, 781 `not_available` i 0 `unknown`,
- 385 kanonicznych atrybutów w 30 kategoriach,
- baza SQLite obejmująca 46 tabele i 11092 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.
<!-- dkb:documentation-baseline:session:end -->

Dodatkowe kontrakty stanu projektu i autonomii są uruchamiane jawnie w CI poza historycznym licznikiem discovery `test_*.py`.

## Verified PDF Residual Review Boundary

Bieżąca kolejka obejmuje dokładnie 1 266 kandydatów zachowanych przez
`verified_pdf_candidate_coverage_reconciliation.json`: 108 `ambiguous` i
1 158 `unresolved`. Są przypisane dokładnie raz do 52 paczek ograniczonych
przez źródło, domenę, stronę i status, po najwyżej 40 kandydatów. Priorytet nie
jest zgodą na import.

Paczki `residual_gap_001`–`residual_gap_005` zostały przejrzane autorsko. Bigster ma 23 decyzje, 36 sygnatur i 143 rekordy. Jogger ma 16 decyzji, 3 sygnatury i 28 rekordów; sprzeczne etykiety mas, starsze wartości Hybrid 155 i dowody przypięte do innych atrybutów pozostają nieimportowalne. Duster ma 5 decyzji, 9 sygnatur i 34 rekordy; dowody ze strony 21 i sąsiednich kandydatów nie są podstawiane. Sandero ma 5 częściowo pokrytych decyzji, 8 sygnatur i 16 rekordów; wartości TCe/manual bez przypiętego dowodu oraz granice masy pojazdu i zespołu pozostają nieinferowane. Sandero Stepway ma 3 częściowo pokryte decyzje i 1 błąd sygnatury, z 5 wybranymi sygnaturami i 15 rekordami; zawieszenie, opony i masy nie są podstawiane do etykiety układu kierowniczego, a masy maksymalne do fragmentu masy minimalnej. Następna paczka obejmuje 1 kandydata technicznego ze strony 21 minibroszury Dustera.

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
