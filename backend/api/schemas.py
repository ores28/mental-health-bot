from typing import Optional

from pydantic import BaseModel


class RegisterIn(BaseModel):
    email: str
    name: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class ChatIn(BaseModel):
    message: str
    session_id: str = "default"
    source: str = "chat"


class AnalyzeIn(BaseModel):
    text: str
    session_id: Optional[str] = None


class SummaryIn(BaseModel):
    session_id: str = "default"


class TTSIn(BaseModel):
    text: str
    voice: str = "en-US-SaraNeural"
