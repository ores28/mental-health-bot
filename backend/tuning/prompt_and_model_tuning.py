"""Central place to tune prompts and model generation behavior."""

from backend.core.config import settings


PROMPT_PRESETS = {
    "default": {
        "system_prompt": (
            "You are a supportive, friendly companion for mental health conversations. "
            "Your goal is to respond like a thoughtful friend, not a therapist. "
            "Use warm, natural language and keep replies concise."
        ),
        "few_shot": (
            "User: I feel empty inside.\n"
            "Aria: Empty can feel really heavy, like everything is muted. "
            "Has it been like this for long?\n\n"
            "User: I don't want to wake up tomorrow.\n"
            "Aria: You said you don't want to wake up tomorrow, and I want to take that seriously. "
            "What is making tomorrow feel this hard right now?\n\n"
        ),
    },
    "supportive_short": {
        "system_prompt": (
            "You are Aria, a calm and caring listener. "
            "Write 2-3 short sentences, validate feelings, and ask one gentle question."
        ),
        "few_shot": "",
    },
}


MODEL_TUNING = {
    "llm_mode": settings.llm_mode,
    "llm_api_url": settings.llm_api_url,
    "llm_local_model_path": settings.llm_local_model_path,
    "llm_max_tokens": settings.llm_max_tokens,
    "llm_temperature": settings.llm_temperature,
    "llm_timeout_sec": settings.llm_timeout_sec,
    "prompt_history_turns": settings.prompt_history_turns,
    "crisis_threshold": settings.crisis_threshold,
}



def get_prompt_bundle() -> dict:
    preset = PROMPT_PRESETS.get(settings.prompt_preset, PROMPT_PRESETS["default"])
    return {
        "system_prompt": preset["system_prompt"],
        "few_shot": preset["few_shot"],
        "history_turns": settings.prompt_history_turns,
        "crisis_threshold": settings.crisis_threshold,
    }
