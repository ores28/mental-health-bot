"""Compatibility entrypoint. Use backend.api.application for implementation."""
from backend.api.application import app
from backend.core.config import settings




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
