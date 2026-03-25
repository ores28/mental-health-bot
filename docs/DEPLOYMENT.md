# Run Modes

## Local Development

1. Install Python dependencies: pip install -r requirements.txt.
2. Install frontend dependencies.
3. Copy .env.example to .env and set required values.
4. Start backend with python app.py.
5. Start frontend with npm run dev.

## Local + Colab Hybrid

1. Keep backend and frontend local.
2. Set LLM_MODE=remote and LLM_API_URL to your Colab endpoint when needed.
3. Set ASR_WS_URL and VITE_ASR_WS_URL to your Colab websocket endpoint when needed.
4. Switch back to local mode by setting LLM_MODE=local.
