\# AI CONTEXT



Instrukcja dla AI pracującej nad projektem Dacia Knowledge Base.



\## Podstawowe zasady



Repozytorium przesłane przez użytkownika jest jedynym źródłem prawdy.



Nie polegaj na pamięci poprzednich rozmów.



W przypadku rozbieżności zawsze obowiązuje zawartość repozytorium.



\## Sposób pracy



1\. Najpierw wykonaj audyt aktualnego repozytorium.

2\. Dopiero po zakończeniu audytu proponuj zmiany.

3\. Rozwijaj istniejące rozwiązania.

4\. Nie projektuj architektury od nowa bez rzeczywistego uzasadnienia wynikającego z repozytorium.

5\. Nie proponuj zmian „na zapas”.

6\. Jeżeli coś działa poprawnie – pozostaw bez zmian.

7\. Jeżeli podczas dalszego audytu okaże się, że wcześniejsza rekomendacja była błędna lub nieoptymalna, popraw ją.
8. Jeden sprint odpowiada jednemu commitowi.

9\. W ramach jednego sprintu każdy plik powinien być modyfikowany tylko raz.

10\. Generuj kompletne pliki, a nie fragmenty.

11\. Commit jest przygotowywany dopiero po zakończeniu wszystkich zmian.

12\. Jeżeli zmiana wpływa na dokumentację, zaktualizuj ją w tym samym sprincie.

13\. Przed rozpoczęciem każdego sprintu przeanalizuj aktualny stan repozytorium.



\## Tryb pracy



Domyślnie AI pracuje do momentu przygotowania kompletnego pakietu zmian.



Nie zatrzymuje się po każdym etapie.



Nie raportuje postępów, jeżeli nie jest to konieczne.



Wynikiem pracy powinien być możliwie kompletny pakiet commit-ready.



\## Polecenie „dalej”



Jeżeli użytkownik napisze:



dalej



oznacza to:



wykonuj kolejne logiczne etapy wynikające z repozytorium aż do przygotowania gotowych artefaktów.



Nie zatrzymuj się po każdym kroku.



\## Artefakty



Preferowane są gotowe artefakty:



\- Markdown

\- CSV

\- Python

\- Excel

\- JSON



Opis stosuj tylko wtedy, gdy jest niezbędny.



\## Ograniczenia



Jeżeli czegoś nie można wykonać z powodu ograniczeń narzędzi:



\- napisz to jednym zdaniem,

\- zaproponuj najbliższą możliwą alternatywę.



\## Priorytety projektu



1\. Jakość wiedzy

2\. Dane

3\. Import

4\. Walidacja

5\. Raporty

6\. Dokumentacja techniczna



\## Czego NIE robić



NIE:



\- nie projektuj architektury od nowa,

\- nie proponuj zmian bez analizy repozytorium,

\- nie twórz nowych katalogów bez uzasadnienia,

\- nie powtarzaj wcześniejszych ustaleń,

\- nie opisuj planów, jeżeli możesz wygenerować gotowe pliki,

\- nie zakładaj, że pamiętasz poprzednie rozmowy.



ZAWSZE:



\- analizuj repozytorium przed rozpoczęciem pracy,

\- rozwijaj istniejące rozwiązania,

\- proponuj minimalne, uzasadnione zmiany,

\- oceniaj projekt przede wszystkim jako bazę wiedzy,

\- dostarczaj gotowe, commit-ready artefakty.



\## Workflow



Domyślny sposób pracy AI:



1\. Analiza aktualnego repozytorium.

2\. Identyfikacja problemów.

3\. Analiza wpływu zmian.

4\. Przygotowanie kompletnego pakietu zmian.

5\. Generowanie gotowych artefaktów.

6\. Propozycja commitu.



AI nie zatrzymuje się po każdym etapie, chyba że wymagana jest decyzja użytkownika lub ograniczenia narzędzi uniemożliwiają dalszą pracę.



\## Zasady odpowiedzi



\- Ograniczaj komentarze do minimum.

\- Nie powtarzaj wcześniejszych ustaleń.

\- Nie podsumowuj każdego etapu.

\- Skupiaj się na nowych ustaleniach.

\- Dostarczaj gotowe pliki zamiast opisu planowanych zmian.



\## Ocena zmian



Każda proponowana zmiana powinna wynikać z rzeczywistego stanu repozytorium.



Nie proponuj zmian wyłącznie dlatego, że są uznawane za dobrą praktykę.



Przed przygotowaniem pakietu zmian zawsze porównuję propozycje z aktualnym stanem repozytorium, aby nie proponować ponownie zmian już wprowadzonych.



\-----------------------------------------------------------------------------

\## AI Working Rules



The assistant must always:



1\. Read START\_HERE.md first.

2\. Analyse the current repository before proposing changes.

3\. Never rely on previous conversations.

4\. Verify that proposed elements do not already exist.

5\. Produce ready-to-commit changes.

6\. Prefer complete domain-oriented sprints over isolated records.

7\. Perform normalization/refactoring sprints when the model reaches sufficient maturity.





attributes.csv

&#x20;       │

&#x20;       ├── domains.csv

&#x20;       ├── units.csv

&#x20;       ├── value\_types.csv

&#x20;       └── validation\_rules.csv



Słowniki referencyjne są źródłem prawdy dla kontrolowanych wartości.



\-----------------------------------------------------------------------

\## File Modification Policy



AI preserves existing project knowledge.



Before replacing an existing file, AI evaluates the scope of changes.



Rules:



\- If changes affect less than approximately 50% of the file, generate only the required modifications.

\- If changes affect most of the file or its structure, generate the complete new file.

\- Never replace an existing file without first analysing its current contents.

\- Never remove existing project knowledge unless it is obsolete or duplicated.

