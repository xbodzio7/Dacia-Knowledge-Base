# Przewodnik konsumenta produktów danych DKB

Ten przewodnik opisuje pełny, powtarzalny przepływ korzystania z gotowych produktów Dacia Knowledge Base bez rozszerzania ani reinterpretowania danych źródłowych.

## Zakres

Przepływ obejmuje:

1. pobranie jawnej, niezmiennej wersji publicznego wydania,
2. automatyczną kontrolę tagu, assetów, manifestu i sum SHA-256,
3. bezpieczne rozpakowanie do lokalnego workspace,
4. nawigację przez lokalny `index.html`,
5. użycie shortlisty, skoroszytu i raportów zakresowych,
6. utworzenie własnego bundle porównań z wybranych konfiguracji,
7. późniejszą, całkowicie offline'ową kontrolę integralności workspace.

Narzędzia nie tworzą rekomendacji zakupowych, nie uzupełniają brakujących wartości i nie porównują konfiguracji należących do niezależnych zakresów raportowych.

## Wymagania

- lokalna kopia repozytorium Dacia Knowledge Base,
- Python zgodny z bramką projektu (3.10 lub 3.13),
- dostęp do internetu wyłącznie podczas pobierania publicznego wydania,
- pusty albo nieistniejący katalog docelowy.

Po zakończeniu pobierania wszystkie opisane produkty działają offline.

## 1. Pobierz jawną wersję

Z katalogu repozytorium uruchom:

```bash
python tools/dkb.py data-product-release-download \
  --version 1.0.0 \
  --output-directory ../dkb-data-products-v1.0.0
```

Komenda wymaga dokładnej wersji `MAJOR.MINOR.PATCH`. Nie obsługuje mutowalnego aliasu `latest`.

Przed opublikowaniem workspace komenda:

- odczytuje publiczny GitHub Release dla tagu `data-products-v1.0.0`,
- rozwiązuje tag do konkretnego commita,
- wymaga dokładnie trzech kanonicznych assetów,
- sprawdza `data-product-release-manifest.json` i `SHA256SUMS`,
- weryfikuje każdy element ZIP,
- bezpiecznie zapisuje tylko zweryfikowane pliki,
- tworzy deterministyczny `index.html`,
- publikuje katalog docelowy atomowym przemianowaniem.

## 2. Otwórz stronę startową

Po sukcesie otwórz:

```text
../dkb-data-products-v1.0.0/index.html
```

Strona działa bez serwera, JavaScriptu, zewnętrznych stylów i fontów. Zawiera:

- wersję, tag, commit i datę snapshotu,
- liczbę konfiguracji i niezależnych zakresów,
- cztery podstawowe produkty,
- wszystkie zakresy porównań,
- odnośniki do oryginalnych assetów proweniencji.

## 3. Użyj gotowych produktów

### Interaktywna shortlista

```text
contents/shortlist/configuration-shortlist.html
```

Shortlista pozwala filtrować źródłowo potwierdzone konfiguracje według modelu, wersji, układu napędowego, skrzyni, ceny, liczby miejsc i wyposażenia. Zaznaczenie konfiguracji jest niezależne od aktualnego filtra.

Z przeglądarki można pobrać deterministyczny plik JSON z wyborem konfiguracji. Zachowaj go poza niezmiennym workspace, na przykład jako:

```text
../configuration-shortlist-selection.json
```

### Skoroszyt porównań

```text
contents/comparison-bundle/configuration-comparison-workbook.xlsx
```

Skoroszyt zawiera sześć arkuszy: `Overview`, `Scopes`, `Configurations`, `Comparisons`, `Sources` i `Artifacts`. Nie zawiera formuł, makr, rankingów ani rekomendacji.

### Manifest bundle

```text
contents/comparison-bundle/comparison-bundle-manifest.json
```

Manifest opisuje wybrane konfiguracje, zakresy porównywalne i singletony, liczbę par i różnic, pliki raportów oraz ich sumy SHA-256.

### Raporty zakresowe

Dla zakresów porównywalnych dostępne są, zależnie od manifestu:

- interaktywny HTML,
- pełny JSON,
- Markdown,
- CSV różnic.

Singleton nie ma raportu par, ponieważ w jego zakresie wybrano tylko jedną konfigurację.

### Notatki wydania

```text
contents/RELEASE_NOTES.md
```

Notatki opisują wersję, snapshot, zakres produktów i granice semantyczne wydania.

## 4. Utwórz własny bundle porównań

Plik wyboru JSON pobrany z shortlisty można przekazać bezpośrednio do generatora:

```bash
python tools/dkb.py configuration-comparison-bundle \
  --shortlist-json ../configuration-shortlist-selection.json \
  --output-directory ../my-comparison-bundle
```

