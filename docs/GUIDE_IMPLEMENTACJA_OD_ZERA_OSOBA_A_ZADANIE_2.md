# Guide implementacji od zera — Zadanie 2, Osoba A

## Wersja dla początkującego developera / studenta

Ten przewodnik tłumaczy **jak samodzielnie zaimplementować zadanie 2 dla osoby A od początku do końca**, nawet jeśli startujesz tylko z wcześniejszej wersji projektu i nie czujesz się jeszcze pewnie w Pythonie, Dockerze, Neo4j, ChromaDB czy Ollama. Został napisany tak, jakbym prowadził Cię przez cały proces przy jednym komputerze: najpierw wyjaśnimy **po co** coś robimy, potem **co dokładnie** trzeba przygotować, a na końcu **jak sprawdzić**, czy działa. 

Ten etap projektu ma jeden bardzo ważny cel: przygotować warstwę danych, z której później będą mogły korzystać kolejne części systemu. Oznacza to, że nie budujemy tutaj jeszcze pełnego „inteligentnego asystenta”, tylko tworzymy jego zaplecze. To zaplecze składa się z trzech filarów. Pierwszym jest **Neo4j**, czyli baza grafowa przechowująca relacje między encjami. Drugim jest **ChromaDB**, czyli baza wektorowa do wyszukiwania semantycznego. Trzecim jest **Ollama**, które lokalnie generuje embeddingi tekstu bez potrzeby używania zewnętrznego API [1] [2] [3].

> Jeśli chcesz zapamiętać tylko jedną rzecz z całego dokumentu, zapamiętaj to: **Neo4j odpowiada na pytania o strukturę danych, a ChromaDB odpowiada na pytania o podobieństwo znaczeniowe tekstu**.

| Warstwa | Po co istnieje | Przykład pytania |
|---|---|---|
| **Neo4j** | Trzyma relacje i strukturę danych | „Jakie filmy należą do gatunku horror?” |
| **ChromaDB** | Trzyma embeddingi i umożliwia wyszukiwanie semantyczne | „Znajdź filmy podobne do opisu o zemście i morderstwie” |
| **Ollama** | Lokalnie generuje embeddingi | „Zamień ten opis filmu na wektor liczb” |

## 1. Co dokładnie implementujesz

Zadanie 2 dla osoby A można potraktować jako budowę małego, ale kompletnego pipeline’u danych. Pipeline oznacza ciąg kroków wykonywanych w odpowiedniej kolejności. W tym projekcie kolejność jest taka sama za każdym razem: najpierw przygotowujemy dane, potem importujemy je do **Neo4j**, później tworzymy embeddingi i zapisujemy je w **ChromaDB**, a na końcu wykonujemy testy kontrolne w **Cypher**, żeby upewnić się, że wynik ma sens.

W praktyce implementacja sprowadza się do odpowiedzi na pięć pytań. Po pierwsze, **skąd biorą się dane** i w jakim formacie mają być zapisane. Po drugie, **jak wgrać te dane do Neo4j**. Po trzecie, **jak zamienić opisy filmów na embeddingi**. Po czwarte, **jak zapisać embeddingi w ChromaDB**. Po piąte, **jak zautomatyzować cały proces**, aby jedna osoba mogła uruchomić wszystko jednym poleceniem i dostać raport końcowy.

| Pytanie implementacyjne | Odpowiedź w projekcie |
|---|---|
| Skąd biorą się dane? | Z przetworzonego pliku `movies_all.json` |
| Gdzie trafiają dane strukturalne? | Do **Neo4j** |
| Gdzie trafiają embeddingi? | Do **ChromaDB** |
| Kto generuje embeddingi? | **Ollama** z modelem `nomic-embed-text` [1] [2] |
| Jak sprawdzić, czy działa? | Przez `neo4j_query_tester.py`, raporty JSON i testy `pytest` |

## 2. Jak myśleć o tym projekcie zanim zaczniesz pisać kod

