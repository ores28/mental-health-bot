import json
import logging
import sqlite3
import time
from contextlib import contextmanager

from backend.core.config import settings
from backend.core.runtime_state import InMemoryRateLimiter
from backend.services.conversation_history import ConversationHistory


log = logging.getLogger("mindcare")

DB_PATH = str(settings.db_path)

SESSION_TTL_HOURS = settings.session_ttl_hours
SESSION_MAX = settings.session_max

sessions: dict[str, ConversationHistory] = {}
_session_last_access: dict[str, float] = {}

limiter = InMemoryRateLimiter(limit=settings.rate_limit, window_sec=settings.rate_window_sec)


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
    finally:
        conn.close()



def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL, password TEXT NOT NULL, created TEXT NOT NULL)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            session_id TEXT UNIQUE NOT NULL, title TEXT,
            conv_type TEXT NOT NULL DEFAULT 'chat',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id))"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL, content TEXT NOT NULL, timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            session_id TEXT, user_text TEXT NOT NULL,
            mental_label TEXT NOT NULL, mental_conf REAL NOT NULL,
            emotion_label TEXT, emotion_conf REAL,
            all_scores TEXT NOT NULL, high_risk INTEGER NOT NULL DEFAULT 0,
            timestamp TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))"""
        )
        conn.commit()

        try:
            conn.execute("ALTER TABLE conversations ADD COLUMN conv_type TEXT NOT NULL DEFAULT 'chat'")
            conn.commit()
        except Exception:
            pass

    log.info("Database initialized")



def evict_stale_sessions() -> None:
    cutoff = time.time() - SESSION_TTL_HOURS * 3600
    stale = [sid for sid, ts in _session_last_access.items() if ts < cutoff]
    for sid in stale:
        sessions.pop(sid, None)
        _session_last_access.pop(sid, None)



def get_session(session_id: str, user_id: int | None = None) -> ConversationHistory:
    if len(sessions) > SESSION_MAX:
        evict_stale_sessions()

    _session_last_access[session_id] = time.time()

    if session_id in sessions:
        return sessions[session_id]

    history = ConversationHistory()
    if user_id:
        try:
            with get_db() as conn:
                conv = conn.execute(
                    "SELECT id FROM conversations WHERE session_id=? AND user_id=?",
                    (session_id, user_id),
                ).fetchone()
                if conv:
                    rows = conn.execute(
                        "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY timestamp ASC",
                        (conv["id"],),
                    ).fetchall()
                    for row in rows:
                        if row["role"] == "user":
                            history.add_user_message(row["content"])
                        else:
                            history.add_assistant_message(row["content"])
        except Exception as exc:
            log.warning("Could not preload session %s: %s", session_id, exc)

    sessions[session_id] = history
    return history



def build_analysis_payload(row):
    return {
        "id": row["id"],
        "sessionId": row["session_id"],
        "userText": row["user_text"],
        "timestamp": row["timestamp"],
        "highRisk": bool(row["high_risk"]),
        "mentalHealth": {
            "label": row["mental_label"],
            "confidence": row["mental_conf"],
        },
        "emotion": {
            "label": row["emotion_label"],
            "confidence": row["emotion_conf"],
        }
        if row["emotion_label"]
        else None,
        "allScores": json.loads(row["all_scores"]),
    }
