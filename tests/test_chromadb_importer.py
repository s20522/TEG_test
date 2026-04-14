import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "import" / "chromadb_importer.py"
SPEC = importlib.util.spec_from_file_location("chromadb_importer", MODULE_PATH)
chromadb_importer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(chromadb_importer)

ChromaDBImporter = chromadb_importer.ChromaDBImporter
OllamaEmbeddingClient = chromadb_importer.OllamaEmbeddingClient


class FakeCollection:
    def __init__(self):
        self.upsert_calls = []
        self.query_calls = []

    def upsert(self, **kwargs):
        self.upsert_calls.append(kwargs)

    def query(self, **kwargs):
        self.query_calls.append(kwargs)
        return {
            "ids": [["tt0000001"]],
            "distances": [[0.05]],
            "metadatas": [[{"title": "Fear House", "imdb_id": "tt0000001"}]],
            "documents": [["Title: Fear House\nSynopsis: A haunted family returns..."]],
        }

    def count(self):
        return 2


class FakeHttpClient:
    def heartbeat(self):
        return True

    def get_or_create_collection(self, name, metadata):
        return FakeCollection()


def load_fixture() -> list:
    fixture_path = Path(__file__).parent / "fixtures" / "movies_sample.json"
    with open(fixture_path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def build_importer(monkeypatch):
    monkeypatch.setattr(chromadb_importer.chromadb, "HttpClient", lambda host, port: FakeHttpClient())
    importer = ChromaDBImporter(
        host="localhost",
        port=8000,
        ollama_url="http://localhost:11434",
        embedding_model="nomic-embed-text",
    )
    importer._collection = FakeCollection()
    return importer


def test_build_document_contains_key_fields():
    movie = load_fixture()[0]
    document = ChromaDBImporter._build_document(movie)

    assert "Title: Fear House" in document
    assert "Synopsis:" in document
    assert "Genres: horror" in document
    assert "Tags: horror, haunted house, family" in document


def test_import_batch_uses_embeddings(monkeypatch):
    fixture_path = Path(__file__).parent / "fixtures" / "movies_sample.json"
    importer = build_importer(monkeypatch)

    monkeypatch.setattr(
        importer.embedding_client,
        "embed_texts",
        lambda texts: [[0.1, 0.2, 0.3] for _ in texts],
    )

    importer.import_movies(str(fixture_path), batch_size=1)

    assert len(importer._collection.upsert_calls) == 2
    first_call = importer._collection.upsert_calls[0]
    assert first_call["ids"] == ["tt0000001"]
    assert first_call["embeddings"] == [[0.1, 0.2, 0.3]]


def test_search_movies_uses_query_embeddings(monkeypatch):
    importer = build_importer(monkeypatch)
    monkeypatch.setattr(importer.embedding_client, "embed_texts", lambda texts: [[0.4, 0.5, 0.6]])

    results = importer.search_movies("haunted family", n_results=3)

    assert len(results) == 1
    assert results[0]["imdb_id"] == "tt0000001"
    assert importer._collection.query_calls[0]["query_embeddings"] == [[0.4, 0.5, 0.6]]


def test_ollama_embedding_client_fallback(monkeypatch):
    client = OllamaEmbeddingClient("http://localhost:11434", "nomic-embed-text", timeout=5)

    responses = [
        Mock(status_code=404, raise_for_status=Mock(side_effect=Exception("404"))),
        Mock(status_code=200, raise_for_status=Mock(return_value=None), json=Mock(return_value={"embedding": [0.7, 0.8]})),
        Mock(status_code=200, raise_for_status=Mock(return_value=None), json=Mock(return_value={"embedding": [0.9, 1.0]})),
    ]

    def fake_post(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(chromadb_importer.requests, "post", fake_post)

    vectors = client.embed_texts(["first text", "second text"])

    assert vectors == [[0.7, 0.8], [0.9, 1.0]]
