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

* `categories.csv`,
* `models.csv`,
* `engines.csv`,
* `gearboxes.csv`,
* `model_engines.csv`,
* `model_gearboxes.csv`,
* `attributes.csv`,
* `body_types.csv`,
* `segments.csv`,
* słowniki wartości wyliczeniowych w `data/master/enums/`.

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
| `sqlite`     | Budowanie lokalnej bazy SQLite            |
| `search`     | Wyszukiwanie danych w plikach CSV         |
| `stats`      | Statystyki zbiorów danych                 |
| `catalog`    | Generowanie katalogu encji                |
| `dictionary` | Generowanie słownika danych               |

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

### Raporty

```bash
python tools/dkb.py catalog
python tools/dkb.py dictionary
```

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
6. kontrolę integralności SQLite i obecności podstawowych tabel.

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
