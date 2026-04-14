"""
Run All Imports - Uruchomienie wszystkich importów danych
"""

import sys
import time
import logging
from pathlib import Path
import os
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
from neo4j_importer import Neo4jImporter
from chromadb_importer import ChromaDBImporter


def main():
    """Główna funkcja"""
    
    logger.info("=" * 60)
    logger.info("URUCHOMIENIE WSZYSTKICH IMPORTÓW")
    logger.info("=" * 60)
    
    # Konfiguracja
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password123')
    neo4j_database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    chromadb_host = os.getenv('CHROMADB_HOST', 'localhost')
    chromadb_port = int(os.getenv('CHROMADB_PORT', '8000'))
    
    data_processed_dir = os.getenv('DATA_PROCESSED_DIR', './data/processed')
    batch_size = int(os.getenv('BATCH_SIZE', '100'))
    
    movies_file = Path(data_processed_dir) / 'movies_all.json'
    
    # Sprawdzenie pliku
    if not movies_file.exists():
        logger.error(f"Plik nie znaleziony: {movies_file}")
        return False
    
    success = True
    
    # 1. Import do Neo4j
    logger.info("\n" + "=" * 60)
    logger.info("1. IMPORT DO NEO4J")
    logger.info("=" * 60)
    
    try:
        neo4j_importer = Neo4jImporter(neo4j_uri, neo4j_user, neo4j_password, neo4j_database)
        
        if neo4j_importer.verify_connection():
            neo4j_importer.create_constraints()
            neo4j_importer.create_indexes()
            neo4j_importer.import_movies(str(movies_file), batch_size=batch_size)
            neo4j_importer.create_sample_relations()
            neo4j_importer.print_statistics()
            logger.info("✓ Import do Neo4j zakończony pomyślnie")
        else:
            logger.error("✗ Nie można połączyć się z Neo4j")
            success = False
        
        neo4j_importer.close()
    except Exception as e:
        logger.error(f"✗ Błąd importu Neo4j: {e}", exc_info=True)
        success = False
    
    # Czekanie między importami
    time.sleep(2)
    
    # 2. Import do ChromaDB
    logger.info("\n" + "=" * 60)
    logger.info("2. IMPORT DO CHROMADB")
    logger.info("=" * 60)
    
    try:
        chromadb_importer = ChromaDBImporter(chromadb_host, chromadb_port)
        
        if chromadb_importer.verify_connection():
            if chromadb_importer.get_or_create_collection():
                chromadb_importer.import_movies(str(movies_file), batch_size=batch_size)
                chromadb_importer.print_statistics()
                
                # Przykładowe wyszukiwanie
                logger.info("\n=== PRZYKŁADOWE WYSZUKIWANIE ===")
                results = chromadb_importer.search_movies("murder and revenge", n_results=3)
                for result in results:
                    logger.info(f"Film: {result['metadata'].get('title', 'N/A')}")
                    logger.info(f"  IMDB ID: {result['imdb_id']}")
                
                logger.info("✓ Import do ChromaDB zakończony pomyślnie")
            else:
                logger.error("✗ Nie można utworzyć kolekcji ChromaDB")
                success = False
        else:
            logger.error("✗ Nie można połączyć się z ChromaDB")
            success = False
    except Exception as e:
        logger.error(f"✗ Błąd importu ChromaDB: {e}", exc_info=True)
        success = False
    
    # Podsumowanie
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✓ WSZYSTKIE IMPORTY ZAKOŃCZONE POMYŚLNIE")
    else:
        logger.info("✗ NIEKTÓRE IMPORTY NIE POWIODŁY SIĘ")
    logger.info("=" * 60)
    
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
