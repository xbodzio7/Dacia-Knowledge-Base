\# DATA SCHEMA



\## Cel



Niniejszy dokument opisuje fizyczną organizację danych w Dacia Knowledge Base.



Stanowi uzupełnienie dokumentu `DATA\_MODEL.md`, który opisuje model logiczny.



\---



\# Zasady ogólne



\- Dane przechowywane są w formacie CSV.

\- Jeden plik odpowiada jednej encji lub jednemu słownikowi.

\- Nazwy plików zapisujemy w `snake\_case`.

\- Kodowanie: UTF-8.

\- Separator: przecinek (`,`).

\- Pierwszy wiersz zawiera nagłówki.



\---



\# Identyfikatory



Każdy rekord powinien posiadać:



\- techniczny identyfikator (`id`),

\- stabilny identyfikator biznesowy (`code`), jeśli ma zastosowanie.



Identyfikatory techniczne nie powinny być wykorzystywane jako dane referencyjne poza repozytorium.



\---



\# Klucze



Relacje pomiędzy encjami realizowane są przy użyciu stabilnych identyfikatorów biznesowych.



\---



\# Nazewnictwo



Nazwy plików:



\- małe litery,

\- `snake\_case`.



Nazwy kolumn:



\- małe litery,

\- `snake\_case`,

\- liczba pojedyncza.



Przykład:



```text

model\_code

engine\_code

attribute\_code

version\_code

```



\---



\# Typy danych



Preferowane typy:



\- string

\- integer

\- decimal

\- boolean

\- date



Jednostki (np. mm, kg, kW) powinny być przechowywane jako dane, a nie część nazwy kolumny.



\---



\# Wersjonowanie



Zmiany schematu powinny być kompatybilne wstecz, jeśli to możliwe.



Zmiany niekompatybilne wymagają odpowiedniej decyzji projektowej i aktualizacji dokumentacji.



\---



\# Zakres



Dokument opisuje wyłącznie sposób przechowywania danych.



Nie opisuje modelu logicznego ani procesu importu danych.