Bardzo częsty błąd początkujących polega na tym, że zaczynają od pisania funkcji bez pełnego obrazu całości. Tutaj warto zrobić odwrotnie. Najpierw zbuduj sobie w głowie **mapę przepływu danych**. Film pojawia się jako rekord wejściowy, potem zostaje przepisany do dwóch form. Jedna forma jest grafowa, czyli nadaje się do Neo4j. Druga jest tekstowa, czyli nadaje się do wygenerowania embeddingu. To są dwa równoległe zastosowania tej samej informacji.

Dzięki takiemu spojrzeniu od razu wiadomo, dlaczego potrzebujesz dwóch baz. Jedna baza nie rozwiązuje wszystkiego. **Neo4j** jest świetne do relacji, ale nie służy do nowoczesnego wyszukiwania semantycznego. **ChromaDB** dobrze radzi sobie z podobieństwem wektorowym, ale nie zastąpi grafu relacji [2] [4]. Razem te dwa komponenty tworzą sensowną architekturę pod dalsze etapy projektu.

## 3. Co musisz mieć przed startem

Zanim cokolwiek uruchomisz, potrzebujesz kilku elementów środowiska. Najprościej myśleć o tym jak o stanowisku laboratoryjnym. Sam kod nie wystarczy. Kod musi mieć gdzie się połączyć i na czym pracować. Dlatego potrzebujesz **Pythona**, **Dockera** albo osobno uruchomionych usług, działającego **Neo4j**, działającego **ChromaDB** i działającego **Ollama** z pobranym modelem embeddingowym [1] [2] [5].

| Narzędzie / usługa | Dlaczego jest potrzebne |
|---|---|
| Python 3.x | Do uruchamiania skryptów projektu |
| `pip` | Do instalacji zależności z `requirements.txt` |
| Docker i Docker Compose | Do uruchomienia usług w kontenerach, jeśli korzystasz z konteneryzacji |
| Neo4j | Do przechowywania struktury i relacji |
| ChromaDB | Do przechowywania dokumentów i embeddingów |
| Ollama | Do lokalnej generacji embeddingów |
| Model `nomic-embed-text` | Do zamiany tekstu na wektory [1] |

Jeżeli korzystasz z Dockera, wygoda polega na tym, że nie musisz ręcznie instalować każdej usługi osobno. Jeśli jednak coś nie działa, warto pamiętać, że „Docker wszystko ukrywa” i przez to czasem trudniej zrozumieć, gdzie jest błąd. Dlatego w tym przewodniku będę stale tłumaczył nie tylko **co uruchomić**, ale też **dlaczego** dany element ma znaczenie.

## 4. Krok pierwszy — pobranie projektu i przygotowanie katalogu roboczego

Zaczynasz od pobrania repozytorium i wejścia do katalogu projektu. To jest najprostszy etap, ale warto zrobić go porządnie. Upewnij się, że jesteś na właściwej gałęzi roboczej i że pracujesz w czystym katalogu.

```bash
git clone https://github.com/s20522/TEG_test.git
cd TEG_test
```

Jeżeli pracujesz nad własną wersją, zwykle od razu warto utworzyć nowy branch. Dzięki temu nie mieszasz swojej pracy z gałęzią główną i w razie problemu łatwo porównać zmiany.

```bash
git checkout -b osoba-a-zadanie-2-praca
```

| Co robisz | Dlaczego to ma znaczenie |
|---|---|
| Klonujesz repozytorium | Pobierasz pełny kod projektu |
| Wchodzisz do katalogu | Wszystkie następne polecenia wykonujesz już we właściwym miejscu |
| Tworzysz branch | Izolujesz swoje zmiany i ułatwiasz ich późniejszy przegląd |

## 5. Krok drugi — zrozumienie struktury katalogów

Zanim uruchomisz projekt, poświęć chwilę na obejrzenie struktury plików. To jest bardzo ważne dla początkującego, bo wtedy kod przestaje wyglądać jak przypadkowa grupa plików. Zaczynasz widzieć, które katalogi odpowiadają za konfigurację, które za dane, a które za logikę importu.

