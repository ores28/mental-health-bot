# Security Baseline

## Required Environment Variables

- JWT_SECRET_KEY must be set in non-dev environments.
- CORS_ORIGINS must be narrowed to trusted frontend origins.
- LLM_API_URL must point to a controlled endpoint.

## Data Handling

- Do not log raw tokens or passwords.
- User text may contain sensitive health data. Minimize retention where possible.
- Use HTTPS for frontend, backend, and LLM integration.

## Runtime Controls

- Keep in-memory rate limits conservative in local runs.
- Run services behind a reverse proxy with TLS termination.
