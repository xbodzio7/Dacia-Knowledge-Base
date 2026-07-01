\# Dacia Knowledge Base (DKB)



\## Cel projektu



Celem projektu jest stworzenie kompletnej, otwartej bazy wiedzy o samochodach marki Dacia.



Repozytorium ma umożliwiać:



\- porównywanie wersji wyposażenia,

\- analizę zmian pomiędzy rocznikami,

\- analizę silników, skrzyń biegów i wyposażenia,

\- import danych z katalogów PDF i cenników,

\- eksport do CSV, Excel i innych formatów.



Projekt nie jest arkuszem Excel.



Excel jest tylko jednym z odbiorców danych.



Repozytorium GitHub jest jedynym źródłem prawdy.



\---



\## Repozytorium



https://github.com/xbodzio7/Dacia-Knowledge-Base



\---



\## Aktualny model



Repozytorium posiada warstwę danych.



Planowana struktura:



/

data/

docs/

project/

scripts/

excel/

reports/

tests/



\---



\## Model danych



Podstawowe encje:



Categories

Models

Versions

Engines

Gearboxes

Attributes

AttributeValues

Sources

Packages

Options

Prices



\---



\## Identyfikatory



Stosujemy identyfikatory tekstowe.



Przykłady:



MODEL\_SANDERO



MODEL\_STEPWAY



ENG\_TCE90



ATTR\_REAR\_CAMERA



CAT\_ADAS



Nigdy nie stosujemy numeracji typu ATR0001.



\---



\## Zasada



Architektura jest zamknięta.



Rozwijamy dane.



Nie projektujemy ponownie struktury bez rzeczywistej potrzeby.



AKTUALNY STAN



Projekt jest po audycie.



Architektura uznana za stabilną.



Repozytorium wymaga już głównie rozwijania danych.





\----------------------------------------------------------------------------------------------------------





\## Aktualny etap projektu



Projekt znajduje się na etapie systematycznego rozwijania bazy wiedzy.



Architektura została uznana za stabilną.



Priorytetem nie jest dalsze projektowanie systemu, lecz rozwój, weryfikacja i utrzymanie wiedzy.



\---



\## Filozofia projektu



Celem DKB nie jest gromadzenie informacji.



Celem jest tworzenie wiarygodnej, spójnej i łatwej do utrzymania bazy wiedzy o samochodach marki Dacia.



Największą wartością projektu jest jakość wiedzy oraz możliwość jej długoterminowego utrzymania.



\---



\## Aktualny etap



Projekt osiągnął stabilny etap architektoniczny.



Priorytetem jest rozwój jakości bazy wiedzy, a nie dalsze projektowanie struktury repozytorium.



\---



\## Główna zasada



DKB rozwijane jest jako referencyjna baza wiedzy.



Kod, skrypty i narzędzia mają wspierać tworzenie i utrzymanie wiedzy.

