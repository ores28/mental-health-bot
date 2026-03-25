from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import (
    EMAIL_RE,
    create_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.api.schemas import LoginIn, RegisterIn
from backend.api.state import get_db


router = APIRouter(tags=["auth"])


@router.post("/register")
def register(body: RegisterIn):
    if not body.email or not body.password or not body.name:
        raise HTTPException(400, "All fields required.")
    if not EMAIL_RE.match(body.email):
        raise HTTPException(400, "Invalid email format.")
    if len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters.")

    with get_db() as conn:
        if conn.execute("SELECT id FROM users WHERE email=?", (body.email,)).fetchone():
            raise HTTPException(400, "Email already registered.")
        created = datetime.utcnow().isoformat()
        cur = conn.execute(
            "INSERT INTO users (email,name,password,created) VALUES (?,?,?,?)",
            (body.email, body.name, hash_password(body.password), created),
        )
        conn.commit()
        user_id = cur.lastrowid

    return {
        "message": "Account created!",
        "token": create_token(user_id, body.email),
        "user": {"id": user_id, "email": body.email, "name": body.name},
    }


@router.post("/login")
def login(body: LoginIn):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email=?", (body.email,)).fetchone()
        if not user or not verify_password(body.password, user["password"]):
            raise HTTPException(401, "Invalid email or password.")

    return {
        "message": "Login successful!",
        "token": create_token(user["id"], user["email"]),
        "user": {"id": user["id"], "email": user["email"], "name": user["name"]},
    }


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    with get_db() as conn:
        user = conn.execute(
            "SELECT id,email,name,created FROM users WHERE id=?",
            (current_user["user_id"],),
        ).fetchone()
        if not user:
            raise HTTPException(404, "User not found.")
        return dict(user)
