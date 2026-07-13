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
* katalog atrybutów: `attributes.csv`, `attribute_categories.csv`,
  `units.csv` i `value_types.csv`,
* słowniki klasyfikacyjne, w tym `body_types.csv`, `segments.csv`
  oraz pliki w `data/master/enums/`.

Ceny są zapisywane jako datowane obserwacje powiązane z konkretnym
dokumentem źródłowym. Nie są traktowane jako bezterminowa deklaracja
aktualnej oferty.

Parametry techniczne konfiguracji również są datowanymi obserwacjami
powiązanymi ze źródłem. Pięć pakietów obejmuje 168 wartości dla siedmiu
konfiguracji Sandero i Sandero Stepway. Zakres obejmuje podstawowe dane
zespołu napędowego, osiągi, masy pojazdu i przyczep, długość, szerokość,
rozstaw osi, zwisy, pojemność bagażnika oraz zużycie paliwa i emisję CO2
w cyklu WLTP.

Dla obserwacji, których znaczenie zależy od użytego paliwa, opcjonalne pole
`fuel_type_code` wskazuje jawnie LPG albo benzynę. Pozostałe obserwacje
zachowują pusty kontekst paliwa zgodnie z decyzją D-014.

Pliki CSV są podstawowym i nadrzędnym źródłem danych. Baza SQLite oraz raporty są artefaktami generowanymi na ich podstawie.

## Narzędzia

Głównym punktem wejścia jest:

```bash
python tools/dkb.py help
```

Dostępne komendy:

| Komenda      | Zastosowanie                              |
| ------------ | ----------------------------------------- |
| `validate`   | Walidacja struktury repozytorium i danych |
| `normalize`  | Kontrola kodowania plików CSV             |
| `quality`    | Pełna lokalna kontrola jakości            |
| `sqlite`     | Budowanie lokalnej bazy SQLite            |
| `sqlite-verify` | Pełna kontrola zgodności SQLite z CSV |
| `search`     | Wyszukiwanie danych w plikach CSV         |
| `stats`      | Statystyki zbiorów danych                 |
| `catalog`    | Generowanie katalogu encji                |
| `dictionary` | Generowanie słownika danych               |
| `package-start` | Synchronizacja `main` i utworzenie gałęzi pakietu |
| `package-review` | Kontrola zakresu, diffu i opcjonalnie jakości |
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
kodowanie i dane, a następnie buduje i porównuje tymczasową
bazę SQLite. Zatrzymuje się na pierwszym nieudanym etapie.
Tymczasowa baza jest automatycznie usuwana.

### Automatyzacja pakietów zmian

Rozpoczęcie pakietu synchronizuje `main`, sprawdza czystość repozytorium
oraz dostępność nazwy i tworzy nową gałąź:

```bash
python tools/dkb.py package-start tooling/example
```

Przegląd przed commitem łączy kontrolę zakresu, `diff --check`, statystyki
zmian, zawartość nowych nieśledzonych plików oraz opcjonalną pełną bramkę
jakości. `--allow` można powtarzać dla plików i katalogów dozwolonych
w pakiecie:

```bash
python tools/dkb.py package-review --allow tools --allow tests --allow README.md --quality --show-diff
```

Po utworzeniu commitu końcowa kontrola sprawdza czystość katalogu,
różnicę względem `origin/main`, listę commitów i plików oraz podaje
bezpieczne polecenie push. Sam push pozostaje operacją jawną:

```bash
python tools/dkb.py package-finish
```

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

Kontrola jest wykonywana w Pythonie 3.10 oraz 3.13 i obejmuje:

1. kompilację źródeł Pythona,
2. uruchomienie testów jednostkowych,
3. kontrolę kodowania CSV,
4. walidację repozytorium, danych i relacji między tabelami,
5. próbne zbudowanie bazy SQLite,
6. pełną kontrolę zgodności tabel, schematów kolumn i zawartości SQLite ze źródłowymi plikami CSV.

Dla Pythona 3.13 workflow zapisuje bazę SQLite oraz raport walidacji jako tymczasowy artefakt GitHub Actions przechowywany przez 7 dni.

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

Zweryfikowany punkt odniesienia po integracji PR-ów #13 i #14 na merge
commit `6224875` obejmuje 149 testów, 32 pliki CSV, 762 rekordy danych,
30 relacji między tabelami oraz 168 obserwacji konfiguracji. Baza SQLite
obejmuje 32 tabele i 762 rekordy, pozostaje zgodna z CSV, a wszystkie
źródłowe pliki CSV są zapisane jako UTF-8.

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
