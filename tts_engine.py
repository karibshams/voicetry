import pyttsx3
import os
import uuid

class TTSService:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 120)
        self.engine.setProperty("volume", 0.95)

        self.voice_map = {
            "male": 0,
            "female": 1
        }

        os.makedirs("audio", exist_ok=True)

    def generate(self, text: str, voice: str) -> str:
        voices = self.engine.getProperty("voices")
        voice_id = self.voice_map.get(voice, 1)

        if voice_id < len(voices):
            self.engine.setProperty("voice", voices[voice_id].id)

        filename = f"audio/{uuid.uuid4()}.wav"
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()

        return filename
