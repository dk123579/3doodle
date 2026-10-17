# 3doodle

3doodle is a Foundry-agent scaffold that combines:

- A React UI for multiturn chat
- A Python API scaffold for agent orchestration
- Downloadable `.3mf` generation (minimal valid package)
- Simulated 3D model preview driven by generated metadata

## Structure

- `src/` React frontend
- `backend/app/main.py` API endpoints for chat, design generation, and file download
- `backend/app/three_mf.py` minimal slicer-ready `.3mf` package generator
- `.vscode/` local debug config for backend agent work

## Run Local

Frontend:

```bash
npm install
npm run dev
```

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:5173.

## Foundry Integration Next Step

The backend is intentionally scaffolded with deterministic placeholders. To connect to Foundry:

1. Copy `backend/.env.example` to `backend/.env`.
2. Add your Foundry project endpoint and model deployment.
3. Replace placeholder chat and geometry planning logic in `backend/app/main.py` with a real Foundry model/tool invocation.

## GitHub Repo Setup

If GitHub CLI is authenticated:

```bash
git init
git add .
git commit -m "Initial 3doodle scaffold"
gh repo create 3doodle --public --source . --remote origin --push
```
