FROM ollama/ollama:latest

# Zainstaluj niezbędne pakiety (dodaj python3-venv)
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Ustaw katalog roboczy
WORKDIR /app

# Stwórz wirtualne środowisko w /opt/venv
RUN python3 -m venv /opt/venv

# Ustaw PATH, aby venv był priorytetowy
ENV PATH="/opt/venv/bin:$PATH"

# Skopiuj requirements.txt
COPY requirements.txt .

# Zainstaluj zależności Python (używamy pip z venv)
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY entrypoint.sh /entrypoint.sh

# Uprawnienia do entrypoint
RUN chmod +x /entrypoint.sh

# Expose port Ollama
EXPOSE 11434

# Uruchom entrypoint
ENTRYPOINT ["/entrypoint.sh"]
