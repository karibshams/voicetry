import os
import requests
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
class VoiceEngine:
    """Handles all voice processing - STT and TTS using ElevenLabs"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'english',
        'hi': 'hindi',
        'pt': 'portuguese'
    }
    
    def __init__(self):
        """Initialize voice engine with API keys"""
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        self.male_voice_id = os.getenv("MALE_VOICE_ID")
        self.female_voice_id = os.getenv("FEMALE_VOICE_ID")
        
        # Validate API keys
        if not self.openai_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
        if not self.elevenlabs_key:
            raise ValueError("❌ ELEVENLABS_API_KEY not found in .env file!")
        if not self.male_voice_id or not self.female_voice_id:
            raise ValueError("❌ Voice IDs not found in .env file!")
        
        self.openai_client = OpenAI(api_key=self.openai_key)
        print("VoiceEngine initialized successfully")
    
    def speech_to_text(self, audio_data: bytes) -> dict:
        """
        Convert speech to text using ElevenLabs STT API
        
        Args:
            audio_data: Audio file bytes (WAV format)
        
        Returns:
            dict: {'text': str, 'language': str}
        """
        try:
            # Prepare audio data
            if isinstance(audio_data, bytes):
                audio_file = BytesIO(audio_data)
            else:
                audio_file = audio_data
            
            audio_file.seek(0)
            
            # ElevenLabs STT API
            url = "https://api.elevenlabs.io/v1/speech-to-text"
            headers = {"xi-api-key": self.elevenlabs_key}
            files = {"file": ("audio.wav", audio_file, "audio/wav")}
            data = {"model_id": "scribe_v1"}
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code != 200:
                print(f"❌ ElevenLabs STT Error: {response.status_code}")
                print(f"Response: {response.text}")
                return {'text': '', 'language': 'en'}
            
            result = response.json()
            text = result.get("text", "")
            
            # Detect language (default to English)
            detected_lang = self._detect_language(text)
            
            return {
                'text': text,
                'language': detected_lang
            }
        
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return {'text': '', 'language': 'en'}
    
    def text_to_speech(self, text: str, language: str = 'en', gender: str = 'female') -> bytes:
        """
        Convert text to speech using ElevenLabs TTS API
        
        Args:
            text: Text to convert
            language: Language code ('en', 'hi', 'pt')
            gender: 'male' or 'female'
        
        Returns:
            bytes: Audio data in WAV format
        """
        try:
            # Select voice based on gender
            voice_id = self.male_voice_id if gender == "male" else self.female_voice_id
            
            if not voice_id:
                print(f"❌ Voice ID not found for {gender}")
                return b''
            
            # ElevenLabs TTS API
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
            headers = {
                "xi-api-key": self.elevenlabs_key,
                "Content-Type": "application/json"
            }
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, stream=True)
            
            if response.status_code != 200:
                print(f"❌ ElevenLabs TTS Error: {response.status_code}")
                print(f"Response: {response.text}")
                return b''
            
            # Collect audio chunks
            audio_chunks = []
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    audio_chunks.append(chunk)
            
            audio_data = b''.join(audio_chunks)
            return audio_data
        
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return b''
    
    def _detect_language(self, text: str) -> str:
        """
        Detect language from text (simple heuristic)
        
        Args:
            text: Input text
        
        Returns:
            str: Language code ('en', 'hi', 'pt')
        """
        if not text:
            return 'en'
        
        # Check for Devanagari script (Hindi)
        if any('\u0900' <= char <= '\u097F' for char in text):
            return 'hi'
        
        # Check for Portuguese specific characters
        portuguese_chars = 'áàâãéêíóôõúç'
        if any(char.lower() in portuguese_chars for char in text):
            return 'pt'
        
        # Default to English
        return 'en'
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get full language name from code
        
        Args:
            lang_code: Language code ('en', 'hi', 'pt')
        
        Returns:
            str: Full language name
        """
        return self.SUPPORTED_LANGUAGES.get(lang_code, 'english')
    


import pyaudio
import wave

def record_audio(duration: int = 5) -> bytes:
    """Record audio from microphone for specified duration"""
    print(f"🎤 Recording for {duration} seconds...")
    
    CHUNK = 1024
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                    input=True, frames_per_buffer=CHUNK)
    
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Convert to WAV format
    wav_buffer = wave.open("temp_audio.wav", "wb")
    wav_buffer.setnchannels(CHANNELS)
    wav_buffer.setsampwidth(p.get_sample_size(FORMAT))
    wav_buffer.setframerate(RATE)
    wav_buffer.writeframes(b"".join(frames))
    wav_buffer.close()
    
    with open("temp_audio.wav", "rb") as f:
        audio_data = f.read()
    
    return audio_data


def main():
    """Test VoiceEngine with 3 languages and 2 voices"""
    
    engine = VoiceEngine()
    
    # Test data: (text, language, language_name)
    test_phrases = [
        ("Hello, how are you today?", "en", "English"),
        ("नमस्ते, आप कैसे हैं?", "hi", "Hindi"),
        ("Olá, como você está?", "pt", "Portuguese")
    ]
    
    genders = ["female", "male"]
    
    print("\n" + "="*60)
    print("🎙️  VOICEENGINE TEST - 3 Languages × 2 Voices")
    print("="*60 + "\n")
    
    # Test Text-to-Speech
    print("📝 TEXT-TO-SPEECH TEST")
    print("-" * 60)
    
    for text, lang, lang_name in test_phrases:
        print(f"\n🌍 Language: {lang_name} ({lang})")
        print(f"   Text: {text}")
        
        for gender in genders:
            print(f"   🎵 Generating {gender} voice...", end=" ")
            audio_data = engine.text_to_speech(text, language=lang, gender=gender)
            
            if audio_data:
                print(f"✅ Success ({len(audio_data)} bytes)")
                # Save for playback
                filename = f"output_{lang}_{gender}.wav"
                with open(filename, "wb") as f:
                    f.write(audio_data)
                print(f"      Saved to: {filename}")
            else:
                print("❌ Failed")
    
    # Test Speech-to-Text
    print("\n\n🎤 SPEECH-TO-TEXT TEST")
    print("-" * 60)
    print("Recording live audio from microphone...")
    
    audio_data = record_audio(duration=5)
    
    if audio_data:
        print("\n🔄 Converting speech to text...", end=" ")
        result = engine.speech_to_text(audio_data)
        
        if result['text']:
            print(f"✅ Success")
            print(f"   Detected Language: {engine.get_language_name(result['language']).upper()}")
            print(f"   Transcribed Text: {result['text']}")
            
            # Generate response in detected language
            print(f"\n🎵 Generating response in detected language...")
            response_audio = engine.text_to_speech(
                f"You said: {result['text']}", 
                language=result['language'],
                gender="female"
            )
            
            if response_audio:
                response_file = "response_audio.wav"
                with open(response_file, "wb") as f:
                    f.write(response_audio)
                print(f"   ✅ Response saved to: {response_file}")
        else:
            print("❌ No text detected")
    else:
        print("❌ Failed to record audio")
    
    print("\n" + "="*60)
    print("✨ Test Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()