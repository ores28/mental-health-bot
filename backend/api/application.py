import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.auth import router as auth_router
from backend.api.routes.chat import router as chat_router
from backend.api.routes.conversations import router as conversations_router
from backend.api.routes.health import router as health_router
from backend.api.routes.history import router as history_router
from backend.api.routes.tts import router as tts_router
from backend.api.state import init_db, limiter
from backend.core.config import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mindcare")


app = FastAPI(title="Mental Health Chatbot API", version="9.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    if not limiter.allow(client_ip):
        from starlette.responses import JSONResponse

        return JSONResponse({"detail": "Too many requests. Please slow down."}, status_code=429)
    return await call_next(request)


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(tts_router)
app.include_router(conversations_router)
app.include_router(history_router)
app.include_router(health_router)


@app.on_event("startup")
async def warmup_models():
    init_db()
    log.info("Warming up models...")
    try:
        from backend.services.detection import _load_emotion_model, _load_sentiment_model

        _load_sentiment_model()
        _load_emotion_model()
        log.info("Detection models loaded")
    except Exception as exc:
        log.error("Detection model warmup failed: %s", exc)
    log.info("Warmup complete")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
