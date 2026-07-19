# Dacia Knowledge Base

# Roadmap

Ten dokument opisuje trwały kierunek rozwoju projektu. Bieżący i następny pakiet nie są tutaj duplikowane.

Aktualny stan operacyjny znajduje się w:

- `project/state.json` — kanoniczny stan maszynowy,
- `project/STATE_SUMMARY.md` — generowane podsumowanie dla człowieka.

Kontrola spójności:

```bash
python tools/dkb.py project-state --check
```

---

# Vision

Celem projektu jest stworzenie kompletnej, weryfikowalnej i maszynowo czytelnej bazy wiedzy dotyczącej samochodów marki Dacia.

Repozytorium ma umożliwiać:

- przechowywanie danych technicznych i handlowych,
- powiązanie każdej obserwacji ze źródłem i datą,
- automatyczną walidację jakości i spójności,
- deterministyczne raporty kompletności, porównania i eksporty,
- eksport danych do SQLite oraz innych formatów użytkowych,
- stopniowe rozszerzanie zakresu modeli bez osłabiania modelu danych.

---

# Strategic Direction

## 1. Source-backed data quality

- utrzymywać konserwatywną zasadę niewnioskowania brakujących wartości,
- zachowywać dokładną proweniencję i kontekst obserwacji,
- rozwijać dane wyłącznie na podstawie zweryfikowanych źródeł,
- rozstrzygać niejednoznaczności przez jawne decyzje architektoniczne.

## 2. Reporting and completeness

- rozwijać porównania konfiguracji, modeli i wersji,
- poprawiać użyteczność raportów bez zmiany semantyki danych,
- utrzymywać deterministyczne katalogi kodów, filtrów i kontekstów,
- publikować artefakty jakościowe możliwe do ponownego odtworzenia.

## 3. Import automation

- rozszerzać deklaratywne importy wartości,
- automatyzować ekstrakcję PDF dopiero po zachowaniu granic dowodowych,
- oddzielać ekstrakcję kandydatów od zatwierdzonego importu do master data,
- zapewniać pełną możliwość weryfikacji i wycofania każdej operacji.

## 4. Model and source expansion

Po zamknięciu bieżących luk i wyborze źródeł rozwijać kolejno:

- Duster,
- Jogger,
- Bigster,
- Spring,
- dalsze warianty Sandero i Sandero Stepway.

---

# Completed Foundations

- stabilna struktura repozytorium i praca przez Pull Requesty,
- zunifikowany interfejs `python tools/dkb.py`,
- walidacja struktury, referencji, statusów, reguł i UTF-8,
- atomowa budowa oraz pełna weryfikacja SQLite,
- źródłowy baseline Sandero i Sandero Stepway,
- model datowanych cen, wartości technicznych i dostępności wyposażenia,
- paliwowy kontekst obserwacji LPG i benzyny,
- deklaratywne importy wartości konfiguracji,
- pipeline kompletności, pokrycia źródeł, triage, dowodów i planowania luk,
- raporty porównawcze konfiguracji i katalog kodów pozycji,
- wersjonowany workflow publikacji pakietów,
- kanoniczny `project/state.json`, automatyczna synchronizacja dokumentacji i polityka `ACTION_REQUIRED`.

## Verified tooling baseline

<!-- dkb:documentation-baseline:roadmap:start -->
- 579 testów automatycznych,
- deterministyczna komenda `documentation-baseline` z kontrolą bieżących podsumowań,
<!-- dkb:documentation-baseline:roadmap:end -->

- 34 deklarowane relacje między tabelami,
- kompatybilność kompilacji i testów w Pythonie 3.10 i 3.13,
- pełna walidacja danych, SQLite i artefaktów w Pythonie 3.13,
- kontrole stanu projektu i autonomii na Linuxie oraz Windows.

---

# Backlog

## Reporting

- wybór najwyżej wartościowego kolejnego pakietu raportowego,
- porównania modeli i wersji wykraczające poza bieżące konfiguracje,
- eksport do Excela,
- stabilne formaty raportów dla użytkowników zewnętrznych.

## Data

- pakiety i opcje po uzyskaniu źródła z jawną ofertą handlową,
- dalsze techniczne wartości konfiguracji,
- dalsze wyposażenie wersji i konfiguracji,
- rozszerzanie pokrycia źródłami.

## Import

- automatyczny potok ekstrakcji PDF,
- ekstrakcja tabel i specyfikacji,
- kontrola pochodzenia kandydatów,
- bezpieczne generowanie deklaratywnych specyfikacji importu.

## Tooling

- dalsza redukcja ręcznego powielania stanu,
- automatyczne kontrole zgodności dokumentów kontraktowych,
- czytelniejsze raportowanie przyczyn `ACTION_REQUIRED`,
- okresowe przeglądy utrzymywalności workflow.

---

# Current Work

Nazwy, cele i statusy bieżącego oraz następnego pakietu są generowane wyłącznie z `project/state.json` do `project/STATE_SUMMARY.md`.

Nie należy dodawać do tego dokumentu ręcznych sekcji `Current Sprint` ani `Next Sprint`.

---

# Historical Record

Szczegółowe dawne sekcje sprintów pozostają dostępne w historii Git oraz w `project/reviews/`.

Granica migracji została opisana w:

- `project/history/legacy-narrative-migration-2026-07-17.md`.
