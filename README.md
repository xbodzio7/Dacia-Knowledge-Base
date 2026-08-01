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

## Wymagania Pythona

Projekt obecnie wymaga Pythona 3.10 lub nowszego. Wsparcie dla 3.10 jest
jednak oznaczone jako wycofywane i zostanie zakończone przed lub wraz z
upstreamowym końcem wsparcia w październiku 2026 r. Planowanym kolejnym
minimum jest Python 3.13, a dla nowych środowisk zalecany jest Python 3.14.

Aktualne minimum nie zmienia się w tym pakiecie. Szczegółową politykę,
zweryfikowane linie CI i warunki późniejszego podniesienia minimum opisuje
[`project/guides/python-runtime-support.md`](project/guides/python-runtime-support.md).

## Gotowe produkty offline

Najnowsze zweryfikowane publiczne wydanie `data-products-v1.8.1` można pobrać, sprawdzić
oraz bezpiecznie rozpakować jedną komendą:

```bash
python tools/dkb.py data-product-release-download \
  --version 1.8.1 \
  --output-directory ../dkb-data-products-v1.8.1
```

Komenda wymaga jawnej, niezmiennej wersji. Sprawdza tag GitHub, dokładny zestaw
trzech assetów, manifest, `SHA256SUMS`, każdy element archiwum i powiązanie z
commitem źródłowym. Po sukcesie tworzy lokalny `index.html` i wskazuje gotowe do
otwarcia: interaktywną shortlistę HTML, przekrojową nawigację pięciu rodzin
modeli, skoroszyt XLSX porównań, manifest pakietu i notatki wydania.

Integralność istniejącego workspace można później sprawdzić całkowicie offline
i bez modyfikowania plików:

```bash
python tools/dkb.py data-product-workspace-verify \
  --workspace-directory ../dkb-data-products-v1.8.1
```

Opcja `--json` zwraca deterministyczny raport dla automatyzacji. Weryfikator
ponownie sprawdza trzy assety, wszystkie rozpakowane pliki, dokładne bajty
`index.html` i bezpieczne lokalne odnośniki.

Pełny przepływ — od pobrania wydania przez shortlistę i własne porównania po
późniejszą kontrolę integralności — opisuje
[`project/guides/data-product-consumer-guide.md`](project/guides/data-product-consumer-guide.md).

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

Katalog Duster III obejmuje 5 aktywnych wersji i 24 źródłowo potwierdzone
kombinacje wersji, napędu i skrzyni biegów z oficjalnego cennika Dacia
Polska obowiązującego od 6 lutego 2026 r. Wszystkie 24 konfiguracje należą
do siedmiu niezależnych, jednorodnych zakresów raportowych Duster w
zamkniętym portfelu 13 zakresów dla Sandero, Duster i Jogger.

Dla wszystkich 24 konfiguracji Duster zapisano również datowane ceny katalogowe
brutto obowiązujące od 6 lutego 2026 r. Promocyjny rabat oraz korzyści finansowania
nie są cenami katalogowymi i nie zostały zaimportowane.

Techniczne tabele stron 8-9 dostarczają 392 datowane obserwacje dla 17
kanonicznych atrybutów Duster. Import zachowuje rozróżnienie LPG i benzyny,
oddzielne moce silnika spalinowego, silnika trakcyjnego i HSG oraz pomija
wartości zależne od wersji, których źródło nie przypisuje do konkretnego trimu.

Macierze wyposażenia stron 4-7 dostarczają 1 392 datowane rekordy
dostępności dla 58 kanonicznych atrybutów i 24 konfiguracji Duster.
Import zachowuje jawne statusy `standard`, `optional` i `not_available`,
a pozycje warunkowe lub bez bezpiecznego mapowania pozostawia poza zakresem.

Kompletny portfel raportowy Duster obejmuje siedem niezależnych zakresów,
24 konfiguracje, techniczny mianownik 392 obserwacji, wyposażeniowy mianownik
1 392 rekordów oraz 30 deterministycznych par porównawczych. Zakresy zachowują
odrębność napędów i skrzyń biegów; wartości, luki dowodowe, przedziały i ceny
pozostają datowane i powiązane ze źródłami.

Parametry techniczne i pozostałe wartości konfiguracji również są
datowanymi obserwacjami powiązanymi ze źródłem. Osiemnaście pakietów obejmuje
310 wartości dla siedmiu konfiguracji Sandero i Sandero Stepway: 168 bazowych
obserwacji technicznych, 30 wartości kół i tapicerki, 7 wartości koloru
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

Bieżąca broszura Spring z 19 lutego 2026 r. dostarcza bezpośrednią macierz
wyposażenia dla wersji Essential, Expression i Extreme. Import obejmuje 126
datowanych rekordów dla 42 istniejących atrybutów i trzech dokładnych
konfiguracji: 106 `standard`, 7 `optional` i 13 `not_available`. Trzy relacje
`source_configurations.csv` wiążą broszurę z dokładnymi konfiguracjami. Statusy są
odczytane z komórek stron 19-20; jawny łańcuch dziedziczenia wersji nie jest
używany do rekonstruowania brakujących danych. Pakiety handlowe, przewód typu
2, kolory, dane techniczne, Cargo oraz elementy bez bezpiecznego mapowania
pozostają poza tym pakietem.

Osobny import handlowy stron 13-15 rejestruje pięć pozycji Spring: przewód
ładowania Type 2 dla wszystkich trzech wersji, Pakiet Techno i samodzielną
opcję ładowania DC 40 kW dla Expression oraz Pakiety Power i City dla
Extreme. Obejmuje 18 powiązań z istniejącymi atrybutami i siedem dokładnych
mapowań do obecnych konfiguracji. Broszura nie podaje kwot, dlatego kwoty
i daty cen pozostają puste; techniczna waluta `PLN` spełnia wymagany klucz
schematu i nie tworzy ceny. Nie dodano modeli, wersji ani konfiguracji.

Paleta Spring ze strony 12 jest modelowana osobno jako sześć wybieralnych
opcji kolorystycznych dla trzech istniejących konfiguracji: Czerwony Brick,
Seafoam, Szary Diamond, Lichen Khaki, Niebieski Stonewash i Biel Alpejska.
Zachowano pięć lakierów niemetalizowanych i jeden metalizowany. Źródło nie
podaje ceny, koloru standardowego ani ograniczeń wersji, więc kwoty i daty
cen są puste, a pojedyncza wartość koloru konfiguracji nie jest wymyślana.

Broszura Spring z 19 lutego 2026 r. dostarcza również bezpośrednie dane techniczne dla trzech istniejących konfiguracji pasażerskich. Import obejmuje 54 wartości skalarnych i trzy domknięte zakresy obrotów mocy: po 18 wartości oraz jednym zakresie dla Essential Electric 70, Expression Electric 70 i Extreme Electric 100. Trzy minimalne pojemności bagażnika mają osobne konteksty ISO 3832 z kanapą w pozycji normalnej i główną komorą bagażową. Nie przeniesiono wartości między napędami ani wersjami.

Pakiet został wykonany przed wcześniej planowanymi lakierami Bigstera, ponieważ bezpośrednio zmniejsza liczbę pól „brak danych” w porównaniach Springa. Poza zakresem pozostały niejednoznaczne jednostki momentu i zużycia energii, ładowanie zależne od opcji, wymiary rozpoznawalne tylko z układu rysunku oraz dane Cargo.

Dwa cenniki Joggera MY26 zachowują jawną zmianę wyposażenia wersji
Expression: na stronie 5 źródła z 1 kwietnia 2026 r. światła
przeciwmgłowe są seryjne, a na stronie 4 źródła z 3 lipca 2026 r.
są niedostępne. Sześć lipcowych obserwacji `fog_lights=not_available`
uzupełnia sześć istniejących rekordów kwietniowych bez ich usuwania.
Użyto ogólnego atrybutu `fog_lights`, ponieważ źródło nie mówi, że są
to światła przednie. Nie dodano modeli, wersji ani konfiguracji.

Koła i tapicerka są modelowane jako wartości konfiguracji zgodnie z D-016.
Import rozdziela rozmiar, materiał, wzór i wykończenie koła oraz zachowuje
tapicerkę jako nazwany wariant. Dla Stepway Essential zapisano wspólny
materiał `steel` oraz źródłowy wzór `ERALIA`, potwierdzony na stronie 2
w sekcji `Felgi`. Wcześniejsza granica konfliktu została rozstrzygnięta
wyłącznie dla `wheel_design`; brak podstaw do wyprowadzania `wheel_finish`
ani drugiej aktywnej wartości wzoru.

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

