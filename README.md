# Dacia Knowledge Base (DKB)

Dacia Knowledge Base (DKB) to referencyjna baza wiedzy o samochodach marki Dacia.

Projekt gromadzi ustrukturyzowane dane dotyczące modeli, wersji wyposażenia, silników, skrzyń biegów, wyposażenia, danych technicznych oraz źródeł informacji.

## Cele projektu

* jedno źródło prawdy dla danych o samochodach Dacia,
* normalizacja danych w czytelnych plikach CSV,
* automatyczna walidacja jakości i spójności danych,
* generowanie raportów i katalogów danych,
* eksport danych do SQLite i innych systemów,
* wygodne wyszukiwanie informacji w repozytorium.

## Struktura repozytorium

```text
.github/workflows/  Automatyczna kontrola jakości
data/               Znormalizowane dane CSV
tools/              Walidatory, raporty, wyszukiwanie i eksport
reports/            Raporty generowane automatycznie
project/            Dokumentacja projektu i aktualny stan prac
tests/              Testy automatyczne
PDF/                Materiały źródłowe w formacie PDF
Archiwum/            Materiały historyczne
```

Dodatkowe katalogi modelowe i źródłowe przechowują materiały robocze związane z konkretnymi samochodami.

## Główne zbiory danych

Repozytorium zawiera między innymi:

* dane pojazdów: `models.csv`, `engines.csv`, `gearboxes.csv`,
  `model_engines.csv` i `model_gearboxes.csv`,
* wersje i konfiguracje: `versions.csv`, `configurations.csv`,
  `source_versions.csv` i `source_configurations.csv`,
* źródła: `sources.csv` i `source_models.csv`,
* obserwacje handlowe: `configuration_prices.csv` i `currencies.csv`,
* obserwacje techniczne konfiguracji:
  `configuration_attribute_values.csv`,
* dostępność wyposażenia konfiguracji:
  `configuration_attribute_availability.csv` oraz kontrolowany słownik
  `equipment_availability_statuses.csv`,
* katalog atrybutów: `attributes.csv`, `attribute_categories.csv`,
  `units.csv` i `value_types.csv`,
* słowniki klasyfikacyjne, w tym `body_types.csv`, `segments.csv`
  oraz pliki w `data/master/enums/`.

Ceny są zapisywane jako datowane obserwacje powiązane z konkretnym
dokumentem źródłowym. Nie są traktowane jako bezterminowa deklaracja
aktualnej oferty.

Parametry techniczne i pozostałe wartości konfiguracji również są
datowanymi obserwacjami powiązanymi ze źródłem. Siedemnaście pakietów obejmuje
309 wartości dla siedmiu konfiguracji Sandero i Sandero Stepway: 168 bazowych
obserwacji technicznych, 29 wartości kół i tapicerki, 7 wartości koloru
nadwozia, 7 pełnych specyfikacji standardowej opony, 7 wartości liczby
drzwi, 7 wartości normy emisji, 7 wartości poziomu hałasu, 7 wartości rodzaju
napędu, 7 wartości maksymalnej ładowności, 28 wartości mocy i momentu
obrotowego, 7 wartości całkowitej liczby zaworów, 14 wartości przyspieszenia
0–100 km/h oraz 14 czasów przejazdu kilometra ze startu zatrzymanego. Zakres
techniczny obejmuje zespół napędowy, osiągi, masy, wymiary, pojemność
bagażnika, zużycie paliwa i emisję CO2 w cyklu WLTP.

Dla obserwacji, których znaczenie zależy od użytego paliwa, opcjonalne pole
`fuel_type_code` wskazuje jawnie LPG albo benzynę. Pozostałe obserwacje
zachowują pusty kontekst paliwa zgodnie z decyzją D-014.

Dostępność wyposażenia jest reprezentowana na poziomie konfiguracji zgodnie
z decyzją D-015. Pole `availability_status` przyjmuje kontrolowane wartości
`standard`, `optional`, `not_available` albo `unknown`. Brak rekordu oznacza,
że dostępność nie została zaimportowana; nie oznacza wartości `unknown` ani
`not_available`.

