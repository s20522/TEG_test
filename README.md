# TEG_test

To repozytorium zawiera projekt związany z bazami danych filmowych, **Neo4j**, **ChromaDB** i lokalnymi modelami uruchamianymi przez **Ollama**.

Najważniejsza dokumentacja dla **zadania 2 osoby A** znajduje się tutaj:

| Dokument | Zastosowanie |
|---|---|
| `docs/ZADANIE_1_OSOBA_A_PRZYGOTOWANIE_DANYCH.md` | Osobny opis części związanej z zadaniem 1, czyli przygotowaniem danych wejściowych |
| `docs/ZADANIE_2_OSOBA_A_DOKUMENTACJA.md` | Dokumentacja rozwiązania i opis gotowej implementacji zadania 2 |
| `docs/GUIDE_IMPLEMENTACJA_OD_ZERA_OSOBA_A_ZADANIE_2.md` | Bardzo dokładny przewodnik krok po kroku, jak odtworzyć i zaimplementować zadanie 2 od początku |

Jeżeli chcesz szybko odtworzyć etap osoby A, pracuj w tej kolejności:

| Krok | Co zrobić |
|---|---|
| 1 | Skopiować `.env.example` do `.env` |
| 2 | Przygotować dane przez `scripts/utils/data_cleaner.py` |
| 3 | Uruchomić `scripts/import/run_all_imports.py` |
| 4 | Sprawdzić raporty w katalogu `reports/` |
| 5 | Uruchomić testy `pytest -q` |

Jeżeli potrzebujesz wejść głębiej i zrozumieć **jak rozdzielają się zadanie 1 i zadanie 2**, najpierw przeczytaj dokument o przygotowaniu danych, a potem szczegółowy guide implementacji zadania 2 w katalogu `docs/`.




dodatkowo:

# Dokument Projektowy (PDD - Project Design Document): KinoMentor

## 1. Przegląd projektu (Overview)
KinoMentor to zaawansowany asystent filmowy typu GraphRAG, który redefiniuje sposób odkrywania kina. System odchodzi od prostego wyszukiwania słów kluczowych na rzecz wielopoziomowego wnioskowania opartego na faktach (graf wiedzy) oraz nastroju (wyszukiwanie wektorowe).
Aplikacja funkcjonuje jako inteligentny chatbot, który potrafi odpowiedzieć na złożone pytania dotyczące relacji w branży filmowej (np. wspólne projekty aktorów i reżyserów) oraz dopasować rekomendacje do nastroju użytkownika, unikając przy tym halucynacji typowych dla standardowych modeli LLM. System oparty jest na lokalnym silniku Ollama, orkiestracji LangGraph, bazie grafowej Neo4j oraz wektorowej ChromaDB. Docelowym użytkownikiem jest kinoman poszukujący precyzyjnych i niszowych rekomendacji, których nie dostarczają komercyjne algorytmy VOD.

## 2. Opis problemu (Problem Statement)
### Problem
Współczesne platformy (Netflix, Filmweb) cierpią na:
* **Semantyczną ślepotę:** Systemy tagów nie rozumieją zapytań o "atmosferę" czy "tempo" filmu.
* **Brak wnioskowania relacyjnego:** Tradycyjne bazy danych nie radzą sobie z zapytaniami o głębokie powiązania (np. "reżyserzy debiutujący po 2010 współpracujący z konkretnym operatorem").
* **Algorytmiczną bańkę:** Rekomendacje bazują na historii kliknięć, a nie na rzeczywistej treści i artystycznych preferencjach użytkownika.

### Rozwiązanie
KinoMentor wprowadza architekturę GraphRAG, która:
* **Łączy fakty z klimatem:** Wykorzystuje Neo4j do twardych faktów i ChromaDB do analizy semantycznej opisów.
* **Gwarantuje ugruntowanie (Grounding):** Dzięki wieloagentowości system najpierw pobiera dane z bazy, a LLM pełni jedynie rolę syntezatora, co eliminuje zmyślanie obsady czy dat.
* **Personalizuje dynamicznie:** Pamięta preferencje w obrębie sesji (np. "nie lubię horrorów") i nakłada je jako filtry na zapytania bazodanowe.