Po imporcie `wheel_design = ERALIA` deterministyczny pipeline kompletności,
pokrycia źródłami, triage, przeglądu stron, klasyfikacji dowodów i planowania
obejmuje 69 aktywnych luk. Zakres techniczny zawiera 310 z 315 oczekiwanych
slotów (98,41%, 5 braków), a wyposażenie 419 z 483 slotów (86,75%, 64 braki).
Aktywne decyzje obejmują 44 wyniki `not_stated` i 25 wyników `out_of_scope`,
przy 0 `found`, 0 `ambiguous`, 0 pakietach kandydackich i 0 planowanych
wierszach. `auto_import` pozostaje wyłączony, a brak stwierdzenia w źródle nie
jest interpretowany jako wartość negatywna.

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
| `configuration-comparison` | Porównanie cen, wartości technicznych i wyposażenia konfiguracji |
| `data-product-release` | Budowa i weryfikacja wersjonowanego pakietu produktów offline |
| `data-product-release-download` | Pobranie, weryfikacja i bezpieczne rozpakowanie publicznego wydania |
| `configuration-gap-resolution-plan` | Planowanie małych pakietów rozstrzygających luki konfiguracji |
| `configuration-gap-source-review` | Weryfikacja luk na istotnych stronach zarejestrowanych PDF |
| `pdf-candidate-ledger` | Budowa i weryfikacja deterministycznego rejestru kandydatów z przypiętych broszur PDF |
| `pdf-candidate-ledger-review` | Pełny przegląd grup dowodowych i przypisań `candidate_id` bez tworzenia importów |
| `pdf-candidate-coverage-reconciliation` | Konserwatywne porównanie kandydatów technicznych i wyposażeniowych z istniejącymi dowodami |
| `pdf-candidate-residual-gap-prioritization` | Priorytetyzacja niejednoznacznych i nierozstrzygniętych kandydatów w małe paczki przeglądu |
| `bigster-technical-page20-ambiguity-review` | Autorski przegląd 23 niejednoznacznych fragmentów tabeli technicznej Bigstera |
| `bigster-technical-page20-unresolved-review-chunk1` | Autorski przegląd pierwszych 40 nierozstrzygniętych kandydatów technicznych Bigstera ze strony 20 |
| `bigster-technical-page20-unresolved-review-chunk2` | Autorski przegląd pozostałych 29 nierozstrzygniętych kandydatów technicznych Bigstera ze strony 20 |
| `jogger-technical-page19-ambiguity-review` | Autorski przegląd 16 niejednoznacznych fragmentów tabeli technicznej Joggera |
| `duster-mini-technical-page20-ambiguity-review` | Autorski przegląd 5 niejednoznacznych fragmentów tabeli technicznej minibroszury Dustera |
| `duster-mini-technical-page21-ambiguity-review` | Autorski przegląd niejednoznacznego wiersza układu kierowniczego Dustera ze strony 21 |
| `duster-mini-equipment-page23-ambiguity-review` | Autorski przegląd 26 niejednoznacznych kandydatów wyposażenia Dustera ze strony 23 |
| `duster-mini-equipment-page22-ambiguity-review` | Autorski przegląd 11 niejednoznacznych kandydatów wyposażenia Dustera ze strony 22 |
| `bigster-equipment-page22-ambiguity-review` | Autorski przegląd 7 niejednoznacznych kandydatów wyposażenia Bigstera ze strony 22 |
| `jogger-equipment-page20-ambiguity-review` | Autorski przegląd 5 niejednoznacznych kandydatów wyposażenia Joggera ze strony 20 |
| `bigster-equipment-page21-ambiguity-review` | Autorski przegląd kandydata panoramicznego dachu Bigstera ze strony 21 |
| `jogger-equipment-page21-ambiguity-review` | Autorski przegląd kandydata podgrzewanej kierownicy Joggera ze strony 21 |
| `sandero-equipment-page18-ambiguity-review` | Autorski przegląd kandydata kamery cofania Sandero ze strony 18 |
| `sandero-equipment-page19-ambiguity-review` | Autorski przegląd wspólnego wiersza regulatora i ogranicznika prędkości Sandero ze strony 19 |
| `sandero-stepway-equipment-page18-ambiguity-review` | Autorski przegląd odrębnych wierszy relingów zwykłych i modułowych Sandero Stepway ze strony 18 |
| `sandero-technical-page17-ambiguity-review` | Autorski przegląd niejednoznacznych kandydatów technicznych Sandero ze strony 17 |
| `sandero-stepway-technical-page17-ambiguity-review` | Autorski przegląd niejednoznacznych kandydatów technicznych Sandero Stepway ze strony 17 |
| `configuration-gap-evidence` | Konserwatywna klasyfikacja dowodów dla luk konfiguracji |
| `configuration-gap-triage` | Deterministyczna kolejka weryfikacji luk konfiguracji |
| `source-coverage` | Raport rejestracji źródeł, sekcji i rekordów |
| `configuration-completeness` | Raport kompletności danych aktywnych konfiguracji |
| `documentation-baseline` | Generowanie i kontrola bieżących liczników dokumentacji |
| `import-configuration-values` | Planowanie, stosowanie i weryfikacja deklaratywnych importów |
| `package-start` | Synchronizacja `main` i utworzenie gałęzi pakietu |
| `package-review` | Kontrola zakresu, diffu i opcjonalnie jakości |
| `package-publish` | Dokładny staging, jeden commit, finish i opcjonalny push |
| `package-finish` | Kontrola commitu przed pushem i Pull Requestem |


### Zweryfikowany rejestr kandydatów PDF

Pięć przypiętych oficjalnych broszur i wszystkie 114 zadeklarowanych stron
można przetworzyć do 4 256 stabilnych kandydatów tekstowych:

```bash
python tools/dkb.py pdf-candidate-ledger
python tools/dkb.py pdf-candidate-ledger --verify
```

Komenda przed ekstrakcją sprawdza ścieżkę, rozmiar, SHA-256 i liczbę stron
każdego PDF-u. Artefakty zachowują źródło, stronę, backend i zakres linii,
lecz nie tworzą danych głównych ani zatwierdzonych specyfikacji importu.
Pusta warstwa tekstowa oznacza `requires_visual_review`, nigdy `not_stated`.
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
kompletności konfiguracji, pokrycia źródłami, kolejkę triage, przegląd stron,
klasyfikację dowodów, plan rozstrzygnięcia i porównanie konfiguracji.
Zatrzymuje się na pierwszym nieudanym etapie. Tymczasowa baza jest
automatycznie usuwana.

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

### Plan rozstrzygnięcia luk konfiguracji

Komenda `configuration-gap-resolution-plan` łączy ukończony raport dowodowy
z aktualnym modelem kanonicznym, istniejącymi wartościami i deklaratywnymi
specyfikacjami importu. Każda z 69 aktywnych decyzji otrzymuje jawny stan
wykonawczy.

Wcześniejszy wynik `wheel_design = ERALIA` został wykonany jako jeden
deklaratywny wiersz ID 310 bez zmiany modelu. Bieżący plan nie zawiera pozycji
`ready_for_import`, pakietów kandydackich ani planowanych wierszy. Zamyka
44 decyzje jako `closed_not_stated` i 25 jako `closed_out_of_scope`, nie
wymaga zmiany modelu ani danych i kieruje następny krok do kamienia milowego
dokumentującego zamknięcie cyklu.

```bash
python tools/dkb.py configuration-gap-resolution-plan   --json ../configuration-gap-resolution-plan.json   --markdown ../configuration-gap-resolution-plan.md
```

Plan nie zapisuje nowych specyfikacji importu, nie modyfikuje `data/master`
i utrzymuje `auto_import = false`. Brak kandydata oznacza zamknięcie bieżącego
cyklu weryfikacji, a nie deklarację kompletności wszystkich danych pojazdu.

### Przegląd rejestru kandydatów PDF

Komenda `pdf-candidate-ledger-review` przypisuje wszystkie 4 256 kandydatów
do 30 źródłowo i stronicowo ograniczonych decyzji grupowych:

```bash
python tools/dkb.py pdf-candidate-ledger-review
python tools/dkb.py pdf-candidate-ledger-review --verify
```