| Ścieżka | Rola |
|---|---|
| `app/config/config.py` | Trzyma konfigurację i wartości odczytywane ze środowiska |
| `.env.example` | Pokazuje, jakie zmienne środowiskowe są potrzebne |
| `data/raw/` | Dane surowe lub wejściowe |
| `data/processed/` | Dane po czyszczeniu, gotowe do importu |
| `scripts/utils/data_cleaner.py` | Przygotowuje dane do wspólnego formatu |
| `scripts/import/neo4j_importer.py` | Ładuje dane do Neo4j |
| `scripts/import/chromadb_importer.py` | Ładuje dokumenty i embeddingi do ChromaDB |
| `scripts/import/neo4j_query_tester.py` | Odpala zestaw bezpiecznych zapytań kontrolnych |
| `scripts/import/run_all_imports.py` | Spina cały proces w jedną komendę |
| `reports/` | Zawiera wyniki i raporty końcowe |
| `tests/` | Zawiera testy automatyczne |

To jest dobry moment, żeby zobaczyć projekt nie jako „kod do uruchomienia”, ale jako **układ odpowiedzialności**. Każdy plik odpowiada za inny etap procesu. Jeśli później coś się zepsuje, ta mentalna mapa bardzo pomoże w debugowaniu.

## 6. Krok trzeci — konfiguracja przez `.env`

Następny krok to przygotowanie własnego pliku `.env` na podstawie `.env.example`. W wielu projektach jest to pierwszy moment, w którym początkujący trochę się gubi, bo nie zawsze rozumie różnicę między kodem a konfiguracją. Zasada jest prosta: **kod opisuje logikę**, a **plik `.env` opisuje środowisko, w którym ta logika działa**.

Najpierw skopiuj plik wzorcowy:

```bash
cp .env.example .env
```

W projekcie szczególnie ważne są ustawienia związane z bazami i Ollama. Poniższa tabela pokazuje najistotniejsze zmienne oraz ich znaczenie.

| Zmienna | Przykład | Co oznacza |
|---|---|---|
| `NEO4J_URI` | `bolt://neo4j:7687` | Adres serwera Neo4j |
| `NEO4J_USER` | `neo4j` | Login do Neo4j |
| `NEO4J_PASSWORD` | `password123` | Hasło do Neo4j |
| `NEO4J_DATABASE` | `neo4j` | Nazwa bazy |
| `CHROMADB_HOST` | `chromadb` | Host serwera ChromaDB |
| `CHROMADB_PORT` | `8000` | Port serwera ChromaDB |
| `CHROMADB_COLLECTION_NAME` | `movies` | Nazwa kolekcji w ChromaDB |
| `OLLAMA_HOST` | `http://ollama-mistral:11434` | Adres Ollama |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Model embeddingowy [1] |
| `OLLAMA_TIMEOUT` | `120` | Maksymalny czas oczekiwania na odpowiedź |
| `DATA_PROCESSED_DIR` | `./data/processed` | Katalog z danymi po czyszczeniu |
| `REPORTS_DIR` | `./reports` | Katalog z raportami |

Warto rozumieć też jedną subtelność. Jeśli uruchamiasz projekt w Dockerze, hosty typu `neo4j` czy `chromadb` często oznaczają **nazwy usług w sieci kontenerów**, a nie dosłownie nazwy widoczne z Twojego systemu operacyjnego. Jeśli uruchamiasz skrypty poza kontenerem, może się okazać, że musisz użyć `localhost` zamiast nazwy kontenera.

> Dla początkującego to jest częsty punkt potknięcia: **adres poprawny w kontenerze nie zawsze jest poprawny poza kontenerem**.

## 7. Krok czwarty — instalacja zależności Pythona

Gdy konfiguracja jest gotowa, zainstaluj zależności projektu. To pozwala interpreterowi Pythona znaleźć wszystkie używane biblioteki, takie jak sterownik do Neo4j, klient ChromaDB, obsługa `.env` i biblioteki testowe.

