"""Ingest documents: load → chunk → embed → store in ChromaDB."""

import time
import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL
from document_loader import load_all_documents
from chunker import chunk_documents


def main():
    start = time.time()

    # Step 1: Load documents
    print("Step 1/4: Loading documents...")
    documents = load_all_documents()
    print(f"  Loaded {len(documents)} documents")

    if not documents:
        print("Error: No documents found. Make sure documents/ folder has content.")
        return

    # Step 2: Chunk documents
    print("\nStep 2/4: Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"  Created {len(chunks)} chunks")

    # Step 3: Generate embeddings
    print(f"\nStep 3/4: Generating embeddings with {EMBEDDING_MODEL}...")
    print("  (First run downloads the model ~80MB, subsequent runs use cache)")
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [c.text for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    print(f"  Generated {len(embeddings)} embeddings (dim={embeddings.shape[1]})")

    # Step 4: Store in ChromaDB
    print(f"\nStep 4/4: Storing in ChromaDB at {CHROMA_DIR}...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete existing collection if it exists (fresh ingest)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Insert in batches
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch_end = min(i + batch_size, len(chunks))
        batch_chunks = chunks[i:batch_end]
        batch_embeddings = embeddings[i:batch_end].tolist()

        collection.add(
            ids=[c.chunk_id for c in batch_chunks],
            documents=[c.text for c in batch_chunks],
            embeddings=batch_embeddings,
            metadatas=[c.metadata for c in batch_chunks],
        )

    elapsed = time.time() - start
    print(f"\nDone! Ingestion complete in {elapsed:.1f}s")
    print(f"  Documents: {len(documents)}")
    print(f"  Chunks: {collection.count()}")
    print(f"  Storage: {CHROMA_DIR}")
    print(f"\nYou can now run: python app.py")


if __name__ == "__main__":
    main()
