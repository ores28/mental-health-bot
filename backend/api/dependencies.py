import re
import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import settings


SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.algorithm
TOKEN_EXPIRE_DAYS = settings.token_expire_days

# Keep passlib for backward compatibility with already-stored bcrypt hashes.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)

EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

_PBKDF2_ALGO = "sha256"
_PBKDF2_ITERATIONS = 390000
_PBKDF2_PREFIX = "pbkdf2_sha256"



def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGO,
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(dk).decode("ascii")
    return f"{_PBKDF2_PREFIX}${_PBKDF2_ITERATIONS}${salt_b64}${hash_b64}"



def verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False

    if hashed.startswith(f"{_PBKDF2_PREFIX}$"):
        try:
            _, iterations_s, salt_b64, hash_b64 = hashed.split("$", 3)
            iterations = int(iterations_s)
            salt = base64.b64decode(salt_b64.encode("ascii"))
            expected = base64.b64decode(hash_b64.encode("ascii"))
            actual = hashlib.pbkdf2_hmac(
                _PBKDF2_ALGO,
                plain.encode("utf-8"),
                salt,
                iterations,
            )
            return hmac.compare_digest(actual, expected)
        except Exception:
            return False

    # Legacy path for existing bcrypt hashes.
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False



def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)



def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token.")
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token.") from exc



def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if not user_id:
            return None
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError:
        return None
