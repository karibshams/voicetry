import os
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as texttospeech

class VoiceEngine:
    """Google Cloud Speech-to-Text and Text-to-Speech handler"""
    
    def __init__(self):
        self.stt_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        
        self.voices = {
            'en': {'male': 'en-US-Neural2-D', 'female': 'en-US-Neural2-F'},
            'hi': {'male': 'hi-IN-Neural2-B', 'female': 'hi-IN-Neural2-A'},
            'pt': {'male': 'pt-BR-Neural2-B', 'female': 'pt-BR-Neural2-A'}
        }
    
    def speech_to_text(self, audio_data: bytes) -> dict:
        """Convert speech to text with language detection"""
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
    
    def text_to_speech(self, text: str, language: str, gender: str = 'female') -> bytes:
        """Convert text to speech"""
        voice_name = self.voices.get(language, self.voices['en'])[gender]
        lang_code = f"{language}-{'US' if language == 'en' else 'IN' if language == 'hi' else 'BR'}"
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_name
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95
        )
        
        response = self.tts_client.synthesize_speech(
            input=texttospeech.SynthesisInput(text=text),
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content


# ==========================================
# TEST CODE
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("Testing VoiceEngine")
    print("=" * 50)
    
    try:
        engine = VoiceEngine()
        print("✅ Initialized")
        
        # Test TTS
        audio = engine.text_to_speech("Hello, I am Juno", 'en', 'female')
        print(f"✅ TTS: {len(audio)} bytes generated")
        
        # Test voice configs
        for lang in ['en', 'hi', 'pt']:
            print(f"✅ {lang}: {engine.voices[lang]}")
        
        print("\n✅ ALL TESTS PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("=" * 50)    