Każdy kandydat występuje dokładnie raz, a 60 kotwic zachowuje `candidate_id`
i niezmieniony tekst źródłowy. Review rozdziela treści opisowe, wymagane
mapowanie encji, rekonsyliację techniki i wyposażenia, semantykę wizualną
wymiarów oraz jawne nie-importy. Nie modyfikuje `data/master` ani nie tworzy
zatwierdzonych specyfikacji w `data/imports`.

### Pojednanie pokrycia kandydatów PDF

Komenda `pdf-candidate-coverage-reconciliation` porównuje 1 583 kandydatów
z dziesięciu grup technicznych i wyposażeniowych z aktywnymi rekordami
źródłowymi:

```bash
python tools/dkb.py pdf-candidate-coverage-reconciliation
python tools/dkb.py pdf-candidate-coverage-reconciliation --verify
```

Bieżący wynik klasyfikuje 122 kandydatów jako `already_covered`, 108 jako
`ambiguous`, 1 158 jako `unresolved` i 195 jako `explicit_non_import`.
Technika wymaga zgodności źródła i strony, a wyposażenie zgodności modelu oraz
uporządkowanego tekstu. Brak dopasowania nie oznacza `not_stated` ani
`not_available`. Artefakt nie zmienia `data/master`, nie tworzy specyfikacji
w `data/imports` i nie zatwierdza automatycznej promocji.

### Priorytetyzacja pozostałych luk kandydatów PDF

Komenda `pdf-candidate-residual-gap-prioritization` dzieli wszystkie 1 266
kandydatów `ambiguous` i `unresolved` na 52 deterministyczne paczki:

```bash
python tools/dkb.py pdf-candidate-residual-gap-prioritization
python tools/dkb.py pdf-candidate-residual-gap-prioritization --verify
```

Każda paczka zachowuje jedną granicę źródła, domeny, strony i statusu oraz
zawiera najwyżej 40 kandydatów. Wszystkie identyfikatory, dokładne teksty,
zakresy linii i dowody są kopiowane bez reinterpretacji. Pierwsza paczka
obejmuje 23 niejednoznaczne wiersze techniczne z 20. strony broszury Bigster,
190 odwołań do sygnatur dowodowych i 703 odwołania do rekordów. Kolejka nie
zmienia `data/master`, nie tworzy importów i nie oznacza zatwierdzenia danych.

### Autorski przegląd tabeli technicznej Bigstera — strona 20

Komenda `bigster-technical-page20-ambiguity-review` rozstrzyga dokładnie
23 kandydatów z paczki `residual_gap_001` na podstawie układu tabeli i
zachowanych sygnatur dowodowych:

```bash
python tools/dkb.py bigster-technical-page20-ambiguity-review
python tools/dkb.py bigster-technical-page20-ambiguity-review --verify
```

Wynik obejmuje 9 kandydatów pokrytych wybranymi dowodami, 3 częściowo
pokryte fragmenty, 7 kwalifikatorów kontekstowych bez samodzielnego importu,
2 odroczenia kolumny Hybrid-G 150 4x4 oraz 2 przypadki niezgodności atrybutu
w sygnaturach heurystycznych. Wybrano 36 sygnatur i 143 dokładne rekordy.
Przegląd nie zmienia `data/master`, nie tworzy ani nie modyfikuje importów i
nie zastępuje masy pojazdu masą zestawu ani masy przyczepy z hamulcem masą
przyczepy bez hamulca.

### Autorski przegląd tabeli technicznej Joggera — strona 19

Komenda `jogger-technical-page19-ambiguity-review` rozstrzyga 16 kandydatów z `residual_gap_002` i wybiera tylko dowody przypięte do dokładnego kandydata:

```bash
python tools/dkb.py jogger-technical-page19-ambiguity-review
python tools/dkb.py jogger-technical-page19-ambiguity-review --verify
```

Wynik obejmuje 1 kandydat pokryty, 2 częściowo pokryte, 7 odroczonych konfliktów źródłowych i 6 niezgodności sygnatur. Wybrano 3 sygnatury i 28 rekordów. Sprzeczne etykiety mas, starsze 105 kW Hybrid 155 i dowody przyspieszenia przypięte do innych atrybutów pozostają nieimportowalne. `data/master` i `data/imports` nie są zmieniane.

### Autorski przegląd tabeli technicznej minibroszury Dustera — strona 20

Komenda `duster-mini-technical-page20-ambiguity-review` rozstrzyga 5 kandydatów z `residual_gap_003` na podstawie układu tabeli i dokładnie przypiętych dowodów:

```bash
python tools/dkb.py duster-mini-technical-page20-ambiguity-review
python tools/dkb.py duster-mini-technical-page20-ambiguity-review --verify
```

Wynik obejmuje 3 kandydatów pokrytych i 2 częściowo pokryte. Wybrano 9 sygnatur oraz 34 rekordy. Wartości Hybrid 155 ze strony 21 i sygnatury przypięte do sąsiedniego kandydata nie są podstawiane do fragmentów strony 20. Kolejność `Maks./min.` ładowności jest zachowana bez semantycznego przemianowania końców przedziału. `data/master` i `data/imports` nie są zmieniane.


### Autorski przegląd tabeli technicznej Sandero — strona 17

Komenda `sandero-technical-page17-ambiguity-review` rozstrzyga 5 kandydatów z `residual_gap_004` na podstawie wizualnego układu tabeli i dokładnie przypiętych dowodów:

```bash
python tools/dkb.py sandero-technical-page17-ambiguity-review
python tools/dkb.py sandero-technical-page17-ambiguity-review --verify
```

Wszystkie 5 kandydatów pozostaje częściowo pokrytych. Wybrano 8 sygnatur i 16 rekordów: pary LPG/benzyna dla mocy i momentu automatu, dwie masy własne Eco-G oraz osobne masy pojazdu i zespołu pojazdów. Wartości TCe i manualnego Eco-G bez przypiętych rekordów pozostają faktami źródłowymi, a dowody `gross_vehicle_weight` i `gross_train_weight` nie są zamieniane między powtarzającymi się fragmentami etykiet. `data/master` i `data/imports` nie są zmieniane.

### Autorski przegląd tabeli technicznej Sandero Stepway — strona 17

Komenda `sandero-stepway-technical-page17-ambiguity-review` rozstrzyga 4 kandydatów z `residual_gap_005` na podstawie wizualnego układu tabeli i dokładnie przypiętych dowodów:

```bash
python tools/dkb.py sandero-stepway-technical-page17-ambiguity-review
python tools/dkb.py sandero-stepway-technical-page17-ambiguity-review --verify
```

Trzy kandydaty są częściowo pokryte, a fragment linii 80 pozostaje nierozstrzygniętym błędem sygnatury. Wybrano 5 sygnatur i 15 rekordów: średnicę zawracania 10,64 m oraz masy 1225 i 1249 kg dla dwóch fragmentów maksymalnej masy własnej. Dowody zawieszenia, opon i mas nie są podstawiane do etykiety układu kierowniczego, a maksymalne masy nie są przenoszone do fragmentu minimalnej masy 1095/1194/1222 kg. `data/master` i `data/imports` nie są zmieniane.

### Autorski przegląd tabeli technicznej Duster Mini — strona 21

Komenda `duster-mini-technical-page21-ambiguity-review` rozstrzyga pojedynczego kandydata z `residual_gap_006` na podstawie wizualnego układu tabeli i dokładnie przypiętych dowodów:

```bash
python tools/dkb.py duster-mini-technical-page21-ambiguity-review
python tools/dkb.py duster-mini-technical-page21-ambiguity-review --verify
```

Kandydat pozostaje częściowo pokryty. Wybrano wyłącznie sygnaturę elektrycznego wspomagania układu kierowniczego z 3 rekordami Hybrid 155. Średnica zawracania, hamulce, opony, masa własna i ładowność należą do innych wierszy i nie są podstawiane. Identyczna wartość w kolumnie Hybrid-G 150 4×4 pozostaje faktem źródłowym bez przypiętych rekordów. `data/master` i `data/imports` nie są zmieniane.


### Autorski przegląd wyposażenia Duster Mini — strona 23

Komenda `duster-mini-equipment-page23-ambiguity-review` rozstrzyga 26 kandydatów z `residual_gap_007` na podstawie wizualnego układu macierzy oraz dokładnie przypiętych dowodów:

```bash
python tools/dkb.py duster-mini-equipment-page23-ambiguity-review
python tools/dkb.py duster-mini-equipment-page23-ambiguity-review --verify
```

