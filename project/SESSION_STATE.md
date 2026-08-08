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

## Verified Quality Baseline

<!-- dkb:documentation-baseline:session:start -->
- 1908 testów automatycznych zakończonych powodzeniem,
- 47 pliki CSV w `data/master`,
- 12007 rekordów danych,
- 51 relacje między tabelami,
- 26 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 3664 obserwacji w `configuration_attribute_values.csv`,
- 139 wersjonowanych specyfikacji w `data/imports/configuration_values`,
- 316 obserwacji w `configuration_attribute_value_ranges.csv`,
- 24 wersjonowanych specyfikacji w `data/imports/configuration_value_ranges`,
- 5911 rekordów w `configuration_attribute_availability.csv`,
- 4595 rekordów `standard`, 516 `optional`, 800 `not_available` i 0 `unknown`,
- 387 kanonicznych atrybutów w 30 kategoriach,
- baza SQLite obejmująca 47 tabele i 12007 rekordów,
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
