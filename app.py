import base64
import requests
import streamlit as st

# ── Page Config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Titanic QA Bot 🚢",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://localhost:8000"

# ── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root variables ────────────────────── */
:root {
    --bg-primary: #0a0a1a;
    --bg-secondary: #1a1a2e;
    --bg-card: #16213e;
    --accent-primary: #e94560;
    --accent-secondary: #0f3460;
    --accent-tertiary: #533483;
    --text-primary: #e8e8f0;
    --text-secondary: #a0a0c0;
    --gradient-1: linear-gradient(135deg, #e94560, #533483);
    --gradient-2: linear-gradient(135deg, #0f3460, #533483);
    --glass: rgba(26, 26, 46, 0.7);
}

/* ── Global ────────────────────────────── */
.stApp {
    background: var(--bg-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Header ────────────────────────────── */
.hero-header {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    background: linear-gradient(180deg, rgba(233,69,96,0.12) 0%, transparent 100%);
    border-bottom: 1px solid rgba(233,69,96,0.15);
    margin-bottom: 1.5rem;
}
.hero-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem;
}
.hero-header p {
    color: var(--text-secondary);
    font-size: 1.05rem;
    margin: 0;
}

/* ── Chat messages ─────────────────────── */
.stChatMessage {
    background: var(--bg-secondary) !important;
    border: 1px solid rgba(233,69,96,0.1) !important;
    border-radius: 16px !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem !important;
    backdrop-filter: blur(10px);
}
[data-testid="stChatMessageContent"] p {
    color: var(--text-primary) !important;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* ── Sidebar ───────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid rgba(233,69,96,0.15) !important;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    color: var(--text-secondary) !important;
}

/* ── Example question buttons ──────────── */
.example-btn {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    background: var(--bg-card);
    border: 1px solid rgba(233,69,96,0.2);
    border-radius: 12px;
    color: var(--text-primary);
    font-size: 0.88rem;
    text-align: left;
    cursor: pointer;
    transition: all 0.25s ease;
}
.example-btn:hover {
    background: rgba(233,69,96,0.15);
    border-color: var(--accent-primary);
    transform: translateX(4px);
}

/* ── Chat input ────────────────────────── */
[data-testid="stChatInput"] textarea {
    background: var(--bg-secondary) !important;
    border: 1px solid rgba(233,69,96,0.25) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(233,69,96,0.15) !important;
}

/* ── Buttons ───────────────────────────── */
.stButton > button {
    background: var(--bg-card) !important;
    border: 1px solid rgba(233,69,96,0.25) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    transition: all 0.25s ease !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: rgba(233,69,96,0.18) !important;
    border-color: var(--accent-primary) !important;
    transform: translateY(-1px) !important;
}

/* ── Spinner ───────────────────────────── */
.stSpinner > div {
    border-top-color: var(--accent-primary) !important;
}

/* ── Scrollbar ─────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent-secondary); border-radius: 3px; }

/* ── Image (chart) cards ───────────────── */
[data-testid="stImage"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(233,69,96,0.15);
}

/* ── Metric cards in sidebar ───────────── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid rgba(233,69,96,0.15);
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
    text-align: center;
}
.metric-card .value {
    font-size: 1.8rem;
    font-weight: 700;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-card .label {
    color: var(--text-secondary);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

/* ── Status badge ──────────────────────── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
}
.status-online {
    background: rgba(0,180,100,0.15);
    color: #00b464;
    border: 1px solid rgba(0,180,100,0.3);
}
.status-offline {
    background: rgba(233,69,96,0.15);
    color: #e94560;
    border: 1px solid rgba(233,69,96,0.3);
}
</style>
""", unsafe_allow_html=True)


# ── Session State ───────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ── Helper Functions ────────────────────────────────────────────

def check_backend_health() -> dict | None:
    """Ping the backend health endpoint."""
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        return r.json() if r.ok else None
    except Exception:
        return None


def ask_question(question: str) -> dict:
    """Send a question to the backend and return the response."""
    try:
        r = requests.post(
            f"{BACKEND_URL}/chat",
            json={"question": question},
            timeout=120,
        )
        if r.ok:
            return r.json()
        else:
            return {"answer": f"❌ Backend error ({r.status_code}): {r.text}", "chart": None}
    except requests.ConnectionError:
        return {"answer": "❌ Cannot connect to the backend. Make sure `uvicorn backend:app --port 8000` is running.", "chart": None}
    except Exception as e:
        return {"answer": f"❌ Error: {str(e)}", "chart": None}


# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚢 Titanic QA Bot")

    # Backend status
    health = check_backend_health()
    if health:
        st.markdown(
            '<div class="status-badge status-online">● Backend Online</div>',
            unsafe_allow_html=True,
        )
        # Dataset metrics
        cols = st.columns(2)
        with cols[0]:
            st.markdown(
                f'<div class="metric-card"><div class="value">{health["rows"]}</div><div class="label">Passengers</div></div>',
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.markdown(
                f'<div class="metric-card"><div class="value">{len(health["columns"])}</div><div class="label">Features</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="status-badge status-offline">● Backend Offline</div>',
            unsafe_allow_html=True,
        )
        st.info("Start the backend with:\n```\nuvicorn backend:app --port 8000\n```")

    st.markdown("---")
    st.markdown("### 💡 Try These Questions")

    example_questions = [
        "What percentage of passengers were male on the Titanic?",
        "Show me a histogram of passenger ages",
        "What was the average ticket fare?",
        "How many passengers embarked from each port?",
        "What was the survival rate by passenger class?",
        "Show me a bar chart of survival by gender",
        "What was the most common age group?",
        "How many children (age < 12) survived?",
    ]

    for q in example_questions:
        if st.button(q, key=f"ex_{hash(q)}", use_container_width=True):
            st.session_state.pending_question = q

    st.markdown("---")
    st.markdown("### 📊 Available Columns")
    if health:
        for col in health["columns"]:
            st.markdown(f"- `{col}`")
    else:
        st.markdown("_Connect to backend to see columns_")

    st.markdown("---")
    st.caption("Built with FastAPI · LangChain · Streamlit")


# ── Main Content ────────────────────────────────────────────────

# Hero header
st.markdown("""
<div class="hero-header">
    <h1>🚢 Titanic Dataset Explorer</h1>
    <p>Ask anything about the Titanic passengers — get answers & visualizations instantly</p>
</div>
""", unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("chart"):
            chart_bytes = base64.b64decode(msg["chart"])
            st.image(chart_bytes, use_container_width=True)

# Handle pending question from sidebar buttons
if st.session_state.pending_question:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = None
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing the Titanic dataset..."):
            response = ask_question(prompt)
        st.markdown(response["answer"])
        if response.get("chart"):
            chart_bytes = base64.b64decode(response["chart"])
            st.image(chart_bytes, use_container_width=True)
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["answer"],
        "chart": response.get("chart"),
    })
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask a question about the Titanic dataset..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing the Titanic dataset..."):
            response = ask_question(prompt)
        st.markdown(response["answer"])
        if response.get("chart"):
            chart_bytes = base64.b64decode(response["chart"])
            st.image(chart_bytes, use_container_width=True)

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["answer"],
        "chart": response.get("chart"),
    })
