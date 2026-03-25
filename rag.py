"""RAG pipeline: retrieve context → build prompt → call Gemini → return answer."""

import chromadb
from google import genai
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL, TOP_K,
)

SYSTEM_PROMPT = """You are the IIC Innovation Advisor at IIT Bombay. You help students navigate IIT Bombay's innovation and entrepreneurship ecosystem with practical, actionable guidance.

WHO YOU ARE:
- A knowledgeable advisor on IIT Bombay's entire innovation ecosystem
- You give SPECIFIC, PRACTICAL answers with real program names, URLs, contacts, and deadlines
- You tailor advice based on the student's current stage

WHAT YOU COVER:
- SINE (Society for Innovation & Entrepreneurship) — incubation, seed funding, mentorship
- DSSE (Desai Sethi School of Entrepreneurship) — 20+ courses, Minor in Entrepreneurship, pre-incubation programs (IDEAS, WiE, I-NCUBATE)
- IRCC (Industrial Research & Consultancy Centre) — patents, IP policy, technology licensing
- E-Cell — Eureka competition, E-Summit, startup support
- Tinkerers' Lab & MakerSpace — prototyping, 3D printing, fabrication
- ASPIRE Research Park — industry collaboration, CoEs
- TIH (Technology Innovation Hub) — IoT/IoE programs, Aarohan seed support
- SemiX — semiconductor technologies
- Government schemes — NIDHI PRAYAS, BIRAC BIG, Startup India, SIH, iDEX
- IIT Bombay Startup Policy — equity, IP ownership, deferred placement

STAGE-BASED GUIDANCE:
When a student asks about their idea/startup, identify their stage and suggest appropriate resources:

1. IDEA STAGE: DSSE foundation courses (ENT101 - Intro to Innovation & Entrepreneurship), E-Cell events, Eureka Junior, ideation workshops
2. VALIDATION: DSSE specialist courses, E-Cell mentorship, DSSE IDEAS pre-incubation program, talk to relevant professors
3. PROTOTYPE: Tinkerers' Lab (24/7 access, 3D printers, laser cutters), MakerSpace (MS101 course), NIDHI PRAYAS (up to Rs 10L for prototyping)
4. EARLY STARTUP: SINE incubation (up to 3 years support), IoE-SINE seed fund (up to Rs 50L), IIT Bombay Startup Policy, Deferred Placement Policy
5. SCALING: SINE Rs 100Cr venture fund, BIRAC BIG (Rs 50L for biotech), ASPIRE Research Park, government schemes

RULES:
1. ONLY answer based on the provided context. If the context doesn't contain the answer, say "I don't have specific information about that, but I'd recommend checking with [relevant office/website]."
2. When mentioning a resource, include: what it is, who it's for, and how to access it.
3. Structure multi-resource answers with clear sections and bullet points.
4. Always be encouraging but honest about requirements and timelines.
5. If asked about something outside IIT Bombay's innovation ecosystem, politely redirect.
6. End answers with a clear "Next Steps" section when appropriate.
7. Cite sources using the format: [Source: filename] at the end of your answer.
8. Use markdown formatting for readability (headers, bullets, bold for key terms).

IMPORTANT: You are NOT a general-purpose AI. You specifically help IIT Bombay students with innovation and entrepreneurship resources. Stay focused on this domain."""


# Module-level singletons (initialized on first call)
_embedding_model = None
_collection = None
_gemini_client = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client


def retrieve_context(query: str) -> list[dict]:
    """Embed query and retrieve top-K relevant chunks."""
    model = _get_embedding_model()
    collection = _get_collection()

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    contexts = []
    if results and results["documents"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            contexts.append({
                "text": doc,
                "source_file": meta.get("source_file", ""),
                "category": meta.get("category", ""),
                "source_url": meta.get("source_url", ""),
                "relevance": 1 - dist,  # cosine distance to similarity
            })

    return contexts


def build_prompt(query: str, contexts: list[dict], history: list[dict]) -> str:
    """Construct the full prompt with context and history."""
    # Format context
    context_parts = []
    for i, ctx in enumerate(contexts, 1):
        context_parts.append(
            f"[Context {i} — {ctx['category']} — {ctx['source_file']}]\n{ctx['text']}"
        )
    context_str = "\n\n".join(context_parts)

    # Format history (last 4 exchanges = 8 messages)
    history_str = ""
    recent_history = history[-8:] if len(history) > 8 else history
    if recent_history:
        history_parts = []
        for msg in recent_history:
            role = "Student" if msg["role"] == "user" else "Advisor"
            history_parts.append(f"{role}: {msg['content']}")
        history_str = "\n".join(history_parts)

    prompt = f"""{SYSTEM_PROMPT}

CONTEXT FROM KNOWLEDGE BASE:
{context_str}

{"CONVERSATION HISTORY:" + chr(10) + history_str if history_str else ""}

STUDENT'S QUESTION: {query}

Provide a helpful, practical answer with specific next steps. Cite your sources at the end."""

    return prompt


def get_answer(query: str, history: list[dict] | None = None) -> dict:
    """Full RAG pipeline: retrieve → prompt → Gemini → answer."""
    if history is None:
        history = []

    # Retrieve relevant context
    contexts = retrieve_context(query)

    # Build prompt
    prompt = build_prompt(query, contexts, history)

    # Call Gemini with retry and fallback
    import time
    client = _get_gemini_client()

    models_to_try = [GEMINI_MODEL, "gemini-2.5-flash-lite", "gemini-2.0-flash-lite"]
    answer = None

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                answer = response.text if response.text else None
                if answer:
                    break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = (attempt + 1) * 5
                    print(f"Rate limited on {model_name}, retrying in {wait}s (attempt {attempt + 1}/3)")
                    time.sleep(wait)
                else:
                    print(f"Error with {model_name}: {err_str[:100]}")
                    break  # Non-rate-limit error, try next model
        if answer:
            break

    if not answer:
        answer = "I'm sorry, the AI service is temporarily unavailable. Please try again in a minute. If the issue persists, the API quota may have been exceeded."

    # Extract source references
    sources = []
    seen_sources = set()
    for ctx in contexts:
        source_key = ctx["source_file"]
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({
                "file": ctx["source_file"],
                "category": ctx["category"],
                "url": ctx["source_url"],
                "relevance": round(ctx["relevance"], 3),
            })

    return {
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":
    # Quick test
    result = get_answer("How do I file a patent at IIT Bombay?")
    print("ANSWER:")
    print(result["answer"])
    print("\nSOURCES:")
    for s in result["sources"]:
        print(f"  [{s['category']}] {s['file']} (relevance: {s['relevance']})")