```bash
pip install -r requirements.txt
```

Jeżeli jesteś w środowisku wirtualnym, polecenie instalacji wykonuj wewnątrz niego. Jeśli nie korzystasz ze środowiska wirtualnego, projekt i tak może działać, ale ryzykujesz konflikty wersji z innymi projektami. W praktyce dla studenta wygodne jest użycie `venv`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

| Opcja | Zalety | Wady |
|---|---|---|
| Instalacja globalna | Szybko i prosto | Łatwo o konflikty między projektami |
| `venv` | Czyste, izolowane środowisko | Trzeba pamiętać o aktywacji |

## 8. Krok piąty — uruchomienie usług: Neo4j, ChromaDB i Ollama

To jest moment, w którym sam kod nadal jeszcze nic nie robi, ale przygotowujesz „serce systemu”. Bez działających usług importer nie ma gdzie wysłać danych. Jeśli korzystasz z `docker-compose.yml`, uruchom kontenery. Jeśli usługi stawiasz ręcznie, zadbaj o to, aby działały na portach zgodnych z konfiguracją.

Przykładowo, w układzie zgodnym z projektem powinny być osiągalne następujące usługi:

| Usługa | Typowe ustawienie |
|---|---|
| Neo4j | port `7687` dla Bolt |
| ChromaDB | port `8000` |
| Ollama | port `11434` |

Po uruchomieniu Ollama pobierz model embeddingowy:

```bash
ollama pull nomic-embed-text
```

To nie jest detal techniczny, tylko absolutnie kluczowy etap. Jeśli model nie zostanie pobrany, import do ChromaDB nie stworzy embeddingów, bo nie będzie miał czym ich generować [1].

## 9. Krok szósty — przygotowanie danych wejściowych

Dane wejściowe w tym zadaniu muszą zostać przygotowane do wspólnego formatu JSON. Właśnie za to odpowiada `scripts/utils/data_cleaner.py`. Jego rola polega na tym, aby dane ze źródeł wejściowych sprowadzić do spójnej struktury, którą potem rozumie zarówno importer Neo4j, jak i importer ChromaDB.

Uruchomienie skryptu czyszczącego ma sens tylko wtedy, gdy rozumiesz, jaki artefakt powinien powstać na końcu. Tym artefaktem jest plik:

```text
data/processed/movies_all.json
```

To jest centralny punkt wejścia dla całego zadania 2. Jeśli ten plik nie istnieje, `run_all_imports.py` zakończy się błędem. W samym skrypcie widać to wprost: pipeline sprawdza obecność `movies_all.json` zanim przejdzie dalej.

| Etap | Oczekiwany wynik |
|---|---|
| Uruchomienie czyszczenia danych | Powstaje plik `movies_all.json` |
| Brak pliku | Pipeline zatrzymuje się przed importem |

Dla początkującego ważne jest, aby rozumieć, że ten plik jest **kontraktem między etapami**. Etap przygotowania danych kończy się na wygenerowaniu JSON-a, a kolejne etapy zakładają, że format tego pliku jest poprawny.

## 10. Krok siódmy — jak działa import do Neo4j

Po przygotowaniu danych pierwszy właściwy import trafia do **Neo4j**. W tym kroku dane są zamieniane na strukturę grafową: pojawiają się węzły reprezentujące filmy, osoby, gatunki i inne encje oraz relacje między nimi. To właśnie dlatego Neo4j jest tu odpowiednim narzędziem — jego model danych jest oparty na węzłach i relacjach, a język **Cypher** został zaprojektowany do pracy na grafach [4] [5].

W praktyce importer Neo4j powinien robić kilka rzeczy w ustalonej kolejności. Najpierw sprawdzić połączenie z bazą. Potem utworzyć ograniczenia i indeksy, jeśli są potrzebne. Następnie wczytać dane z `movies_all.json`. Na końcu może dodać relacje pomocnicze albo wypisać statystyki.

