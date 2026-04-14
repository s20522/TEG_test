"""
ChromaDB Importer - import danych filmowych do ChromaDB
Zadanie 2 osoby A:
- generowanie lokalnych embeddingów przez Ollama (np. nomic-embed-text),
- zapis embeddingów i metadanych do ChromaDB,
- wyszukiwanie semantyczne po embeddingach.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
import requests
from chromadb.api.models.Collection import Collection
from dotenv import load_dotenv

# Załadowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja loggingu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaEmbeddingClient:
    """Klient pomocniczy do generowania embeddingów lokalnie przez Ollama."""

    def __init__(self, base_url: str, model_name: str, timeout: int = 120):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.timeout = timeout

    def verify_connection(self) -> bool:
        """Sprawdza, czy Ollama działa i odpowiada."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            logger.info("✓ Połączenie z Ollama potwierdzone")
            return True
        except Exception as exc:
            logger.error(f"✗ Błąd połączenia z Ollama: {exc}")
            return False

    def model_exists(self) -> bool:
        """Sprawdza, czy wybrany model embeddingowy jest dostępny lokalnie."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            models = payload.get("models", [])
            available_names = {m.get("name", "") for m in models}
            available_bases = {name.split(":")[0] for name in available_names}
            return self.model_name in available_names or self.model_name in available_bases
        except Exception as exc:
            logger.error(f"Nie udało się sprawdzić modelu embeddingowego: {exc}")
            return False

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generuje embeddingi dla listy tekstów.

        Najpierw próbuje nowszego endpointu `/api/embed`, a jeśli serwer go nie obsługuje,
        przechodzi na starszy endpoint `/api/embeddings` i wykonuje embedding pojedynczo.
        """
        if not texts:
            return []

        normalized_texts = [text if text and text.strip() else "Brak opisu filmu." for text in texts]

        # Nowy endpoint wspierający batch
        try:
            response = requests.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model_name, "input": normalized_texts},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            embeddings = payload.get("embeddings", [])
            if embeddings:
                return embeddings
        except Exception as exc:
            logger.warning(f"Endpoint /api/embed niedostępny lub zwrócił błąd: {exc}")

        # Fallback dla starszych wersji Ollama
        embeddings: List[List[float]] = []
        for text in normalized_texts:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            vector = payload.get("embedding")
            if not vector:
                raise RuntimeError("Ollama nie zwróciła embeddingu dla tekstu.")
            embeddings.append(vector)

        return embeddings


