from typing import Dict, Tuple, Optional
from .stt_tts import STTTTSService
from .openai_agent import OpenAIAgent
from .sentiment import SentimentAnalyzer

class WellnessCoach:
    """Voice journaling and coaching pipeline orchestrator"""
    
    def __init__(self, openai_agent: OpenAIAgent):
        self.stt_tts = STTTTSService()
        self.openai_agent = openai_agent
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def process_voice_journal(self, audio_data: bytes, language: str = 'en') -> Dict[str, any]:
        """Complete voice journaling pipeline"""
        # 1. Convert speech to text
        transcript = self.stt_tts.speech_to_text(audio_data, language)
        
        # 2. Analyze sentiment
        sentiment_data = self.sentiment_analyzer.analyze_sentiment(transcript)
        
        # 3. Generate AI response
        if sentiment_data['crisis_detected']:
            response_text = self._get_crisis_response(language)
        else:
            response_text = self.openai_agent.summarize_journal(transcript, language)
        
        # 4. Convert response to speech
        response_audio = self.stt_tts.text_to_speech(response_text, language)
        
        return {
            'transcript': transcript,
            'sentiment': sentiment_data,
            'response_text': response_text,
            'response_audio': response_audio,
            'avatar_emotion': self._get_avatar_emotion(sentiment_data['mood'])
        }
    
    def _get_crisis_response(self, language: str) -> str:
        """Crisis intervention response"""
        responses = {
            'en': "I'm here for you. Let's try a breathing exercise. Please reach out to someone you trust.",
            'hi': "मैं आपके साथ हूं। आइए सांस लेने का अभ्यास करते हैं। कृपया किसी भरोसेमंद व्यक्ति से संपर्क करें।",
            'pt': "Estou aqui para você. Vamos tentar um exercício de respiração. Entre em contato com alguém de confiança."
        }
        return responses.get(language, responses['en'])
    
    def _get_avatar_emotion(self, mood: str) -> str:
        """Map mood to avatar expression"""
        emotion_map = {
            'happy': 'smile',
            'calm': 'peaceful',
            'anxious': 'concerned',
            'sad': 'empathetic',
            'neutral': 'attentive'
        }
        return emotion_map.get(mood, 'attentive')