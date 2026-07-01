# Dacia Knowledge Base (DKB)

Dacia Knowledge Base (DKB) to referencyjna baza wiedzy o samochodach marki Dacia.

Projekt gromadzi ustrukturyzowane dane dotyczące modeli, wersji wyposażenia, silników, skrzyń biegów, wyposażenia opcjonalnego, danych technicznych oraz źródeł informacji.

## Cele projektu

- jedno źródło prawdy dla danych o samochodach Dacia,
- normalizacja danych w postaci prostych plików CSV,
- możliwość walidacji i automatycznego importu danych,
- łatwe generowanie raportów,
- możliwość eksportu do innych systemów.

## Struktura repozytorium

```
Archiwum/          Materiały historyczne
Bigster/           Dane dotyczące modelu Bigster
Dane/              Dane źródłowe
Import/            Dane do importu
Raporty/           Raporty generowane automatycznie
Skrypty/           Narzędzia pomocnicze
project/           Dokumentacja projektu
```

## Główne zbiory danych

Docelowo repozytorium będzie zawierało między innymi:

- categories.csv
- models.csv
- versions.csv
- engines.csv
- gearboxes.csv
- attributes.csv
- attribute_values.csv
- packages.csv
- options.csv
- sources.csv

## Zasady

- repozytorium jest jedynym źródłem prawdy,
- dane przechowywane są w postaci czytelnych plików CSV,
- dokumentacja opisuje strukturę danych i proces ich utrzymania,
- zmiany wykonywane są w małych, logicznych pakietach.

## Status projektu

Architektura projektu została zakończona.

Obecny etap prac obejmuje rozwój danych, przygotowanie plików CSV, walidację oraz narzędzia wspomagające import danych.