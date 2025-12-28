from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from tts_engine import TTSService

app = FastAPI(title="TTS API")
tts = TTSService()

class TTSRequest(BaseModel):
    text: str
    voice: str = "female"

@app.post("/tts")
def generate_tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")

    audio_path = tts.generate(req.text, req.voice)

    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename="speech.wav"
    )

@app.get("/voices")
def voices():
    return {"voices": ["male", "female"]}
