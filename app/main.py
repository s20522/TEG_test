import sys
from pathlib import Path

# Uruchomienie z katalogu głównego repo: `python app/main.py`
_app_dir = Path(__file__).resolve().parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

import ollama
from config.config import OLLAMA_HOST

client = ollama.Client(host=OLLAMA_HOST)

def translate_to_cypher(user_prompt, schema_context):
    system_message = f"""
    You are a Neo4j Cypher expert. 
    Convert the user's natural language question into a valid Cypher query.
    
    SCHEMA:
    {schema_context}

    RULES:
    1. Respond ONLY with the Cypher query. 
    2. Do not include markdown code blocks (no ```cypher).
    3. Do not explain the query.
    """

    response = ollama.generate(
        model='mistral',
        system=system_message,
        prompt=user_prompt,
        options={"temperature": 0}
    )

    return response['response'].strip()

if __name__ == "__main__":       
    # Artificial schema and q for testing
    schema = """
    Nodes: 
    (:Movie {title, releaseYear, rating}), 
    (:Actor {name, birthYear}), 
    (:Director {name})

    Relationships: 
    (:Actor)-[:ACTED_IN]->(:Movie), 
    (:Director)-[:DIRECTED]->(:Movie)
    """

    question = input("Ask question: ")

    print("Translating...")
    cypher = translate_to_cypher(question, schema)
    print(f"Generated Cypher: \n{cypher}")