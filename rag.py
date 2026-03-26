"""RAG pipeline: retrieve context → build prompt → call Groq LLM → return answer."""

import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL,
    GROQ_API_KEY, GROQ_MODEL, TOP_K,
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
- IIT Bombay Faculty (869+ professors) — recommend professors whose research areas match the student's startup domain

PROFESSOR RECOMMENDATIONS:
When a student describes their idea or domain, ALWAYS recommend relevant IIT Bombay professors from the context:
- Match professors by their research areas/specializations to the student's idea domain
- Include the professor's name, department, email, and research areas
- Explain WHY this professor is relevant to their specific idea
- Suggest 2-5 relevant professors when possible
- Advise students on how to approach a professor: send a concise email, mention how their research connects to the idea, ask for mentorship/guidance
- Having a faculty advisor strengthens SINE incubation applications

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
7. Use markdown formatting for readability (headers, bullets, bold for key terms).

IMPORTANT: You are NOT a general-purpose AI. You specifically help IIT Bombay students with innovation and entrepreneurship resources. Stay focused on this domain."""


# Module-level singletons
_embedding_model = None
_collection = None
_groq_client = None


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


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


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
                "relevance": 1 - dist,
            })

    return contexts


def get_answer(query: str, history: list[dict] | None = None) -> dict:
    """Full RAG pipeline: retrieve → prompt → Groq → answer."""
    if history is None:
        history = []

    # Retrieve relevant context
    contexts = retrieve_context(query)

    # Format context
    context_parts = []
    for i, ctx in enumerate(contexts, 1):
        context_parts.append(
            f"[Context {i} — {ctx['category']} — {ctx['source_file']}]\n{ctx['text']}"
        )
    context_str = "\n\n".join(context_parts)

    # Format history (last 4 exchanges)
    recent_history = history[-8:] if len(history) > 8 else history

    # Build messages for Groq chat API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in recent_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    user_message = f"""CONTEXT FROM KNOWLEDGE BASE:
{context_str}

STUDENT'S QUESTION: {query}

Provide a helpful, practical answer with specific next steps."""

    messages.append({"role": "user", "content": user_message})

    # Call Groq (blazing fast)
    client = _get_groq_client()
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Sorry, something went wrong: {str(e)[:100]}. Please try again."

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