Sześć pełnych wierszy jest pokrytych, a 20 fragmentów wielowierszowych pozostaje częściowo pokrytych. Wybrano 43 sygnatury i 518 rekordów. Symbole `•`, `¤` i `-` zachowują znaczenie standardu, opcji i niedostępności; element pakietu nie staje się wyposażeniem standardowym. Dowody `one_touch_windows`, regulacji lędźwiowej, zwykłego regulatora prędkości i innych sąsiednich atrybutów nie są podstawiane do analizowanych wierszy. `data/master` i `data/imports` nie są zmieniane.

### Autorski przegląd wyposażenia Duster Mini — strona 22

Komenda `duster-mini-equipment-page22-ambiguity-review` rozstrzyga 11 kandydatów z `residual_gap_008` na podstawie wizualnego układu macierzy oraz dokładnie przypiętych dowodów:

```bash
python tools/dkb.py duster-mini-equipment-page22-ambiguity-review
python tools/dkb.py duster-mini-equipment-page22-ambiguity-review --verify
```

Trzy pełne wiersze są pokryte, a osiem fragmentów wielowierszowych pozostaje częściowo pokrytych. Wybrano 23 sygnatury i 524 rekordy. Automatyczne światła nie dziedziczą dowodów czujnika deszczu, tylny czujnik parkowania nie dziedziczy dowodu przedniego, a opcjonalne czujniki przednie i boczne nie są przepisywane jako standard. Wiersze ESC/HSA oraz pasów z napinaczami i bez regulacji wysokości zachowują odrębne atrybuty we wspólnych granicach wizualnych. `data/master` i `data/imports` nie są zmieniane.

### Autorski przegląd wyposażenia Bigster — strona 22

Komenda `bigster-equipment-page22-ambiguity-review` rozstrzyga 7 kandydatów z `residual_gap_009` na podstawie wizualnego układu macierzy oraz dokładnie przypiętych dowodów:

```bash
python tools/dkb.py bigster-equipment-page22-ambiguity-review
python tools/dkb.py bigster-equipment-page22-ambiguity-review --verify
```

Trzy pełne wiersze są pokryte, a cztery fragmenty wielowierszowych opisów pozostają częściowo pokryte. Zachowano wszystkie 18 sygnatur i 126 rekordów. Klimatyzacja automatyczna, dwustrefowość i nawiewy z tyłu pozostają odrębnymi faktami jednego wiersza; warianty konsoli centralnej nie są łączone; kierownica i szyba z pakietów zimowych pozostają opcjonalne albo niedostępne, a nie standardowe. `data/master` i `data/imports` nie są zmieniane.

### Autorski przegląd wyposażenia Jogger — strona 20

Komenda `jogger-equipment-page20-ambiguity-review` rozstrzyga 5 kandydatów z `residual_gap_010` na podstawie wizualnego układu macierzy oraz dokładnie przypiętych dowodów:

```bash
python tools/dkb.py jogger-equipment-page20-ambiguity-review
python tools/dkb.py jogger-equipment-page20-ambiguity-review --verify
```

Trzy fragmenty wielowierszowych opisów są częściowo pokryte. Końcowa klauzula o dezaktywacji poduszki pasażera pozostaje kontekstem bez importu, ponieważ przypięte sygnatury opisują wyłącznie obecność poduszek. Pełny wiersz kamery cofania pozostaje odroczonym konfliktem: broszura z 17.12.2025 oznacza Journey jako niedostępne, a cennik z 01.04.2026 zawiera Journey jako standard. Zachowano 8 sygnatur i 154 rekordy bez automatycznego rozstrzygnięcia konfliktu. `data/master` i `data/imports` nie są zmieniane.

### Autorski przegląd wyposażenia Bigster — strona 21

Komenda `bigster-equipment-page21-ambiguity-review` rozstrzyga pojedynczy kandydat z `residual_gap_011`:

```bash
python tools/dkb.py bigster-equipment-page21-ambiguity-review
python tools/dkb.py bigster-equipment-page21-ambiguity-review --verify
```

Kompletny wiersz otwieranego panoramicznego dachu jest pokryty wszystkimi 3 sygnaturami i 14 rekordami. Essential i Expression pozostają niedostępne, Journey opcjonalne, a Extreme standardowe. Symbol opcji Journey nie jest przepisywany jako standard ani zatwierdzenie importu. `data/master` i `data/imports` nie są zmieniane.

### Przegląd stron źródłowych dla luk konfiguracji

Komenda `configuration-gap-source-review` ponownie wylicza decyzje dla 44
aktywnych pozycji wskazanych w wersjonowanej specyfikacji. Każdy PDF jest
sprawdzany przez rejestr źródeł i SHA-256. Ekstrakcja wybiera najlepiej
skalibrowany tekst strony na podstawie istniejących kotwic proweniencji.

Bieżący wynik obejmuje 0 decyzji `found`, 44 decyzje `not_stated` i 0
`ambiguous`; 25 decyzji `out_of_scope` pozostaje poza przeglądem stron.
Przejrzano 19 par źródło–strona w siedmiu dokumentach, bez niekompletnych
ekstrakcji i bez wartości kandydackich. Wykonany wynik `ERALIA` został usunięty
z aktywnej kolejki po źródłowym imporcie.

```bash
python tools/dkb.py configuration-gap-source-review \
  --verify \
  --json ../configuration-gap-source-review.json \
  --markdown ../configuration-gap-source-review.md
```

Reguły przeglądu są wersjonowane w
`data/reporting/configuration_gap_source_review.json`. Brak dopasowania na
wszystkich istotnych stronach daje `not_stated`; wiele różnych dopasowań albo
niedostateczna ekstrakcja pozostawiają `ambiguous`. Automatyczny import jest
wyłączony.

### Przegląd dowodowy luk konfiguracji

Komenda `configuration-gap-evidence` łączy wersjonowaną specyfikację decyzji
z dokładną kolejką `configuration-gap-triage`. Każda decyzja zachowuje
konfigurację, źródło, datę dokumentu, ścieżkę i SHA-256.

Bieżąca specyfikacja obejmuje 69 aktywnych decyzji: 0 `found`, 44
`not_stated`, 25 `out_of_scope` i 0 `ambiguous`. Nie ma kandydatów importu ani
pozycji wymagających dalszego ręcznego przeglądu stron. Wcześniejszy wynik
`wheel_design = ERALIA` został zamknięty przez kontrolowany import ID 310.

```bash
python tools/dkb.py configuration-gap-evidence   --json ../configuration-gap-evidence.json   --markdown ../configuration-gap-evidence.md
```

Klasyfikacje `found` i `not_stated` zachowują odpowiednio dokładny tekst
źródłowy albo listę przejrzanych stron. `auto_import` pozostaje wyłączony.

### Triage luk konfiguracji

Komenda `configuration-gap-triage` łączy raport kompletności z raportem
pokrycia źródłami. Oba wejścia muszą wskazywać dokładnie ten sam zestaw luk,
datę, konfigurację, źródło, kategorię, atrybut i kontekst paliwa.

Kolejka obejmuje 69 brakujących rekordów przy 0 brakujących źródłach:
5 kandydatów technicznych i 64 kandydatów wyposażenia. Ma neutralny,
leksykograficzny porządek służący wyłącznie powtarzalności; nie jest to
priorytet biznesowy. Każdy wpis otrzymuje stan
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

Bieżący snapshot obejmuje siedem aktywnych konfiguracji i siedem źródeł.
Zakres techniczny ma 310 z 315 slotów, 5 braków i pokrycie 98,41%.
Wyposażenie ma 419 z 483 slotów, 64 braki i pokrycie 86,75%, w tym 389
rekordów `standard` oraz 30 `not_available`.

### Shortlista konfiguracji

Komenda `configuration-shortlist` filtruje wszystkie aktywne konfiguracje na
podstawie jawnych kryteriów użytkowych, zachowując daty i źródła ceny, liczby
miejsc oraz wymaganego wyposażenia. Wyniki są uporządkowane według ceny
katalogowej, modelu, wersji i kodu konfiguracji.

```bash
python tools/dkb.py configuration-shortlist \
  --transmission automatic \
  --max-price 100000 \
  --require-equipment rear_view_camera \
  --json ../configuration-shortlist.json \
  --markdown ../configuration-shortlist.md \
  --csv ../configuration-shortlist.csv \
  --html ../configuration-shortlist.html
```

