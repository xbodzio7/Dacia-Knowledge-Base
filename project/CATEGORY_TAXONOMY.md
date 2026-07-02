\# CATEGORY TAXONOMY



\## Cel



Dokument definiuje kontrolowaną taksonomię wiedzy wykorzystywaną w Dacia Knowledge Base (DKB).



Stanowi wspólny słownik kategorii dla całego projektu i jest niezależny od sposobu przechowywania danych.



Nie opisuje modelu danych ani implementacji.



\---



\# Hierarchia



```text

Vehicle

├── Identification

├── Powertrain

│   ├── Engine

│   ├── Transmission

│   ├── Drivetrain

│   ├── Hybrid System

│   └── Electric System

├── Performance

├── Consumption

├── Emissions

├── Dimensions

├── Weights

├── Capacities

├── Chassis

│   ├── Suspension

│   ├── Steering

│   └── Brakes

├── Wheels \& Tyres

├── Exterior

├── Interior

├── Comfort

├── Climate

├── Lighting

├── Multimedia

├── Connectivity

├── Driver Assistance (ADAS)

├── Safety

├── Maintenance

├── Diagnostics

├── Parts

├── Accessories

├── Warranty

├── Documentation

└── References

```



\---



\# Zasady



\* Każdy atrybut należy do dokładnie jednej kategorii.

\* Kategorie opisują obszary wiedzy, a nie sposób przechowywania danych.

\* Nazwy kategorii powinny być stabilne i zmieniać się wyłącznie w uzasadnionych przypadkach.

\* Nowe kategorie dodajemy tylko wtedy, gdy nie można logicznie przypisać informacji do istniejącej struktury.



\---



\# Przykłady



| Informacja             | Kategoria                |

| ---------------------- | ------------------------ |

| Moc silnika            | Engine                   |

| Moment obrotowy        | Engine                   |

| Skrzynia biegów        | Transmission             |

| Napęd 4x4              | Drivetrain               |

| Zużycie paliwa         | Consumption              |

| Emisja CO₂             | Emissions                |

| Długość pojazdu        | Dimensions               |

| Masa własna            | Weights                  |

| Pojemność bagażnika    | Capacities               |

| Android Auto           | Connectivity             |

| Kamera cofania         | Driver Assistance (ADAS) |

| Harmonogram przeglądów | Maintenance              |

| Instrukcja obsługi     | Documentation            |

| Cennik                 | References               |



\---



\# Status



Dokument stanowi referencyjną klasyfikację wiedzy dla DKB.



Na jego podstawie mogą być budowane słowniki, pliki CSV oraz mechanizmy wyszukiwania, jednak sama taksonomia pozostaje niezależna od implementacji.



