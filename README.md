# Ask Talal — v3 (Dark Editorial)

Same login + admin-dashboard backend as v2, with a redesigned frontend:
dark editorial theme (near-black background, violet/cyan accent, monospace
labels, restrained motion) plus a "Selected work" section on the homepage.

## Structure
- `backend/` — FastAPI + Groq LLM + SQLite (visitors + messages), unchanged from v2
- `frontend/` — source frontend files (new design)
- `docs/` — copy of frontend for GitHub Pages

## Setup
Same as v2 — see backend/.env.example for required env vars (GROQ_API_KEY, ADMIN_KEY).

1. `cd backend && pip install -r requirements.txt`
2. Copy `.env.example` to `.env`, fill in your keys
3. `uvicorn main:app --reload`
4. Serve `frontend/` locally (e.g. `python -m http.server 5500` inside frontend/) — don't open index.html directly
5. Update `BACKEND_URL` in script.js once backend is deployed

## Deployment
- Backend: Railway (root dir = backend, env vars GROQ_API_KEY + ADMIN_KEY)
- Frontend: GitHub Pages from /docs folder on main branch
