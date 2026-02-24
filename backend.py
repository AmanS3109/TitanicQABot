import os
import io
import re
import base64
import traceback
from contextlib import contextmanager

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend — no GUI
import matplotlib.pyplot as plt
import seaborn as sns

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# ── Env & Config ────────────────────────────────────────────────
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "titanic.csv")

# ── Load Dataset ────────────────────────────────────────────────
if not os.path.exists(DATA_PATH):
    # Auto-bootstrap if missing
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df = sns.load_dataset("titanic")
    df.to_csv(DATA_PATH, index=False)
else:
    df = pd.read_csv(DATA_PATH)

DATASET_INFO = f"""Dataset: Titanic passengers ({len(df)} rows, {len(df.columns)} columns)
Columns: {', '.join(df.columns.tolist())}
Dtypes:
{df.dtypes.to_string()}

Sample (first 3 rows):
{df.head(3).to_string()}
"""

# ── FastAPI App ─────────────────────────────────────────────────
app = FastAPI(title="Titanic QA Bot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    chart: str | None = None  # base64-encoded PNG, or null


# ── Chart-capture helper ────────────────────────────────────────

@contextmanager
def capture_charts():
    """
    Context manager that monkey-patches plt.show() and plt.savefig()
    so any chart the agent creates is captured into an in-memory buffer.
    Yields a list that will contain 0 or 1 base64 PNG strings on exit.
    """
    charts: list[str] = []
    _original_show = plt.show
    _original_savefig = plt.savefig

    def _fake_show(*args, **kwargs):
        buf = io.BytesIO()
        plt.gcf().savefig(buf, format="png", dpi=150, bbox_inches="tight",
                          facecolor="#1a1a2e", edgecolor="none")
        buf.seek(0)
        charts.append(base64.b64encode(buf.read()).decode())
        plt.close("all")

    def _fake_savefig(*args, **kwargs):
        _fake_show()

    plt.show = _fake_show      # type: ignore[assignment]
    plt.savefig = _fake_savefig  # type: ignore[assignment]
    try:
        yield charts
    finally:
        plt.show = _original_show          # type: ignore[assignment]
        plt.savefig = _original_savefig    # type: ignore[assignment]
        plt.close("all")


# ── Agent builder ───────────────────────────────────────────────

AGENT_PREFIX = """You are an expert data analyst assistant. You have access to a Pandas DataFrame called `df` that contains the Titanic passenger dataset.

IMPORTANT RULES:
1. When the user asks for a visualization, chart, plot, histogram, or graph:
   - Use matplotlib and/or seaborn to create a beautiful chart
   - ALWAYS call plt.show() after creating the chart so it gets captured
   - Use a dark theme: set facecolor='#1a1a2e', text color='white'
   - Use vibrant colors from this palette: '#e94560', '#0f3460', '#16213e', '#533483', '#e94560', '#00b4d8', '#90e0ef'
   - Add proper titles, axis labels, and legends
   - Make the chart visually appealing with proper formatting
2. When the user asks a factual question, provide a clear, concise text answer with relevant numbers and percentages.
3. Always be precise with numbers — round to 2 decimal places.
4. If you create a chart, still provide a brief text summary of what the chart shows.

The DataFrame `df` has these columns: {columns}
""".format(columns=", ".join(df.columns.tolist()))


def build_agent():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # successor to llama3-70b-8192
        temperature=0,
        api_key=GROQ_API_KEY,
    )
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_type="tool-calling", # use standard tool calling for Groq
        prefix=AGENT_PREFIX,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
        max_iterations=15,
        return_intermediate_steps=False,
    )
    return agent


# ── Endpoints ───────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "rows": len(df), "columns": list(df.columns)}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    if not GROQ_API_KEY:
        raise HTTPException(500, "GROQ_API_KEY is not configured. Please get a free API key at console.groq.com and put it in your .env file.")

    try:
        agent = build_agent()

        with capture_charts() as charts:
            result = agent.invoke({"input": req.question})

        answer = result.get("output", str(result))
        chart_b64 = charts[0] if charts else None

        return ChatResponse(answer=answer, chart=chart_b64)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"Agent error: {str(e)}")


@app.get("/dataset-info")
async def dataset_info():
    """Return basic dataset metadata for the frontend."""
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "sample": df.head(3).to_dict(orient="records"),
    }
