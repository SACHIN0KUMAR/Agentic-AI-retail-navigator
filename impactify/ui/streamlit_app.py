# ui/streamlit_app.py
import sys
import os

# Add the project root directory to the python path
# This allows the 'from impactify.graph.graph import ...' line to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from impactify.graph.graph import build_graph

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Impactify",
    page_icon="🛒",
    layout="centered",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Root theme */
:root {
    --bg:        #0d0d0d;
    --surface:   #161616;
    --border:    #2a2a2a;
    --accent:    #00e5a0;
    --accent2:   #ff6b35;
    --text:      #f0f0f0;
    --muted:     #888;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Hero header */
.hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 3rem;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent) 0%, #00b4d8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero p {
    color: var(--muted);
    font-size: 1rem;
    margin-top: 0.4rem;
    font-weight: 300;
}

/* Cart sidebar panel */
.cart-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.cart-box h4 {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent);
    margin: 0 0 0.7rem;
}
.cart-item {
    display: flex;
    justify-content: space-between;
    font-size: 0.88rem;
    padding: 0.3rem 0;
    border-bottom: 1px solid var(--border);
    color: var(--text);
}
.cart-total {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--accent);
    text-align: right;
    margin-top: 0.6rem;
}
.cart-empty {
    color: var(--muted);
    font-size: 0.85rem;
    font-style: italic;
}

/* Chat bubbles */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
    padding: 0.5rem 0;
}
.bubble {
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 16px;
    font-size: 0.92rem;
    line-height: 1.55;
    animation: fadeUp 0.3s ease;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.bubble.bot {
    background: var(--surface);
    border: 1px solid var(--border);
    border-bottom-left-radius: 4px;
    align-self: flex-start;
    color: var(--text);
}
.bubble.user {
    background: linear-gradient(135deg, #00e5a0 0%, #00b4d8 100%);
    border-bottom-right-radius: 4px;
    align-self: flex-end;
    color: #0d0d0d;
    font-weight: 500;
}
.bubble-label {
    font-size: 0.7rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
    color: var(--muted);
}
.bubble.user .bubble-label { color: #065; text-align: right; }

/* Input area */
[data-testid="stChatInput"] textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,229,160,0.15) !important;
}

/* Status badge */
.status-badge {
    display: inline-block;
    background: rgba(0,229,160,0.1);
    border: 1px solid var(--accent);
    color: var(--accent);
    font-size: 0.72rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    margin-bottom: 1rem;
}

/* Done banner */
.done-banner {
    background: linear-gradient(135deg, #00e5a0, #00b4d8);
    color: #0d0d0d;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    text-align: center;
    padding: 1rem;
    border-radius: 12px;
    font-size: 1.1rem;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Session state init ────────────────────────────────────────────────────────
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "state" not in st.session_state:
    st.session_state.state = {
        "messages": [],
        "cart": [],
        "user_profile": {"user_id": "user_1", "pincode": "110001"},
        "store": {"id": "store_1"},
        "route": "BOSS",
        "done": False,
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "bot"/"user", "text": str}


# ─── Layout ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>IMPACTIFY</h1>
    <p>Retail Navigator — powered by Agentic AI</p>
</div>
""", unsafe_allow_html=True)

col_chat, col_cart = st.columns([2, 1], gap="large")

# ── Cart panel ─────────────────────────────────────────────────────────────────
with col_cart:
    cart = st.session_state.state.get("cart", [])
    st.markdown('<div class="cart-box">', unsafe_allow_html=True)
    st.markdown('<h4>🛒 Your Cart</h4>', unsafe_allow_html=True)

    if not cart:
        st.markdown('<div class="cart-empty">Empty — start shopping!</div>', unsafe_allow_html=True)
    else:
        total = 0
        for item in cart:
            subtotal = item.get("price", 0) * item.get("qty", 1)
            total += subtotal
            st.markdown(
                f'<div class="cart-item"><span>{item["qty"]}× {item["name"]}</span>'
                f'<span>₹{subtotal}</span></div>',
                unsafe_allow_html=True
            )
        st.markdown(f'<div class="cart-total">Total: ₹{total}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick tips
    st.markdown('<div class="cart-box">', unsafe_allow_html=True)
    st.markdown('<h4>💡 Try saying</h4>', unsafe_allow_html=True)
    tips = ["milk", "add milk 1L 2", "any offers?", "checkout"]
    for tip in tips:
        st.markdown(f'<div class="cart-item"><span style="color:#888">→</span> <span>{tip}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Chat panel ─────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown('<div class="status-badge">● Live</div>', unsafe_allow_html=True)

    # Render chat history
    chat_html = '<div class="chat-wrap">'
    if not st.session_state.chat_history:
        chat_html += '<div class="bubble bot"><div class="bubble-label">Impactify</div>Hello! Tell me what you\'d like to buy today 🛒</div>'
    for msg in st.session_state.chat_history:
        role_class = "user" if msg["role"] == "user" else "bot"
        label = "You" if msg["role"] == "user" else "Impactify"
        chat_html += f'<div class="bubble {role_class}"><div class="bubble-label">{label}</div>{msg["text"]}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # Done banner
    if st.session_state.state.get("done", False):
        st.markdown('<div class="done-banner">✅ Order complete! Thank you for shopping with Impactify.</div>', unsafe_allow_html=True)
        if st.button("🔄 Start New Session"):
            for key in ["graph", "state", "chat_history"]:
                del st.session_state[key]
            st.rerun()

    # Chat input
    if not st.session_state.state.get("done", False):
        user_input = st.chat_input("Type here... (e.g. milk, add milk 1L 2, checkout)")
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "text": user_input})

            # Update state
            st.session_state.state.setdefault("messages", []).append(
                HumanMessage(content=user_input)
            )
            st.session_state.state["last_user_message"] = user_input

            # Run graph
            with st.spinner("Thinking..."):
                updated = st.session_state.graph.invoke(st.session_state.state.copy()) # type: ignore
                if isinstance(updated, tuple):
                    updated = updated[0]
                st.session_state.state = updated

            # Get bot reply
            messages = st.session_state.state.get("messages", [])
            if messages and isinstance(messages[-1], AIMessage):
                bot_text = messages[-1].content
                st.session_state.chat_history.append({"role": "bot", "text": bot_text})

            st.rerun()