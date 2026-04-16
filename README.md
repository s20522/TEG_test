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
