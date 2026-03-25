import io

import edge_tts
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.api.schemas import TTSIn


router = APIRouter(tags=["tts"])


@router.post("/api/tts")
async def tts(body: TTSIn):
    if not body.text or not body.text.strip():
        raise HTTPException(400, "Text cannot be empty.")

    text = body.text.strip()[:2000]
    try:
        communicate = edge_tts.Communicate(text, body.voice, rate="-5%", pitch="+5Hz")
        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
        audio_buffer.seek(0)
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=tts.mp3"},
        )
    except Exception as exc:
        raise HTTPException(500, "TTS generation failed.") from exc
