import os
import sqlite3
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from knowledge_base import TALAL_KNOWLEDGE_BASE

load_dotenv()

app = FastAPI(title="Ask Talal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your real frontend domain once deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file.")

# Simple shared secret so only you can view the admin dashboard.
# Change this in your .env file (ADMIN_KEY=something-only-you-know)
ADMIN_KEY = os.getenv("ADMIN_KEY", "changeme")

client = Groq(api_key=GROQ_API_KEY)

DB_PATH = os.path.join(os.path.dirname(__file__), "ask_talal.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()

SYSTEM_PROMPT = f"""You are "Ask Talal" — an AI agent that answers questions on behalf of Talal Noor,
a BS Artificial Intelligence student and AI/ML engineer. You speak in first person AS Talal,
in a friendly, confident, concise tone. Only answer using the facts provided below. If asked
something outside this knowledge, politely say you don't have that info and suggest they reach
out to Talal directly.

KNOWLEDGE BASE ABOUT TALAL:
{TALAL_KNOWLEDGE_BASE}

Rules:
- Keep answers punchy and precise, not verbose.
- Speak in first person ("I built...", "I'm currently...").
- Never make up projects, skills, or experience not listed above.
- If asked for contact info, direct them to the site's contact/GitHub links.
"""


# ---------- Models ----------

class LoginRequest(BaseModel):
    name: str
    email: str


class LoginResponse(BaseModel):
    visitor_id: str
    name: str


class ChatRequest(BaseModel):
    visitor_id: str
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str


# ---------- Routes ----------

@app.get("/")
def root():
    return {"status": "Ask Talal API is running"}


@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    name = req.name.strip()
    email = req.email.strip()
    if not name or not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid name and email.")

    visitor_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO visitors (id, name, email, created_at) VALUES (?, ?, ?, ?)",
        (visitor_id, name, email, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()

    return LoginResponse(visitor_id=visitor_id, name=name)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Verify visitor exists
    conn = get_db()
    visitor = conn.execute("SELECT * FROM visitors WHERE id = ?", (req.visitor_id,)).fetchone()
    if not visitor:
        conn.close()
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in req.history[-10:]:
        if turn.get("role") in ("user", "assistant") and turn.get("content"):
            messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": req.message})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.6,
            max_tokens=500,
        )
        reply = completion.choices[0].message.content

        # Log both sides of the conversation
        now = datetime.utcnow().isoformat()
        conn.execute(
            "INSERT INTO messages (visitor_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (req.visitor_id, "user", req.message, now),
        )
        conn.execute(
            "INSERT INTO messages (visitor_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (req.visitor_id, "assistant", reply, now),
        )
        conn.commit()
        conn.close()

        return ChatResponse(reply=reply)
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/admin/visitors")
def admin_visitors(key: str):
    """Private dashboard data. Visit /admin/visitors?key=YOUR_ADMIN_KEY to view.
    Set ADMIN_KEY in your .env to something only you know."""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")

    conn = get_db()
    visitors = conn.execute("SELECT * FROM visitors ORDER BY created_at DESC").fetchall()
    result = []
    for v in visitors:
        messages = conn.execute(
            "SELECT role, content, created_at FROM messages WHERE visitor_id = ? ORDER BY created_at ASC",
            (v["id"],),
        ).fetchall()
        result.append({
            "name": v["name"],
            "email": v["email"],
            "visited_at": v["created_at"],
            "messages": [dict(m) for m in messages],
        })
    conn.close()
    return {"visitors": result}