Dostępne kryteria obejmują dokładne kody modelu i wersji, typ skrzyni,
fragment nazwy napędu, minimalną i maksymalną cenę katalogową brutto w PLN,
liczbę miejsc oraz dwa poziomy wymagań wyposażenia. Powtarzane wartości
modelu, wersji, skrzyni i napędu są łączone przez OR, a różne wymiary filtrów
i wymagania wyposażenia przez AND.

`--require-equipment` akceptuje status `standard` albo `optional`, natomiast
`--require-standard-equipment` wyłącznie `standard`. Brak źródłowego
stwierdzenia nie spełnia kryterium i jest raportowany osobno od
`not_available`. Analogicznie brak ceny lub liczby miejsc pozostaje jawną
niewiadomą, a nie wartością domyślną.

JSON zawiera pełne filtry, niełączne statystyki przyczyn wykluczeń i liczniki
niewiadomych. Markdown dostarcza czytelną shortlistę, a CSV jeden płaski wiersz
na dopasowaną konfigurację z proweniencją ceny, miejsc i wyposażenia.

HTML osadza pełny aktywny snapshot dla wskazanej daty, a kryteria CLI
ustawiają początkowy stan formularza. Wyczyszczenie filtrów przywraca cały
katalog, podczas gdy JSON, Markdown i CSV pozostają wynikami filtrów
wykonanych po stronie Pythona. Plik działa bez serwera i nie pobiera
zewnętrznych skryptów, stylów ani fontów.

Każda karta w przeglądarce może zostać jawnie wybrana do porównania. Wybór jest
niezależny od filtrów: ukryte konfiguracje pozostają zaznaczone, a akcje
`Wybierz widoczne`, usuwanie pojedynczych pozycji i `Wyczyść wybór` nie
zmieniają kryteriów shortlisty. Panel wyboru zachowuje deterministyczną
kolejność katalogu.

Interfejs v1.2 zastępuje natywne listy wielokrotnego wyboru wyposażenia grupami przycisków. Wybrane elementy pozostają widoczne nad przewijaną listą jako usuwalne etykiety, a tryb `Pokaż tylko wybrane` pozwala szybko sprawdzić aktywne kryteria. Karty konfiguracji pokazują nazwane pakiety i opcje oraz wyliczają najtańszy źródłowo udokumentowany zestaw pokrywający wybrane wyposażenie.

W interfejsie przygotowanym dla wydania `data-products-v1.1.0` modele są wyświetlane bez wewnętrznych kodów w nawiasach. Lista wersji pojawia się dopiero po wybraniu modelu i zawiera wyłącznie wersje tego modelu. Skrzynia biegów jest filtrem pojedynczego wyboru, natomiast napędy tworzą stabilną listę wielokrotnego wyboru.

`Pobierz JSON` zapisuje wybór w formacie bezpośrednio obsługiwanym przez
`configuration-comparison-bundle`, wraz z datą snapshotu i metadanymi
źródłowymi ceny oraz liczby miejsc. `Pobierz kody TXT` zapisuje jeden dokładny
kod konfiguracji na linię. Eksport nie zawiera czasu uruchomienia, dlatego ten
sam snapshot i wybór tworzą identyczne bajty.

### Pakiet porównań z shortlisty

Komenda `configuration-comparison-bundle` łączy jawnie wybrane konfiguracje z
istniejącymi, jednorodnymi zakresami raportowymi. Przyjmuje powtarzalne kody
konfiguracji oraz raporty JSON wygenerowane przez `configuration-shortlist`.
Ich suma jest deterministycznie deduplikowana.

```bash
python tools/dkb.py configuration-comparison-bundle \
  --shortlist-json ../configuration-shortlist.json \
  --configuration-code duster_iii_expression_ecog100_4x2_manual \
  --output-directory ../comparison-bundle
```

Wybrane konfiguracje są grupowane według 17 bieżących specyfikacji
kompletności. Grupy zawierające co najmniej dwie konfiguracje generują
istniejące raporty JSON, Markdown, CSV różnic i interaktywny HTML. Grupy
jednoelementowe są zapisane jako singletony bez sztucznego porównania.
Konfiguracje z różnych zakresów nigdy nie tworzą wspólnej pary.

Dla każdej porównywalnej grupy filtrowane są zarówno wpisy konfiguracji w
specyfikacji kompletności, jak i decyzje w specyfikacji dowodowej. Mianowniki,
algorytm par i klasyfikacje dowodowe pozostają bez zmian, a istniejący silnik
porównawczy wykonuje raporty bez osłabienia walidacji.

Publikacja katalogu jest transakcyjna. Niepusty katalog wyjściowy nie jest
nadpisywany, a błąd wejścia lub raportowania nie pozostawia częściowego
pakietu. `comparison-bundle-manifest.json` zawiera wybór, grupy, singletony,
liczby par i różnic oraz ścieżki, rozmiary i SHA-256 wszystkich raportów. Pole
`cross_scope_pairs_generated` zawsze ma wartość `false`.

Pakiet tworzy także deterministyczny skoroszyt XLSX z ośmioma arkuszami. Oprócz pełnych stanów porównań i proweniencji zawiera filtrowalne arkusze `Equipment` oraz `Commercial Offers`, które pokazują wyposażenie, pakiety, opcje, ceny i źródła dla wybranych konfiguracji. Szczegółowy kontrakt wersji 1.2 opisuje `project/packages/commercial-options-equipment-filters-workbook-v1.2.md`.

### Wersjonowana dystrybucja produktów

Komenda `data-product-release` buduje jeden deterministyczny kandydat wydania
obejmujący kompletną shortlistę 67 aktywnych konfiguracji i pełny pakiet
porównań dla 17 niezależnych zakresów.

```bash
python tools/dkb.py data-product-release \
  --version 1.0.0 \
  --commit-sha 0123456789012345678901234567890123456789 \
  --output-directory ../data-product-release
```

Powstają dokładnie trzy assety: wersjonowane archiwum ZIP, zewnętrzny
`data-product-release-manifest.json` i `SHA256SUMS`. Archiwum bieżącego snapshotu zawiera 75 plików:
shortlistę JSON, Markdown, CSV i HTML, 17 grup raportowych, manifest bundle oraz
ośmioarkuszowy XLSX. Manifest zachowuje rozmiary, typy MIME i SHA-256 każdego
pliku; nie jest kopiowany do ZIP, aby uniknąć samoodniesienia hashu archiwum.

Tryb `--verify` sprawdza istniejący katalog bez przebudowy. Workflow
`Versioned Data Product Release` buduje read-only kandydat na Pull Requestach,
a utworzenie tagu `data-products-vMAJOR.MINOR.PATCH` i GitHub Release jest
możliwe wyłącznie przez ręczny `workflow_dispatch` z `main`. Istniejące tagi i
wydania nie są nadpisywane. Pełny kontrakt opisuje
`project/packages/versioned-data-product-release-publication.md`.

Pierwsze publiczne wydanie zostało opublikowane jako [`data-products-v1.0.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.0.0) z commita `653ddacf9dcaeefa356f53e3c00e71666f5c5b3e`. Trzy publiczne assety zostały ponownie pobrane, zweryfikowane przez `data-product-release --verify` i zapisane w `project/releases/data-products-v1.0.0.md`.

Wydanie [`data-products-v1.1.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.1.0) zostało opublikowane z dokładnego commita `397958ba740c0b3b9370822d7e1d473c4829c11e`. Obejmuje 67 konfiguracji, 17 zakresów i poprawiony samodzielny selektor HTML. Wszystkie trzy publiczne assety zostały ponownie pobrane i zweryfikowane; trwały zapis znajduje się w `project/releases/data-products-v1.1.0.md`.

Poprawka [`data-products-v1.1.1`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.1.1) została opublikowana z dokładnego commita `b333f74e8426993e797a79c2e8621bd2f0f7bf4e`. Usuwa zawieszanie przeglądarki przy wyborze wyposażenia, zachowując ten sam zestaw 67 konfiguracji, 17 zakresów, dane źródłowe i semantykę porównań. Trwały zapis znajduje się w `project/releases/data-products-v1.1.1.md`.

Poprawka [`data-products-v1.1.2`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.1.2) została opublikowana z dokładnego commita `8b08dbd8d846610577437c150a0d39aeb3d868f4`. Udostępnia jeden filtr wyposażenia, a przy cenie każdego pasującego wariantu pokazuje, czy wybrany element jest seryjny, znajduje się w pakiecie, jest osobną opcją albo ma nieustaloną dopłatę. Trwały zapis znajduje się w `project/releases/data-products-v1.1.2.md`.

