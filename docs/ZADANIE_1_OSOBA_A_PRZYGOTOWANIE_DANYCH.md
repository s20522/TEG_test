# Zadanie 1 — Osoba A

## Przygotowanie danych wejściowych do dalszych etapów projektu

Ten dokument wydziela te elementy dokumentacji, które dotyczą **zadania 1**, czyli przygotowania danych wejściowych dla dalszych etapów projektu. Chodzi przede wszystkim o etap poprzedzający właściwy import do **Neo4j** i **ChromaDB**, a więc o moment, w którym dane są pobierane, czyszczone, porządkowane i zapisywane do wspólnego formatu JSON.

Najważniejszy rezultat zadania 1 to plik:

```text
data/processed/movies_all.json
```

To właśnie ten plik staje się wejściem dla **zadania 2**. Innymi słowy, zadanie 1 przygotowuje materiał, a zadanie 2 ten materiał wykorzystuje do budowy warstwy bazodanowej i semantycznej.

| Etap | Co powstaje | Do czego to później służy |
|---|---|---|
| Zadanie 1 | `movies_all.json` | Wejście do importu Neo4j i ChromaDB |
| Zadanie 2 | Dane w Neo4j, embeddingi w ChromaDB, raporty | Wyszukiwanie, testy i dalsza logika projektu |

## Po co w ogóle wydzielać zadanie 1

Dla początkującego bardzo ważne jest rozdzielenie etapów. Jeśli wszystko opisze się w jednym dokumencie, łatwo pomylić to, co jest przygotowaniem danych, z tym, co jest ich importem i testowaniem. Tymczasem są to dwa różne problemy techniczne. 

W **zadaniu 1** interesuje nas przede wszystkim jakość i format danych. W **zadaniu 2** interesuje nas to, jak te dane wykorzystać w bazie grafowej, bazie wektorowej i testach zapytań.

> Najprostsza zasada brzmi tak: **zadanie 1 kończy się na poprawnym przygotowaniu danych, a zadanie 2 zaczyna się od użycia tych danych**.

## Jak rozumieć rolę `data_cleaner.py`

Skrypt `scripts/utils/data_cleaner.py` odpowiada za etap przygotowania danych. Jego zadaniem nie jest jeszcze praca na bazie danych, tylko uporządkowanie surowego materiału wejściowego tak, aby kolejne skrypty dostały spójny, przewidywalny format.

To zwykle oznacza trzy rzeczy. Po pierwsze, dane są pobierane albo odczytywane ze źródeł wejściowych. Po drugie, teksty i pola są czyszczone, aby ograniczyć błędy i niespójności. Po trzecie, wynik jest zapisywany do jednego pliku JSON, z którego później korzysta reszta pipeline’u.

| Odpowiedzialność `data_cleaner.py` | Dlaczego jest ważna |
|---|---|
| Pobranie / odczyt danych źródłowych | Bez źródła nie ma czego przetwarzać |
| Czyszczenie tekstów i pól | Ułatwia późniejszy import i ogranicza bałagan w danych |
| Zapis do wspólnego JSON | Daje jeden, przewidywalny format dla dalszych skryptów |

## Jak wygląda efekt końcowy zadania 1

Po poprawnym wykonaniu etapu przygotowania danych powinien istnieć plik `movies_all.json` w katalogu przetworzonych danych. To nie jest tylko „jeden z plików projektu”, ale bardzo ważny kontrakt między etapami. Kolejne skrypty zakładają, że ten plik już istnieje i ma poprawny format.

Jeśli plik nie powstał, zadanie 2 nie powinno ruszać dalej. To zachowanie jest poprawne, bo importer nie może zgadywać danych, których nie dostał.

| Pytanie kontrolne | Oczekiwany wynik |
|---|---|
| Czy istnieje `data/processed/movies_all.json`? | Tak |
| Czy plik zawiera komplet rekordów filmowych? | Tak |
| Czy dane są wystarczająco spójne do importu? | Tak |

## Jak to odtwarzać od zera

Jeżeli ktoś ma tylko wcześniejszą wersję projektu i chce samodzielnie dojść do końca zadania 1, powinien zacząć od zrozumienia, skąd pochodzą dane i jaki wynik ma zostać zapisany. Dopiero potem ma sens uruchamianie skryptu czyszczącego.

Praktycznie patrząc, warto pracować w takiej kolejności:

| Krok | Co robisz | Po co |
|---|---|---|
| 1 | Sprawdzasz strukturę katalogów `data/raw` i `data/processed` | Żeby wiedzieć, skąd dane wchodzą i gdzie wychodzą |
| 2 | Czytasz `scripts/utils/data_cleaner.py` | Żeby zrozumieć logikę transformacji |
| 3 | Uruchamiasz skrypt czyszczący | Żeby wygenerować wspólny plik wejściowy |
| 4 | Sprawdzasz, czy powstał `movies_all.json` | Żeby potwierdzić sukces etapu |
| 5 | Weryfikujesz przykładowe rekordy | Żeby upewnić się, że wynik ma sens |

## Jak to się łączy z zadaniem 2

Po wykonaniu zadania 1 możesz przejść do zadania 2. Wtedy `movies_all.json` przestaje być wynikiem, a staje się wejściem. Właśnie z tego pliku korzystają importer **Neo4j**, importer **ChromaDB** i skrypt spinający cały pipeline.

To oznacza, że jeśli w zadaniu 2 pojawi się błąd typu „brak `movies_all.json`”, to nie jest to zwykle błąd samego zadania 2, tylko sygnał, że **zadanie 1 nie zostało jeszcze poprawnie domknięte**.

## Co sprawdzić przed przejściem dalej

Przed wejściem w zadanie 2 warto przejść krótką checklistę jakościową.

| Pytanie | Jeśli odpowiedź brzmi „nie”, to co zrobić |
|---|---|
| Czy plik `movies_all.json` istnieje? | Uruchomić ponownie etap przygotowania danych |
| Czy rekordy wyglądają sensownie? | Sprawdzić logikę czyszczenia w `data_cleaner.py` |
| Czy format jest spójny? | Ujednolicić pola, zanim dane trafią do importerów |
| Czy katalog `data/processed/` zawiera wynik końcowy? | Sprawdzić ścieżki i konfigurację zapisu |

## Podsumowanie

Ten dokument celowo wydziela część związaną z **zadaniem 1**, aby nie mieszać przygotowania danych z importem do baz i testami. Dzięki temu łatwiej zrozumieć, że projekt składa się z etapów. Najpierw przygotowujesz dane. Dopiero potem budujesz nad nimi logikę bazodanową i semantyczną.

Jeżeli chcesz przejść do kolejnego etapu, po poprawnym przygotowaniu `movies_all.json` wróć do dokumentacji zadania 2, która opisuje import do **Neo4j**, generowanie embeddingów przez **Ollama** i zapis do **ChromaDB**.
