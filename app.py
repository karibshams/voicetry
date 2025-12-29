from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
import pyttsx3

app = FastAPI(title="TTS API")

engine = pyttsx3.init()
engine.setProperty("rate", 120)
engine.setProperty("volume", 0.95)

VOICE_MAP = {
    "male": 0,
    "female": 1
}

os.makedirs("audio", exist_ok=True)

class TTSRequest(BaseModel):
    text: str
    voice: str = "female"

@app.get("/")
def root():
    return {"status": "TTS API running"}

@app.get("/voices")
def get_voices():
    return {"voices": list(VOICE_MAP.keys())}

@app.post("/tts")
def generate_tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    voices = engine.getProperty("voices")
    voice_id = VOICE_MAP.get(req.voice, 1)

    if voice_id < len(voices):
        engine.setProperty("voice", voices[voice_id].id)

    filename = f"audio/{uuid.uuid4()}.wav"
    engine.save_to_file(req.text, filename)
    engine.runAndWait()

    return FileResponse(
        filename,
        media_type="audio/wav",
        filename="speech.wav"
    )
