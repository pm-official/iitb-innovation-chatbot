"""Load documents from the documents/ directory into structured objects."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

from config import DOCUMENTS_DIR, CATEGORY_NAMES


@dataclass
class Document:
    content: str
    metadata: dict = field(default_factory=dict)


def _get_category(folder_name: str) -> str:
    """Convert folder name to display category."""
    return CATEGORY_NAMES.get(folder_name, folder_name)


def _load_txt(filepath: Path, category: str) -> Document | None:
    """Load a .txt file, extract source URL from header."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return None

    # Extract source URL from header line
    source_url = ""
    lines = text.split("\n")
    content_lines = []
    for i, line in enumerate(lines):
        if line.startswith("SOURCE URL:"):
            source_url = line.replace("SOURCE URL:", "").strip()
        elif line.startswith("=" * 10):
            continue
        else:
            content_lines.append(line)

    content = "\n".join(content_lines).strip()

    if len(content) < 50:
        return None  # Skip near-empty files

    return Document(
        content=content,
        metadata={
            "source_file": filepath.name,
            "category": category,
            "source_url": source_url,
            "file_type": "text",
        },
    )


def _load_pdf(filepath: Path, category: str) -> Document | None:
    """Load a .pdf file using pdfplumber."""
    try:
        pages_text = []
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages_text.append(f"--- Page {i + 1} ---\n{text.strip()}")

        if not pages_text:
            print(f"  Warning: No text extracted from {filepath}")
            return None

        content = "\n\n".join(pages_text)

        return Document(
            content=content,
            metadata={
                "source_file": filepath.name,
                "category": category,
                "source_url": "",
                "file_type": "pdf",
                "page_count": len(pages_text),
            },
        )
    except Exception as e:
        print(f"  Warning: Could not process PDF {filepath}: {e}")
        return None


def load_all_documents() -> list[Document]:
    """Load all .txt and .pdf files from the documents directory."""
    documents = []

    if not DOCUMENTS_DIR.exists():
        print(f"Error: Documents directory not found at {DOCUMENTS_DIR}")
        return documents

    for folder in sorted(DOCUMENTS_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue

        category = _get_category(folder.name)

        for filepath in sorted(folder.iterdir()):
            # Skip HTML files (we have .txt versions)
            if filepath.suffix == ".html":
                continue

            if filepath.suffix == ".txt":
                doc = _load_txt(filepath, category)
                if doc:
                    documents.append(doc)

            elif filepath.suffix == ".pdf":
                doc = _load_pdf(filepath, category)
                if doc:
                    documents.append(doc)

    return documents


if __name__ == "__main__":
    docs = load_all_documents()
    print(f"\nLoaded {len(docs)} documents")
    for doc in docs:
        preview = doc.content[:80].replace("\n", " ")
        print(f"  [{doc.metadata['category']}] {doc.metadata['source_file']} "
              f"({len(doc.content)} chars) — {preview}...")