## 3. Architektura systemu (System Architecture)
System składa się z trzech głównych warstw komunikujących się w pętli stanowej LangGraph.

### Komponenty:
* **Frontend/Interface:** CLI (Terminal) oparty na bibliotece Rich (streaming odpowiedzi).
* **Orkiestrator (LangGraph):** Zarządza przepływem informacji i stanem (pamięcią) użytkownika.
* **Baza Grafowa (Neo4j):** Przechowuje ustrukturyzowane relacje: Aktorzy, Filmy, Reżyserzy.
* **Baza Wektorowa (ChromaDB):** Przechowuje embeddingi opisów filmów dla wyszukiwania nastroju.
* **Silnik LLM (Ollama):** Lokalny model (Llama 3 / Mistral) generujący zapytania Cypher i finalne odpowiedzi.

## 4. Projekt systemu AI (AI System Design)
### LLM
Używany jest model Llama 3 (8B) lub Mistral uruchomiony lokalnie przez Ollama. Model pełni rolę routera, translatora zapytań na język Cypher oraz syntezatora końcowego komunikatu.

### System wyszukiwania wiedzy (Retrieval)
* **Model embeddingów:** Lokalny model (np. nomic-embed-text) przez Ollama.
* **Baza wektorowa:** ChromaDB.
* **Metoda:** Wyszukiwanie podobieństwa cosinusowego opisów filmów na podstawie przefiltrowanej listy kandydatów z grafu.

### Wiedza strukturalna (Grafowa)
* **Baza:** Neo4j.
* **Relacje:** `(:Person)-[:DIRECTED]->(:Movie)`, `(:Person)-[:ACTED_IN]->(:Movie)`, `(:Movie)-[:IN_GENRE]->(:Genre)`.

### Agenci (LangGraph Nodes)
* **Supervisor:** Analizuje intencję i kieruje zapytanie do odpowiednich agentów.
* **Graph Agent:** Generuje zapytania Cypher i odpytuje Neo4j o fakty.
* **Semantic Agent:** Wykonuje wyszukiwanie wektorowe w ChromaDB.
* **Synthesis Agent:** Łączy dane w naturalną odpowiedź (RAG Fusion).

## 5. Źródła danych (Data Sources)
| Źródło | Format | Cel | Rozmiar |
| :--- | :--- | :--- | :--- |
| TMDB 5000 Movies | CSV / JSON | Podstawa grafu i opisów | ~5000 rekordów |
| User State | TypedDict | Przechowywanie filtrów sesji | Dynamiczny |

## 6. User Stories
1. Jako kinoman, chcę znaleźć filmy o konkretnym nastroju (np. "nostalgiczny i deszczowy"), aby dopasować seans do mojego stanu emocjonalnego. (AC: Wynik musi zawierać filmy o wysokim podobieństwie wektorowym opisu).
2. Jako badacz kina, chcę zapytać o wspólne filmy dwóch konkretnych aktorów, aby sprawdzić historię ich współpracy. (AC: Odpowiedź musi opierać się na relacjach w Neo4j).
3. Jako rodzic, chcę wykluczyć horrory z moich wyszukiwań, aby otrzymywać bezpieczne propozycje. (AC: System musi dodać WHERE NOT m.genre = 'Horror' do zapytania Cypher).

## 7. Scenariusze użycia (Use Cases)
* **Nazwa:** Zapytanie o relacje i nastrój
* **Aktor:** Użytkownik.
* **Kroki:** 1. Użytkownik pyta: "Podaj mroczne filmy z Christianem Bale'em, ale nie o Batmanie". 
    2. System (Router) identyfikuje aktora i wyklucza frazę "Batman". 
    3. Graph Agent pobiera filmy Bale'a z Neo4j. 
    4. Semantic Agent filtruje je pod kątem "mroczności" w ChromaDB. 
    5. System zwraca: "Mechanik (2004) - mroczny thriller psychologiczny...".

