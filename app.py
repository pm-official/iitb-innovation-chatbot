"""FastAPI server for the IIC Innovation Chatbot."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import STATIC_DIR, CHROMA_DIR, COLLECTION_NAME, HOST, PORT

app = FastAPI(title="IITB Innovation Chatbot", version="1.0.0")


class ChatRequest(BaseModel):
    query: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


@app.on_event("startup")
def startup():
    """Validate that ingestion has been run."""
    import chromadb
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_collection(COLLECTION_NAME)
        count = collection.count()
        print(f"Knowledge base loaded: {count} chunks")
    except Exception:
        print("WARNING: Knowledge base not found!")
        print("Run 'python ingest.py' first to ingest documents.")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Handle a chat query using the RAG pipeline."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    from rag import get_answer
    result = get_answer(req.query.strip(), req.history)
    return ChatResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", PORT))
    print(f"\nStarting IITB Innovation Chatbot at http://localhost:{port}")
    print("Press Ctrl+C to stop\n")
    uvicorn.run("app:app", host=HOST, port=port, reload=False)
