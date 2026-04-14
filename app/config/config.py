import os
from dotenv import load_dotenv

# Załaduj zmienne z .env
load_dotenv()

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama-mistral:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# ChromaDB Configuration
CHROMADB_HOST = os.getenv("CHROMADB_HOST", "chromadb")
CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", "8000"))
CHROMADB_COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "movies")

# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))

# Data Paths
DATA_RAW_DIR = os.getenv("DATA_RAW_DIR", "/app/data/raw")
DATA_PROCESSED_DIR = os.getenv("DATA_PROCESSED_DIR", "/app/data/processed")
