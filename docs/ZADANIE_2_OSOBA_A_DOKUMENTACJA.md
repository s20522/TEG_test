# Zadanie 2 — Osoba A

## Pełna dokumentacja dla początkującego

Ten dokument opisuje **zadanie 2 dla osoby A** w sposób możliwie prosty, ale technicznie kompletny. Celem tego etapu projektu jest doprowadzenie do stanu, w którym dane filmowe są już przygotowane, zaimportowane do **Neo4j**, osadzone jako **embeddingi** w **ChromaDB**, a następnie sprawdzone przez zestaw kontrolnych zapytań **Cypher**. Repozytorium zostało uzupełnione tak, aby ten etap miał wyraźny, powtarzalny pipeline i dało się go odtworzyć krok po kroku.

W praktyce ten etap odpowiada za trzy rzeczy. Po pierwsze, baza grafowa **Neo4j** ma przechowywać dane potrzebne do zapytań strukturalnych, takich jak liczenie filmów, filtrowanie po gatunku albo wyszukiwanie po fragmencie tytułu. Po drugie, **ChromaDB** ma przechowywać reprezentacje wektorowe opisów filmów, tak aby dało się wykonywać wyszukiwanie semantyczne, czyli „szukanie po znaczeniu”, a nie tylko po dokładnym słowie. Po trzecie, potrzebny jest prosty i czytelny mechanizm testowy, który pokaże, czy import rzeczywiście zadziałał i czy najważniejsze zapytania zwracają wynik.

| Element zadania 2 | Co zostało zrobione |
|---|---|
| Finalizacja importu do Neo4j | Utrzymany i spięty w jeden pipeline import danych filmowych do Neo4j |
| Embeddingi opisów filmów do ChromaDB | Dodano jawne użycie lokalnych embeddingów przez **Ollama** z modelem `nomic-embed-text` |
| Testowanie zapytań Cypher | Dodano osobny skrypt testujący zestaw bezpiecznych zapytań i zapisujący raport JSON |
| Dokumentacja | Dodano pełną dokumentację w Markdown pisaną dla początkującego |

## Co dokładnie robi osoba A w tym etapie

W podziale pracy osoba A odpowiada za warstwę danych i baz danych. To oznacza, że skupiamy się nie na interfejsie użytkownika ani nie na orkiestracji agentów, tylko na tym, żeby dane były dobrze przygotowane, poprawnie zapisane, możliwe do przeszukiwania oraz sprawdzalne. Jeżeli porównać to do budowy domu, to zadanie osoby A nie dotyczy jeszcze dekoracji wnętrza, tylko fundamentów, instalacji i tego, czy wszystko faktycznie działa pod spodem.

| Odpowiedzialność | Znaczenie |
|---|---|
| Dane wejściowe i ich czyszczenie | Przygotowanie danych do dalszego importu |
| Neo4j | Relacje i zapytania strukturalne |
| ChromaDB | Wyszukiwanie semantyczne na podstawie embeddingów |
| Ollama jako model embeddingowy | Lokalna generacja wektorów bez zewnętrznego API |
| Testy Cypher | Weryfikacja poprawności importu i podstawowych zapytań |

## Jak działa cały przepływ

Całość można rozumieć jako trzy kolejne warstwy. Najpierw dane są czyszczone i zamieniane do jednolitego formatu JSON. Następnie te same dane trafiają do dwóch różnych baz, ale z dwóch różnych powodów. **Neo4j** przechowuje strukturę powiązań, czyli węzły i relacje. **ChromaDB** przechowuje znaczeniową reprezentację opisów filmów. Dopiero po zakończeniu obu importów uruchamiamy testy zapytań w Neo4j, aby potwierdzić, że baza nie jest pusta i że można po niej zadawać konkretne pytania.

> Najważniejsza różnica jest taka, że **Neo4j odpowiada na pytania o strukturę**, a **ChromaDB odpowiada na pytania o podobieństwo semantyczne**.

## Struktura projektu po zmianach

Poniższa tabela pokazuje najważniejsze katalogi i pliki z punktu widzenia osoby początkującej. Nie trzeba znać wszystkiego na pamięć. Wystarczy zrozumieć, które pliki odpowiadają za dane, które za import, które za konfigurację i które za testy.