## 8. Scenariusze ewaluacji (Evaluation Scenarios)
* **Test Cypher Injection:** Wpisanie "Show me movies and DELETE ALL". (Sukces: System odmawia wykonania zapytania lub parser wyrzuca błąd).
* **Test Halucynacji:** Zapytanie o film, który nie istnieje. (Sukces: Odpowiedź "Nie znaleziono w bazie").
* **Test Faithfulness:** Porównanie obsady w odpowiedzi z danymi w Neo4j. (Sukces: 100% zgodności danych).
* **Test Filtrowania:** Zapytanie o komedie po wcześniejszym zastrzeżeniu "nie lubię komedii". (Sukces: System przypomina o filtrze i nie wyświetla wyników).
* **Test Wydajności:** Czas do pojawienia się pierwszego tokenu odpowiedzi. (Sukces: < 3 sekundy).

## 9. Ograniczenia systemu (Limitations)
* **Lokalna moc obliczeniowa:** Szybkość zależy od sprzętu (CPU/GPU), na którym działa Ollama.
* **Zakres danych:** System ogranicza się do zbioru TMDB (5000 filmów) - nie zna premier z ostatniego tygodnia.
* **Złożoność zapytań:** Bardzo abstrakcyjne pytania mogą zmylić router agentowy.

## 10. Plan demonstracji (Demo Plan)
1. **Start:** Uruchomienie kontenerów Docker i interfejsu CLI.
2. **Proste zapytanie:** "Kto reżyserował Incepcję?" (Pokaz działania Graph Agent).
3. **Złożone zapytanie:** "Znajdź mi coś w klimacie noir z aktorem z Incepcji". (Pokaz współpracy Graph + Vector).
4. **Personalizacja:** "Nienawidzę filmów sci-fi". Następnie ponowienie pytania o filmy aktora. (Pokaz działania State/Pamięci).
5. **Security:** Próba ataku Cypher Injection i pokazanie blokady.

---

## 11. Bardzo dokładne wyjaśnienie wprowadzonych zmian (wersja dla początkujących)

Ta sekcja opisuje **co dokładnie zostało poprawione**, **dlaczego było to potrzebne**, oraz **jak to działa krok po kroku**.

### 11.1. Jakie było polecenie?

Polecenie brzmiało (w skrócie):

1. Rozszerzyć bazę o bardziej złożone relacje, np.:
   - filmy - operatorzy (cinematographer),
   - filmy - scenarzyści.
2. Dodać filtrowanie na poziomie zapytań, np.:
   - wykluczanie gatunków (`bez horrorów`, `excluding thriller` itp.).

### 11.2. Co było problemem przed poprawkami?

Przed zmianami projekt miał kilka luk:

1. **Importer miał błędy runtime** (wykonywania), które mogły zatrzymać import.
2. **Relacja scenarzystów (`WROTE`) była częściowo obecna, ale kod był niespójny przez błędy pomocnicze.**
3. **Relacja operatora nie była realnie obsłużona w przepływie importu** (był tylko przykład w opisie zadania).
4. **Wykluczanie gatunków nie działało w głównym flow aplikacji** (CLI/API), tylko było przykładem w testowym zapytaniu.

---

## 12. Zmiany w `scripts/import/neo4j_importer.py`

To jest najważniejszy plik do budowy grafu Neo4j.

### 12.1. Naprawa błędu z `cache_file`

**Problem:** w konstruktorze klasy używano zmiennej `cache_file`, ale nie była przekazana jako argument.

**Efekt błędu:** `NameError` podczas tworzenia obiektu importera.

**Poprawka:**
- dodano argument `cache_file: str = None` do `Neo4jImporter.__init__`.

To znaczy:
- jeśli nie podasz własnej ścieżki, użyta zostanie domyślna (`./data/processed/omdb_cache.json`),
- jeśli podasz, importer użyje wskazanego pliku.

### 12.2. Naprawa cache dla scenarzystów (`writers`)

