# Prompt and Model Tuning Guide

Edit this layer when experimenting locally or with Colab.

## Prompt Tuning

- File: backend/tuning/prompt_and_model_tuning.py
- Key knobs:
  - PROMPT_PRESETS
  - prompt_history_turns
  - crisis_threshold

## Model Tuning

Use .env for runtime changes without touching code:

- LLM_MODE=auto|local|remote
- LLM_API_URL=<colab endpoint>
- LLM_LOCAL_MODEL_PATH=<local gguf path>
- LLM_MAX_TOKENS=300
- LLM_TEMPERATURE=0.7
- LLM_TIMEOUT_SEC=120
- DETECTION_MAX_LEN=256
- DETECTION_STRIDE=64

## Suggested Workflow

1. Start with local backend and frontend.
2. Point LLM_API_URL to Colab only when needed.
3. Iterate prompt presets and compare outputs.
4. Keep one stable preset and one experimental preset.
