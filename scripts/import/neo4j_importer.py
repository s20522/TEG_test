"""
Neo4j Importer - Import danych filmowych do Neo4j
Tworzy węzły: Movie, Person, Genre
Relacje: DIRECTED, ACTED_IN, IN_GENRE
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Session
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


class Neo4jImporter:
    """Klasa do importu danych do Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """Inicjalizacja połączenia z Neo4j"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        logger.info(f"Połączenie z Neo4j: {uri}")
        
    def close(self):
        """Zamknięcie połączenia"""
        self.driver.close()
        logger.info("Połączenie z Neo4j zamknięte")
    
    def verify_connection(self) -> bool:
        """Weryfikacja połączenia z bazą"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1")
                result.consume()
            logger.info("✓ Połączenie z Neo4j potwierdzone")
            return True
        except Exception as e:
            logger.error(f"✗ Błąd połączenia: {e}")
            return False
    
    def clear_database(self):
        """Wyczyszczenie bazy danych"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Baza danych wyczyszczona")
    
    def create_constraints(self):
        """Utworzenie ograniczeń unikalności"""
        constraints = [
            "CREATE CONSTRAINT movie_imdb_id IF NOT EXISTS FOR (m:Movie) REQUIRE m.imdb_id IS UNIQUE",
            "CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
            "CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
        ]
        
        with self.driver.session(database=self.database) as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"✓ Ograniczenie utworzone")
                except Exception as e:
                    logger.debug(f"Ograniczenie już istnieje: {e}")
    
    def create_indexes(self):
        """Utworzenie indeksów"""
        indexes = [
            "CREATE INDEX movie_title IF NOT EXISTS FOR (m:Movie) ON (m.title)",
            "CREATE INDEX movie_genres IF NOT EXISTS FOR (m:Movie) ON (m.genres)",
            "CREATE INDEX genre_name IF NOT EXISTS FOR (g:Genre) ON (g.name)",
        ]
        
        with self.driver.session(database=self.database) as session:
            for index in indexes:
                try:
                    session.run(index)
                    logger.info(f"✓ Indeks utworzony")
                except Exception as e:
                    logger.debug(f"Indeks już istnieje: {e}")
    
    def import_movies(self, json_file: str, batch_size: int = 100):
        """Import filmów do Neo4j"""
        
        logger.info(f"Czytanie pliku: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            movies = json.load(f)
        
        logger.info(f"Liczba filmów do importu: {len(movies)}")
        
        # Import w batchach
        for i in range(0, len(movies), batch_size):
            batch = movies[i:i+batch_size]
            self._import_batch(batch)
            logger.info(f"Zaimportowano {min(i+batch_size, len(movies))}/{len(movies)} filmów")
        
        logger.info(f"✓ Import filmów zakończony")
    
    def _import_batch(self, batch: List[Dict[str, Any]]):
        """Import batcha filmów"""
        
        with self.driver.session(database=self.database) as session:
            for movie in batch:
                # Utworzenie węzła Movie
                session.run(
                    """
                    MERGE (m:Movie {imdb_id: $imdb_id})
                    SET m.title = $title,
                        m.plot_synopsis = $plot_synopsis,
                        m.tags = $tags,
                        m.synopsis_source = $synopsis_source,
                        m.review = $review
                    """,
                    imdb_id=movie['imdb_id'],
                    title=movie['title'],
                    plot_synopsis=movie['plot_synopsis'],
                    tags=movie['tags'],
                    synopsis_source=movie['synopsis_source'],
                    review=movie['review']
                )
                
                # Utworzenie węzłów Genre i relacji IN_GENRE
                for genre in movie.get('genres', []):
                    session.run(
                        """
                        MERGE (g:Genre {name: $genre_name})
                        WITH g
                        MATCH (m:Movie {imdb_id: $imdb_id})
                        MERGE (m)-[:IN_GENRE]->(g)
                        """,
                        genre_name=genre,
                        imdb_id=movie['imdb_id']
                    )
    
    def create_sample_relations(self):
        """Utworzenie przykładowych relacji DIRECTED i ACTED_IN"""
        
        logger.info("Tworzenie przykładowych relacji...")
        
        with self.driver.session(database=self.database) as session:
            # Przykład: Dodanie reżysera
            session.run(
                """
                MATCH (m:Movie)
                WHERE m.title CONTAINS 'fear' OR m.title CONTAINS 'horror'
                LIMIT 5
                MERGE (p:Person {name: 'Sample Director'})
                MERGE (p)-[:DIRECTED]->(m)
                """
            )
            
            # Przykład: Dodanie aktora
            session.run(
                """
                MATCH (m:Movie)
                WHERE m.title CONTAINS 'fear' OR m.title CONTAINS 'horror'
                LIMIT 5
                MERGE (a:Person {name: 'Sample Actor'})
                MERGE (a)-[:ACTED_IN]->(m)
                """
            )
        
        logger.info("✓ Przykładowe relacje utworzone")
    
    def get_statistics(self) -> Dict[str, int]:
        """Pobranie statystyk bazy danych"""
        
        with self.driver.session(database=self.database) as session:
            stats = {}
            
            # Liczba filmów
            result = session.run("MATCH (m:Movie) RETURN count(m) as count")
            stats['movies'] = result.single()['count']
            
            # Liczba gatunków
            result = session.run("MATCH (g:Genre) RETURN count(g) as count")
            stats['genres'] = result.single()['count']
            
            # Liczba osób
            result = session.run("MATCH (p:Person) RETURN count(p) as count")
            stats['persons'] = result.single()['count']
            
            # Liczba relacji
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats['relations'] = result.single()['count']
            
            return stats
    
    def print_statistics(self):
        """Wydrukowanie statystyk"""
        
        stats = self.get_statistics()
        logger.info("\n=== STATYSTYKI NEO4J ===")
        logger.info(f"Filmy: {stats['movies']}")
        logger.info(f"Gatunki: {stats['genres']}")
        logger.info(f"Osoby: {stats['persons']}")
        logger.info(f"Relacje: {stats['relations']}")


def main():
    """Główna funkcja"""
    
    # Konfiguracja z zmiennych środowiskowych
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password123')
    neo4j_database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    data_processed_dir = os.getenv('DATA_PROCESSED_DIR', './data/processed')
    batch_size = int(os.getenv('BATCH_SIZE', '100'))
    
    # Inicjalizacja importera
    importer = Neo4jImporter(neo4j_uri, neo4j_user, neo4j_password, neo4j_database)
    
    try:
        # Weryfikacja połączenia
        if not importer.verify_connection():
            logger.error("Nie można połączyć się z Neo4j")
            return
        
        # Wyczyszczenie bazy (opcjonalnie)
        # importer.clear_database()
        
        # Utworzenie ograniczeń i indeksów
        importer.create_constraints()
        importer.create_indexes()
        
        # Import filmów
        movies_file = Path(data_processed_dir) / 'movies_all.json'
        if movies_file.exists():
            importer.import_movies(str(movies_file), batch_size=batch_size)
        else:
            logger.error(f"Plik nie znaleziony: {movies_file}")
            return
        
        # Utworzenie przykładowych relacji
        importer.create_sample_relations()
        
        # Wydrukowanie statystyk
        importer.print_statistics()
        
        logger.info("\n✓ Import zakończony pomyślnie!")
        
    except Exception as e:
        logger.error(f"Błąd podczas importu: {e}", exc_info=True)
    finally:
        importer.close()


if __name__ == '__main__':
    main()