Wydanie [`data-products-v1.2.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.2.0) zostało opublikowane z dokładnego commita `2982ff68b8e1f3097403d96afd1754ae473c2aa3`. Dynamicznie ukrywa wyposażenie niedostępne w bieżącej grupie wariantów, zapobiega wyzerowaniu wyników przez niemożliwą kombinację, porównuje dowolną liczbę zaznaczonych konfiguracji bezpośrednio w HTML i pokazuje offline miniatury modeli. Trwały zapis znajduje się w `project/releases/data-products-v1.2.0.md`.

Wydanie [`data-products-v1.3.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.3.0) zostało opublikowane z dokładnego commita `beb2151853b2d3de8837ff7c5e8d2b55b78af76e`. Układa filtry pionowo, pokazuje rozpoznawalne sylwetki modeli i wersji, przenosi nazwę samochodu na górę karty, porównuje całe źródłowo opisane wyposażenie oraz udostępnia tryb „Pokaż tylko różnice”. Rejestruje też oficjalne konfiguratory Dacia Polska jako datowane, zmienne źródła do późniejszego importu opcji i dopłat. Trwały zapis znajduje się w `project/releases/data-products-v1.3.0.md`.

Wydanie [`data-products-v1.4.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.4.0) zostało opublikowane z dokładnego commita `85fff3f69cae97de900bf9422f2418de9f8335ee`. Dodaje pięć aktualnych cen oficjalnych konfiguracji Sandero Stepway Eco-G 120 oraz 24 bezpośrednio potwierdzone obserwacje wyposażenia seryjnego. Pakiet MEDIA DISPLAY widoczny w domyślnym stanie TCe 110 pozostaje jawnym non-importem i nie jest przypisywany do Eco-G bez dowodu. Trwały zapis znajduje się w `project/releases/data-products-v1.4.0.md`.

Wydanie [`data-products-v1.5.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.5.0) zostało opublikowane z dokładnego commita `7f325d254b68eb495204c01c075727ee34893e1f`. Dodaje cztery oficjalnie potwierdzone stany Sandero Eco-G 120 Expression/Journey z ręczną lub automatyczną skrzynią, cztery aktualne ceny katalogowe, 16 obserwacji wyposażenia seryjnego oraz osobny zakres porównawczy automatów. Niepotwierdzone pakiety i opcje domyślnego Essential TCe 100 pozostają jawnymi non-importami. Trwały zapis znajduje się w `project/releases/data-products-v1.5.0.md`.

Wydanie [`data-products-v1.6.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.6.0) zostało opublikowane z dokładnego commita `539fba58d1ee2ef538c782b20e049be482d72988`. Używa oficjalnych zdjęć pięciu rodzin modeli Dacia Polska z lokalnym fallbackiem SVG, przedstawia wybory w stylu konfiguratora, umieszcza ceny minimalną i maksymalną w jednym wierszu, pokazuje wyłącznie źródłowo kompletne i rzeczywiście różnicujące wyposażenie oraz porównuje wszystkie zapisane parametry techniczne i wyposażenie. Trwały zapis publikacji znajduje się w `project/releases/data-products-v1.6.0.md`.

Poprawka [`data-products-v1.6.1`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.6.1) została opublikowana z dokładnego commita `4b77571c788b862a6543161b9343a35f464bd7c6`. Pole „Filtruj listę wyposażenia” rzeczywiście ukrywa niedopasowane nazwy, wybrane pozycje pozostają aktywne do jawnego usunięcia, a lista oferuje wyłącznie źródłowo kompletne dodatki zgodne z bieżącym wyborem. Alternatywy wzajemnie się wykluczające są ukrywane, natomiast braki danych o opcjach innych modeli nadal pozostają niewiadomą. Trwały zapis publikacji znajduje się w `project/releases/data-products-v1.6.1.md`, a opis poprawki w `project/packages/equipment-facet-interaction-fix.md`.

Najnowsze wydanie [`data-products-v1.7.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.7.0) zostało opublikowane z dokładnego commita `99e0e19b86cad6eae619f37702464e6a5a761cd8`. Obejmuje 72 aktywne konfiguracje, 19 niezależnych zakresów, 114 par i 1695 różnic w 83-elementowym archiwum JSON, Markdown, CSV, HTML i XLSX. Publiczne assety, tag, offline workspace oraz dokładny HTML zostały ponownie pobrane i niezależnie zweryfikowane. Trwały zapis publikacji znajduje się w `project/releases/data-products-v1.7.0.md`.

Bieżący przekrojowy import wyposażenia zapisuje 31 dokładnych obserwacji fabrycznej anteny typu „płetwa rekina” dla Sandero, Sandero Stepway i Joggera oraz sześć nowszych obserwacji seryjnych elektrycznie składanych lusterek dla Joggera Journey. Wersje z jawnie wskazaną anteną biczową otrzymują status fabrycznej płetwy `not_available`; akcesoria, nieudowodnione rozszerzenia pakietów i niejednoznaczne stany Dustera pozostają poza importem. Szczegóły zawiera `project/packages/official-configurator-cross-model-option-coverage-20260724.md`.

Najnowszy import Dustera dodaje trzy dokładne konfiguracje Eco-G 120 z automatyczną skrzynią: Expression, Extreme i Journey. Zapisuje jawne ceny katalogowe 96 900 zł, 110 300 zł i 107 600 zł, seryjne składane lusterka dla Extreme i Journey oraz trzy cechy silnika wspólne dla dokładnie potwierdzonego automatu: 1199 cm³, trzy cylindry i 12 zaworów. Sprzeczny stan lusterek Expression, typ anteny, masa przyczepy i bagażnik pozostają niewiadomą. Szczegóły zawiera `project/packages/duster-ecog120-automatic-stock-intake-20260724.md`.

Najnowsze rozszerzenie dokładnych konfiguracji Dustera zapisuje 203 nowe datowane obserwacje wyposażenia dla automatów Expression, Extreme i Journey bez kopiowania danych z wersji manualnych. Nowy import zawiera 199 stanów `standard` i 4 jawne `not_available`; dwa wcześniejsze seryjne stany składanych lusterek Extreme i Journey są ponownie używane bez duplikacji. Pakiety PARKING i ZIMOWY PLUS dla Extreme i Journey mają osobne rekordy dostępności/ceny z oficjalnego cennika oraz późniejsze rekordy potwierdzające wybór w konkretnych egzemplarzach. Antena i składane lusterka Expression pozostają nierozstrzygnięte. Szczegóły zawiera `project/packages/duster-exact-stock-equipment-expansion-20260725.md`.

Kolejny pakiet uzupełnia te trzy automaty o 60 dokładnych wartości i 18 przedziałów technicznych potwierdzonych na oficjalnych kartach automatycznego Eco-G 120. Obejmuje moc i moment dla benzyny/LPG, osiągi, spalanie, masy, ładowność oraz holowanie; pojemność bagażnika i emisja CO2 dla benzyny nadal pozostają niewiadome. Szczegóły zawiera `project/packages/duster-ecog120-automatic-homologation-evidence-20260725.md`.

Następny pakiet zamyka lukę bagażnika automatów na podstawie oficjalnego polskiego cennika MY26: każda z konfiguracji Expression, Extreme i Journey otrzymuje 439 dm3 ISO 3832 bez koła zapasowego oraz 1373 dm3 maksymalnej pojemności. Wartość 123 g/km z kolumny dwupaliwowej nie jest przypisywana benzynie bez jawnego rozdzielenia paliwa. Szczegóły zawiera `project/packages/duster-ecog120-automatic-cargo-emissions-review-20260725.md`.

Kolejny pakiet archiwizuje i rejestruje pięć oficjalnych polskich broszur Dacii: Bigster, Jogger, Sandero, Sandero Stepway i Duster. Broszury są powiązane wyłącznie z modelami, a audyt klasyfikuje wartości powtarzające istniejące źródła, dane wymagające kontekstu biegu, układu siedzeń lub standardu pomiaru oraz jawne zakazy importu. W tym pakiecie nie dodano żadnych obserwacji technicznych. Szczegóły zawierają `project/packages/official-dacia-brochure-source-registration-20260725.md` i `project/reviews/official-dacia-brochure-gap-review-2026-07-25.md`.

