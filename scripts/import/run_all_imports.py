"""
Run All Imports - uruchomienie całego zadania 2 osoby A:
1. import do Neo4j,
2. import embeddingów do ChromaDB,
3. testy zapytań Cypher,
4. zapis raportów końcowych.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Załadowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja loggingu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import modułów
sys.path.insert(0, str(Path(__file__).parent))
from chromadb_importer import ChromaDBImporter
from neo4j_importer import Neo4jImporter
from neo4j_query_tester import Neo4jQueryTester


def main():
    """Główna funkcja uruchamiająca zadanie 2 osoby A."""

    logger.info("=" * 60)
    logger.info("URUCHOMIENIE ZADANIA 2 - OSOBA A")
    logger.info("=" * 60)

    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password123')
    neo4j_database = os.getenv('NEO4J_DATABASE', 'neo4j')

    chromadb_host = os.getenv('CHROMADB_HOST', 'localhost')
    chromadb_port = int(os.getenv('CHROMADB_PORT', '8000'))
    ollama_url = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    embedding_model = os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text')
    timeout = int(os.getenv('OLLAMA_TIMEOUT', '120'))

    data_processed_dir = Path(os.getenv('DATA_PROCESSED_DIR', './data/processed'))
    reports_dir = Path(os.getenv('REPORTS_DIR', './reports'))
    batch_size = int(os.getenv('BATCH_SIZE', '100'))

    movies_file = data_processed_dir / 'movies_all.json'
    if not movies_file.exists():
        logger.error(f"Plik nie znaleziony: {movies_file}")
        logger.error("Najpierw uruchom skrypt czyszczący dane i generujący movies_all.json")
        return False

    reports_dir.mkdir(parents=True, exist_ok=True)
    success = True
    summary = {
        "neo4j_import": False,
        "chromadb_import": False,
        "neo4j_query_tests": False,
    }

    # 1. Import do Neo4j
    logger.info("\n" + "=" * 60)
    logger.info("1. IMPORT DO NEO4J")
    logger.info("=" * 60)

    neo4j_importer = None
    try:
        neo4j_importer = Neo4jImporter(neo4j_uri, neo4j_user, neo4j_password, neo4j_database)
        if neo4j_importer.verify_connection():
            neo4j_importer.create_constraints()
            neo4j_importer.create_indexes()
            neo4j_importer.import_movies(str(movies_file), batch_size=batch_size)
            neo4j_importer.create_sample_relations()
            neo4j_importer.print_statistics()
            summary["neo4j_import"] = True
            logger.info("✓ Import do Neo4j zakończony pomyślnie")
        else:
            logger.error("✗ Nie można połączyć się z Neo4j")
            success = False
    except Exception as exc:
        logger.error(f"✗ Błąd importu Neo4j: {exc}", exc_info=True)
        success = False
    finally:
        if neo4j_importer is not None:
            neo4j_importer.close()

    time.sleep(2)

    # 2. Import do ChromaDB
    logger.info("\n" + "=" * 60)
    logger.info("2. IMPORT DO CHROMADB Z LOKALNYMI EMBEDDINGAMI")
    logger.info("=" * 60)

    try:
        chromadb_importer = ChromaDBImporter(
            host=chromadb_host,
            port=chromadb_port,
            ollama_url=ollama_url,
            embedding_model=embedding_model,
            timeout=timeout,
        )

        if chromadb_importer.verify_connection():
            if chromadb_importer.get_or_create_collection():
                chromadb_importer.import_movies(str(movies_file), batch_size=batch_size)
                chromadb_importer.print_statistics()

                logger.info("\n=== PRZYKŁADOWE WYSZUKIWANIE SEMANTYCZNE ===")
                results = chromadb_importer.search_movies("murder and revenge", n_results=3)
                for result in results:
                    logger.info(f"Film: {result['metadata'].get('title', 'N/A')}")
                    logger.info(f"  IMDB ID: {result['imdb_id']}")
                    logger.info(f"  Dystans: {result['distance']}")

                summary["chromadb_import"] = True
                logger.info("✓ Import do ChromaDB zakończony pomyślnie")
            else:
                logger.error("✗ Nie można utworzyć kolekcji ChromaDB")
                success = False
        else:
            logger.error("✗ Nie można połączyć się z ChromaDB lub Ollama")
            success = False
    except Exception as exc:
        logger.error(f"✗ Błąd importu ChromaDB: {exc}", exc_info=True)
        success = False

    time.sleep(1)

    # 3. Testy zapytań Cypher
    logger.info("\n" + "=" * 60)
    logger.info("3. TESTY ZAPYTAŃ CYPHER")
    logger.info("=" * 60)

    tester = None
    try:
        tester = Neo4jQueryTester(neo4j_uri, neo4j_user, neo4j_password, neo4j_database)
        if tester.verify_connection():
            report = tester.run_smoke_tests()
            tester.save_report(report, str(reports_dir / 'neo4j_query_report.json'))
            summary["neo4j_query_tests"] = report["tests_failed"] == 0
            if report["tests_failed"] == 0:
                logger.info("✓ Wszystkie testy zapytań Cypher zakończone pomyślnie")
            else:
                logger.warning("! Część testów Cypher zakończyła się błędem — sprawdź raport JSON")
                success = False
        else:
            logger.error("✗ Nie można połączyć się z Neo4j do testów Cypher")
            success = False
    except Exception as exc:
        logger.error(f"✗ Błąd testów Cypher: {exc}", exc_info=True)
        success = False
    finally:
        if tester is not None:
            tester.close()

    summary_path = reports_dir / 'task2_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as file_handle:
        json.dump(summary, file_handle, ensure_ascii=False, indent=2)

    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✓ ZADANIE 2 ZAKOŃCZONE POMYŚLNIE")
    else:
        logger.info("✗ ZADANIE 2 ZAKOŃCZYŁO SIĘ CZĘŚCIOWYM NIEPOWODZENIEM")
    logger.info(f"Raport podsumowania: {summary_path}")
    logger.info("=" * 60)

    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
