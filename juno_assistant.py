import os
from typing import Dict, List, Optional, Union
from .stt_tts import STTTTSService
from .openai_agent import OpenAIAgent
from .sentiment import SentimentAnalyzer
from .coach import WellnessCoach
from .guide import AppGuide
from .extras import JunoExtras

class JunoAssistant:
    """
    Main Juno AI Assistant orchestrator class.
    Single entry point for all AI operations.
    """
    
    def __init__(self):
        # Initialize core services
        self.openai_agent = OpenAIAgent(os.getenv('OPENAI_API_KEY'))
        self.stt_tts = STTTTSService()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Initialize specialized modules
        self.coach = WellnessCoach(self.openai_agent)
        self.guide = AppGuide(self.openai_agent)
        self.extras = JunoExtras(self.openai_agent)
        
        # Default language
        self.default_language = os.getenv('DEFAULT_LANG', 'en')
    
    def process_voice_journal(self, audio_data: bytes, language: str = None) -> Dict[str, any]:
        """
        Complete voice journaling pipeline
        
        Args:
            audio_data: Raw audio bytes
            language: User's preferred language ('en', 'hi', 'pt')
            
        Returns:
            Complete journal processing result with AI response
        """
        lang = language or self.default_language
        return self.coach.process_voice_journal(audio_data, lang)
    
    def get_chat_response(self, message: str, context: List[Dict] = None, language: str = None) -> Dict[str, any]:
        """
        Generate contextual chat response
        
        Args:
            message: User's text message
            context: Previous conversation context
            language: User's preferred language
            
        Returns:
            AI chat response with sentiment analysis
        """
        lang = language or self.default_language
        context = context or []
        
        # Analyze message sentiment
        sentiment = self.sentiment_analyzer.analyze_sentiment(message)
        
        # Generate response
        response_text = self.openai_agent.get_chat_response(message, context, lang)
        
        # Convert to audio
        response_audio = self.stt_tts.text_to_speech(response_text, lang)
        
        return {
            'response_text': response_text,
            'response_audio': response_audio,
            'sentiment': sentiment,
            'avatar_emotion': self._get_avatar_emotion(sentiment['mood'])
        }
    
    def get_help_response(self, query: str, language: str = None) -> Dict[str, any]:
        """
        Get app feature help and guidance
        
        Args:
            query: User's help question
            language: User's preferred language
            
        Returns:
            Helpful response with tutorial info
        """
        lang = language or self.default_language
        help_result = self.guide.get_help_response(query, lang)
        
        # Add voice response
        response_audio = self.stt_tts.text_to_speech(help_result['response_text'], lang)
        help_result['response_audio'] = response_audio
        
        return help_result
    
    def generate_affirmation(self, mood: str = None, language: str = None) -> Dict[str, any]:
        """
        Generate personalized affirmation
        
        Args:
            mood: Current user mood
            language: User's preferred language
            
        Returns:
            Affirmation with audio and avatar action
        """
        lang = language or self.default_language
        mood = mood or 'neutral'
        
        affirmation_result = self.extras.generate_daily_affirmation(mood, lang)
        
        # Add voice version
        affirmation_audio = self.stt_tts.text_to_speech(affirmation_result['text'], lang)
        affirmation_result['audio'] = affirmation_audio
        
        return affirmation_result
    
    def check_achievements(self, user_activity: Dict) -> List[Dict]:
        """
        Check for earned badges and achievements
        
        Args:
            user_activity: User's activity data
            
        Returns:
            List of earned badges
        """
        return self.extras.check_badges(user_activity)
    
    def recommend_music(self, mood: str, language: str = None) -> Dict[str, any]:
        """
        Get mood-based music recommendations
        
        Args:
            mood: Current user mood
            language: User's preferred language
            
        Returns:
            Music recommendations
        """
        lang = language or self.default_language
        return self.extras.recommend_music(mood, lang)
    
    def analyze_text_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyze text sentiment and mood
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result
        """
        return self.sentiment_analyzer.analyze_sentiment(text)
    
    def convert_text_to_speech(self, text: str, language: str = None) -> bytes:
        """
        Convert any text to natural speech
        
        Args:
            text: Text to convert
            language: Voice language
            
        Returns:
            Audio bytes
        """
        lang = language or self.default_language
        return self.stt_tts.text_to_speech(text, lang)
    
    def _get_avatar_emotion(self, mood: str) -> str:
        """Get appropriate avatar emotion for mood"""
        return self.extras.avatar_controller.get_expression(mood)
