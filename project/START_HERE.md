\# START HERE



Jeżeli jesteś AI rozpoczynającą pracę nad projektem Dacia Knowledge Base (DKB), przeczytaj ten dokument przed wykonaniem jakichkolwiek zmian.



\---



\# Cel projektu



Dacia Knowledge Base (DKB) jest rozwijana jako referencyjna baza wiedzy o samochodach marki Dacia.



Projekt nie jest typowym projektem programistycznym.



Kod, skrypty i narzędzia mają funkcję pomocniczą.



Najważniejszym produktem projektu jest wiarygodna, spójna i łatwa do utrzymania wiedza.



\---



\# Jedno źródło prawdy



Jedynym źródłem prawdy jest aktualne repozytorium.



Nie opieraj się na pamięci poprzednich rozmów.



Jeżeli rozmowa jest sprzeczna z repozytorium, zawsze obowiązuje repozytorium.



\---



\# Dokumentacja projektu



Przed rozpoczęciem pracy przeczytaj kolejno:



1\. PROJECT_CONTEXT.md

2\. AI_CONTEXT.md

3\. DECISIONS.md

4\. ROADMAP.md

5\. SESSION_STATE.md



Dopiero potem analizuj pozostałą część repozytorium.



\---



\# Workflow



Domyślny sposób pracy:



1\. Przeanalizuj aktualny stan repozytorium.

2\. Zidentyfikuj rzeczywiste problemy.

3\. Oceń wpływ zmian.

4\. Przygotuj kompletny pakiet zmian.

5\. Wygeneruj gotowe artefakty.

6\. Zaproponuj commit.



Nie zatrzymuj się po każdym etapie.



\---



\# Zasady projektowe



Rozwijaj istniejące rozwiązania.



Nie projektuj architektury od nowa bez rzeczywistej potrzeby.



Nie proponuj zmian "na zapas".



Jeżeli coś działa dobrze — pozostaw bez zmian.



Każda zmiana musi wynikać z analizy repozytorium.



\---



\# Odpowiedzi



Preferowane są gotowe artefakty.



Ogranicz opisy do minimum.



Nie powtarzaj wcześniejszych ustaleń.



Nie opisuj planów, jeżeli możesz wygenerować gotowe pliki.



\---



\# Kolejne sesje



Nie wykonuj ponownie pełnego audytu całego projektu.



Zakładaj, że pełny audyt został już wykonany.



Analizuj jedynie:



\- aktualny stan repozytorium,

\- zmiany od poprzedniej sesji,

\- wpływ nowych zmian.



Pełny audyt wykonuj wyłącznie na wyraźne polecenie użytkownika.



\---



\# Wynik pracy



Każda sesja powinna kończyć się możliwie kompletnym pakietem commit-ready.



Pakiet powinien zawierać:



\- listę zmodyfikowanych plików,

\- listę nowych plików (jeżeli są potrzebne),

\- krótkie uzasadnienie,

\- gotowe treści plików,

\- propozycję commit message.



\## Development Workflow (DKB v2)



The repository contained in the current ZIP is the single source of truth.



Every work session starts with repository analysis.



Rules:



\- One sprint = one logical change.

\- Prefer domain-oriented sprints.

\- Typical sprint size: 10–20 records or one coherent refactoring.

\- Never mix unrelated domains in one commit.

\- Data quality has priority over data quantity.

\- Documentation is updated only when required by model changes.





\## Current Architecture (DKB v2.1)



The project is organized around four layers:



1\. Core data (`attributes.csv`)

2\. Reference dictionaries (`domains.csv`, `units.csv`, `value\_types.csv`)

3\. Validation rules (`validation\_rules.csv`)

4\. Project governance (`project/`)

