"""IITB Innovation Chatbot — Professional Streamlit App"""

import streamlit as st
import os

# Ensure env vars are set for Streamlit Cloud
if not os.getenv("GROQ_API_KEY"):
    try:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

# Page config — must be first
st.set_page_config(
    page_title="IITB Innovation Chatbot",
    page_icon="💡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Professional CSS with animations ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --iitb-blue: #00529b;
        --iitb-dark: #003366;
        --iitb-gold: #f5a623;
        --bg-primary: #f8fafc;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --border: #e2e8f0;
    }

    .stApp { font-family: 'Inter', -apple-system, sans-serif !important; }
    .block-container { max-width: 800px !important; padding-top: 0 !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu, footer { display: none !important; }

    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .hero-banner {
        background: linear-gradient(135deg, #00529b 0%, #003366 50%, #001d3d 100%);
        background-size: 200% 200%;
        animation: gradientFlow 8s ease infinite, slideDown 0.6s ease-out;
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin: 0.5rem 0 1.5rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%; right: -20%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(245,166,35,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-content {
        display: flex; align-items: center; gap: 16px;
        position: relative; z-index: 1;
    }
    .hero-logo {
        width: 56px; height: 56px;
        background: linear-gradient(135deg, #f5a623, #e8951a);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 18px; color: #003366;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(245,166,35,0.3);
    }
    .hero-text h1 { margin: 0; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; }
    .hero-text p { margin: 2px 0 0; font-size: 0.85rem; opacity: 0.8; }
    .hero-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.12);
        padding: 4px 12px; border-radius: 20px;
        font-size: 0.72rem; margin-top: 8px; font-weight: 500;
    }
    .hero-badge .dot {
        width: 6px; height: 6px;
        background: #4ade80; border-radius: 50%;
        animation: pulse 2s ease infinite;
    }

    .welcome-card {
        text-align: center;
        padding: 2rem 1.5rem 1rem;
        animation: slideUp 0.5s ease-out 0.2s both;
    }
    .welcome-card h2 { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem; }
    .welcome-card p { color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; max-width: 500px; margin: 0 auto 1.5rem; }
    .welcome-features {
        display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-bottom: 1.5rem;
    }
    .feature-chip {
        display: inline-flex; align-items: center; gap: 6px;
        background: white; border: 1px solid var(--border);
        padding: 5px 12px; border-radius: 20px;
        font-size: 0.78rem; color: var(--text-secondary); font-weight: 500;
    }

    div[data-testid="stVerticalBlock"] > div > div > .stButton > button {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: var(--iitb-blue) !important;
        background: white !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stVerticalBlock"] > div > div > .stButton > button:hover {
        border-color: var(--iitb-blue) !important;
        background: #f0f7ff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07) !important;
    }

    .stChatMessage { animation: scaleIn 0.3s ease-out; }

    .source-tag {
        display: inline-block;
        background: linear-gradient(135deg, #e8f0fe, #dbeafe);
        color: var(--iitb-blue);
        padding: 3px 10px; border-radius: 6px;
        font-size: 0.72rem; font-weight: 600;
        margin: 2px 4px 2px 0;
    }
    .source-file { font-size: 0.8rem; color: var(--text-secondary); }

    .app-footer {
        text-align: center; padding: 0.5rem;
        font-size: 0.72rem; color: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="hero-banner">
    <div class="hero-content">
        <div class="hero-logo">IIC</div>
        <div class="hero-text">
            <h1>IITB Innovation Chatbot</h1>
            <p>Institution's Innovation Council, IIT Bombay</p>
            <div class="hero-badge">
                <span class="dot"></span>
                869 Professors &bull; 2400+ Knowledge Sources &bull; Powered by AI
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Load models once ──
from rag import load_embedding_model, load_collection, stream_answer

with st.spinner("⚡ Loading knowledge base..."):
    load_embedding_model()
    load_collection()

# ── Session state ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ── Welcome screen (only if no messages) ──
if not st.session_state.messages and not st.session_state.pending_query:
    st.markdown("""
    <div class="welcome-card">
        <h2>How can I help you innovate?</h2>
        <p>Ask me anything about IIT Bombay's innovation ecosystem — I'll find the right courses, labs, funding, professors, and resources for your idea.</p>
        <div class="welcome-features">
            <span class="feature-chip">🎓 869+ Professors</span>
            <span class="feature-chip">🔬 Labs & MakerSpaces</span>
            <span class="feature-chip">💰 Funding Schemes</span>
            <span class="feature-chip">🚀 SINE Incubation</span>
            <span class="feature-chip">📜 Patent & IP</span>
            <span class="feature-chip">📚 20+ Courses</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    starters = [
        ("💡", "I have a startup idea — where do I start?"),
        ("🎓", "What entrepreneurship courses does DSSE offer?"),
        ("🤖", "AI healthcare startup — which professors can help?"),
        ("🔧", "How can I use Tinkerers' Lab for prototyping?"),
        ("📜", "How do I file a patent at IIT Bombay?"),
        ("💰", "What funding is available for early-stage startups?"),
    ]

    cols = st.columns(2)
    for i, (icon, q) in enumerate(starters):
        if cols[i % 2].button(f"{icon}  {q}", key=f"s_{i}", use_container_width=True):
            st.session_state.pending_query = q
            st.rerun()

# ── Display chat history ──
for msg in st.session_state.messages:
    avatar = "💡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            with st.expander(f"📎 {len(msg['sources'])} sources referenced"):
                for src in msg["sources"]:
                    tag = f'<span class="source-tag">{src["category"]}</span>'
                    name = f'<span class="source-file">{src["file"]}</span>'
                    st.markdown(f"{tag} {name}", unsafe_allow_html=True)

# ── Handle pending query from starter buttons ──
query = st.session_state.pending_query
st.session_state.pending_query = None

# ── Chat input ──
if chat_input := st.chat_input("Ask about courses, labs, funding, patents, professors..."):
    query = chat_input

# ── Process query ──
if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user", avatar="👤"):
        st.markdown(query)

    with st.chat_message("assistant", avatar="💡"):
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]

        stream, sources = stream_answer(query, history)
        response = st.write_stream(stream)

        if sources:
            with st.expander(f"📎 {len(sources)} sources referenced"):
                for src in sources:
                    tag = f'<span class="source-tag">{src["category"]}</span>'
                    name = f'<span class="source-file">{src["file"]}</span>'
                    st.markdown(f"{tag} {name}", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "sources": sources,
    })

# ── Footer ──
st.markdown("""
<div class="app-footer">
    Powered by IIC, IIT Bombay &bull; AI-generated answers — verify important details with the relevant office
</div>
""", unsafe_allow_html=True)
