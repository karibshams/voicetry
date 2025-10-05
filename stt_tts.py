import os
from google.cloud import speech, texttospeech
from typing import Optional, Tuple

class STTTTSService:
    """Google Speech-to-Text and Text-to-Speech service handler"""
    
    def __init__(self):
        self.stt_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        self.voice_config = {
            'en': {'language_code': 'en-US', 'name': 'en-US-Neural2-F'},
            'hi': {'language_code': 'hi-IN', 'name': 'hi-IN-Neural2-A'},
            'pt': {'language_code': 'pt-BR', 'name': 'pt-BR-Neural2-A'}
        }
    
    def speech_to_text(self, audio_data: bytes, language: str = 'en') -> str:
        """Convert audio to text"""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.voice_config[language]['language_code']
        )
        audio = speech.RecognitionAudio(content=audio_data)
        response = self.stt_client.recognize(config=config, audio=audio)
        return ' '.join([result.alternatives[0].transcript for result in response.results])
    
    def text_to_speech(self, text: str, language: str = 'en') -> bytes:
        """Convert text to natural voice audio"""
        voice_settings = self.voice_config[language]
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_settings['language_code'],
            name=voice_settings['name']
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content