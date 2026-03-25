# Architecture

## Current Modular Layout

- Backend runtime entrypoint: app.py
- Backend implementation: backend/api/application.py
- Backend shared config: backend/core/config.py
- Backend runtime utilities: backend/core/runtime_state.py
- Backend domain services: backend/services/
- Frontend app: src/
- Detection models: backend/models/detection/

## Backend Flow

1. Input arrives at FastAPI endpoints.
2. Session state is loaded from memory.
3. Pipeline runs input gate, detection, prompt building, LLM generation, safety guardrails.
4. Response and analysis are persisted to SQLite.

## Scaling Notes

- Rate limiting is in-memory for local and single-node deployments.
- Local and Colab hybrid integrations are configured through .env values.
- Session state is still in-memory and suitable for single-node deployments.

## Repository Rules

- Detection folder is now part of this repository and should not contain nested git metadata.
- Configuration must be injected through environment variables.
