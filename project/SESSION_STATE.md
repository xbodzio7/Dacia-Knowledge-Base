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
- 1788 testów automatycznych zakończonych powodzeniem,
- 46 pliki CSV w `data/master`,
- 11713 rekordów danych,
- 51 relacje między tabelami,
- 25 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 3567 obserwacji w `configuration_attribute_values.csv`,
- 138 wersjonowanych specyfikacji w `data/imports/configuration_values`,
- 316 obserwacji w `configuration_attribute_value_ranges.csv`,
- 24 wersjonowanych specyfikacji w `data/imports/configuration_value_ranges`,
- 5906 rekordów w `configuration_attribute_availability.csv`,
- 4592 rekordów `standard`, 514 `optional`, 800 `not_available` i 0 `unknown`,
- 385 kanonicznych atrybutów w 30 kategoriach,
- baza SQLite obejmująca 46 tabele i 11713 rekordów,
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

Paczki `residual_gap_001`–`residual_gap_005` zostały przejrzane autorsko. Bigster ma 23 decyzje, 36 sygnatur i 143 rekordy. Jogger ma 16 decyzji, 3 sygnatury i 28 rekordów; sprzeczne etykiety mas, starsze wartości Hybrid 155 i dowody przypięte do innych atrybutów pozostają nieimportowalne. Duster ma 5 decyzji, 9 sygnatur i 34 rekordy; dowody ze strony 21 i sąsiednich kandydatów nie są podstawiane. Sandero ma 5 częściowo pokrytych decyzji, 8 sygnatur i 16 rekordów; wartości TCe/manual bez przypiętego dowodu oraz granice masy pojazdu i zespołu pozostają nieinferowane. Sandero Stepway ma 3 częściowo pokryte decyzje i 1 błąd sygnatury, z 5 wybranymi sygnaturami i 15 rekordami; zawieszenie, opony i masy nie są podstawiane do etykiety układu kierowniczego, a masy maksymalne do fragmentu masy minimalnej. Duster ze strony 21 ma 1 częściowo pokrytą decyzję, 1 sygnaturę i 3 rekordy Hybrid 155; dowody z wierszy średnicy zawracania, hamulców, opon, masy i ładowności nie są podstawiane do typu układu kierowniczego. Duster ze strony 23 ma 6 pokrytych i 20 częściowo pokrytych decyzji, 43 sygnatury oraz 518 rekordów; symbole standardu, opcji i niedostępności oraz granice wielowierszowych nazw i pakietów pozostają zachowane. Duster ze strony 22 ma 3 pokryte i 8 częściowo pokrytych decyzji, 23 sygnatury oraz 524 rekordy; światła i czujnik deszczu, ESC i HSA, napinacze i regulacja wysokości pasów oraz tylne i przednio-boczne czujniki parkowania pozostają odrębnymi atrybutami. Bigster ze strony 22 ma 3 pokryte i 4 częściowo pokryte decyzje, wszystkie 18 sygnatur oraz 126 rekordów; klimatyzacja, dwustrefowość i nawiewy, warianty konsoli oraz elementy pakietów zimowych pozostają rozdzielone. Jogger ze strony 20 ma 3 częściowo pokryte decyzje, 1 kontekst bez importu i 1 odroczony konflikt źródeł, 8 sygnatur oraz 154 rekordy; obecność poduszek nie zastępuje dowodu dezaktywacji, a stan kamery Journey z broszury 2025-12 i cennika 2026-04 pozostaje nierozstrzygnięty. Bigster ze strony 21 ma 1 pokrytą decyzję, wszystkie 3 sygnatury oraz 14 rekordów; Journey pozostaje opcjonalne, a Extreme standardowe. Jogger ze strony 21 ma 1 odroczony konflikt źródeł, obie sygnatury i 30 rekordów; broszurowy standard Journey nie jest zastępowany późniejszą niedostępnością. Sandero ze strony 18 ma 1 odroczony konflikt źródeł, obie sygnatury i 4 rekordy; opcja Expression z broszury i cennika nie jest zastępowana późniejszym stanem seryjnym ze strony oficjalnej, a standard Journey pozostaje odrębny. Sandero ze strony 19 ma 1 pokrytą decyzję, obie standardowe sygnatury i 4 rekordy; regulator oraz ogranicznik prędkości pozostają odrębnymi atrybutami, a trzy broszurowe stany seryjne nie są projekcją rekordów między wersjami. Sandero Stepway ze strony 18 ma 1 pokrytą decyzję, 1 wybraną sygnaturę i rekord zwykłych relingów oraz 1 zachowaną i jawnie odrzuconą sygnaturę relingów modułowych z 2 rekordami; dwa sąsiednie wiersze i ich przeciwne układy wersji pozostają rozdzielone. Pierwszy fragment nierozstrzygniętych tabel technicznych Bigstera ze strony 20 obejmuje 40 kandydatów pogrupowanych w 18 wizualnych wierszy: 16 kompletnych wierszy pozostaje błędami niedopasowania sygnatury, 24 nagłówki i fragmenty są kontekstem bez importu, a liczba przypiętych sygnatur i rekordów pozostaje zerowa. Fragmenty tylnych hamulców odsyłają do wcześniejszej decyzji `residual_gap_001`, a pięciopakietowy przegląd nie wymagał nowej decyzji architektonicznej ani osobnego PR-a audytowego. Drugi fragment obejmuje pozostałych 29 kandydatów pogrupowanych w 16 wizualnych obszarów: 8 kompletnych wierszy pozostaje błędami niedopasowania sygnatury, a 21 zawiniętych fragmentów, etykiet, przypisów i not jest kontekstem bez importu. Wydrukowana sekwencja `1960**` oraz `2002 / 1981` pozostaje literalna i bez wymyślonej interpretacji; liczba przypiętych sygnatur i rekordów nadal wynosi zero. Następna paczka rozpoczyna przegląd nierozstrzygniętych kandydatów technicznych minibroszury Dustera ze strony 21.

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
