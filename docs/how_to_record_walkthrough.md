# How to Record a Walkthrough

This guide explains how to run the project locally and record a short demo video showcasing the system. It focuses on local development (no Docker required).

## Requirements

- Node.js 18+ and npm
- Python 3.11+
- A browser (Chrome/Firefox)
- Screen recording tool (OBS Studio, QuickTime, or similar)

## Preparation

1. Pull the latest code and ensure tests pass:

```bash
git pull origin main
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ../scripts/create_db.py
pytest -q

# Frontend
cd ../frontend
npm install
npm run build # optional test build step
```

2. Open two terminals for backend and frontend.

## Run the app locally

### Start backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Start frontend

```bash
cd frontend
npm run dev
```

- App: http://localhost:5173 (or port printed by Vite)

## What to record (recommended ~3–6 minutes)

1. Title slide (5–10s): project name, author, and short goal.
2. 0:10–0:40 — Quick architecture overview (1–2 sentences).
3. 0:40–1:30 — Create a wall (5m × 5m) with the default obstacles and explain parameters (spacing, clearance).
4. 1:30–2:30 — Generate Zigzag plan, play the visualization at 1x and 5x, show quick-jump.
5. 2:30–3:30 — Regenerate with Spiral pattern, show aesthetics and (if chosen) tight spacing for full coverage.
6. 3:30–4:00 — Open API docs and show a sample `POST /v1/trajectories/walls/{id}/plan` request and response (briefly).
7. 4:00–4:30 — Mention tests and show `pytest` passing (short clip)
8. Closing slide (10s): next steps and where to find repository + contact info.

## Recording tips

- Use 1920×1080 resolution, 30fps
- Keep narration concise and speak through the key steps
- Highlight cursor/areas with zoom or pointer for clarity
- If you want to pause while the path generates, use the playback controls in the app

## Exporting

- Export MP4 (H.264) for compatibility
- Keep video under 10 minutes

## Submitting

- Upload the video to a private link (Google Drive / YouTube unlisted) and add the link to `SUBMISSION.md` in the repo root.


---

This guide ensures the reviewer can reproduce the demo locally and follow along in the video without needing container or cloud deployment instructions.
