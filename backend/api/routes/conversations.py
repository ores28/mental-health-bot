from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_current_user
from backend.api.state import get_db


router = APIRouter(tags=["conversations"])


@router.get("/api/conversations")
def get_conversations(current_user=Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute(
            """SELECT c.id, c.session_id, c.title, c.conv_type, c.created_at, c.updated_at,
            (SELECT COUNT(*) FROM messages WHERE conversation_id=c.id) as msg_count
            FROM conversations c WHERE c.user_id=? ORDER BY c.updated_at DESC LIMIT 50""",
            (current_user["user_id"],),
        ).fetchall()

        conversations = []
        for row in rows:
            last = conn.execute(
                "SELECT content,role FROM messages WHERE conversation_id=? ORDER BY timestamp DESC LIMIT 1",
                (row["id"],),
            ).fetchone()
            conversations.append(
                {
                    "session_id": row["session_id"],
                    "title": row["title"],
                    "conv_type": row["conv_type"] or "chat",
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "message_count": row["msg_count"],
                    "last_message": last["content"][:100] if last else "",
                    "last_role": last["role"] if last else "",
                }
            )
        return {"conversations": conversations}


@router.get("/api/conversations/{session_id}")
def get_conversation_messages(session_id: str, current_user=Depends(get_current_user)):
    with get_db() as conn:
        conv = conn.execute(
            "SELECT id,title FROM conversations WHERE session_id=? AND user_id=?",
            (session_id, current_user["user_id"]),
        ).fetchone()
        if not conv:
            raise HTTPException(404, "Conversation not found.")

        msgs = conn.execute(
            "SELECT role,content,timestamp FROM messages WHERE conversation_id=? ORDER BY timestamp ASC",
            (conv["id"],),
        ).fetchall()

        return {
            "session_id": session_id,
            "title": conv["title"],
            "messages": [
                {"role": m["role"], "content": m["content"], "timestamp": m["timestamp"]}
                for m in msgs
            ],
        }


@router.delete("/api/conversations/{session_id}")
def delete_conversation(session_id: str, current_user=Depends(get_current_user)):
    with get_db() as conn:
        conv = conn.execute(
            "SELECT id FROM conversations WHERE session_id=? AND user_id=?",
            (session_id, current_user["user_id"]),
        ).fetchone()
        if not conv:
            raise HTTPException(404, "Conversation not found.")

        conn.execute("DELETE FROM messages WHERE conversation_id=?", (conv["id"],))
        conn.execute("DELETE FROM conversations WHERE id=?", (conv["id"],))
        conn.execute(
            "DELETE FROM analysis_history WHERE session_id=? AND user_id=?",
            (session_id, current_user["user_id"]),
        )
        conn.commit()

    return {"message": "Conversation deleted."}


@router.delete("/api/conversations")
def clear_all_conversations(current_user=Depends(get_current_user)):
    with get_db() as conn:
        conv_rows = conn.execute(
            "SELECT id FROM conversations WHERE user_id=?",
            (current_user["user_id"],),
        ).fetchall()

        for row in conv_rows:
            conn.execute("DELETE FROM messages WHERE conversation_id=?", (row["id"],))

        conn.execute("DELETE FROM conversations WHERE user_id=?", (current_user["user_id"],))
        conn.execute("DELETE FROM analysis_history WHERE user_id=?", (current_user["user_id"],))
        conn.commit()

    return {"message": "All conversations cleared."}