To jest bardzo dobry przykład myślenia programistycznego w kategoriach **precondition → action → verification**. Najpierw upewniasz się, że baza jest dostępna. Potem wykonujesz operację. Na końcu sprawdzasz, czy operacja faktycznie zadziałała.

## 11. Krok ósmy — jak działa import do ChromaDB

Druga połowa zadania 2 dotyczy **ChromaDB** i lokalnych embeddingów. To jest najważniejsza część z punktu widzenia nowoczesnego wyszukiwania semantycznego. Chroma przechowuje dokumenty, metadane i embeddingi, a następnie pozwala wyszukiwać podobne treści [2] [3].

W tym projekcie każdy film jest zamieniany do postaci tekstowego dokumentu, który zawiera m.in. tytuł, synopsis, gatunki i tagi. Ten tekst jest przekazywany do Ollama. Model `nomic-embed-text` zwraca wektor liczb reprezentujący znaczenie tekstu. Ten wektor, razem z dokumentem i metadanymi, jest zapisywany do kolekcji w ChromaDB [1] [2] [3].

| Element dokumentu | Po co jest dodawany |
|---|---|
| Tytuł | Ułatwia identyfikację filmu |
| Synopsis | Dostarcza głównej treści semantycznej |
| Gatunki | Dodają kontekst tematyczny |
| Tagi | Uzupełniają opis i zwiększają szansę dobrego dopasowania |

Tu warto zatrzymać się na chwilę i zrozumieć ideę embeddingu. Embedding to nie jest „streszczenie tekstu” ani „tag”. To liczbowy zapis znaczenia tekstu w przestrzeni wektorowej. Dwa teksty podobne znaczeniowo powinny mieć embeddingi położone bliżej siebie niż teksty niepowiązane [1] [2]. Dzięki temu zapytanie użytkownika także może zostać zamienione na embedding i porównane z wcześniej zapisanymi filmami.

## 12. Krok dziewiąty — po co potrzebny jest `neo4j_query_tester.py`

Bardzo wielu studentów kończy implementację na samym imporcie danych, ale to za mało. Jeśli potrafisz tylko „wgrać dane”, a nie potrafisz pokazać, że baza odpowiada poprawnie na zapytania, to Twoja implementacja jest trudniejsza do obrony i trudniejsza do utrzymania. Właśnie dlatego został dodany skrypt `neo4j_query_tester.py`.

Ten skrypt robi coś bardzo rozsądnego: uruchamia zestaw **smoke tests**, czyli szybkich testów kontrolnych. Nie są one bardzo rozbudowane, ale odpowiadają na podstawowe pytanie: „czy ta baza po imporcie naprawdę działa?”. To jest często ważniejsze niż piękny kod, bo pokazuje, że system jest używalny.

| Typ testu | Co potwierdza |
|---|---|
| Liczba filmów | Czy import w ogóle coś wgrał |
| Gatunki | Czy relacje tematyczne istnieją |
| Wyszukiwanie po tytule | Czy da się zadawać praktyczne pytania |
| Relacje osób | Czy baza ma sens grafowy, a nie tylko listę rekordów |

Szczególnie ważne jest też używanie **parametrów** w zapytaniach Cypher zamiast ręcznego wklejania wartości do tekstu zapytania. To jest podstawowa praktyka bezpieczeństwa i dobra praktyka programistyczna [5].

## 13. Krok dziesiąty — spięcie wszystkiego w jeden pipeline

Najbardziej dojrzała wersja implementacji nie wymaga ręcznego odpalania pięciu różnych skryptów w odpowiedniej kolejności. Zamiast tego ma jeden plik wejściowy, który koordynuje cały proces. W tym projekcie tę rolę spełnia `scripts/import/run_all_imports.py`.

