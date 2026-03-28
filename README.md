# Mental Health Chatbot

This repository has been restructured into a modular and reproducible layout.

## What Changed

- Detection is now part of this repository directly.
- Backend implementation moved under backend/.
- Root entrypoint app.py is a thin launcher for backend/api/application.py.
- Environment-based configuration is standardized with .env.example.
- Prompt/model tuning is centralized for quick experimentation.

## Project Layout

- backend/api/application.py: FastAPI application
- backend/core/config.py: Environment-backed settings
- backend/core/runtime_state.py: Rate limiter implementations
- backend/tuning/prompt_and_model_tuning.py: Prompt and model tuning knobs
- backend/services/: Pipeline, detection, prompts, safety, summaries
- backend/models/detection/: Detection model artifacts and assets
- src/: React frontend
- docs/: Architecture, deployment, security, privacy notes
- scripts/: Local setup and run scripts

## Quick Start
1. Inside backend/models/detection, add Goemotion-detection and Sentiment-analysis folders

2. Copy .env.example to .env and set your values.
   You have to add/change the following - 

      JWT_SECRET_KEY= from https://www.jwt.io/

      LLM_MODE=remote

      LLM_API_URL=https://random.dev

      ASR_WS_URL=wss://random-free.dev/ws/asr
      
      VITE_ASR_WS_URL=wss://random-free.dev/ws/asr

3. Install backend dependencies:
   - pip install -r requirements.txt
4. Install frontend dependencies:
   - npm install
5. Run backend:
   - python app.py
6. Run frontend:
   - npm run dev

## Notes

- Use .env to switch between local and Colab endpoints.
- Detection model path can be overridden with DETECTION_MODELS_DIR.

## Local + Colab Hybrid

1. Keep backend/frontend running locally.
2. For Colab LLM, set LLM_MODE=remote and LLM_API_URL in .env.
3. For local LLM, set LLM_MODE=local and ensure LLM_LOCAL_MODEL_PATH exists.
4. For Colab ASR, set ASR_WS_URL and VITE_ASR_WS_URL.