Bieżące dane główne zawierają pierwszy import na poziomie konkretnej konfiguracji z oficjalnych stron Sandero Stepway: pięć aktywnych stanów Eco-G 120 z cenami obserwowanymi 23 lipca 2026 r. oraz wyłącznie te wyróżniki wyposażenia, które producent pokazuje dla odpowiedniej wersji. Pakiet widoczny w domyślnym konfiguratorze TCe 110 nie jest automatycznie przypisywany do Eco-G. Szczegóły znajdują się w `project/packages/official-configurator-sandero-stepway-configuration-import.md`.

Bieżący pakiet rozszerza zwykłe Sandero do czterech oficjalnie potwierdzonych stanów Eco-G 120: Expression i Journey z ręczną lub automatyczną skrzynią. Dodaje dwie konfiguracje automatyczne, cztery ceny obserwowane 23 lipca 2026 r. i wyłącznie wyróżniki wyposażenia pokazane na odpowiadających stronach wersji. Pakiety z ogólnych stron wyposażenia oraz opcje domyślnego Essential TCe 100 pozostają nieprzypisane bez dowodu dla dokładnej konfiguracji. Szczegóły znajdują się w `project/packages/official-configurator-sandero-configuration-import.md`.

Dla użytkownika końcowego preferowaną ścieżką jest komenda
`data-product-release-download`. Pobiera ona dokładnie wskazaną wersję, rozwiązuje
tag do commita, weryfikuje trzy publiczne assety istniejącym kontraktem i zapisuje
zweryfikowane pliki w `assets/`, a bezpiecznie rozpakowane produkty w `contents/`.
Szczegóły opisuje `project/packages/verified-data-product-release-download-cli.md`.

### Porównanie konfiguracji

Komenda `configuration-comparison` generuje deterministyczny raport JSON,
Markdown i samodzielny interaktywny HTML dla wszystkich par aktywnych
konfiguracji oraz opcjonalny płaski CSV zawierający wyłącznie rzeczywiste różnice. Bieżący zakres siedmiu
konfiguracji tworzy 21 par i 305 wierszy różnic.

```bash
python tools/dkb.py configuration-comparison \
  --json ../configuration-comparison.json \
  --markdown ../configuration-comparison.md \
  --csv ../configuration-comparison-differences.csv \
  --html ../configuration-comparison.html
```

JSON, Markdown i HTML pozostają pełnymi formatami: zawierają stany równe,
`different` oraz `not_comparable`. HTML zawiera wbudowane style i skrypt
filtrowania, działa bez serwera i nie pobiera zewnętrznych zasobów. CSV jest
eksportem użytkowym i pomija wszystkie wyniki inne niż `different`.

Każdy wiersz CSV zachowuje:

- kod i typ pary,
- domenę oraz kod i nazwę atrybutu albo wymiar ceny,
- kategorię, kontekst paliwa lub rynku i jednostkę,
- konfigurację, wersję i typ skrzyni po obu stronach,
- oba stany, wartości, źródła oraz daty obserwacji,
- różnicę kwotową dla cen bez wyliczania różnic technicznych.

Opcjonalny `--difference-domain` ogranicza wyłącznie płaski CSV do jednej
kontrolowanej domeny: `prices`, `technical` albo `equipment`. Pełny CSV
pozostaje zachowaniem domyślnym. Filtr nie zmienia JSON, Markdown, podsumowań
raportu ani globalnego snapshotu dowodowego.

```bash
python tools/dkb.py configuration-comparison \
  --difference-domain prices \
  --csv ../configuration-comparison-price-differences.csv
```

Bieżący pełny zakres daje 21 cenowych, 260 technicznych albo 24 wyposażeniowe
wiersze po wybraniu pojedynczej domeny.

Opcjonalny `--difference-item-code` ogranicza wyłącznie płaski CSV do jednego
dokładnego kodu pozycji znanego pełnemu aktywnemu raportowi. Bieżący raport
zawiera 109 poprawnych kodów bez kolizji między domenami. Nieznany kod jest
odrzucany, natomiast poprawny kod bez różnic po zastosowaniu innych filtrów
tworzy prawidłowy CSV zawierający sam nagłówek.

```bash
python tools/dkb.py configuration-comparison \
  --difference-domain technical \
  --difference-item-code co2_emissions \
  --csv ../configuration-comparison-co2-differences.csv
```

Bieżący `co2_emissions` daje 34 wiersze w pełnym raporcie.

Opcjonalny `--pair-type` ogranicza wszystkie trzy wyjścia do jednej istniejącej
klasy pary:

- `same_version_different_transmission`,
- `different_version_same_transmission`,
- `same_version_same_transmission`,
- `different_version_different_transmission`.

Filtry `--pair-type`, `--difference-domain` i `--difference-item-code` można
łączyć. Pierwszy ogranicza pary i przelicza pełny raport, natomiast dwa
pozostałe filtrują wyłącznie wiersze CSV.

```bash
python tools/dkb.py configuration-comparison \
  --pair-type same_version_different_transmission \
  --difference-domain technical \
  --difference-item-code co2_emissions \
  --json ../configuration-comparison-transmission.json \
  --markdown ../configuration-comparison-transmission.md \
  --csv ../configuration-comparison-transmission-co2-differences.csv
```

Bieżący filtr skrzyni wybiera dwie pary Stepway Expression i Extreme:
2 różnice cenowe, 21 technicznych, 0 wyposażeniowych, 19 stanów
`not_comparable` w pełnym raporcie. Złożony filtr `co2_emissions` daje
2 wiersze CSV.

Wynik `different` może powstać wyłącznie wtedy, gdy obie konfiguracje mają
zapisane, źródłowe stany. Brak rekordu, `not_stated`, `out_of_scope`,
`ambiguous` i `not_applicable` pozostają `not_comparable` i nigdy nie trafiają
do CSV. Jawne `not_available` jest pełnoprawnym zapisanym stanem wyposażenia
i może tworzyć rzeczywistą różnicę względem `standard`, `optional` albo
`unknown`.

Raport nie uzupełnia ani nie wyprowadza wartości brakujących.

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
10. deterministyczne wygenerowanie kolejki triage luk konfiguracji,
11. weryfikację przeglądu istotnych stron źródłowych,
12. deterministyczne wygenerowanie klasyfikacji dowodów dla luk,
13. deterministyczne wygenerowanie planu rozstrzygnięcia luk.
14. deterministyczne wygenerowanie raportu porównania konfiguracji.

Dla Pythona 3.13 workflow zapisuje bazę SQLite, raport walidacji, bazowe
liczniki, raport kompletności, raport pokrycia źródłami, kolejkę triage,
przegląd stron źródłowych, klasyfikację dowodów, plan rozstrzygnięcia
oraz porównanie konfiguracji w formatach JSON, Markdown i CSV jako tymczasowy
artefakt GitHub Actions
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

* praktyczne wykorzystanie zamkniętego portfela danych,
* interaktywne i eksportowalne porównania konfiguracji,
* filtrowanie i tworzenie shortlist konfiguracji,
* transakcyjne pakiety porównań z jawnych wyborów shortlisty,
* walidację struktury i relacji,
* raportowanie jakości oraz kompletności danych,
* wyszukiwanie informacji,
* generowanie lokalnej bazy SQLite,
* automatyzację kontroli jakości,
* rozwój spójnego interfejsu narzędziowego.

### Jogger MY26 source-backed catalogue and technical foundation

Oficjalny polski cennik Jogger MY26 z 1.04.2026 jest przechowywany w
repozytorium z dokładnym SHA-256. Katalog obejmuje 4 wersje, 22 konfiguracje
(11 pięciomiejscowych i 11 siedmiomiejscowych), 22 ceny katalogowe oraz 22
datowane wartości `number_of_seats`.

Pierwszy pakiet techniczny dodaje 312 dokładnych obserwacji ze strony 6 w 17
deklaratywnych specyfikacjach. Zachowuje konteksty LPG i benzyny, rozróżnia
wartości dla 5 i 7 miejsc oraz przechowuje oddzielnie silnik spalinowy, silnik
trakcyjny i HSG układu Hybrid 155. Zakresy WLTP, masy minimalne, ładowność,
pomiary bagażnika, para pojemności LPG i pozostałe niezgodne semantycznie pola
pozostają jawnym zakresem odroczonym. Dodatkowy kontrolowany import obejmuje
32 dokładne wartości `injection_type`: osobne układy benzyny i LPG dla Eco-G
oraz źródłowe wartości TCe 110 i Hybrid 155.

