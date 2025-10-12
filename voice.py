import os
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as texttospeech
from typing import Dict

class VoiceEngine:
    """Handles Speech-to-Text, Text-to-Speech with Google Cloud API"""
    
    def __init__(self):
        # Uses GOOGLE_CLOUD_API_KEY from environment automatically
        self.stt_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        
        self.voices = {
            'en': {'male': 'en-US-Neural2-D', 'female': 'en-US-Neural2-F'},
            'hi': {'male': 'hi-IN-Neural2-B', 'female': 'hi-IN-Neural2-A'},
            'pt': {'male': 'pt-BR-Neural2-B', 'female': 'pt-BR-Neural2-A'}
        }
        
        self.language_codes = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'pt': 'pt-BR'
        }
    
    def speech_to_text(self, audio_data: bytes) -> Dict[str, str]:
        """Convert speech to text with auto language detection"""
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
            return {'text': '', 'language': 'en', 'speaker_gender': 'female'}
        
        result = response.results[0]
        transcript = result.alternatives[0].transcript
        detected_lang = result.language_code[:2] if hasattr(result, 'language_code') else 'en'
        
        return {
            'text': transcript,
            'language': detected_lang,
            'speaker_gender': 'female'
        }
    
    def text_to_speech(self, text: str, language: str, gender: str = 'female') -> bytes:
        """Convert text to natural speech with gender matching"""
        voice_name = self.voices.get(language, self.voices['en'])[gender]
        lang_code = self.language_codes.get(language, 'en-US')
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_name
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,
            pitch=0.0
        )
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        response = self.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content


# ==========================================
# TEST CODE FOR voice.py
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("TESTING: VoiceEngine Module")
    print("=" * 50)
    
    try:
        voice = VoiceEngine()
        print("✅ VoiceEngine initialized successfully")
        
        # Test TTS
        test_text = "Hello, I am Juno, your wellness assistant."
        audio = voice.text_to_speech(test_text, 'en', 'female')
        print(f"✅ TTS Working: Generated {len(audio)} bytes of audio")
        print(f"✅ Test text: '{test_text}'")
        
        # Test voice configurations
        for lang in ['en', 'hi', 'pt']:
            print(f"✅ Language '{lang}' configured: {voice.language_codes[lang]}")
        
        print("\n✅ ALL TESTS PASSED for voice.py")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("=" * 50)