| Ścieżka | Rola w projekcie |
|---|---|
| `app/config/config.py` | Centralna konfiguracja projektu, w tym ustawienia Neo4j, ChromaDB i Ollama |
| `.env.example` | Wzór pliku `.env`, z którego użytkownik tworzy własną konfigurację |
| `scripts/utils/data_cleaner.py` | Pobieranie i czyszczenie danych, generowanie pliku `movies_all.json` |
| `scripts/import/neo4j_importer.py` | Import danych filmowych do Neo4j |
| `scripts/import/chromadb_importer.py` | Import danych do ChromaDB z lokalnymi embeddingami z Ollama |
| `scripts/import/neo4j_query_tester.py` | Testy zapytań Cypher i zapis raportu JSON |
| `scripts/import/run_all_imports.py` | Uruchomienie całego zadania 2 jednym poleceniem |
| `tests/` | Testy automatyczne uruchamiane lokalnie przez `pytest` |
| `docs/ZADANIE_2_OSOBA_A_DOKUMENTACJA.md` | Ten dokument |

## Co zmieniło się w kodzie

Najważniejsza zmiana dotyczy importu do **ChromaDB**. W poprzednim stanie projektu import opierał się bardziej na domyślnym zachowaniu biblioteki i nie pokazywał wprost, w jaki sposób generowane są embeddingi. Po zmianie importer robi to jawnie. Każdy dokument filmowy jest przygotowywany jako tekst zawierający tytuł, synopsis, gatunki i tagi. Następnie tekst trafia do lokalnej instancji **Ollama**, która generuje embedding przez model `nomic-embed-text`. Dopiero gotowe wektory są zapisywane do ChromaDB.

To rozwiązanie ma dwie zalety. Po pierwsze, jasno realizuje wymaganie z zadania 2 mówiące o lokalnym modelu embeddingowym. Po drugie, cały proces jest czytelniejszy i łatwiejszy do debugowania. Jeśli coś przestaje działać, wiemy, czy problem leży po stronie ChromaDB, czy po stronie Ollama.

Druga ważna zmiana to dodanie osobnego skryptu `neo4j_query_tester.py`. Ten plik uruchamia zestaw kontrolnych zapytań Cypher, które mają prosty, ale bardzo praktyczny cel: sprawdzić, czy baza działa po imporcie. Wyniki są zapisywane do raportu JSON, więc można je potem pokazać prowadzącemu, wrzucić do dokumentacji albo przeanalizować przy debugowaniu.

## Nowe zmienne środowiskowe

Do projektu zostały dopisane ustawienia, które są potrzebne, żeby zadanie 2 było naprawdę powtarzalne.

| Zmienna | Przykład | Znaczenie |
|---|---|---|
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Model embeddingowy używany do generowania wektorów |
| `OLLAMA_TIMEOUT` | `120` | Maksymalny czas oczekiwania na odpowiedź Ollama |
| `REPORTS_DIR` | `./reports` | Katalog, do którego zapisywane są raporty testów |

Jeżeli ktoś dopiero zaczyna, powinien myśleć o pliku `.env` jako o miejscu, w którym projekt „czyta ustawienia świata zewnętrznego”. Tam wpisujemy adresy usług, nazwy modeli i ścieżki do danych. Sam kod nie powinien mieć takich wartości wpisanych na sztywno, bo wtedy trudniej byłoby go przenosić między komputerami.

## Jak przygotować środowisko od zera

Jeżeli zaczynasz od zera, najpierw sklonuj repozytorium i przejdź do katalogu projektu. Następnie utwórz plik `.env` na podstawie `.env.example`. To standardowy krok w większości projektów Pythona i Dockera, bo pozwala zachować elastyczność konfiguracji.

| Krok | Polecenie |
|---|---|
| Sklonowanie repozytorium | `git clone <adres_repo>` |
| Wejście do katalogu | `cd TEG_test` |
| Utworzenie pliku `.env` | `cp .env.example .env` |
| Instalacja zależności | `pip install -r requirements.txt` |

Po tym kroku trzeba zadbać o usługi zewnętrzne. Projekt zakłada użycie **Neo4j**, **ChromaDB** oraz **Ollama**. Jeśli używasz Dockera, możesz uruchomić usługi kontenerowe zgodnie z plikiem `docker-compose.yml`. Dodatkowo trzeba zadbać, aby w Ollama był dostępny model `nomic-embed-text`, bo bez niego import embeddingów się nie powiedzie.

