from fastapi import APIRouter

from backend.api.state import get_db, limiter, sessions
from backend.services.detection import _emotion_model, _sentiment_model
from backend.services.pipeline import _llm_responder


router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    db_ok = False
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
            db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "version": "9.0.0",
        "models": {
            "sentiment": _sentiment_model is not None,
            "emotion": _emotion_model is not None,
            "llm": _llm_responder is not None,
        },
        "database": db_ok,
        "rate_limiter": limiter.__class__.__name__,
        "active_sessions": len(sessions),
    }
