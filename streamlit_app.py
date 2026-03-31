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

    /* ── Floating Feedback Button ── */
    .floating-feedback {
        position: fixed;
        bottom: 90px;
        right: 28px;
        z-index: 9999;
        animation: slideUp 0.6s ease-out 1s both;
    }
    .floating-feedback a {
        display: flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, var(--iitb-blue), #003d7a);
        color: white !important;
        text-decoration: none !important;
        padding: 12px 20px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 15px rgba(0,82,155,0.35);
        transition: all 0.3s ease;
    }
    .floating-feedback a:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(0,82,155,0.45);
        background: linear-gradient(135deg, #0066cc, var(--iitb-blue));
    }
    .feedback-icon {
        font-size: 1.1rem;
        animation: pulse 2s ease infinite;
    }

    /* ── Inline Feedback (thumbs) ── */
    .inline-feedback {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 8px;
        padding: 6px 0;
    }
    .inline-feedback span.label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        font-weight: 500;
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
                818 Professors &bull; 3200+ Courses &bull; 19 Knowledge Categories &bull; Powered by AI
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Load models once ──
from rag import load_collection, stream_answer

with st.spinner("⚡ Loading knowledge base..."):
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
            <span class="feature-chip">🎓 818 Professors</span>
            <span class="feature-chip">📚 3200+ Courses</span>
            <span class="feature-chip">🔬 Labs & MakerSpaces</span>
            <span class="feature-chip">💰 Funding Schemes</span>
            <span class="feature-chip">🚀 SINE Incubation</span>
            <span class="feature-chip">📜 Patent & IP</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    starters = [
        ("💡", "I have a startup idea in AI. How do I start? Give me the full process."),
        ("🎓", "What courses should I take for an EdTech startup?"),
        ("🤖", "I want to build a healthcare startup — which professors and courses can help?"),
        ("🔍", "How do I do customer discovery for my startup idea?"),
        ("📜", "How do I file a patent at IIT Bombay?"),
        ("💰", "What funding and incubation support is available at IIT Bombay?"),
    ]

    cols = st.columns(2)
    for i, (icon, q) in enumerate(starters):
        if cols[i % 2].button(f"{icon}  {q}", key=f"s_{i}", use_container_width=True):
            st.session_state.pending_query = q
            st.rerun()

# ── Feedback state ──
if "feedback" not in st.session_state:
    st.session_state.feedback = {}  # msg_index -> "up" or "down"

FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe-CYwCXVW00JxGJekeHrXqr9oCl9mLguuXAD-XtaAd08nokQ/viewform"

# ── Display chat history ──
for idx, msg in enumerate(st.session_state.messages):
    avatar = "💡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if "sources" in msg and msg["sources"]:
                with st.expander(f"📎 {len(msg['sources'])} sources referenced"):
                    for src in msg["sources"]:
                        tag = f'<span class="source-tag">{src["category"]}</span>'
                        name = f'<span class="source-file">{src["file"]}</span>'
                        st.markdown(f"{tag} {name}", unsafe_allow_html=True)
            # Inline thumbs feedback
            fb_key = f"fb_{idx}"
            existing = st.session_state.feedback.get(fb_key)
            if existing:
                if existing == "up":
                    st.markdown('<div class="inline-feedback"><span class="label">Thanks for the feedback!</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="inline-feedback"><span class="label">Thanks! We\'ll improve.</span></div>', unsafe_allow_html=True)
            else:
                col1, col2, col3 = st.columns([0.18, 0.18, 0.64])
                with col1:
                    if st.button("👍 Helpful", key=f"up_{idx}", use_container_width=True):
                        st.session_state.feedback[fb_key] = "up"
                        st.rerun()
                with col2:
                    if st.button("👎 Not helpful", key=f"dn_{idx}", use_container_width=True):
                        st.session_state.feedback[fb_key] = "down"
                        st.rerun()

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

# ── Floating Feedback Button ──
st.markdown(f"""
<div class="floating-feedback">
    <a href="{FEEDBACK_FORM_URL}" target="_blank" rel="noopener noreferrer">
        <span class="feedback-icon">💬</span>
        Give Feedback
    </a>
</div>
""", unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div class="app-footer">
    Powered by IIC, IIT Bombay &bull; AI-generated answers — verify important details with the relevant office
</div>
""", unsafe_allow_html=True)
