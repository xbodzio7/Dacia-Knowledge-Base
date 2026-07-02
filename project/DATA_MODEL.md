\# DATA MODEL



\## Cel



DKB wykorzystuje model danych oparty na czterech podstawowych encjach:



```

Category

&#x20;   ↓

Attribute

&#x20;   ↓

Version

&#x20;   ↓

Value

```



Model został zaprojektowany tak, aby umożliwić przechowywanie danych o różnych modelach samochodów bez konieczności przebudowy struktury bazy.



\---



\## Diagram logiczny



```

Category

&#x20;   ↓

Attribute

&#x20;   ↓

Version

&#x20;   ↓

Value

```



\---



\## Category



Najwyższy poziom organizacji danych.



Przykładowe kategorie:



\* Engine

\* Dimensions

\* Equipment

\* Safety

\* Multimedia

\* Maintenance

\* Performance

\* Consumption



Jedna kategoria zawiera wiele atrybutów.



\---



\## Attribute



Opisuje pojedynczą cechę pojazdu.



Przykłady:



\* Power

\* Torque

\* Fuel type

\* Length

\* Width

\* Android Auto

\* Airbags



Każdy atrybut należy do dokładnie jednej kategorii.



Atrybut definiowany jest tylko raz i może być wykorzystywany przez wiele wersji pojazdu.



\---



\## Version



Opisuje konkretną konfigurację pojazdu.



Version identyfikuje zestaw danych, dla którego przechowywane są wartości atrybutów.



Przykład:



\* Duster III

\* Journey

\* Hybrid 140

\* MY2025

\* PL



Szczegółowy sposób identyfikacji Version zostanie doprecyzowany podczas projektowania struktury danych.


### Identyfikacja Version

`Version` reprezentuje pojedynczą, jednoznacznie zidentyfikowaną konfigurację pojazdu.

Powinna być stabilnym identyfikatorem wykorzystywanym przez wszystkie dane przechowywane w DKB.

Przykładowo Version może być definiowana przez następujące elementy:

- Model
- Generation
- Model Year (MY)
- Market
- Trim
- Powertrain

Nie oznacza to, że wszystkie powyższe informacje muszą być zapisane w samym identyfikatorze. Są to elementy opisujące konfigurację, której dotyczą wartości atrybutów.

Przykład logiczny:

Model: Duster  
Generation: III  
MY: 2025  
Market: PL  
Trim: Journey  
Powertrain: Hybrid 140

Wszystkie wartości (Value) odnoszą się do jednej, konkretnej Version.



\---



\## Value



Przechowuje rzeczywistą wartość konkretnego atrybutu dla konkretnej wersji pojazdu.



Przykłady:



```

Power = 140 HP

Fuel = Hybrid

Length = 4343 mm

Android Auto = Yes

```



Każda wartość jest przypisana jednocześnie do:



\* jednej Version,

\* jednego Attribute.



\---



\## Relacje



```

Category

1 → N Attribute



Attribute

1 → N Value



Version

1 → N Value



Value

N → 1 Attribute



Value

N → 1 Version

```



\---



\## Założenia modelu



\* Kategorie nie przechowują danych.

\* Atrybuty definiowane są tylko raz.

\* Version identyfikuje konkretną konfigurację pojazdu.

\* Wszystkie wartości odnoszą się jednocześnie do Version i Attribute.

\* Model umożliwia dodawanie nowych kategorii i nowych atrybutów bez przebudowy struktury danych.



\---



\## Możliwe rozszerzenia



Model może zostać w przyszłości rozszerzony o encje pomocnicze, takie jak:



\* Source

\* Market

\* Language

\* Unit

\* Media



Rozszerzenia nie powinny zmieniać podstawowej relacji:



```

Category

&#x20;   ↓

Attribute

&#x20;   ↓

Version

&#x20;   ↓

Value

```



\---



\## Status



Model przedstawiony w tym dokumencie stanowi logiczną podstawę Dacia Knowledge Base.



Kolejne pliki danych oraz struktury CSV powinny być projektowane zgodnie z opisanym modelem.



## Zakres dokumentu

Niniejszy dokument opisuje wyłącznie logiczny model danych wykorzystywany przez Dacia Knowledge Base.

Nie definiuje:

- struktury plików,
- nazw kolumn,
- formatów identyfikatorów,
- sposobu przechowywania danych,
- procesu importu lub eksportu danych.

Szczegóły implementacyjne powinny być dokumentowane oddzielnie.