Generator:

- deduplikuje jawny wybór,
- grupuje konfiguracje według istniejących niezależnych zakresów,
- nie generuje par między zakresami,
- tworzy JSON, Markdown, CSV i HTML dla grup porównywalnych,
- zachowuje singletony w manifeście,
- tworzy deterministyczny sześciarkuszowy XLSX,
- publikuje wynik transakcyjnie.

Można też wskazać kody bez pliku shortlisty:

```bash
python tools/dkb.py configuration-comparison-bundle \
  --configuration-code CODE_A \
  --configuration-code CODE_B \
  --output-directory ../my-comparison-bundle
```

Kody muszą należeć do aktywnego, jawnie zmapowanego zakresu raportowego.

## 5. Zweryfikuj workspace później

Po skopiowaniu, synchronizacji albo archiwizacji workspace uruchom kontrolę całkowicie offline:

```bash
python tools/dkb.py data-product-workspace-verify \
  --workspace-directory ../dkb-data-products-v1.0.0
```

Weryfikator tylko odczytuje pliki. Ponownie sprawdza:

- dokładny zestaw trzech assetów,
- manifest, `SHA256SUMS` i ZIP,
- pełny inwentarz `contents/`,
- rozmiar i SHA-256 każdego rozpakowanego pliku,
- dokładne bajty deterministycznego `index.html`,
- każdy lokalny odnośnik strony startowej,
- brak zewnętrznych zależności runtime.

Dla automatyzacji użyj stabilnego raportu JSON:

```bash
python tools/dkb.py data-product-workspace-verify \
  --workspace-directory ../dkb-data-products-v1.0.0 \
  --json
```

Raport nie zawiera czasu uruchomienia, nazwy hosta ani bezwzględnej ścieżki.

## 6. Co zrobić po błędzie weryfikacji

Weryfikator nie naprawia uszkodzeń i nie modyfikuje workspace.

Zalecana procedura:

1. zachowaj uszkodzony katalog do analizy, jeżeli jest potrzebny,
2. nie zastępuj pojedynczych plików ręcznie,
3. pobierz tę samą jawną wersję do nowego, pustego katalogu,
4. ponownie uruchom weryfikację offline,
5. porównuj własne pliki robocze wyłącznie poza katalogiem wydania.

Przykład ponownego pobrania:

```bash
python tools/dkb.py data-product-release-download \
  --version 1.0.0 \
  --output-directory ../dkb-data-products-v1.0.0-fresh
```

## 7. Proweniencja i niezależna kontrola

Oryginalne pobrane assety pozostają w:

```text
assets/
```

Katalog zawiera:

- `data-products-v1.0.0.zip`,
- `data-product-release-manifest.json`,
- `SHA256SUMS`.

Manifest wiąże wersję wydania z konkretnym commitem repozytorium i opisuje każdy członek archiwum. `SHA256SUMS` pozwala niezależnie sprawdzić ZIP i manifest.

## 8. Granice interpretacji

Produkty zachowują następujące zasady:

- brak rekordu nie jest wartością negatywną,
- brak danych nie jest automatycznie `unknown`,
- obserwacje są datowane i powiązane ze źródłami,
- statusy dostępności zachowują jawne znaczenie,
- wartości zależne od paliwa zachowują kontekst LPG albo benzyny,
- zakresy raportowe pozostają niezależne,
- nie są generowane rankingi ani rekomendacje,
- nie są inferowane brakujące wartości.

## 9. Najczęstsze zadania

| Zadanie | Polecenie lub plik |
|---|---|
| Pobranie wydania | `data-product-release-download --version 1.0.0` |
| Główna nawigacja | `index.html` |
| Filtrowanie konfiguracji | `contents/shortlist/configuration-shortlist.html` |
| Gotowy przegląd tabelaryczny | `configuration-comparison-workbook.xlsx` |
| Struktura zakresów i artefaktów | `comparison-bundle-manifest.json` |
| Własny bundle | `configuration-comparison-bundle` |
| Późniejsza kontrola integralności | `data-product-workspace-verify` |
| Raport dla automatyzacji | `data-product-workspace-verify --json` |

## 10. Kontrakt wersji

Zawsze zapisuj używaną wersję w skryptach, instrukcjach i wynikach automatyzacji. Dla tego przewodnika wersją referencyjną jest `1.0.0`, tag `data-products-v1.0.0`.

Nowa wersja wydania jest osobnym, niezmiennym snapshotem. Nie zakładaj, że katalog wcześniejszej wersji można bezpiecznie aktualizować przez kopiowanie wybranych plików z nowszej wersji.