Pierwsze dwa źródłowe pakiety dostępności obejmują 419 datowanych
rekordów dla siedmiu konfiguracji Sandero i Sandero Stepway oraz 69 funkcji
wyposażenia. Import zachowuje 389 jawnych pozycji `standard` i 30 jawnych
wartości `not_available`. Pierwszy pakiet obejmuje multimedia, komfort,
szyby i lusterka, oświetlenie, parkowanie, wybrane systemy ADAS oraz
klimatyzację. Drugi dodaje jednoznaczne wyposażenie bezpieczeństwa pasywnego,
w tym poduszki powietrzne, napinacze pasów, przypomnienia o pasach, ABS,
eCall, automatyczne blokowanie drzwi, ostrzeżenie o bezpiecznej odległości
i przygotowanie do blokady alkoholowej. Oryginalne brzmienie pozycji i numer
strony PDF są zachowane w polu `notes`.

Koła i tapicerka są modelowane jako wartości konfiguracji zgodnie z D-016.
Import rozdziela rozmiar, materiał, wzór i wykończenie koła oraz zachowuje
tapicerkę jako nazwany wariant. Dla Stepway Essential zapisano wyłącznie
wspólny materiał `steel`; sprzeczne wzory ERALIA/TAMIA BI-TON i wynikające
z nich wykończenie pozostają celowo bez rekordu.

Kolor nadwozia jest datowaną wartością konfiguracji. Siedem bieżących źródeł
wskazuje `biel alpejska`; zapis `0 zł` pozostaje w `notes` jako część
źródłowego opisu wybranego składnika i nie tworzy osobnej opcji ani ceny
składnika.

Standardowa opona jest datowaną wartością konfiguracji zgodnie z D-018.
Siedem bieżących źródeł wskazuje `205/60 R16 92H`. Wartość zachowuje pełną
specyfikację bez przypisywania jej do osi i bez reinterpretowania `92H` jako
maksymalnego indeksu. Nie zastępuje też rozmiaru felgi przechowywanego w
`wheel_size`.

Liczba drzwi jest datowaną wartością konfiguracji. Wszystkie siedem źródeł
wskazuje na stronie 5 w sekcji `Typ nadwozia` wartość `Liczba Drzwi 5`.
Import używa istniejącego atrybutu integer `number_of_doors` i nie tworzy
wartości dla `number_of_side_doors`.

Normy emisji korzystają z kontrolowanego słownika. Decyzja D-019 zachowuje
`Euro 6e BIS` jako odrębną aktywną wartość `euro_6e_bis`; nie redukuje jej do
ogólniejszego `Euro 6e`. Wszystkie siedem bieżących konfiguracji ma datowaną
wartość `emission_standard = euro_6e_bis` z zachowaniem strony 6 i dokładnego
brzmienia źródła. Poziom hałasu 67 dB pozostaje osobnym faktem.

Poziom hałasu przy 50 km/h jest odrębnym pomiarem akustycznym. Decyzja D-020
wprowadza kategorię `Acoustics`, jednostkę `dB` i atrybut decimal
`noise_level_at_50_kmh`. Wszystkie siedem bieżących konfiguracji ma datowaną
wartość `noise_level_at_50_kmh = 67` z zachowaniem strony 6 i dokładnego
brzmienia źródła. Warunek 50 km/h pozostaje częścią znaczenia; import nie
zakłada pomiaru wewnętrznego, zewnętrznego, stacjonarnego, przejazdowego ani
ważenia `dB(A)`.

Rodzaj napędu jest datowaną wartością konfiguracji. Wszystkie siedem źródeł
wskazuje na stronie 5 w sekcji `Układ napędowy` pole
`Rodzaj Napędu przedni`. Import używa istniejącego aktywnego enumu
`drive_type` i kontrolowanej wartości `fwd`; nie tworzy równoległych wartości
string `drive_layout` ani `drivetrain_type`.

Maksymalna ładowność jest modelowana zgodnie z D-021 jako aktywny atrybut
integer `maximum_payload` w kategorii `Weights`, z jednostką `kg`. Wszystkie
siedem konfiguracji ma datowaną, źródłową wartość od 371 do 385 kg, zachowującą
stronę 5, sekcję `Dopuszczalna masa całkowita` i pole
`Maksymalna Ładowność (Kg)`. Import nie wylicza wartości z różnicy
`gross_vehicle_weight` i `kerb_weight` oraz nie utożsamia jej z obciążeniem
dachu, masą przyczepy ani masą zespołu pojazdów.

