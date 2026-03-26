"""Ingest documents: load -> chunk -> store in ChromaDB (with built-in ONNX embeddings)."""

import time
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from config import CHROMA_DIR, COLLECTION_NAME
from document_loader import load_all_documents
from chunker import chunk_documents


def main():
    start = time.time()

    # Step 1: Load documents
    print("Step 1/3: Loading documents...")
    documents = load_all_documents()
    print(f"  Loaded {len(documents)} documents")

    if not documents:
        print("Error: No documents found. Make sure documents/ folder has content.")
        return

    # Step 2: Chunk documents
    print("\nStep 2/3: Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"  Created {len(chunks)} chunks")

    # Step 3: Store in ChromaDB (embeddings computed automatically via ONNX)
    print(f"\nStep 3/3: Storing in ChromaDB with ONNX embeddings...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Use ChromaDB's built-in ONNX embedding function (all-MiniLM-L6-v2)
    embedding_fn = DefaultEmbeddingFunction()

    # Delete existing collection if it exists (fresh ingest)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_fn,
    )

    # Insert in batches — ChromaDB computes embeddings automatically
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch_end = min(i + batch_size, len(chunks))
        batch_chunks = chunks[i:batch_end]

        collection.add(
            ids=[c.chunk_id for c in batch_chunks],
            documents=[c.text for c in batch_chunks],
            metadatas=[c.metadata for c in batch_chunks],
        )
        print(f"  Stored batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")

    elapsed = time.time() - start
    print(f"\nDone! Ingestion complete in {elapsed:.1f}s")
    print(f"  Documents: {len(documents)}")
    print(f"  Chunks: {collection.count()}")
    print(f"  Storage: {CHROMA_DIR}")
    print(f"\nYou can now run: streamlit run streamlit_app.py")


if __name__ == "__main__":
    main()
