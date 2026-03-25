# Mental Health Chatbot - Project Documentation (Current)

## Repository Layout

- app.py: Thin launcher for backend/api/application.py
- backend/: Python backend package
- backend/api/: FastAPI bootstrap, dependencies, shared state, route modules
- backend/services/: Core service logic (pipeline, detection, prompting, safety, summaries)
- backend/tuning/: Prompt and model tuning controls
- backend/models/detection/: Detection model artifacts and reference files
- src/: React frontend app
- docs/: Architecture, deployment, security, privacy notes
- scripts/: Local setup and backend run scripts
- requirements.txt: Single Python dependency source
- package.json: Frontend dependency source and scripts

## Python Dependencies

Only one requirements file is used:

- requirements.txt

Install with:

- pip install -r requirements.txt

## Run Locally

1. Copy .env.example to .env and set values.
2. Install Python dependencies: pip install -r requirements.txt
3. Install frontend dependencies: npm install
4. Run backend: python app.py
5. Run frontend: npm run dev

## Local + Colab Hybrid

- Use LLM_MODE=remote and LLM_API_URL for Colab-hosted LLM.
- Use LLM_MODE=local and LLM_LOCAL_MODEL_PATH for local model inference.
- Use ASR_WS_URL and VITE_ASR_WS_URL for Colab ASR websocket.

## Notes

- CI/CD and test pipeline scaffolding were removed.
- Docker files were removed.
- Root-level legacy wrappers were removed to keep structure clean.
