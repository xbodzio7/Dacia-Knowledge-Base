# Dacia KB — audyt inwentarza pól portfela

**Zakres:** aktualne dane z ZIP repozytorium, konfiguracje `status=active`; audyt odczytowy, bez zmian w master data.

**Ograniczenie:** to nie jest certyfikowany audyt kompletności. Repozytorium nie dostarcza jednego, zweryfikowanego wymagania pól dla każdej z 94 konfiguracji. „Brak względem unii rodziny” oznacza wyłącznie, że pole występuje u innej aktywnej konfiguracji tej rodziny; nie oznacza, że pole jest obowiązkowe albo źródło go podaje.

## Inwentarz wg rodziny

| Rodzina | Konfiguracje | Wartości techniczne | Rekordy wyposażenia | Rekordy cen | Relacje źródeł |
|---|---:|---:|---:|---:|---:|
| Sandero | 9 | 688 | 1199 | 22 | 59 |
| Sandero Stepway | 10 | 799 | 1527 | 28 | 70 |
| Duster | 30 | 2275 | 2972 | 58 | 97 |
| Jogger | 22 | 2652 | 2070 | 56 | 110 |
| Bigster | 20 | 1567 | 2195 | 27 | 55 |
| Spring | 3 | 219 | 137 | 3 | 11 |

## Uwaga na starsze completeness specs

W `data/reporting/*completeness.json` istnieją specyfikacje dla wybranych zestawów konfiguracji. Ich część jest nieaktualna względem aktywnego inwentarza: uruchomienie raportera dla wielu specyfikacji kończy się błędem `observed technical slots are absent from spec`, co świadczy o zaobserwowanych polach spoza specyfikacji. Nie należy ich używać jako kompletnego i aktualnego denominatora dla całego portfela bez przeglądu i wersjonowania.

## Jak używać plików

- `dkb_field_inventory_audit.csv`: 1 wiersz na aktywną konfigurację, z licznikami oraz liczbą pól obserwowanych w unii rodziny.
- `dkb_peer_union_candidate_gaps.csv`: lista pól, które pojawiają się u innych konfiguracji tej rodziny, ale nie w danej konfiguracji. Kandydaci do źródłowej weryfikacji, nie automatyczne braki.

## Następny krok techniczny

Wymagany jest zatwierdzony kontrakt pól per model/powertrain/body style (lub per rodzina), z zasadami `required`, `not_applicable`, `source_not_stated`, `conflict` i `unreviewed`. Dopiero na nim należy oprzeć raport braków. Do czasu ustalenia tego kontraktu nie przypisuję procentów kompletności.