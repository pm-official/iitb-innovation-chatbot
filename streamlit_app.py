"""IITB Innovation Chatbot — Streamlit App"""

import streamlit as st
from rag import get_answer

# Page config
st.set_page_config(
    page_title="IITB Innovation Chatbot",
    page_icon="💡",
    layout="centered",
)

# Custom CSS
st.markdown("""
<style>
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #00529b, #003d75);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .main-header .logo-circle {
        width: 50px; height: 50px;
        background: #f5a623;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 16px; color: #003d75;
        flex-shrink: 0;
    }
    .main-header h1 { margin: 0; font-size: 1.4rem; }
    .main-header p { margin: 0; font-size: 0.85rem; opacity: 0.85; }

    /* Source badges */
    .source-badge {
        display: inline-block;
        background: #e8f0fe;
        color: #00529b;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin: 2px 3px;
        font-weight: 500;
    }

    /* Chat input styling */
    .stChatInput > div { border-radius: 12px !important; }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Starter buttons */
    .starter-container { display: flex; flex-wrap: wrap; gap: 8px; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="logo-circle">IIC</div>
    <div>
        <h1>IITB Innovation Chatbot</h1>
        <p>Institution's Innovation Council, IIT Bombay</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show starter questions if no messages yet
if not st.session_state.messages:
    st.markdown("#### Ask me anything about IIT Bombay's innovation ecosystem")
    st.markdown("Courses, labs, funding, incubation, patents, professors — I've got you covered.")

    cols = st.columns(2)
    starters = [
        "What courses does DSSE offer for entrepreneurship?",
        "How do I file a patent at IIT Bombay?",
        "I have a startup idea — where do I start?",
        "What funding is available for my prototype?",
        "Tell me about SINE incubation",
        "I want to build an AI healthcare startup. Which professors can help?",
    ]
    for i, q in enumerate(starters):
        if cols[i % 2].button(q, key=f"starter_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="💡" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

        # Show sources for assistant messages
        if msg["role"] == "assistant" and "sources" in msg:
            with st.expander(f"📎 {len(msg['sources'])} sources"):
                for src in msg["sources"]:
                    badge = f'<span class="source-badge">{src["category"]}</span>'
                    if src.get("url"):
                        st.markdown(f'{badge} [{src["file"]}]({src["url"]})', unsafe_allow_html=True)
                    else:
                        st.markdown(f'{badge} {src["file"]}', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask about courses, labs, funding, patents, professors..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant", avatar="💡"):
        with st.spinner("Thinking..."):
            # Build history for context
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]  # exclude current query
            ]
            result = get_answer(prompt, history)

        st.markdown(result["answer"])

        # Show sources
        if result["sources"]:
            with st.expander(f"📎 {len(result['sources'])} sources"):
                for src in result["sources"]:
                    badge = f'<span class="source-badge">{src["category"]}</span>'
                    if src.get("url"):
                        st.markdown(f'{badge} [{src["file"]}]({src["url"]})', unsafe_allow_html=True)
                    else:
                        st.markdown(f'{badge} {src["file"]}', unsafe_allow_html=True)

    # Save assistant response with sources
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
