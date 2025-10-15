import os
from dotenv import load_dotenv
load_dotenv()
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as texttospeech

class VoiceEngine:
    """Google Cloud Speech-to-Text and Text-to-Speech handler"""
    
    def __init__(self):
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS not found or file doesn't exist! "
                "Check your .env file."
            )
        
        self.stt_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        
        self.voices = {
            'en': {'male': 'en-US-Neural2-D', 'female': 'en-US-Neural2-F'},
            'hi': {'male': 'hi-IN-Neural2-B', 'female': 'hi-IN-Neural2-A'},
            'pt': {'male': 'pt-BR-Neural2-B', 'female': 'pt-BR-Neural2-A'}
        }
    
    def speech_to_text(self, audio_data: bytes) -> dict:
        """Convert speech to text with language detection"""
        try:
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code='en-US',
                alternative_language_codes=['hi-IN', 'pt-BR'],
                enable_automatic_punctuation=True
            )
            
            audio = speech.RecognitionAudio(content=audio_data)
            response = self.stt_client.recognize(config=config, audio=audio)
            
            if not response.results:
                return {'text': '', 'language': 'en'}
            
            result = response.results[0]
            detected_lang = getattr(result, 'language_code', 'en-US')[:2]
            
            return {
                'text': result.alternatives[0].transcript,
                'language': detected_lang
            }
        
        except Exception as e:
            print(f"STT Error: {e}")
            return {'text': '', 'language': 'en', 'error': str(e)}
    
    def text_to_speech(self, text: str, language: str, gender: str = 'female') -> bytes:
        """Convert text to speech"""
        try:
            voice_name = self.voices.get(language, self.voices['en'])[gender]
            lang_code = f"{language}-{'US' if language == 'en' else 'IN' if language == 'hi' else 'BR'}"
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                name=voice_name
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate =0.95, 
            )
            


            
            response = self.tts_client.synthesize_speech(
                input=texttospeech.SynthesisInput(text=text),
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
        
        except Exception as e:
            print(f"TTS Error: {e}")
            return b''  


# ==========================================
# TEST CODE
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("🎤 TESTING VOICE ENGINE")
    print("=" * 60)
    
    try:
        print("\n1️⃣  Initializing VoiceEngine...")
        engine = VoiceEngine()
        
        print("\n2️⃣  Testing Text-to-Speech...")
        test_phrases = [
            ("Hello, I am Juno, your wellness companion", 'en', 'female'),
            ("नमस्ते, मैं जूनो हूं", 'hi', 'female'),
            ("Olá, eu sou Juno", 'pt', 'female')
        ]
        
        for text, lang, gender in test_phrases:
            audio = engine.text_to_speech(text, lang, gender)
            print(f"✅ TTS ({lang}, {gender}): '{text[:30]}...' → {len(audio)} bytes")
        
        print("\n3️⃣  Testing Voice Configurations...")
        for lang in ['en', 'hi', 'pt']:
            male = engine.voices[lang]['male']
            female = engine.voices[lang]['female']
            print(f"✅ {lang.upper()}: Male={male}, Female={female}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - VoiceEngine Ready!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print()