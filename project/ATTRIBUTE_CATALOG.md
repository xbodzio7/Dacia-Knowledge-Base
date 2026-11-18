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

## Fuel-tank capacity semantics (D-032)

| Code | Name | Type | Unit | Description |
| ---- | ---- | ---- | ---- | ----------- |
| `fuel_tank_capacity` | Fuel tank capacity | decimal | L | Fuel tank capacity where the source supplies one undivided value. |
| `lpg_vessel_capacity_total` | Total LPG vessel capacity | decimal | L | Total internal capacity of the LPG pressure vessel. |
| `lpg_vessel_filling_capacity` | LPG vessel filling capacity | decimal | L | Source-stated LPG volume available or permitted for filling, distinct from total vessel capacity. |

For bi-fuel configurations, use `fuel_type_code` where the source explicitly distinguishes fuels. The LPG total and filling attributes must be populated separately only when the source provides both meanings. No generic duplicate total/usable attributes are added. See `DECISIONS.md` D-032.
