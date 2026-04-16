# TEG_test

To repozytorium zawiera projekt związany z bazami danych filmowych, **Neo4j**, **ChromaDB** i lokalnymi modelami uruchamianymi przez **Ollama**.

Najważniejsza dokumentacja dla **zadania 2 osoby A** znajduje się tutaj:

| Dokument | Zastosowanie |
|---|---|
| `docs/ZADANIE_2_OSOBA_A_DOKUMENTACJA.md` | Dokumentacja rozwiązania i opis gotowej implementacji |
| `docs/GUIDE_IMPLEMENTACJA_OD_ZERA_OSOBA_A_ZADANIE_2.md` | Bardzo dokładny przewodnik krok po kroku, jak odtworzyć i zaimplementować całość od początku |

Jeżeli chcesz szybko odtworzyć etap osoby A, pracuj w tej kolejności:

| Krok | Co zrobić |
|---|---|
| 1 | Skopiować `.env.example` do `.env` |
| 2 | Przygotować dane przez `scripts/utils/data_cleaner.py` |
| 3 | Uruchomić `scripts/import/run_all_imports.py` |
| 4 | Sprawdzić raporty w katalogu `reports/` |
| 5 | Uruchomić testy `pytest -q` |

Jeżeli potrzebujesz wejść głębiej i zrozumieć **dlaczego** projekt został zrobiony w ten sposób oraz **jak samemu zbudować go od zera**, zacznij od szczegółowego guide’a w katalogu `docs/`.
