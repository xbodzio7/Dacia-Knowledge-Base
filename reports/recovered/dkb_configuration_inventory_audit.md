# Dacia KB — audyt inwentarza rekordów konfiguracji

Data źródła: ZIP repozytorium z 28.10.2026. To audyt obecności rekordów, nie dowód kompletności merytorycznej.

Konfiguracje aktywne: 94; aktywne atrybuty: 416; rekordy techniczne: 8200; rekordy statusów wyposażenia: 10100; rekordy cen: 194; relacje źródło-konfiguracja: 402.

| Model | Konfiguracje | Tech. rekordy | Tech. atrybuty unique (sum) | Wyposażenie rekordy | Wyposażenie atrybuty unique (sum) | Konfiguracje z ceną |
|---|---:|---:|---:|---:|---:|---:|
| Bigster | 20 | 1567 | 1285 | 2195 | 1898 | 20/20 |
| Duster | 30 | 2275 | 1343 | 2972 | 2067 | 30/30 |
| Jogger | 22 | 2652 | 1680 | 2070 | 1440 | 22/22 |
| Sandero | 9 | 688 | 511 | 1199 | 781 | 9/9 |
| Sandero Stepway | 10 | 799 | 582 | 1527 | 886 | 10/10 |
| Spring | 3 | 219 | 192 | 137 | 137 | 3/3 |

## Ograniczenia audytu

- Obecność co najmniej jednego rekordu w tabeli nie oznacza kompletności dla wymaganych pól.
- Kontrakt narzędzia `configuration_completeness.py` opiera się na jawnej specyfikacji `data/reporting/configuration_completeness.json`; aktualna specyfikacja obejmuje tylko 7 konfiguracji.
- Raport wygenerowany przez ten kontrakt wskazuje 90,25% pokrycia technicznego (58 luk) i 99,59% wyposażenia (2 luki) — wyłącznie dla tych 7 konfiguracji. Nie wolno ekstrapolować na 94.
- Repozytorium nie dostarcza w tym specyfikacyjnym pliku uniwersalnego denominatora wymaganych atrybutów dla wszystkich 94 konfiguracji. Aby policzyć rzeczywiste braki dla całego portfela, potrzebna jest rozszerzona jawna specyfikacja zakresów/slotów per konfiguracja i atrybutów wyposażenia.

## Najkrótsza ścieżka

1. Rozszerzyć completeness spec na wszystkie 94 aktywne konfiguracje, z właściwym źródłem per konfiguracja.
2. Zdefiniować wymagane technical_slots oraz equipment_attributes, z jawnie notowanymi not_applicable.
3. Uruchomić istniejący `tools/configuration_completeness.py` — nie pisać nowego walidatora.
4. Ceny: dopisać do raportu denominator ceny aktualne/obowiązujące per konfiguracja (obecny inventory wykazuje rekordy, ale nie weryfikuje daty/źródła właściwego dla release).