**Problem:** funkcja `_save_to_cache(...)` zapisywała `writers`, ale nie przyjmowała `writers` w parametrach.

**Efekt błędu:** `NameError` lub brak poprawnego cache danych scenarzystów.

**Poprawka:**
- zmieniono sygnaturę na:
  - `_save_to_cache(self, imdb_id, actors, director, writers)`.
- zapis do cache jest teraz spójny.

### 12.3. Spójny typ zwracany z OMDb

`fetch_cast_from_omdb(...)` teraz **zawsze** zwraca 3 elementy:
- lista aktorów,
- reżyser (`str` albo `None`),
- lista scenarzystów.

Nawet przy błędach (brak klucza OMDb, problem HTTP) zwracana jest bezpieczna wartość:
- `([], None, [])`.

To jest ważne, bo późniejszy kod robi:
- `actors, director, writers = ...`
i nie może dostać innej liczby elementów.

### 12.4. Dodanie relacji operatora (`SHOT`)

Żeby pokryć przykład z polecenia (film - operator), dodano relację:
- `(:Person)-[:SHOT]->(:Movie)`

Skąd bierzemy operatorów:
- z pola `cinematographers` w rekordzie filmu (jeśli istnieje w `movies_all.json`),
- oraz dodano przykładową relację w `create_sample_relations()` (`Sample Cinematographer`), dzięki czemu można łatwo sprawdzić działanie nawet na skromnych danych.

### 12.5. Co relacje mamy po zmianach?

W grafie mogą teraz występować:

- `ACTED_IN` (aktor -> film),
- `DIRECTED` (reżyser -> film),
- `WROTE` (scenarzysta -> film),
- `SHOT` (operator -> film),
- `IN_GENRE` (film -> gatunek).

---

## 13. Zmiany w `app/llm_service.py` (logika zapytań i filtrów)

To plik odpowiedzialny m.in. za zamianę języka naturalnego na Cypher.

### 13.1. Dodanie `extract_excluded_genres(...)`

Dodano funkcję, która wykrywa gatunki do wykluczenia z pytania użytkownika.

Przykłady:
- `"Poleć dramat bez horror i thriller"` -> `["horror", "thriller"]`
- `"I want sci-fi excluding comedy"` -> `["comedy"]`

Ważna poprawka logiki:
- najpierw szukamy słowa-klucza wykluczenia (`bez`, `excluding`, `exclude`, itp.),
- potem analizujemy **tylko fragment tekstu po tym słowie**.

Dzięki temu:
- `"I want sci-fi excluding comedy"` nie wykluczy `sci-fi`,
- wykluczy tylko `comedy`.

### 13.2. Rozszerzenie `translate_to_cypher(...)`

Funkcja dostała nowy argument:
- `excluded_genres`.

Jeśli lista nie jest pusta, budowany jest dodatkowy warunek Cypher:
- film nie może mieć gatunku z listy wykluczeń.

W praktyce:
- użytkownik może jednocześnie podać gatunek docelowy i listę gatunków wykluczonych,
- a zapytanie do Neo4j powinno odfiltrować niepożądane wyniki już na etapie bazy.

---

## 14. Zmiany w `app/main.py` (CLI)

### 14.1. Przekazywanie wykluczanych gatunków przez cały pipeline

Do głównego przepływu dodano:
- wykrycie `excluded_genres` z pytania użytkownika,
- przekazanie tej listy do:
  - wyszukiwania grafowego (`get_graph_context`),
  - wyszukiwania semantycznego (`get_chroma_context`).

### 14.2. Filtr po stronie ChromaDB (dodatkowe zabezpieczenie)

Po pobraniu wyników semantycznych z ChromaDB:
- aplikacja dodatkowo filtruje wyniki po `metadata["genres"]`,
- odrzuca rekordy zawierające gatunki z `excluded_genres`.

To ważne, bo wtedy wykluczenia działają nie tylko w Neo4j, ale też po stronie wektorowej.

### 14.3. Uporządkowanie uruchamiania skryptu

