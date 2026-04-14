#!/bin/bash

ollama serve &

echo "Waiting for Ollama server to start..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 1
done

echo "Ollama is up! Pulling Mistral model..."
ollama pull mistral

echo "Model pulled successfully. Ready for Text-to-Cypher."
wait $!