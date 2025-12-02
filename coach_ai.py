import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from textblob import TextBlob

from voice import VoiceEngine
from prompt import Prompts

load_dotenv()

class CoachAI:
    """Scalable Christian Life Coach AI with flexible voice and text support"""
    
    def __init__(self):
        """Initialize Coach AI with voice engine and OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
        
        self.client = OpenAI(api_key=api_key)
        self.voice = VoiceEngine()
        self.prompts = Prompts()
        self.conversation_history = []
        self.user_context = {
            'lang': 'en',
            'gender_preference': 'female',
            'name': 'User',
            'session_start': datetime.now().isoformat()
        }
        print("✅ CoachAI initialized successfully")
    
    def process_voice(self, audio_data: bytes, lang: str = 'en', gender: str = 'female') -> Dict:
        """
        Process voice input and return voice + text response
        Uses Guided Micro-Step Coaching approach (under 70 words, empathetic, actionable)
        
        Args:
            audio_data: Audio bytes (WAV format)
            lang: 'en', 'hi', or 'pt' - user selected language
            gender: 'male' or 'female' - user selected voice gender
        
        Returns:
            dict: {text_input, coach_reply, audio_reply, sentiment, lang, gender}
        """
        stt_result = self.voice.speech_to_text(audio_data)
        user_text = stt_result['text']
        detected_lang = stt_result['language']
        
        if not user_text:
            return self._error_response("I couldn't hear you clearly", lang, gender)
        lang = detected_lang if detected_lang else lang
        self.user_context['lang'] = lang
        self.user_context['gender_preference'] = gender
        coach_reply = self._generate_coach_response(user_text, lang)
        audio_reply = self.voice.text_to_speech(coach_reply, lang, gender)
        sentiment = self._get_sentiment(user_text)
        
        self._save_conversation(user_text, coach_reply, lang, 'voice')
        
        return {
            'type': 'voice',
            'text_input': user_text,
            'coach_reply': coach_reply,
            'audio_reply': audio_reply,
            'sentiment': sentiment['mood'],
            'lang': lang,
            'gender': gender,
            'timestamp': datetime.now().isoformat()
        }
    
    def process_text(self, user_text: str, lang: str = 'en', gender: str = 'female') -> Dict:
        """
        Process text input and return text + voice response
        Uses Guided Micro-Step Coaching approach (under 70 words, empathetic, actionable)
        
        Args:
            user_text: User input text
            lang: 'en', 'hi', or 'pt' - user selected language
            gender: 'male' or 'female' - user selected voice gender
        
        Returns:
            dict: {text_input, coach_reply, audio_reply, sentiment, lang, gender}
        """
        if not user_text or not user_text.strip():
            return self._error_response("Please share what's on your mind", lang, gender)
        
        user_text = user_text.strip()
        self.user_context['lang'] = lang
        self.user_context['gender_preference'] = gender
        
        # Generate coaching response using exact coach prompt
        coach_reply = self._generate_coach_response(user_text, lang)
        
        # Convert response to speech with user's selected gender voice
        audio_reply = self.voice.text_to_speech(coach_reply, lang, gender)
        
        # Analyze sentiment
        sentiment = self._get_sentiment(user_text)
        
        self._save_conversation(user_text, coach_reply, lang, 'text')
        
        return {
            'type': 'text',
            'text_input': user_text,
            'coach_reply': coach_reply,
            'audio_reply': audio_reply,
            'sentiment': sentiment['mood'],
            'lang': lang,
            'gender': gender,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_coach_response(self, user_text: str, lang: str) -> str:
        """
        Generate personalized coaching response using exact coach prompt from Prompts.COACH
        Guided Micro-Step Coaching style: empathy + 2-3 tiny doable actions
        
        Args:
            user_text: User input
            lang: Language code ('en', 'hi', 'pt')
        
        Returns:
            str: Coaching response (under 70 words as per prompt)
        """
        # Get exact COACH prompt from prompt.py Prompts.COACH[lang]
        system_prompt = Prompts.get('coach', lang)
        
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Include recent conversation context for continuity
        recent_history = self.conversation_history[-4:] if len(self.conversation_history) > 0 else []
        for entry in recent_history:
            messages.append({'role': 'user', 'content': entry['user_text']})
            messages.append({'role': 'assistant', 'content': entry['coach_reply']})
        
        messages.append({'role': 'user', 'content': user_text})
        
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=120,
            temperature=0.6
        )
        
        return response.choices[0].message.content
    
    def _get_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of user input"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.3:
            mood = 'happy'
        elif polarity > 0:
            mood = 'calm'
        elif polarity > -0.3:
            mood = 'neutral'
        elif polarity > -0.6:
            mood = 'sad'
        else:
            mood = 'anxious'
        
        return {'mood': mood, 'polarity': polarity}
    
    def _save_conversation(self, user_text: str, coach_reply: str, lang: str, input_type: str):
        """Store conversation in memory"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_text': user_text,
            'coach_reply': coach_reply,
            'lang': lang,
            'input_type': input_type
        })
    
    def _error_response(self, message: str, lang: str, gender: str) -> Dict:
        """Return error response with voice and text"""
        audio = self.voice.text_to_speech(message, lang, gender)
        return {
            'type': 'error',
            'text_input': '',
            'coach_reply': message,
            'audio_reply': audio,
            'sentiment': 'neutral',
            'lang': lang,
            'gender': gender,
            'timestamp': datetime.now().isoformat()
        }
    
    def set_user_context(self, name: str = None, lang: str = None, gender: str = None):
        """
        Update user context for personalization
        
        Args:
            name: User's name
            lang: Preferred language ('en', 'hi', 'pt')
            gender: Preferred coach voice gender ('male', 'female')
        """
        if name:
            self.user_context['name'] = name
        if lang:
            self.user_context['lang'] = lang
        if gender:
            self.user_context['gender_preference'] = gender
    
    def get_conversation_history(self, limit: int = None) -> list:
        """Get conversation history (backend handles persistence)"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear all conversation history"""
        self.conversation_history = []
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        moods = [entry.get('sentiment', 'neutral') for entry in self.get_conversation_history()]
        
        return {
            'total_messages': len(self.conversation_history),
            'moods': list(set(moods)),
            'languages_used': list(set(e.get('lang', 'en') for e in self.conversation_history)),
            'session_start': self.user_context['session_start'],
            'current_language': self.user_context['lang'],
            'preferred_voice': self.user_context['gender_preference']
        }