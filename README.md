# Ask Talal — Personal AI Agent (v2)

An AI agent that answers questions about Talal Noor's projects, skills, and
experience — now with visitor login (lead capture), suggested question chips,
a typing indicator, and a refreshed gradient UI.

## What's new in v2
- **Login before chat**: visitors enter name + email (no password) so Talal knows who visited
- **Private admin dashboard**: see every visitor and their full conversation at `/admin/visitors?key=YOUR_ADMIN_KEY`
- **Suggested question chips**: one-tap starter questions
- **Typing indicator**: animated dots while the agent is "thinking"
- **Refreshed UI**: purple/blue gradient accent theme, glow background, rounded chat bubbles

## Structure
- `backend/` — FastAPI + Groq LLM + SQLite (visitors + messages)
- `frontend/` — source frontend files
- `docs/` — copy of frontend, used for GitHub Pages (must be named `docs` for GitHub Pages support)

## Setup

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`, fill in:
   - `GROQ_API_KEY` — from console.groq.com
   - `ADMIN_KEY` — any secret word only you know, used to view your visitor dashboard
4. `uvicorn main:app --reload`
5. Runs at http://localhost:8000
6. A `ask_talal.db` SQLite file is created automatically on first run — this stores visitors + messages

### Frontend
1. Open `frontend/index.html` via a local server (e.g. `python -m http.server 5500` inside `frontend/`)
   — do NOT double-click it directly, browsers block API calls from `file://` pages
2. Set `BACKEND_URL` in `frontend/script.js` to match your backend

### Viewing who visited (admin dashboard)
Once deployed, visit:
```
https://your-backend-url/admin/visitors?key=YOUR_ADMIN_KEY
```
This returns JSON with every visitor's name, email, visit time, and full conversation.
(Optional: you can later wrap this in a small HTML page for a nicer view.)

## Deployment
- Backend: Railway (root dir = `backend`, add GROQ_API_KEY + ADMIN_KEY env vars)
- Frontend: GitHub Pages, serving from the `docs/` folder on the `main` branch
- After deploying backend, update `BACKEND_URL` in BOTH `frontend/script.js` AND `docs/script.js`, then push

## Editing the agent's knowledge
Edit `backend/knowledge_base.py` — the agent only answers from what's written there.