Moc i moment obrotowy silnika są datowanymi obserwacjami z jawnym kontekstem
paliwa. Dla każdej z siedmiu konfiguracji zapisano `engine_power = 84 kW` i
`engine_torque = 190 Nm` dla benzyny oraz `engine_power = 90 kW` i
`engine_torque = 197 Nm` dla LPG. Import zachowuje stronę 6, sekcję `Silnik`
i pełne źródłowe brzmienie, w tym zakresy obrotów pozostawione w `notes`;
nie tworzy z nich osobnych, wyprowadzonych rekordów.

Całkowita liczba zaworów jest modelowana zgodnie z D-022 jako aktywny atrybut
integer `total_valve_count` w kategorii `Engine`, bez jednostki. Wszystkie
siedem konfiguracji ma datowaną wartość `12`, z pustym kontekstem paliwa,
stroną 6, sekcją `Silnik` i polem `Liczba Zaworów 12`. Wartość pozostaje
odrębna od `valves_per_cylinder` i nie jest dzielona przez liczbę cylindrów.

Przyspieszenie 0–100 km/h jest datowaną obserwacją osiągów z jawnym
kontekstem paliwa. Wszystkie siedem konfiguracji ma osobne wartości LPG
od 10,0 do 10,4 s oraz benzyny od 11,0 do 11,4 s. Import używa istniejącego
aktywnego atrybutu decimal `acceleration_0_100`, zachowuje stronę 5, sekcję
`Osiągi` i pełne źródłowe brzmienie każdej pary paliwowej.

Przejazd 1000 m ze startu zatrzymanego jest przechowywany w istniejącym
aktywnym atrybucie decimal `standing_km` z jednostką `s`. Wszystkie siedem
konfiguracji ma osobne wartości LPG 32,1 lub 32,4 s oraz benzyny 33,1 lub
33,4 s, z datą obserwacji, stroną 5, sekcją `Osiągi` i pełną proweniencją.

Końcowa ponowna ocena 43 grup technicznych po 309 wartościach nie wskazała
żadnego kolejnego kandydata spełniającego jednocześnie wymagania kompletności
siedmiu źródeł, jednoznacznego mapowania modelu, braku istniejącego rekordu
i bezpiecznego formatu wartości. Obecny sweep jawnych wartości technicznych
Sandero jest zamknięty bez tworzenia dodatkowego modelu.

Pliki CSV są podstawowym i nadrzędnym źródłem danych. Baza SQLite oraz raporty są artefaktami generowanymi na ich podstawie.

## Narzędzia

Głównym punktem wejścia jest:

```bash
python tools/dkb.py help
```

Dostępne komendy:

| Komenda | Zastosowanie |
| --- | --- |
| `validate` | Walidacja struktury repozytorium i danych |
| `normalize` | Kontrola kodowania plików CSV |
| `quality` | Pełna lokalna kontrola jakości |
| `sqlite` | Budowanie lokalnej bazy SQLite |
| `sqlite-verify` | Pełna kontrola zgodności SQLite z CSV |
| `search` | Wyszukiwanie danych w plikach CSV |
| `stats` | Statystyki zbiorów danych |
| `catalog` | Generowanie katalogu encji |
| `dictionary` | Generowanie słownika danych |
| `configuration-gap-triage` | Deterministyczna kolejka weryfikacji luk konfiguracji |
| `source-coverage` | Raport rejestracji źródeł, sekcji i rekordów |
| `configuration-completeness` | Raport kompletności danych aktywnych konfiguracji |
| `documentation-baseline` | Generowanie i kontrola bieżących liczników dokumentacji |
| `import-configuration-values` | Planowanie, stosowanie i weryfikacja deklaratywnych importów |
| `package-start` | Synchronizacja `main` i utworzenie gałęzi pakietu |
| `package-review` | Kontrola zakresu, diffu i opcjonalnie jakości |
| `package-publish` | Dokładny staging, jeden commit, finish i opcjonalny push |
| `package-finish` | Kontrola commitu przed pushem i Pull Requestem |

### Walidacja

Komenda sprawdza strukturę repozytorium, kodowanie UTF-8 i strukturę plików CSV, unikalność kluczy `id` i `code`, relacje między tabelami, poprawność zakresów lat, spójność statusów i cyklu życia encji, zgodność okresów dostępności powiązań z okresami encji nadrzędnych, brak zduplikowanych i nakładających się okresów dla tej samej pary powiązań, zgodność deklaratywnych reguł danych z aktualnym schematem tabel oraz wykonuje te reguły na katalogu atrybutów. Reguły o poziomie `warning` są raportowane, ale nie powodują niepowodzenia walidacji.

