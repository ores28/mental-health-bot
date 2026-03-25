import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_optional_user
from backend.api.schemas import AnalyzeIn, ChatIn, SummaryIn
from backend.api.state import get_db, get_session, sessions
from backend.services.conversation_history import ConversationHistory
from backend.services.detection import analyze_full
from backend.services.pipeline import end_session, process_user_input


log = logging.getLogger("mindcare")
router = APIRouter(tags=["chat"])


@router.post("/api/chat")
def chat(body: ChatIn, current_user=Depends(get_optional_user)):
    if not body.message or not body.message.strip():
        raise HTTPException(400, "Message cannot be empty.")

    user_message = body.message.strip()
    session_id = body.session_id
    user_id = current_user["user_id"] if current_user else None

    history = get_session(session_id, user_id)
    try:
        result = process_user_input(user_message, history)
    except Exception as exc:
        log.exception("/api/chat pipeline failed: %s", exc)
        raise HTTPException(status_code=500, detail="Chat pipeline failed") from exc

    if current_user:
        try:
            with get_db() as conn:
                conv = conn.execute(
                    "SELECT id FROM conversations WHERE session_id=? AND user_id=?",
                    (session_id, current_user["user_id"]),
                ).fetchone()
                now = datetime.utcnow().isoformat()

                if not conv:
                    title = user_message[:80] + ("..." if len(user_message) > 80 else "")
                    conv_type = body.source if body.source in ("chat", "voice") else "chat"
                    cur = conn.execute(
                        "INSERT INTO conversations (user_id,session_id,title,conv_type,created_at,updated_at) VALUES (?,?,?,?,?,?)",
                        (current_user["user_id"], session_id, title, conv_type, now, now),
                    )
                    conv_id = cur.lastrowid
                else:
                    conv_id = conv["id"]
                    conn.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conv_id))

                conn.execute(
                    "INSERT INTO messages (conversation_id,role,content,timestamp) VALUES (?,?,?,?)",
                    (conv_id, "user", user_message, now),
                )
                conn.execute(
                    "INSERT INTO messages (conversation_id,role,content,timestamp) VALUES (?,?,?,?)",
                    (conv_id, "assistant", result["response"], now),
                )

                if result.get("category"):
                    conn.execute(
                        """INSERT INTO analysis_history
                        (user_id,session_id,user_text,mental_label,mental_conf,emotion_label,emotion_conf,all_scores,high_risk,timestamp)
                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (
                            current_user["user_id"],
                            session_id,
                            user_message[:1000],
                            result.get("category", "Normal"),
                            round(result.get("category_score", 0), 4),
                            result.get("emotion"),
                            round(result.get("emotion_score", 0), 4)
                            if result.get("emotion_score")
                            else None,
                            json.dumps(result.get("all_scores", {})),
                            int(result.get("category") == "Suicidal"),
                            now,
                        ),
                    )
                conn.commit()
        except Exception as exc:
            log.error("Failed to save to DB: %s", exc)

    return result


@router.post("/analyze")
def analyze(body: AnalyzeIn, current_user=Depends(get_optional_user)):
    if not body.text or not body.text.strip():
        raise HTTPException(400, "Text cannot be empty.")

    result = analyze_full(body.text)
    if current_user:
        try:
            with get_db() as conn:
                mental = result.get("mental_state", {})
                emotion = result.get("emotion", {})
                conn.execute(
                    """INSERT INTO analysis_history
                    (user_id,session_id,user_text,mental_label,mental_conf,emotion_label,emotion_conf,all_scores,high_risk,timestamp)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (
                        current_user["user_id"],
                        body.session_id,
                        body.text[:1000],
                        mental.get("label", "Normal"),
                        round(mental.get("confidence", 0), 4),
                        emotion.get("label") if emotion else None,
                        round(emotion.get("confidence", 0), 4) if emotion else None,
                        json.dumps(mental.get("all_scores", {})),
                        int(result.get("high_risk", False)),
                        datetime.utcnow().isoformat(),
                    ),
                )
                conn.commit()
        except Exception as exc:
            log.error("Failed to save analysis: %s", exc)

    return result


@router.get("/api/sentiment")
def sentiment(session_id: str = "default"):
    history = sessions.get(session_id)
    return {"scores": history.get_score_history() if history else []}


@router.post("/api/summary")
def summary(body: SummaryIn, current_user=Depends(get_optional_user)):
    history = sessions.get(body.session_id)
    if history and len(history) > 0:
        return end_session(history)

    if not current_user:
        return {"message_count": 0, "summary_text": "No messages."}

    try:
        with get_db() as conn:
            conv = conn.execute(
                "SELECT id FROM conversations WHERE session_id=? AND user_id=?",
                (body.session_id, current_user["user_id"]),
            ).fetchone()
            if not conv:
                return {"message_count": 0, "summary_text": "No messages."}

            rows = conn.execute(
                """SELECT user_text, mental_label, mental_conf,
                   emotion_label, emotion_conf, timestamp
                   FROM analysis_history
                   WHERE session_id=? AND user_id=?
                   ORDER BY timestamp ASC""",
                (body.session_id, current_user["user_id"]),
            ).fetchall()

            if not rows:
                return {"message_count": 0, "summary_text": "No messages."}

            rebuilt = ConversationHistory()
            for row in rows:
                rebuilt.add_user_message(
                    content=row["user_text"],
                    emotion=row["emotion_label"],
                    emotion_score=row["emotion_conf"] or 0.0,
                    category=row["mental_label"],
                    category_score=row["mental_conf"] or 0.0,
                )
            return end_session(rebuilt)
    except Exception as exc:
        log.error("Failed to rebuild summary from DB: %s", exc)
        return {"message_count": 0, "summary_text": "No messages."}