Ten skrypt robi trzy główne rzeczy. Najpierw sprawdza, czy istnieje `movies_all.json`. Potem uruchamia importer Neo4j. Następnie uruchamia importer ChromaDB z embeddingami przez Ollama. Na końcu uruchamia testy Cypher i zapisuje raporty do katalogu `reports/`.

Uruchomienie wygląda tak:

```bash
python scripts/import/run_all_imports.py
```

Z punktu widzenia architektury to bardzo dobra decyzja. Zamiast zmuszać użytkownika do pamiętania kolejności kroków, kod pilnuje kolejności za niego. To zmniejsza liczbę błędów operacyjnych i ułatwia pokazanie działania projektu prowadzącemu albo drugiej osobie w zespole.

## 14. Jak powinien wyglądać poprawny wynik pipeline’u

Po poprawnym zakończeniu działania pipeline’u powinieneś zobaczyć trzy rodzaje efektów. Pierwszy to dane zaimportowane do **Neo4j**. Drugi to kolekcja z dokumentami i embeddingami w **ChromaDB**. Trzeci to raporty zapisane lokalnie do katalogu `reports/`.

| Oczekiwany artefakt | Gdzie go szukać | Co oznacza |
|---|---|---|
| Zaimportowane węzły i relacje | Neo4j Browser / baza | Dane grafowe są gotowe |
| Kolekcja `movies` | ChromaDB | Dokumenty i embeddingi zostały zapisane |
| `neo4j_query_report.json` | `reports/` | Testy kontrolne Neo4j zostały wykonane |
| `task2_summary.json` | `reports/` | Powstało końcowe podsumowanie etapu |

Jeśli któregoś z tych elementów brakuje, nie traktuj tego od razu jak porażki. Potraktuj to jak informację diagnostyczną. W programowaniu bardzo ważne jest, żeby nauczyć się czytać objawy i cofać się do ich przyczyny.

## 15. Jak testować to sensownie jako developer, a nie tylko „czy się uruchamia”

W tym projekcie testowanie odbywa się na dwóch poziomach. Pierwszy poziom to **test infrastrukturalny**, czyli prawdziwe połączenie z działającymi usługami. Drugi poziom to **testy automatyczne**, które weryfikują logikę kodu bez konieczności podnoszenia całej infrastruktury.

Testy automatyczne uruchamiasz tak:

```bash
pytest -q
```

Ich zadaniem nie jest sprawdzić, czy kontener Neo4j działa, tylko czy kod działa poprawnie na poziomie logiki. To oznacza między innymi sprawdzenie, czy dokument filmowy jest budowany poprawnie, czy embeddingi są przekazywane do kolekcji i czy raporty mają właściwy format.

| Rodzaj testu | Co sprawdza | Kiedy używać |
|---|---|---|
| `pytest` | Logikę kodu i strukturę działania | Po każdej zmianie w kodzie |
| `run_all_imports.py` | Cały pipeline i integrację usług | Przed oddaniem pracy albo demo |
| `neo4j_query_tester.py` | Tylko warstwę zapytań Cypher | Gdy chcesz szybko sprawdzić Neo4j |

Dojrzały developer nie pyta tylko „czy działa?”, ale też „**co dokładnie zostało sprawdzone?**”. To jest bardzo ważna różnica.

## 16. Typowy plan implementacji od zera

Jeśli miałbyś odtworzyć całość od wcześniejszej wersji repozytorium, bez kopiowania gotowego rozwiązania, sensowna kolejność prac wygląda tak:

| Kolejność | Zadanie | Dlaczego właśnie tak |
|---|---|---|
| 1 | Zrozumieć wymaganie i rolę osoby A | Bez tego nie wiadomo, co naprawdę budować |
| 2 | Uporządkować `.env.example` i konfigurację | Kod bez poprawnej konfiguracji nie ruszy |
| 3 | Upewnić się, że działa przygotowanie danych | Wszystkie dalsze etapy zależą od `movies_all.json` |
| 4 | Doprowadzić do stabilnego importu Neo4j | To pierwszy filar danych |
| 5 | Dodać jawny importer ChromaDB z Ollama | To główny punkt zadania 2 |
| 6 | Napisać tester zapytań Cypher | To daje dowód, że dane są używalne |
| 7 | Spiąć wszystko w `run_all_imports.py` | Automatyzuje uruchamianie całości |
| 8 | Dodać testy `pytest` | Pozwala sprawdzać kod szybciej i pewniej |
| 9 | Napisać dokumentację | Ułatwia odtworzenie i obronę rozwiązania |