class ChromaDBImporter:
    """Klasa do importu danych do ChromaDB z lokalnymi embeddingami przez Ollama."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: Optional[str] = None,
        ollama_url: Optional[str] = None,
        embedding_model: Optional[str] = None,
        timeout: int = 120,
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name or os.getenv("CHROMADB_COLLECTION_NAME", "movies")
        self.ollama_url = ollama_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.embedding_model = embedding_model or os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self.timeout = timeout

        self._client = chromadb.HttpClient(host=host, port=port)
        self._collection: Optional[Collection] = None
        self.embedding_client = OllamaEmbeddingClient(
            base_url=self.ollama_url,
            model_name=self.embedding_model,
            timeout=self.timeout,
        )

        logger.info(f"Połączenie z ChromaDB: http://{host}:{port}")
        logger.info(f"Model embeddingowy Ollama: {self.embedding_model}")

    def verify_connection(self) -> bool:
        """Weryfikacja połączenia z ChromaDB i Ollama."""
        try:
            self._client.heartbeat()
            logger.info("✓ Połączenie z ChromaDB potwierdzone")
        except Exception as exc:
            logger.error(f"✗ Błąd połączenia z ChromaDB: {exc}")
            return False

        if not self.embedding_client.verify_connection():
            return False

        if not self.embedding_client.model_exists():
            logger.error(
                f"✗ Model embeddingowy '{self.embedding_model}' nie jest dostępny lokalnie w Ollama"
            )
            logger.error(
                f"Uruchom najpierw: ollama pull {self.embedding_model}"
            )
            return False

        logger.info("✓ ChromaDB i lokalne embeddingi Ollama są gotowe")
        return True

    def get_or_create_collection(self) -> bool:
        """Pobranie lub utworzenie kolekcji."""
        try:
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",
                    "description": "Film synopses embedded locally with Ollama"
                },
            )
            logger.info(f"✓ Kolekcja '{self.collection_name}' gotowa")
            return True
        except Exception as exc:
            logger.error(f"✗ Nie można utworzyć / otworzyć kolekcji: {exc}")
            return False

    @staticmethod
    def _build_document(movie: Dict[str, Any]) -> str:
        """Buduje tekst dokumentu do embedowania i przechowywania w ChromaDB."""
        plot_synopsis = (movie.get('plot_synopsis') or '').strip()
        title = (movie.get('title') or '').strip()
        genres = ', '.join(movie.get('genres', []))
        tags = ', '.join(movie.get('tags', []))

        parts = [
            f"Title: {title}" if title else "",
            f"Synopsis: {plot_synopsis}" if plot_synopsis else "",
            f"Genres: {genres}" if genres else "",
            f"Tags: {tags}" if tags else "",
        ]
        document = "\n".join(part for part in parts if part).strip()
        return document or "Brak opisu filmu."

    def import_movies(self, json_file: str, batch_size: int = 100):
        """Import filmów do ChromaDB wraz z lokalnie wygenerowanymi embeddingami."""
        if self._collection is None:
            raise RuntimeError("Wywołaj get_or_create_collection() przed importem")

        logger.info(f"Czytanie pliku: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as file_handle:
            movies = json.load(file_handle)

        logger.info(f"Liczba filmów do importu: {len(movies)}")

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        for movie in movies:
            documents.append(self._build_document(movie))
            metadatas.append(
                {
                    'imdb_id': movie['imdb_id'],
                    'title': movie['title'],
                    'genres': ','.join(movie.get('genres', [])),
                    'tags': ','.join(movie.get('tags', [])),
                    'synopsis_source': movie.get('synopsis_source', 'unknown'),
                    'split': movie.get('split', 'unknown'),
                }
            )
            ids.append(movie['imdb_id'])

        for index in range(0, len(documents), batch_size):
            batch_docs = documents[index:index + batch_size]
            batch_meta = metadatas[index:index + batch_size]
            batch_ids = ids[index:index + batch_size]
            self._import_batch(batch_docs, batch_meta, batch_ids)
            logger.info(
                f"Zaimportowano {min(index + batch_size, len(documents))}/{len(documents)} filmów"
            )

        logger.info("✓ Import do ChromaDB zakończony")

    def _import_batch(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Import pojedynczego batcha do ChromaDB."""
        if self._collection is None:
            raise RuntimeError("Kolekcja nie została przygotowana.")

        try:
            embeddings = self.embedding_client.embed_texts(documents)
            self._collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
        except Exception as exc:
            logger.error(f"Błąd podczas importu batcha: {exc}")
            raise

    def search_movies(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Wyszukiwanie filmów na podstawie embeddingu zapytania."""
        if self._collection is None:
            return []

        try:
            query_embedding = self.embedding_client.embed_texts([query])[0]
            data = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['distances', 'metadatas', 'documents'],
            )
            results = []
            if data.get('ids') and len(data['ids']) > 0:
                for idx, movie_id in enumerate(data['ids'][0]):
                    results.append(
                        {
                            'imdb_id': movie_id,
                            'distance': data['distances'][0][idx] if data.get('distances') else None,
                            'metadata': data['metadatas'][0][idx] if data.get('metadatas') else {},
                            'document': data['documents'][0][idx] if data.get('documents') else '',
                        }
                    )
            return results
        except Exception as exc:
            logger.error(f"Błąd wyszukiwania: {exc}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Pobranie statystyk kolekcji."""
        if self._collection is None:
            return {}
        try:
            return {
                'name': self.collection_name,
                'count': self._collection.count(),
                'embedding_model': self.embedding_model,
                'ollama_url': self.ollama_url,
            }
        except Exception as exc:
            logger.error(f"Błąd pobrania statystyk: {exc}")
            return {}

    def print_statistics(self):
        """Wydrukowanie statystyk."""
        stats = self.get_collection_stats()
        logger.info("\n=== STATYSTYKI CHROMADB ===")
        logger.info(f"Kolekcja: {stats.get('name', 'N/A')}")
        logger.info(f"Liczba dokumentów: {stats.get('count', 'N/A')}")
        logger.info(f"Model embeddingowy: {stats.get('embedding_model', 'N/A')}")
        logger.info(f"Ollama URL: {stats.get('ollama_url', 'N/A')}")


def main():
    """Główna funkcja importu do ChromaDB."""
    chromadb_host = os.getenv('CHROMADB_HOST', 'localhost')
    chromadb_port = int(os.getenv('CHROMADB_PORT', '8000'))
    data_processed_dir = os.getenv('DATA_PROCESSED_DIR', './data/processed')
    batch_size = int(os.getenv('BATCH_SIZE', '100'))
    ollama_url = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    embedding_model = os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text')
    timeout = int(os.getenv('OLLAMA_TIMEOUT', '120'))

    importer = ChromaDBImporter(
        host=chromadb_host,
        port=chromadb_port,
        ollama_url=ollama_url,
        embedding_model=embedding_model,
        timeout=timeout,
    )

    try:
        if not importer.verify_connection():
            logger.error("Nie można połączyć się z ChromaDB lub Ollama")
            return

        if not importer.get_or_create_collection():
            logger.error("Nie można utworzyć kolekcji")
            return

        movies_file = Path(data_processed_dir) / 'movies_all.json'
        if movies_file.exists():
            importer.import_movies(str(movies_file), batch_size=batch_size)
        else:
            logger.error(f"Plik nie znaleziony: {movies_file}")
            return

        importer.print_statistics()

        logger.info("\n=== PRZYKŁADOWE WYSZUKIWANIE SEMANTYCZNE ===")
        results = importer.search_movies("murder and revenge", n_results=3)
        for result in results:
            logger.info(f"Film: {result['metadata'].get('title', 'N/A')}")
            logger.info(f"  IMDB ID: {result['imdb_id']}")
            logger.info(f"  Dystans: {result['distance']}")

        logger.info("\n✓ Import do ChromaDB zakończony pomyślnie!")

    except Exception as exc:
        logger.error(f"Błąd podczas importu: {exc}", exc_info=True)


if __name__ == '__main__':
    main()
