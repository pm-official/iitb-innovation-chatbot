FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model during build (not at runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY config.py document_loader.py chunker.py ingest.py rag.py app.py ./
COPY static/ ./static/
COPY documents/ ./documents/

# Run ingestion at build time so chroma_db is baked into the image
RUN python ingest.py

# Expose port
EXPOSE 8000

# Start server
CMD ["python", "app.py"]
