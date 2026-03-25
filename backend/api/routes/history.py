from fastapi import APIRouter, Depends

from backend.api.dependencies import get_current_user
from backend.api.state import build_analysis_payload, get_db


router = APIRouter(tags=["history"])


@router.get("/history")
def get_analysis_history(current_user=Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM analysis_history WHERE user_id=? ORDER BY timestamp DESC LIMIT 500",
            (current_user["user_id"],),
        ).fetchall()
        return {"history": [build_analysis_payload(row) for row in rows]}


@router.delete("/history/clear")
def clear_analysis_history(current_user=Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM analysis_history WHERE user_id=?", (current_user["user_id"],))
        conn.commit()
    return {"message": "Analysis history cleared."}