To podejście jest lepsze niż chaotyczne „dopisywanie po trochu”, bo tworzy naturalne kamienie milowe. Po każdym etapie masz coś konkretnego, co można uruchomić, sprawdzić i pokazać.

## 17. Jak samodzielnie zaprojektować importer ChromaDB

Gdybyś musiał zaimplementować importer od zera, pomyśl o nim jako o klasie odpowiedzialnej za pięć osobnych zadań. Po pierwsze, musi umieć połączyć się z ChromaDB. Po drugie, musi umieć skontaktować się z Ollama. Po trzecie, musi umieć zbudować dokument tekstowy z pojedynczego filmu. Po czwarte, musi umieć wygenerować embeddingi w batchach. Po piąte, musi umieć zapisać wynik do kolekcji.

| Odpowiedzialność importera | Dlaczego jest osobna |
|---|---|
| Połączenie z ChromaDB | To osobny punkt awarii |
| Połączenie z Ollama | Embeddingi zależą od innej usługi niż baza |
| Budowanie dokumentu | To logika transformacji danych |
| Batch processing | Duże zbiory lepiej obsługiwać partiami |
| Upsert do kolekcji | To finalny zapis do bazy |

Takie rozbicie jest ważne nie tylko organizacyjnie. Ono bezpośrednio wpływa na testowalność. Gdy każda odpowiedzialność jest wyraźna, łatwiej napisać testy i łatwiej zlokalizować błąd.

## 18. Jak samodzielnie zaprojektować tester zapytań Cypher

Podobnie warto myśleć o `neo4j_query_tester.py`. To nie powinien być chaotyczny plik z pojedynczym `print()`. Lepszym wzorcem jest klasa lub moduł, który umie: sprawdzić połączenie, wykonać pojedyncze zapytanie, zebrać wyniki w ujednoliconym formacie i zapisać raport JSON.

To daje trzy korzyści. Po pierwsze, wynik jest czytelny. Po drugie, raport można potem wykorzystać w dokumentacji. Po trzecie, jeśli dodasz nowe testy, nie trzeba zmieniać całej struktury skryptu, tylko dopisać kolejną pozycję do listy zapytań.

## 19. Najczęstsze błędy początkujących podczas implementacji

Warto znać typowe pułapki, bo wtedy dużo szybciej zauważysz, co poszło nie tak. W takich projektach błędy rzadko wynikają z „magii”. Najczęściej problem leży w jednej z kilku powtarzalnych kategorii.

| Problem | Co zwykle naprawdę oznacza | Jak diagnozować |
|---|---|---|
| `Connection refused` | Usługa nie działa lub adres jest zły | Sprawdź kontenery, porty i hosty |
| Brak `movies_all.json` | Pipeline został uruchomiony za wcześnie | Najpierw wykonaj etap czyszczenia danych |
| ChromaDB działa, ale brak sensownych wyników | Dokumenty lub embeddingi są źle przygotowane | Sprawdź, jak budowany jest tekst dokumentu |
| Neo4j ma mało danych albo ich nie ma | Import nie wgrał pełnego zestawu rekordów | Sprawdź logi importera i statystyki |
| `pytest` nie przechodzi | Zmiana zepsuła logikę albo importy modułów | Czytaj pierwszy błąd od góry, nie ostatni |

Jedna bardzo praktyczna rada brzmi tak: **nie poprawiaj wszystkiego naraz**. Jeśli masz błąd połączenia, najpierw napraw połączenie. Jeśli nie ma danych wejściowych, najpierw wygeneruj dane. To wydaje się oczywiste, ale wiele osób próbuje „na ślepo” zmieniać kilka plików jednocześnie i przez to jeszcze bardziej zaciemnia problem.

