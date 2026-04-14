"""
Neo4j Query Tester
Zadanie 2 osoby A:
- testowanie zapytań Cypher na zaimportowanych danych,
- zapis raportu do pliku JSON,
- bezpieczne przekazywanie parametrów do zapytań.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Załadowanie zmiennych środowiskowych
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


DEFAULT_QUERIES: List[Dict[str, Any]] = [
    {
        "name": "count_movies",
        "description": "Policz wszystkie filmy w bazie.",
        "query": "MATCH (m:Movie) RETURN count(m) AS total_movies",
        "parameters": {},
    },
    {
        "name": "top_genres",
        "description": "Pokaż najczęściej występujące gatunki.",
        "query": (
            "MATCH (m:Movie)-[:IN_GENRE]->(g:Genre) "
            "RETURN g.name AS genre, count(m) AS movie_count "
            "ORDER BY movie_count DESC LIMIT 10"
        ),
        "parameters": {},
    },
    {
        "name": "movies_by_genre",
        "description": "Pokaż przykładowe filmy z wybranego gatunku.",
        "query": (
            "MATCH (m:Movie)-[:IN_GENRE]->(g:Genre {name: $genre}) "
            "RETURN m.title AS title, m.imdb_id AS imdb_id "
            "ORDER BY title ASC LIMIT 10"
        ),
        "parameters": {"genre": "horror"},
    },
    {
        "name": "title_keyword_search",
        "description": "Wyszukaj filmy po fragmencie tytułu.",
        "query": (
            "MATCH (m:Movie) "
            "WHERE toLower(m.title) CONTAINS toLower($keyword) "
            "RETURN m.title AS title, m.imdb_id AS imdb_id "
            "ORDER BY title ASC LIMIT 10"
        ),
        "parameters": {"keyword": "fear"},
    },
    {
        "name": "person_relations_check",
        "description": "Sprawdź, czy istnieją relacje osób z filmami.",
        "query": (
            "MATCH (p:Person)-[r:DIRECTED|ACTED_IN]->(m:Movie) "
            "RETURN p.name AS person, type(r) AS relation, m.title AS title "
            "ORDER BY person ASC LIMIT 10"
        ),
        "parameters": {},
    },
]


class Neo4jQueryTester:
    """Uruchamia zestaw kontrolnych zapytań Cypher i zapisuje raport."""

    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        logger.info(f"Połączenie z Neo4j: {uri}")

    def close(self):
        self.driver.close()
        logger.info("Połączenie z Neo4j zamknięte")

    def verify_connection(self) -> bool:
        try:
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1 AS ok").consume()
            logger.info("✓ Połączenie z Neo4j potwierdzone")
            return True
        except Exception as exc:
            logger.error(f"✗ Błąd połączenia z Neo4j: {exc}")
            return False

    def run_query(
        self,
        name: str,
        description: str,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        parameters = parameters or {}
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters)
            rows = [record.data() for record in result]

        return {
            "name": name,
            "description": description,
            "query": query,
            "parameters": parameters,
            "row_count": len(rows),
            "rows": rows,
            "status": "ok",
        }

    def run_smoke_tests(self, queries: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        report_items = []
        success_count = 0
        queries_to_run = queries or DEFAULT_QUERIES

        for query_config in queries_to_run:
            try:
                query_result = self.run_query(
                    name=query_config["name"],
                    description=query_config["description"],
                    query=query_config["query"],
                    parameters=query_config.get("parameters", {}),
                )
                success_count += 1
                report_items.append(query_result)
                logger.info(f"✓ Test zapytania zakończony: {query_config['name']}")
            except Exception as exc:
                logger.error(f"✗ Błąd zapytania {query_config['name']}: {exc}")
                report_items.append(
                    {
                        "name": query_config["name"],
                        "description": query_config["description"],
                        "query": query_config["query"],
                        "parameters": query_config.get("parameters", {}),
                        "row_count": 0,
                        "rows": [],
                        "status": "error",
                        "error": str(exc),
                    }
                )

        report = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "database": self.database,
            "tests_total": len(queries_to_run),
            "tests_passed": success_count,
            "tests_failed": len(queries_to_run) - success_count,
            "results": report_items,
        }
        return report

    @staticmethod
    def save_report(report: Dict[str, Any], output_path: str) -> str:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as file_handle:
            json.dump(report, file_handle, ensure_ascii=False, indent=2)
        return str(output_file)


def main():
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password123')
    neo4j_database = os.getenv('NEO4J_DATABASE', 'neo4j')
    reports_dir = Path(os.getenv('REPORTS_DIR', './reports'))
    report_path = reports_dir / 'neo4j_query_report.json'

    tester = Neo4jQueryTester(neo4j_uri, neo4j_user, neo4j_password, neo4j_database)

    try:
        if not tester.verify_connection():
            logger.error("Nie można uruchomić testów zapytań Cypher")
            return

        report = tester.run_smoke_tests()
        saved_path = tester.save_report(report, str(report_path))

        logger.info("\n=== RAPORT TESTÓW CYPHER ===")
        logger.info(f"Liczba testów: {report['tests_total']}")
        logger.info(f"Zaliczone: {report['tests_passed']}")
        logger.info(f"Nieudane: {report['tests_failed']}")
        logger.info(f"Raport zapisany do: {saved_path}")

    except Exception as exc:
        logger.error(f"Błąd podczas testowania zapytań: {exc}", exc_info=True)
    finally:
        tester.close()


if __name__ == '__main__':
    main()