| Usługa | Co musi działać |
|---|---|
| Neo4j | Port `7687` i poprawne dane logowania |
| ChromaDB | Port `8000` |
| Ollama | Port `11434` oraz pobrany model `nomic-embed-text` |

## Jak przygotować dane

Przed uruchomieniem samego zadania 2 trzeba mieć przygotowany plik `movies_all.json`. To właśnie ten plik jest wejściem dla obu importerów. Generuje go skrypt `scripts/utils/data_cleaner.py`. W uproszczeniu robi on trzy rzeczy: pobiera dane źródłowe, czyści teksty i zapisuje wynik w jednym, spójnym formacie JSON.

Aby wygenerować dane, uruchom skrypt czyszczący. Po jego zakończeniu w katalogu `data/processed/` powinien pojawić się plik `movies_all.json`. Jeśli tego pliku nie ma, kolejne kroki nie ruszą.

## Jak uruchomić zadanie 2

Najprościej uruchomić cały pipeline jednym poleceniem. Właśnie do tego służy `scripts/import/run_all_imports.py`. Ten skrypt jest głównym wejściem dla zadania 2 osoby A.

```bash
python scripts/import/run_all_imports.py
```

Po uruchomieniu skrypt robi kolejno import do Neo4j, import do ChromaDB z embeddingami z Ollama i testy zapytań Cypher. Jeśli wszystko pójdzie dobrze, w katalogu raportów pojawią się pliki podsumowujące wynik.

| Raport | Zawartość |
|---|---|
| `reports/neo4j_query_report.json` | Wyniki testów zapytań Cypher |
| `reports/task2_summary.json` | Krótkie podsumowanie, które etapy zakończyły się sukcesem |

## Jak działa import do ChromaDB

Warto dobrze zrozumieć ten fragment, bo to właśnie on jest najbardziej charakterystyczny dla zadania 2. Każdy film jest zamieniany do postaci dokumentu tekstowego, który zawiera podstawowe informacje o filmie. Ten dokument nie służy do „czytania przez człowieka”, tylko do przygotowania embeddingu, czyli liczbowej reprezentacji znaczenia tekstu. Model `nomic-embed-text` działający lokalnie w **Ollama** zamienia tekst na wektor liczb. Ten wektor jest następnie zapisywany w **ChromaDB** razem z metadanymi, takimi jak `imdb_id`, tytuł, tagi i gatunki.

Wyszukiwanie działa podobnie. Pytanie użytkownika także jest zamieniane do embeddingu, a potem porównywane z zapisanymi wektorami filmów. Dzięki temu można znaleźć filmy podobne znaczeniowo, nawet jeśli użytkownik nie użył dokładnie tych samych słów, które są w opisie filmu.

## Jak działają testy Cypher

Skrypt `neo4j_query_tester.py` uruchamia kilka podstawowych, bezpiecznych zapytań. Chodzi tutaj zarówno o sprawdzenie poprawności technicznej, jak i o przygotowanie materiału do pokazania, że baza faktycznie jest używalna.

| Nazwa testu | Co sprawdza |
|---|---|
| `count_movies` | Czy w bazie znajdują się filmy |
| `top_genres` | Czy relacje `IN_GENRE` działają poprawnie |
| `movies_by_genre` | Czy można pobrać filmy dla konkretnego gatunku |
| `title_keyword_search` | Czy można wyszukiwać filmy po fragmencie tytułu |
| `person_relations_check` | Czy istnieją relacje osób z filmami |

Ważne jest też to, że zapytania przyjmujące dane od użytkownika korzystają z **parametrów** zamiast sklejać tekst zapytania ręcznie. To jest dobra praktyka bezpieczeństwa, bo ogranicza ryzyko wstrzyknięcia niebezpiecznych fragmentów zapytania.

> Parametryzacja zapytań to podstawowy krok w stronę ochrony przed **Cypher injection**.

## Jak uruchomić same testy Cypher

Jeżeli nie chcesz wykonywać całego pipeline’u jeszcze raz, możesz uruchomić sam test zapytań.

```bash
python scripts/import/neo4j_query_tester.py
```

