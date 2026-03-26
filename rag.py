"""RAG pipeline: retrieve context → build prompt → stream from Groq."""

import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
import streamlit as st

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

STAGE-BASED GUIDANCE:
1. IDEA STAGE: DSSE foundation courses, E-Cell events, Eureka, ideation workshops
2. VALIDATION: DSSE specialist courses, E-Cell mentorship, IDEAS pre-incubation, relevant professors
3. PROTOTYPE: Tinkerers' Lab (24/7, 3D printers), MakerSpace, NIDHI PRAYAS (up to Rs 10L)
4. EARLY STARTUP: SINE incubation (3yr support), IoE-SINE seed fund (Rs 50L), Startup Policy, Deferred Placement
5. SCALING: SINE Rs 100Cr fund, BIRAC BIG (Rs 50L biotech), ASPIRE Research Park, govt schemes

RULES:
1. ONLY answer based on the provided context. If missing, say so and suggest where to check.
2. Include: what each resource is, who it's for, how to access it.
3. Use markdown: headers, bullets, bold for key terms.
4. End with clear "Next Steps" when appropriate.
5. Stay focused on IIT Bombay's innovation ecosystem."""


@st.cache_resource(show_spinner=False)
def load_embedding_model():
    """Load and cache the embedding model at startup."""
    return SentenceTransformer(EMBEDDING_MODEL)


@st.cache_resource(show_spinner=False)
def load_collection():
    """Load and cache the ChromaDB collection."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_collection(COLLECTION_NAME)


def get_groq_client():
    """Get Groq client."""
    return Groq(api_key=GROQ_API_KEY)


def retrieve_context(query: str) -> list[dict]:
    """Embed query and retrieve top-K relevant chunks."""
    model = load_embedding_model()
    collection = load_collection()

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


def build_messages(query: str, contexts: list[dict], history: list[dict]) -> list[dict]:
    """Build message list for Groq chat API."""
    context_parts = []
    for i, ctx in enumerate(contexts, 1):
        context_parts.append(
            f"[Context {i} — {ctx['category']} — {ctx['source_file']}]\n{ctx['text']}"
        )
    context_str = "\n\n".join(context_parts)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    recent_history = history[-8:] if len(history) > 8 else history
    for msg in recent_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({
        "role": "user",
        "content": f"CONTEXT FROM KNOWLEDGE BASE:\n{context_str}\n\nSTUDENT'S QUESTION: {query}\n\nProvide a helpful, practical answer with specific next steps."
    })

    return messages


def stream_answer(query: str, history: list[dict] | None = None):
    """Stream answer from Groq for instant response feel."""
    if history is None:
        history = []

    contexts = retrieve_context(query)
    messages = build_messages(query, contexts, history)

    client = get_groq_client()
    raw_stream = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=2000,
        stream=True,
    )

    # Wrap to yield plain strings (required by st.write_stream)
    def text_stream():
        for chunk in raw_stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    # Extract sources
    sources = []
    seen = set()
    for ctx in contexts:
        key = ctx["source_file"]
        if key not in seen:
            seen.add(key)
            sources.append({
                "file": ctx["source_file"],
                "category": ctx["category"],
                "url": ctx["source_url"],
            })

    return text_stream(), sources