```bash
python tools/dkb.py validate
```

Walidator zapisuje szczegółowy raport w `reports/validation_report.md`. Jest to generowany artefakt lokalny, ignorowany przez Git i publikowany przez workflow CI.

### Kontrola kodowania CSV

Tryb kontrolny nie modyfikuje plików:

```bash
python tools/dkb.py normalize
```

Konwersja wykrytych plików Windows-1250 do UTF-8:

```bash
python tools/dkb.py normalize --apply
```

### Lokalna kontrola jakości

```bash
python tools/dkb.py quality
```

Komenda odtwarza lokalnie pełną kontrolę wykonywaną przez
GitHub Actions: kompiluje źródła, uruchamia testy, sprawdza
kodowanie i dane, buduje i porównuje tymczasową bazę SQLite,
weryfikuje bieżące liczniki dokumentacji, a następnie generuje raporty
kompletności konfiguracji, pokrycia źródłami i kolejkę triage. Zatrzymuje się
na pierwszym nieudanym etapie. Tymczasowa baza jest automatycznie usuwana.

Tryb zwięzły zachowuje pełny verbose log w pliku, przy sukcesie pokazuje
wyłącznie liczbę testów i podsumowania etapów, a przy błędzie odtwarza pełne
nazwy testów oraz tracebacki:

```bash
python tools/dkb.py quality \
  --concise \
  --log-file ../quality.log \
  --summary-json ../quality-summary.json
```

### Automatyzacja pakietów zmian

Rozpoczęcie pakietu synchronizuje `main`, sprawdza czystość repozytorium
oraz dostępność nazwy i tworzy nową gałąź:

```bash
python tools/dkb.py package-start tooling/example
```

Przegląd przed commitem łączy kontrolę zakresu, `diff --check`, statystyki
zmian, zawartość nowych nieśledzonych plików oraz opcjonalną pełną bramkę
jakości. Proste pakiety mogą nadal używać powtarzalnego `--allow`.

Dla pakietów publikowanych zalecany jest manifest JSON przechowywany poza
repozytorium:

```json
{
  "version": 1,
  "branch": "tooling/example",
  "base_sha": "0123456789abcdef0123456789abcdef01234567",
  "commit_message": "tooling: example change",
  "expected_commits": 1,
  "paths": ["README.md", "tools/example.py"]
}
```

Przegląd z manifestem wymaga dokładnej gałęzi, niezmienionego SHA bazowego,
pre-commitowego `HEAD` równego bazie oraz dokładnego zestawu plików:

```bash
python tools/dkb.py package-review --manifest ../package.json --quality --show-diff
```

Przegląd z pełną jakością zapisuje obok manifestu `quality-receipt.json` oraz
pełny `quality.log`. Receipt jest związany z gałęzią, bazowym SHA, tematem,
dokładnym zestawem ścieżek, drzewem z tymczasowego indeksu Git i surowym
SHA-256 bajtów plików.

Trwała publikacja sprawdza pusty staging i brak dodatkowych zmian, bezpiecznie
ponownie używa wyłącznie dokładnego receipt, stage'uje tylko manifest, wykonuje
`git diff --cached --check`, tworzy jeden commit i uruchamia `package-finish`:

```bash
python tools/dkb.py package-publish --manifest ../package.json
```

Obok `package-publish.log` powstaje mały `handoff.json`. Push jest wykonywany
wyłącznie po jawnej fladze `--push`; bez niej publikacja kończy się na lokalnym
commicie i kontroli finish. Ponowne uruchomienie bezpiecznie wznawia dokładny,
już utworzony commit zamiast tworzyć drugi.

Końcową kontrolę można nadal uruchomić osobno:

```bash
python tools/dkb.py package-finish --manifest ../package.json
```

Procesy Git i lokalnej jakości wymuszają UTF-8. Plik `.gitattributes`
utrzymuje zakończenia LF dla źródeł, dokumentacji, CSV, JSON i YAML.

### Eksport SQLite

Domyślna baza lokalna:

```bash
python tools/dkb.py sqlite
```