Dalsza rekonsyliacja skrzyń biegów dodaje 38 dokładnych obserwacji `gearbox_type` i `gear_count`, zachowuje brak liczby przełożeń dla Hybrid 155 Multi-mode oraz aktualizuje asocjacje Jogger z `mt6`, `edc6`, `e_dht140` i `e_dht155`.

Pakiet minimalnej masy własnej Jogger dodaje odrębny atrybut `minimum_kerb_weight` i 22 dokładne obserwacje dla konfiguracji pięcio- i siedmiomiejscowych, bez spłaszczania kwalifikatora minimum do ogólnego `kerb_weight`.

Pomiary bagażnika Jogger zachowują dwie odrębne granice VDA: do wysokości rolety i do wysokości oparcia. Pakiet dodaje dwa precyzyjne atrybuty oraz 44 obserwacje bez nadpisywania ogólnych `boot_capacity` ani `cargo_volume_vda`.

Pojemności LPG Jogger są rozdzielone na całkowitą pojemność zbiornika ciśnieniowego i pojemność napełniania. Pakiet dodaje dwa atrybuty oraz 20 obserwacji z kontekstem `lpg`, bez zmian w benzynowym `fuel_tank_capacity`.

Całkowita moc układu hybrydowego Jogger Hybrid 155 jest zapisana jako odrębny atrybut `hybrid_system_power_total` z sześcioma obserwacjami 116 kW, bez sumowania mocy silnika spalinowego i maszyn elektrycznych.

Macierze wyposażenia Jogger ze stron 4-5 dostarczają 1 166 datowanych rekordów dostępności dla 53 kanonicznych atrybutów i 22 konfiguracji. Import zachowuje statusy seryjne, opcjonalne i niedostępne oraz kwalifikatory pakietów i napędów.

### Bigster MY26 source-backed technical specifications

Oficjalny polski cennik Bigster MY26 z 3.07.2026 dostarcza 552 dokładne
wartości techniczne dla 14 aktywnych konfiguracji. Dane są zapisane w 41
deklaratywnych specyfikacjach i obejmują napęd, skrzynie biegów, silniki,
elektryfikację, osiągi, zużycie paliwa, emisję CO2, pojemności, masy oraz
wymiary.

Konteksty benzyny i LPG pozostają rozdzielone. Moc silnika spalinowego,
całkowita moc układu Hybrid 155, silnik trakcyjny i HSG nie są sumowane ani
spłaszczane. Wymiary 4x2 i 4x4 zachowują odrębne wartości wysokości, rozstawu
osi, tylnego zwisu i prześwitu. Czternaście drukowanych par maksymalnej
ładowności jest przechowywanych jako domknięte zakresy, a nie fałszywe
wartości dokładne.

Pięć neutralnych atrybutów zachowuje kwalifikatory źródła dla filtra cząstek,
napięcia układu hybrydowego, nieokreślonego rodzaju pojemności baterii oraz
dwóch pomiarów bagażnika ISO 3832. Cały pakiet można zweryfikować poleceniem:

```bash
python tools/import_bigster_technical_specifications.py --check
```


### Jogger equipment page-21 ambiguity review

Komenda `jogger-equipment-page21-ambiguity-review` rozstrzyga pojedynczy kandydat z `residual_gap_012`:

```bash
python tools/dkb.py jogger-equipment-page21-ambiguity-review
python tools/dkb.py jogger-equipment-page21-ambiguity-review --verify
```

Pakiet zachowuje stan broszury: Essential i Expression — niedostępne, Extreme — opcja, Journey — standard. Późniejsze cenniki oznaczają Journey jako niedostępne, dlatego konflikt pozostaje jawny i nie jest zgodą na import.

### Sandero equipment page-18 ambiguity review

Komenda `sandero-equipment-page18-ambiguity-review` rozstrzyga pojedynczy kandydat z `residual_gap_013`:

```bash
python tools/dkb.py sandero-equipment-page18-ambiguity-review
python tools/dkb.py sandero-equipment-page18-ambiguity-review --verify
```

Broszura zachowuje trzy odrębne stany kamery cofania: Essential — niedostępna, Expression — opcja, Journey — standard. Cennik nadal potwierdza opcję dla Expression manual, natomiast późniejsza oficjalna strona wersji oznacza kamerę jako seryjną dla Expression manual i automatic. Konflikt pozostaje jawny i nie jest zgodą na import.

### Sandero equipment page-19 ambiguity review

Komenda `sandero-equipment-page19-ambiguity-review` rozstrzyga pojedynczy kandydat z `residual_gap_014`:

```bash
python tools/dkb.py sandero-equipment-page19-ambiguity-review
python tools/dkb.py sandero-equipment-page19-ambiguity-review --verify
```

Broszura drukuje jeden kompletny wiersz regulatora i ogranicznika prędkości, oba seryjne w Essential, Expression i Journey. Pakiet zachowuje `cruise_control` i `speed_limiter` jako dwa odrębne atrybuty, obie przypięte sygnatury oraz wszystkie 4 dokładne rekordy; nie projektuje brakujących rekordów na Essential i nie zatwierdza importu.

### Sandero Stepway equipment page-18 ambiguity review

Komenda `sandero-stepway-equipment-page18-ambiguity-review` rozstrzyga pojedynczy kandydat z `residual_gap_015`:

```bash
python tools/dkb.py sandero-stepway-equipment-page18-ambiguity-review
python tools/dkb.py sandero-stepway-equipment-page18-ambiguity-review --verify
```

Broszura drukuje dwa kolejne, lecz odrębne wiersze: zwykłe relingi są seryjne tylko w Essential, a modułowe relingi w kolorze szary Megalith są seryjne w Expression i Extreme. Pakiet wybiera dokładny rekord `roof_rails:standard` dla Essential, zachowuje i jawnie odrzuca sygnaturę `modular_roof_rails:standard` z dwoma rekordami Expression oraz nie projektuje brakujących stanów między wersjami.

### Bigster technical page-20 unresolved review — chunk 1

Komenda `bigster-technical-page20-unresolved-review-chunk1` przegląda pierwsze 40 kandydatów z `residual_gap_016`:

```bash
python tools/dkb.py bigster-technical-page20-unresolved-review-chunk1
python tools/dkb.py bigster-technical-page20-unresolved-review-chunk1 --verify
```

Pakiet odtwarza wizualny układ czterech kolumn napędowych i 18 grup wierszy. Szesnaście kompletnych wierszy pozostaje `unresolved_signature_mismatch`, ponieważ pakiet nie zawiera żadnej przypiętej sygnatury ani rekordu, a 24 nagłówki i zawinięte fragmenty są `context_only_non_import`. Wartości widoczne w źródle są zapisane wyłącznie jako ustalenia przeglądu, bez zgody na import; fragmenty tylnych hamulców odsyłają do wcześniejszej decyzji `residual_gap_001`. Przegląd pięciu ostatnich pakietów nie wymagał nowej decyzji architektonicznej ani osobnego PR-a audytowego.

### Bigster technical page-20 unresolved review — chunk 2

Komenda `bigster-technical-page20-unresolved-review-chunk2` przegląda pozostałych 29 kandydatów z `residual_gap_017`:

```bash
python tools/dkb.py bigster-technical-page20-unresolved-review-chunk2
python tools/dkb.py bigster-technical-page20-unresolved-review-chunk2 --verify
```

Pakiet zamyka 69-elementową grupę nierozstrzygniętych kandydatów strony 20. Osiem kompletnych wierszy pozostaje `unresolved_signature_mismatch`, ponieważ pakiet nie zawiera żadnej przypiętej sygnatury ani rekordu, a 21 zawiniętych fragmentów, etykiet, przypisów i not źródłowych jest `context_only_non_import`. Wartości są zachowane literalnie — w tym wydrukowana sekwencja `1960**` oraz `2002 / 1981` — bez wymyślania interpretacji, projekcji między napędami lub konfiguracjami i bez zgody na import. Pierwszy fragment `residual_gap_016` pozostaje niezmieniony.

<!-- dkb:documentation-baseline:readme:start -->
Zweryfikowany model obejmuje 1715 testów, 46 pliki CSV, 11660 rekordów
danych, 51 relacje między tabelami, 3552 wartości konfiguracji, 138 skalarnych specyfikacji importu, 301 zakresów konfiguracji i 24
specyfikacji zakresów oraz 5902 rekordów dostępności wyposażenia.
Katalog zawiera 385 kanonicznych atrybutów i 30 kategorii atrybutów. Baza
SQLite obejmuje 46 tabele i 11660 rekordów, pozostaje zgodna z CSV, a wszystkie
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