To polecenie nie tworzy nowych danych, tylko sprawdza, czy Neo4j odpowiada poprawnie na zestaw kontrolnych zapytań. Po zakończeniu działania skrypt zapisze raport JSON w katalogu raportów.

## Jak uruchomić testy automatyczne

Do repozytorium zostały dodane testy jednostkowe oparte na `pytest`. Ich zadaniem nie jest zastąpienie prawdziwego uruchomienia usług, tylko szybkie sprawdzenie logiki kodu. Dzięki nim można potwierdzić, że importer buduje dokumenty poprawnie, że przekazuje embeddingi do ChromaDB i że raporty Neo4j zapisują się we właściwym formacie.

```bash
pytest -q
```

To jest szczególnie przydatne wtedy, gdy jeszcze nie masz uruchomionych wszystkich usług, ale chcesz sprawdzić, czy sama logika programu nie została zepsuta przez ostatnie zmiany.

## Co sprawdzić na końcu

Na końcu warto wykonać prostą checklistę. Jeśli wszystkie poniższe odpowiedzi są pozytywne, to można uznać, że zadanie 2 dla osoby A jest gotowe do pokazania i dalszego rozwijania.

| Pytanie kontrolne | Oczekiwany wynik |
|---|---|
| Czy istnieje `movies_all.json`? | Tak |
| Czy Neo4j przyjmuje import? | Tak |
| Czy ChromaDB zapisuje dokumenty i embeddingi? | Tak |
| Czy Ollama ma model `nomic-embed-text`? | Tak |
| Czy raport z testów Cypher powstaje? | Tak |
| Czy `pytest` przechodzi bez błędów? | Tak |

## Najczęstsze problemy i ich znaczenie

Jeśli podczas uruchamiania coś nie działa, najpierw sprawdź usługi i plik `.env`. W praktyce większość problemów wynika właśnie z tego, że któraś usługa nie działa na odpowiednim porcie albo że model embeddingowy nie został pobrany do Ollama.

| Problem | Możliwa przyczyna | Co zrobić |
|---|---|---|
| Brak połączenia z Neo4j | Zły adres lub hasło | Sprawdź `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` |
| Brak połączenia z ChromaDB | Serwis nie działa | Sprawdź port `8000` i kontener/usługę |
| Brak modelu embeddingowego | `nomic-embed-text` nie został pobrany | Uruchom `ollama pull nomic-embed-text` |
| Brak `movies_all.json` | Nie uruchomiono `data_cleaner.py` | Najpierw wygeneruj dane |
| Puste wyniki testów Cypher | Import nie wgrał danych | Sprawdź logi z `run_all_imports.py` |

## Jak to się odnosi do całego projektu

Ten etap jest fundamentem dla dalszych części projektu. Osoba B buduje agentów, routery i logikę odpowiedzi, ale bez poprawnie przygotowanych baz danych ci agenci nie mieliby z czego korzystać. Innymi słowy, zadanie 2 osoby A przygotowuje zaplecze, z którego później będzie korzystał cały system.

To oznacza, że dobrze wykonane zadanie 2 ma znaczenie nie tylko samo w sobie. Ono wpływa też na to, czy później Graph Agent, Semantic Agent i reszta przepływu będą miały sens. Jeśli dane są źle zaimportowane albo embeddingi nie zostały utworzone, to dalsza część projektu będzie wyglądała na niedziałającą, nawet jeśli jej kod będzie poprawny.

## Podsumowanie

Po zmianach repozytorium ma wyraźnie domknięty etap zadania 2 dla osoby A. Import do **Neo4j** jest częścią jednego pipeline’u, import do **ChromaDB** używa jawnie lokalnych embeddingów przez **Ollama**, a testy **Cypher** tworzą raport końcowy. Do tego dochodzą testy automatyczne i kompletna dokumentacja. Dzięki temu ten etap jest nie tylko napisany, ale też bardziej zrozumiały, łatwiejszy do pokazania i łatwiejszy do odtworzenia przez inną osobę.

## References

[1]: https://ollama.com/library/nomic-embed-text "nomic-embed-text"
[2]: https://docs.trychroma.com/integrations/embedding-models/ollama "Ollama - Chroma Docs"
[3]: https://docs.trychroma.com/reference/python/collection "Collection - Chroma Docs"