Własna ścieżka wyjściowa:

```bash
python tools/dkb.py sqlite --output reports/dkb.sqlite
```

Wygenerowana baza jest artefaktem lokalnym i nie jest śledzona przez Git.

Kontrola integralności, zestawu tabel, schematów kolumn i zawartości danych:

```bash
python tools/dkb.py sqlite-verify reports/dkb.sqlite
```

### Wyszukiwanie

```bash
python tools/dkb.py search Duster
```

Wyszukiwanie w konkretnym polu:

```bash
python tools/dkb.py search Duster --field name
```

Eksport wyników do CSV:

```bash
python tools/dkb.py search Duster --export reports/duster_search.csv
```

Eksport ma stały układ kolumn zbudowany ze wszystkich przeszukiwanych tabel. Wartości są wyrównywane według nazw kolumn, a sam plik wynikowy jest wykluczany z wyszukiwania.

### Statystyki

```bash
python tools/dkb.py stats
```

Statystyki obejmują wyłącznie źródłowe pliki CSV znajdujące się w `data/master`, również w jego podkatalogach. Lokalne eksporty i dane generowane nie wpływają na wynik.

### Triage luk konfiguracji

Komenda `configuration-gap-triage` łączy raport kompletności z raportem
pokrycia źródłami. Oba wejścia muszą wskazywać dokładnie ten sam zestaw luk,
datę, konfigurację, źródło, kategorię, atrybut i kontekst paliwa.

Kolejka ma neutralny, leksykograficzny porządek służący wyłącznie
powtarzalności. Nie jest to priorytet biznesowy. Każdy wpis otrzymuje stan
`source_verification_required`, priorytet `unassigned` oraz
`auto_import = false`.

```bash
python tools/dkb.py configuration-gap-triage   --json ../configuration-gap-triage.json   --markdown ../configuration-gap-triage.md
```

Raport zachowuje datę dokumentu, ścieżkę i SHA-256. Wskazuje kandydatów do
ręcznej weryfikacji w zarejestrowanym źródle, ale nie sugeruje wartości i nie
uruchamia importu.

### Pokrycie źródłami

Raport `source-coverage` używa tego samego wersjonowanego mianownika co raport
kompletności konfiguracji. Dla każdego oczekiwanego źródła sprawdza osobno:

* rejestrację aktywnego źródła, datę dokumentu, ścieżkę i SHA-256,
* powiązania z modelem, wersją i konfiguracją,
* obecność datowanej ceny,
* pokrycie technicznych slotów i atrybutów wyposażenia,
* sekcje całkowicie pokryte, częściowe i bez obserwacji.

Brak lub nieaktywność źródła jest raportowana jako `source_missing`, natomiast
brak wartości przy poprawnie zarejestrowanym źródle jako `record_missing`.
Raport nie zakłada, że brak rekordu oznacza brak cechy w dokumencie.

```bash
python tools/dkb.py source-coverage \
  --json ../source-coverage.json \
  --markdown ../source-coverage.md
```

Opcjonalne `--as-of YYYY-MM-DD` tworzy historyczny snapshot względem dat
źródeł, cen i obserwacji.

### Kompletność danych konfiguracji

Raport używa wersjonowanej specyfikacji
`data/reporting/configuration_completeness.json`. Specyfikacja jawnie określa
aktywne konfiguracje i źródła, techniczne sloty atrybutu i kontekstu paliwa,
atrybuty dostępności wyposażenia oraz wyjątki `not_applicable`.

Brak rekordu jest raportowany jako `missing`. Jawne stany `unknown` i
`not_available` pozostają osobnymi wynikami, a `not_applicable` może wynikać
wyłącznie z wersjonowanego wyjątku. Raport niczego nie uzupełnia przez
zgadywanie.

```bash
python tools/dkb.py configuration-completeness \
  --json ../configuration-completeness.json \
  --markdown ../configuration-completeness.md
```

Opcjonalne `--as-of YYYY-MM-DD` ogranicza obserwacje do wskazanej daty.
Raport grupuje luki według konfiguracji, kategorii i źródła.

### Bieżące liczniki dokumentacji

Komenda generuje deterministyczny zestaw liczników używanych w bieżących podsumowaniach projektu:

```bash
python tools/dkb.py documentation-baseline \
  --json ../documentation-baseline.json \
  --markdown ../documentation-baseline.md
```

