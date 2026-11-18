\# ATTRIBUTE CATALOG



\## Cel



Dokument definiuje kanoniczny słownik atrybutów wykorzystywanych w Dacia Knowledge Base (DKB).



Każdy atrybut opisuje jedną cechę pojazdu i może być wykorzystywany przez wiele modeli, wersji oraz roczników.



Dokument stanowi źródło referencyjne dla implementacji danych.



\---



\# Zasady



\## Stabilność



Kod atrybutu jest niezmienny.



Zmiana nazwy wyświetlanej nie powoduje zmiany kodu.



\---



\## Nazewnictwo



\* `snake\_case`

\* język angielski

\* bez skrótów, jeśli nie są powszechnie stosowane

\* jeden kod opisuje dokładnie jedno znaczenie



\---



\## Typy danych



Dozwolone typy:



\* string

\* integer

\* decimal

\* boolean

\* date

\* enum



\---



\## Jednostki



Jednostka jest definiowana oddzielnie od kodu atrybutu.



Przykład:



\* `engine\_power`

\* jednostka: `kW`



\---



\# Katalog atrybutów



\## Engine



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Transmission



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Drivetrain



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Dimensions



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Weights



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Capacities



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Performance



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Consumption



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Emissions



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Safety



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\## Driver Assistance (ADAS)



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



## Multimedia

| Code | Name | Type | Unit | Description |
| ---- | ---- | ---- | ---- | ----------- |

## Connectivity

| Code | Name | Type | Unit | Description |
| ---- | ---- | ---- | ---- | ----------- |


\## Maintenance



| Code | Name | Type | Unit | Description |

| ---- | ---- | ---- | ---- | ----------- |



\---



\# Status



Dokument jest rozwijany iteracyjnie.



Nowe atrybuty dodawane są wyłącznie po analizie źródeł i zaakceptowaniu ich miejsca w taksonomii DKB.

## Fuel-tank capacity semantics (D-019)

| Code | Name | Type | Unit | Description |
| ---- | ---- | ---- | ---- | ----------- |
| `fuel_tank_capacity_total` | Fuel tank capacity (total) | decimal | L | Total physical fuel-tank capacity explicitly stated by the source; not assumed to be usable capacity. |
| `fuel_tank_capacity_usable` | Fuel tank capacity (usable) | decimal | L | Usable fuel volume explicitly stated by the source; not inferred from total capacity. |

The legacy `fuel_tank_capacity` attribute is retained unchanged. New source observations must use the semantically precise attribute when the source establishes the distinction. See `DECISIONS.md` D-019.
