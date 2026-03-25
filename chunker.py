"""Split documents into chunks suitable for embedding and retrieval."""

import hashlib
import re
from dataclasses import dataclass, field

from document_loader import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_SIZE


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    chunk_id: str = ""


_chunk_counter = 0

def _make_chunk_id(text: str, source: str) -> str:
    """Create a unique ID for each chunk."""
    global _chunk_counter
    _chunk_counter += 1
    h = hashlib.md5(f"{source}:{text[:200]}:{_chunk_counter}".encode()).hexdigest()[:16]
    return f"{h}_{_chunk_counter}"


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs."""
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def _split_long_paragraph(text: str, max_size: int) -> list[str]:
    """Split a long paragraph by sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    parts = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) + 1 > max_size and current:
            parts.append(current.strip())
            current = sent
        else:
            current = f"{current} {sent}" if current else sent
    if current.strip():
        parts.append(current.strip())
    return parts


def chunk_document(doc: Document) -> list[Chunk]:
    """Chunk a single document into overlapping pieces."""
    paragraphs = _split_into_paragraphs(doc.content)

    # Split any paragraph that's too long
    processed = []
    for para in paragraphs:
        if len(para) > CHUNK_SIZE:
            processed.extend(_split_long_paragraph(para, CHUNK_SIZE))
        else:
            processed.append(para)

    # Merge small paragraphs into chunks of ~CHUNK_SIZE
    chunks = []
    current_text = ""

    for para in processed:
        if len(current_text) + len(para) + 2 > CHUNK_SIZE and current_text:
            chunks.append(current_text.strip())
            # Overlap: keep the last CHUNK_OVERLAP chars
            if len(current_text) > CHUNK_OVERLAP:
                current_text = current_text[-CHUNK_OVERLAP:]
            current_text = f"{current_text}\n\n{para}"
        else:
            current_text = f"{current_text}\n\n{para}" if current_text else para

    if current_text.strip():
        chunks.append(current_text.strip())

    # Create Chunk objects with metadata context header
    category = doc.metadata.get("category", "General")
    source = doc.metadata.get("source_file", "unknown")

    result = []
    for i, text in enumerate(chunks):
        if len(text) < MIN_CHUNK_SIZE:
            continue

        # Prepend context for better embedding
        enriched_text = f"[{category} | {source}]\n{text}"

        chunk = Chunk(
            text=enriched_text,
            metadata={
                **doc.metadata,
                "chunk_index": i,
            },
            chunk_id=_make_chunk_id(text, source),
        )
        result.append(chunk)

    return result


def chunk_documents(documents: list[Document]) -> list[Chunk]:
    """Chunk all documents."""
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    return all_chunks


if __name__ == "__main__":
    from document_loader import load_all_documents

    docs = load_all_documents()
    chunks = chunk_documents(docs)
    print(f"\n{len(docs)} documents → {len(chunks)} chunks")
    print(f"\nSample chunks:")
    for chunk in chunks[:3]:
        print(f"\n--- [{chunk.metadata['category']}] {chunk.metadata['source_file']} ---")
        print(chunk.text[:300])
        print("...")
