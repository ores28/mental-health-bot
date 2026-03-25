import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_local_env_file() -> None:
    """Load key=value pairs from .env into process env if not already set."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    jwt_secret_key: str
    algorithm: str
    token_expire_days: int
    db_path: Path
    cors_origins: list[str]
    api_host: str
    api_port: int
    llm_api_url: str
    llm_mode: str
    llm_local_model_path: str
    llm_max_tokens: int
    llm_temperature: float
    llm_timeout_sec: int
    asr_ws_url: str
    session_ttl_hours: int
    session_max: int
    rate_limit: int
    rate_window_sec: int
    prompt_preset: str
    prompt_history_turns: int
    crisis_threshold: float
    detection_models_dir: str
    detection_max_len: int
    detection_stride: int



def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]



def load_settings() -> Settings:
    _load_local_env_file()
    jwt_secret_key = os.environ.get("JWT_SECRET_KEY", "change-this-in-production")
    return Settings(
        jwt_secret_key=jwt_secret_key,
        algorithm=os.environ.get("JWT_ALGORITHM", "HS256"),
        token_expire_days=int(os.environ.get("TOKEN_EXPIRE_DAYS", "30")),
        db_path=Path(os.environ.get("DB_PATH", str(PROJECT_ROOT / "mental_health.db"))),
        cors_origins=_split_csv(os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")),
        api_host=os.environ.get("API_HOST", "127.0.0.1"),
        api_port=int(os.environ.get("API_PORT", "8000")),
        llm_api_url=os.environ.get("LLM_API_URL", "").strip(),
        llm_mode=os.environ.get("LLM_MODE", "auto").strip().lower(),
        llm_local_model_path=os.environ.get(
            "LLM_LOCAL_MODEL_PATH",
            str(PROJECT_ROOT / "Counselor_Llama3_Q4.gguf"),
        ),
        llm_max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "300")),
        llm_temperature=float(os.environ.get("LLM_TEMPERATURE", "0.7")),
        llm_timeout_sec=int(os.environ.get("LLM_TIMEOUT_SEC", "120")),
        asr_ws_url=os.environ.get("ASR_WS_URL", ""),
        session_ttl_hours=int(os.environ.get("SESSION_TTL_HOURS", "4")),
        session_max=int(os.environ.get("SESSION_MAX", "200")),
        rate_limit=int(os.environ.get("RATE_LIMIT", "30")),
        rate_window_sec=int(os.environ.get("RATE_WINDOW_SEC", "60")),
        prompt_preset=os.environ.get("PROMPT_PRESET", "default"),
        prompt_history_turns=int(os.environ.get("PROMPT_HISTORY_TURNS", "6")),
        crisis_threshold=float(os.environ.get("CRISIS_THRESHOLD", "0.55")),
        detection_models_dir=os.environ.get("DETECTION_MODELS_DIR", str(PROJECT_ROOT / "backend" / "models" / "detection")),
        detection_max_len=int(os.environ.get("DETECTION_MAX_LEN", "256")),
        detection_stride=int(os.environ.get("DETECTION_STRIDE", "64")),
    )


settings = load_settings()