## 20. Jak opowiadać o tej implementacji na zaliczeniu albo review

Jeżeli później będziesz tłumaczył swoją pracę prowadzącemu, nie zaczynaj od detali bibliotek. Zacznij od architektury i przepływu. Powiedz, że osoba A odpowiada za przygotowanie zaplecza danych. Następnie pokaż, że dane są przetwarzane do `movies_all.json`, importowane do **Neo4j**, a ich opisy są embedowane przez **Ollama** i zapisywane w **ChromaDB**. Na końcu pokaż, że są uruchamiane testy kontrolne i powstają raporty.

To jest dobra narracja, bo pokazuje nie tylko „napisałem kod”, ale też „rozumiem, po co ten kod istnieje”. Dla recenzenta albo prowadzącego to jest często ważniejsze niż pojedyncza linijka implementacji.

## 21. Jak rozbudowywać to dalej po zadaniu 2

Po zakończeniu tego etapu masz już fundament do kolejnych części projektu. Możesz rozwijać bardziej zaawansowane wyszukiwanie semantyczne, dołożyć warstwę agentów, budować routing zapytań między bazą grafową i bazą wektorową albo tworzyć API nad tym pipeline’em. Wszystkie te dalsze kroki mają sens właśnie dlatego, że wcześniej poprawnie przygotowano warstwę danych.

To jest też powód, dla którego warto pisać dokumentację „jak dla początkującego”. Dobrze udokumentowany fundament zwiększa szanse, że inna osoba z zespołu będzie umiała wejść do projektu bez zgadywania, co autor miał na myśli.

## 22. Minimalna checklista końcowa

Na sam koniec przed oddaniem pracy sprawdź poniższe rzeczy. To jest prosty, ale bardzo praktyczny rytuał jakościowy.

| Pytanie kontrolne | Odpowiedź, której oczekujesz |
|---|---|
| Czy `.env` ma poprawne hosty i porty? | Tak |
| Czy `movies_all.json` istnieje? | Tak |
| Czy Neo4j odpowiada? | Tak |
| Czy ChromaDB odpowiada? | Tak |
| Czy Ollama ma model `nomic-embed-text`? | Tak |
| Czy `run_all_imports.py` kończy się sukcesem? | Tak |
| Czy raporty powstały w `reports/`? | Tak |
| Czy `pytest -q` przechodzi? | Tak |

## 23. Podsumowanie dla osoby, która robi to pierwszy raz

Jeżeli to Twój pierwszy kontakt z takim projektem, najważniejsze jest to, żeby nie patrzeć na wszystko naraz. Nie myśl „muszę ogarnąć Neo4j, ChromaDB, Dockera, Ollama i testy w jednej chwili”. Myśl etapami. Najpierw konfiguracja. Potem dane. Potem Neo4j. Potem embeddingi i ChromaDB. Potem testy. Potem automatyzacja. Potem dokumentacja.

Właśnie tak pracuje się przy bardziej złożonych projektach: nie przez jeden wielki skok, tylko przez **ciąg małych, sprawdzalnych kroków**. Jeżeli opanujesz ten sposób myślenia, to ten projekt nie będzie już wyglądał jak zbiór przypadkowych technologii, tylko jak logicznie ułożony system.

## References

[1]: https://ollama.com/library/nomic-embed-text "nomic-embed-text"
[2]: https://docs.trychroma.com/integrations/embedding-models/ollama "Ollama - Chroma Docs"
[3]: https://docs.trychroma.com/reference/python/collection "Collection - Chroma Docs"
[4]: https://neo4j.com/docs/getting-started/graph-database/ "What is a Graph Database? - Neo4j"
[5]: https://neo4j.com/docs/cypher-manual/current/introduction/ "Cypher Manual - Neo4j"
