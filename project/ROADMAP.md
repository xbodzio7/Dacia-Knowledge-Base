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
- samodzielny interaktywny HTML porównań z filtrowaniem i proweniencją,
- deterministyczna shortlista konfiguracji z filtrami ceny, napędu, skrzyni, miejsc i wyposażenia,
- interaktywna przeglądarkowa shortlista konfiguracji z pełnym snapshotem i testami parytetu semantyki,
- transakcyjny pakiet porównań z shortlisty z grupowaniem według jednorodnych zakresów i manifestem SHA-256,
- trwały wybór konfiguracji w przeglądarce z deterministycznym eksportem JSON i TXT zgodnym z pakietem porównań,
- interaktywna shortlista v1.2 z grupowanym wyborem wyposażenia, trwałym panelem zaznaczeń i źródłowym wyliczaniem cen pakietów,
- zależny wybór modelu i wersji, pojedynczy filtr skrzyni oraz wielokrotny filtr napędów przygotowany dla `data-products-v1.1.0`,
- kanoniczny model nazwanych pakietów i opcji oraz ośmioarkuszowy filtrowalny skoroszyt porównań,
- deterministyczny XLSX z identycznymi bajtami na Linuxie oraz Windows,
- wersjonowane, deterministyczne archiwa produktów z manifestem, SHA-256 i ręczną publikacją GitHub Release,
- pierwsze publiczne wydanie `data-products-v1.0.0` z trzema pobranymi i ponownie zweryfikowanymi assetami,
- publiczne wydanie `data-products-v1.1.0` z poprawionym selektorem HTML, 67 konfiguracjami, 17 zakresami i trzema ponownie zweryfikowanymi assetami,
- poprawka `data-products-v1.1.1` usuwająca pętlę odświeżania DOM i opóźnienia przy wyborze wyposażenia, z ponowną weryfikacją publicznych assetów,
- interaktywna shortlista HTML v1.3 z dynamicznymi fasetami wyposażenia, porównaniem wielu konfiguracji oraz deterministycznymi miniaturami modeli działającymi całkowicie offline,
- poprawka `data-products-v1.1.2` upraszczająca wybór wyposażenia do jednego filtra oraz pokazująca status seryjny, pakiet lub opcję przy cenie dopasowanego wariantu,
- pakiet przeglądarki `v1.3.0` z pionowymi filtrami, pełnym porównaniem wyposażenia, trybem „Pokaż tylko różnice”, sylwetkami modeli i datowanym intake konfiguratorów producenta,
- publiczne wydanie `data-products-v1.3.0` z pełnym porównaniem wyposażenia, pionowymi filtrami, sylwetkami modeli i niezależnie zweryfikowanymi trzema assetami,
- pierwszy import oficjalnego konfiguratora na poziomie pięciu dokładnych konfiguracji Sandero Stepway Eco-G 120, z cenami, wyróżnikami wyposażenia i jawnym zakazem przenoszenia opcji między napędami,
- publiczne wydanie `data-products-v1.4.0` z konfiguratorowym importem Stepway, trzema niezależnie zweryfikowanymi assetami i dokładnym powiązaniem tagu z zielonym commitem,
- import oficjalnych stron Sandero na poziomie czterech dokładnych stanów Eco-G 120, z dwiema nowymi konfiguracjami automatycznymi, czterema cenami, 16 wyróżnikami seryjnymi i nowym zakresem porównawczym,
- publiczne wydanie `data-products-v1.5.0` z konfiguratorowym importem Sandero, trzema niezależnie zweryfikowanymi assetami i dokładnym powiązaniem tagu z zielonym commitem,
- pakiet interfejsu `v1.6.0` z oficjalnymi zdjęciami modeli i fallbackiem offline, kaflami w stylu konfiguratora, źródłowo kompletnymi fasetami wyposażenia oraz pełnym porównaniem danych technicznych i wyposażenia,
- publiczne wydanie `data-products-v1.6.0` z trzema niezależnie zweryfikowanymi assetami, dokładnym powiązaniem tagu z zielonym commitem i audytem opublikowanego HTML,
- poprawka `data-products-v1.6.1` naprawiająca widoczne wyszukiwanie wyposażenia, zachowanie zaznaczeń i kompatybilne fasety, z niezależną weryfikacją publicznych assetów oraz dokładnego HTML,
- publiczne wydanie `data-products-v1.7.0` z 72 konfiguracjami, 19 niezależnymi zakresami, 83-elementowym archiwum, dokładnym powiązaniem tagu z zielonym commitem oraz niezależnym audytem assetów, offline workspace i opublikowanego HTML,
- publiczne wydanie `data-products-v1.8.0` z 85-elementowym archiwum, przekrojową nawigacją pięciu rodzin modeli, 19 zachowanymi zakresami, dokładnym powiązaniem tagu z zielonym commitem oraz niezależnym audytem trzech assetów i offline workspace,
- publiczne wydanie `data-products-v1.8.1` z naprawionym filtrowaniem wyposażenia, kolejnością modeli według minimalnej ceny katalogowej, niezmienionym 85-elementowym archiwum i niezależnym audytem publicznych assetów, shortlisty oraz offline workspace,
- przekrojowy import dwóch myląco niepełnych cech wyposażenia z dziewięciu oficjalnych stron wersji: 31 obserwacji anteny typu „płetwa rekina”, sześć aktualizacji składanych lusterek Joggera Journey i jawny non-import Dustera,
- trzy dokładne konfiguracje Duster Eco-G 120 automatic z oficjalnych kart samochodów, trzema cenami katalogowymi, dwoma pozytywnymi stanami składanych lusterek, dziewięcioma wartościami silnikowymi i odrębnym zakresem porównawczym,
- dokładne wyposażenie trzech automatów Duster Eco-G 120 z 203 nowymi obserwacjami, czterema źródłowo wycenionymi pakietami i odrębnymi stanami pakietów wybranych w konkretnych egzemplarzach,
- automatyczne dane homologacyjne Duster Eco-G 120: 60 wartości skalarnych i 18 przedziałów mocy, momentu, osiągów, WLTP, mas oraz holowania, bez dziedziczenia niepotwierdzonego bagażnika,
- sześć katalogowych obserwacji bagażnika ISO 3832 dla Duster Eco-G 120 automatic: 439 dm3 bez koła zapasowego i 1373 dm3 maksymalnej pojemności dla Expression, Extreme i Journey, z zachowaniem benzynowego CO2 jako niewiadomego,
- pięć zarchiwizowanych oficjalnych broszur Bigster, Jogger, Sandero, Sandero Stepway i Duster z przypiętymi SHA-256, modelowymi relacjami źródłowymi oraz audytem luk zachowującym kontekst standardu pomiaru, siedzeń, biegu i wyposażenia bagażnika,
- publiczne wydanie `data-products-v1.2.0` z dynamicznymi fasetami wyposażenia, bezpośrednim porównaniem wielu konfiguracji, offline miniaturami modeli i trzema ponownie zweryfikowanymi assetami,
- zweryfikowane pobieranie i bezpieczne rozpakowanie jawnej wersji publicznego wydania do lokalnego workspace,
- deterministyczna lokalna strona startowa HTML łącząca produkty, zakresy porównań i proweniencję wydania,
- całkowicie offline'owa i tylko do odczytu ponowna weryfikacja assetów, rozpakowanych plików, indeksu i lokalnych odnośników workspace,
- jeden źródłowy przewodnik konsumencki obejmujący pobranie, nawigację, wybór, własne porównania, proweniencję i kontrolę integralności,
- wersjonowany workflow publikacji pakietów,
- kanoniczny `project/state.json`, automatyczna synchronizacja dokumentacji i polityka `ACTION_REQUIRED`.
- źródłowy katalog, wyposażenie, oferty handlowe i techniczne specyfikacje Bigster MY26 dla 14 konfiguracji.
- deterministyczna kolejka 52 małych paczek przeglądu dla 1 266 niejednoznacznych i nierozstrzygniętych kandydatów PDF, z zachowaniem źródła, strony, tekstu i dowodów oraz bez automatycznej promocji.

## Verified tooling baseline

<!-- dkb:documentation-baseline:roadmap:start -->
- 1138 testów automatycznych,
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
- dalsze stabilne formaty raportów dla użytkowników zewnętrznych.

## Data

- dalsze pakiety, opcje i reguły zgodności po uzyskaniu jednoznacznych źródeł handlowych,
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