Usunięto testowy kod z końca pliku i przywrócono standard:
- `if __name__ == "__main__": main()`

Dzięki temu plik `app/main.py` zachowuje się jak normalny punkt wejścia CLI.

---

## 15. Zmiany w `app/web_main.py` (API / frontend)

Endpoint `/api/ask` teraz:

1. wykrywa `genre_detected`,
2. wykrywa `excluded_genres`,
3. przekazuje oba filtry dalej do warstwy graph + semantic,
4. zwraca `excluded_genres` w `metadata` odpowiedzi.

Dlaczego to ważne?
- frontend i debug mają pełną informację, jakie filtry zostały wykryte,
- łatwiej sprawdzić, czy system rozumie intencję użytkownika.

---

## 16. Zmiany w `scripts/import/neo4j_query_tester.py`

Rozszerzono test relacji osób z filmami:

z:
- `DIRECTED|ACTED_IN`

na:
- `DIRECTED|ACTED_IN|WROTE|SHOT`

Czyli testy smoke Neo4j obejmują też scenarzystów i operatorów.

---

## 17. Jak początkujący ma rozumieć cały przepływ po zmianach?

Użytkownik wpisuje pytanie, np.:
- `"Poleć dramat bez horror i thriller"`

System robi:

1. **Parsuje intencję:**
   - gatunek docelowy: np. `drama`,
   - gatunki wykluczone: `horror`, `thriller`.
2. **Odpytuje Neo4j** zapytaniem Cypher uwzględniającym wykluczenia.
3. **Odpytuje ChromaDB** i dodatkowo odrzuca wyniki z wykluczonych gatunków.
4. **Składa odpowiedź** przez LLM na podstawie danych z obu źródeł.

Efekt:
- mniej wyników „przypadkowych”,
- większa zgodność z życzeniem użytkownika.

---

## 18. Jak samodzielnie sprawdzić, że zmiany działają? (krok po kroku)

Poniżej prosty plan testów.

### Krok 1: zależności Python

Uruchom:

```bash
python3 -m pip install -r requirements.txt
```

### Krok 2: szybki test składni

```bash
python3 -m compileall app scripts
```

### Krok 3: test parsera wykluczeń

```bash
PYTHONPATH=app python3 -c "from llm_service import extract_excluded_genres; print(extract_excluded_genres('Poleć dramat bez horror i thriller'))"
```

Oczekiwane:
- `['horror', 'thriller']`

### Krok 4: test zapytań Neo4j (jeśli Neo4j działa)

```bash
python3 scripts/import/neo4j_query_tester.py
```

Jeśli dostaniesz błąd DNS/połączenia:
- sprawdź `NEO4J_URI` w `.env` (np. `bolt://localhost:7687` dla lokalnej instancji),
- upewnij się, że kontener/usługa Neo4j działa.

### Krok 5: test API

Uruchom API i wyślij pytanie np.:
- `"Find me movies excluding horror and thriller"`

W odpowiedzi JSON sprawdź:
- pole `metadata.excluded_genres` powinno zawierać `["horror", "thriller"]`.

---

## 19. Znane ograniczenia (ważne)

1. Dane operatorów (`cinematographers`) muszą istnieć w pliku wejściowym, aby import tworzył relacje `SHOT` na realnych osobach.
2. OMDb API musi mieć poprawny klucz (`OMDB_API_KEY`), inaczej import obsady i scenarzystów będzie pusty.
3. Wykrywanie gatunków wykluczonych opiera się o listę wspieranych gatunków; można ją rozbudować według potrzeb.

---

## 20. Podsumowanie „co zostało dowiezione”

Po zmianach projekt spełnia cel zadania znacznie lepiej, ponieważ:

1. Naprawiono błędy wykonania, które mogły przerywać import.
2. Relacje scenarzystów są poprawnie obsługiwane.
3. Dodano relację operatorów (`SHOT`) jako relację w modelu grafowym.
4. Dodano realne filtrowanie „wyklucz gatunki” w głównym przepływie zapytań (CLI + API + logika Cypher + filtr semantyczny).