Tryb `--check` porównuje wyliczone wartości z czterema zarządzanymi blokami README, changeloga, roadmapy i stanu sesji. Tryb `--apply` aktualizuje wyłącznie te bloki. Po przekazaniu `--database` liczba tabel i rekordów SQLite musi być zgodna z plikami master CSV.

### Raporty

```bash
python tools/dkb.py catalog
python tools/dkb.py dictionary
```

Katalog encji i słownik danych są generowane wyłącznie na podstawie plików z `data/master`. Eksporty z `reports/` oraz dane generowane są pomijane.

## Automatyczna kontrola jakości

Workflow `.github/workflows/quality.yml` uruchamia kontrolę jakości:

* po pushu do `main` i gałęzi `dev/**`,
* dla każdego Pull Requestu,
* ręcznie przez `workflow_dispatch`.

Python 3.10 wykonuje kompilację i pełny zestaw testów kompatybilności.
Python 3.13 wykonuje kompilację, testy, kontrolę CSV, walidację danych, budowę
i weryfikację SQLite oraz generowanie artefaktów. Dodatkowy job Windows
uruchamia regresje workflow, receipt, publikacji, CLI i UTF-8.

Kontrola obejmuje:

1. kompilację źródeł Pythona,
2. uruchomienie testów jednostkowych,
3. kontrolę kodowania CSV,
4. walidację repozytorium, danych i relacji między tabelami,
5. próbne zbudowanie bazy SQLite,
6. pełną kontrolę zgodności tabel, schematów kolumn i zawartości SQLite ze źródłowymi plikami CSV,
7. kontrolę generowanych liczników i zarządzanych bloków dokumentacji,
8. deterministyczne wygenerowanie raportu kompletności konfiguracji,
9. deterministyczne wygenerowanie raportu pokrycia źródłami,
10. deterministyczne wygenerowanie kolejki triage luk konfiguracji.

Dla Pythona 3.13 workflow zapisuje bazę SQLite, raport walidacji, bazowe
liczniki, raport kompletności, raport pokrycia źródłami i kolejkę triage
w formatach JSON oraz Markdown jako tymczasowy artefakt GitHub Actions
przechowywany przez 7 dni.

## Zasady projektu

* repozytorium GitHub jest jedynym źródłem prawdy,
* dane źródłowe przechowywane są w plikach CSV zapisanych w UTF-8,
* artefakty generowane nie zastępują danych źródłowych,
* dokumentacja pozostaje zsynchronizowana z kodem i danymi,
* zmiany wykonywane są w małych, logicznych pakietach,
* nowa funkcjonalność jest weryfikowana przed utworzeniem commita,
* kontrola jakości musi przejść przed połączeniem zmian z główną gałęzią.

## Status projektu

Architektura repozytorium jest stabilna.

Aktualny etap obejmuje:

* rozwój i uzupełnianie danych,
* walidację struktury i relacji,
* raportowanie jakości oraz kompletności danych,
* wyszukiwanie informacji,
* generowanie lokalnej bazy SQLite,
* automatyzację kontroli jakości,
* rozwój spójnego interfejsu narzędziowego.

<!-- dkb:documentation-baseline:readme:start -->
Zweryfikowany model obejmuje 362 testów, 34 pliki CSV, 1379 rekordów
danych, 34 relacje między tabelami, 309 wartości konfiguracji, 10
deklaratywnych specyfikacji importu oraz 419 rekordów dostępności wyposażenia.
Katalog zawiera 351 kanonicznych atrybutów i 30 kategorii atrybutów. Baza
SQLite obejmuje 34 tabele i 1379 rekordów, pozostaje zgodna z CSV, a wszystkie
źródłowe pliki CSV są zapisane jako UTF-8.
<!-- dkb:documentation-baseline:readme:end -->

## Development workflow

Projekt rozwijany jest iteracyjnie.

Każdy sprint:

* rozpoczyna się analizą aktualnego stanu gałęzi,
* obejmuje jeden spójny zakres zmian,
* dostarcza kompletne pliki,
* obejmuje lokalną weryfikację działania,
* aktualizuje dokumentację, gdy zmiana wpływa na sposób używania projektu,
* kończy się jednym logicznym commitem,
* po pushu jest automatycznie sprawdzany przez GitHub Actions.
