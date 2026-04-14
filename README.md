# TEG_test

To repozytorium zawiera projekt związany z bazami danych filmowych, Neo4j, ChromaDB i lokalnymi modelami uruchamianymi przez Ollama.

Najważniejsza dokumentacja dla **zadania 2 osoby A** znajduje się tutaj:

`docs/ZADANIE_2_OSOBA_A_DOKUMENTACJA.md`

Jeżeli chcesz szybko odtworzyć etap osoby A, pracuj w tej kolejności:

| Krok | Co zrobić |
|---|---|
| 1 | Skopiować `.env.example` do `.env` |
| 2 | Przygotować dane przez `scripts/utils/data_cleaner.py` |
| 3 | Uruchomić `scripts/import/run_all_imports.py` |
| 4 | Sprawdzić raporty w katalogu `reports/` |
| 5 | Uruchomić testy `pytest -q` |

Pełny opis plików, działania projektu i instrukcję dla początkującego znajdziesz w dokumentacji Markdown.
