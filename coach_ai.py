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
        # Convert speech to text
        stt_result = self.voice.speech_to_text(audio_data)
        user_text = stt_result['text']
        detected_lang = stt_result['language']
        
        if not user_text:
            return self._error_response("I couldn't hear you clearly", lang, gender)
        
        # Use detected language or user preference
        lang = detected_lang if detected_lang else lang
        self.user_context['lang'] = lang
        self.user_context['gender_preference'] = gender
        
        # Generate coaching response using exact coach prompt
        coach_reply = self._generate_coach_response(user_text, lang)
        
        # Convert response to speech with user's selected gender voice
        audio_reply = self.voice.text_to_speech(coach_reply, lang, gender)
        
        # Analyze sentiment
        sentiment = self._get_sentiment(user_text)
        
        self._save_conversation(user_text, coach_reply, lang, 'voice', None)
        
        return {
            'type': 'voice',
            'text_input': user_text,
            'coach_reply': coach_reply,
            'audio_reply': audio_reply,
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
        
        self._save_conversation(user_text, coach_reply, lang, 'text', None)
        
        return {
            'type': 'text',
            'text_input': user_text,
            'coach_reply': coach_reply,
            'audio_reply': audio_reply,
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
            max_tokens=70,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _get_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of user input"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        return {'mood': None, 'polarity': polarity}
    
    def _save_conversation(self, user_text: str, coach_reply: str, lang: str, input_type: str, sentiment: str = 'neutral'):
        """Store conversation in memory"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_text': user_text,
            'coach_reply': coach_reply,
            'lang': lang,
            'input_type': input_type,
            'sentiment': sentiment
        })
    
    def _error_response(self, message: str, lang: str, gender: str) -> Dict:
        """Return error response with voice and text"""
        audio = self.voice.text_to_speech(message, lang, gender)
        return {
            'type': 'error',
            'text_input': '',
            'coach_reply': message,
            'audio_reply': audio,
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
        return {
            'total_messages': len(self.conversation_history),
            'languages_used': list(set(e.get('lang', 'en') for e in self.conversation_history)),
            'session_start': self.user_context['session_start'],
            'current_language': self.user_context['lang'],
            'preferred_voice': self.user_context['gender_preference']
        }

from coach_ai import CoachAI

coach = CoachAI()

def test_text(text, lang='en'):
    """Test text input"""
    response = coach.process_text(text, lang=lang)
    
    print(f"\n💭 You: {response['text_input']}")
    print(f"💬 Coach: {response['coach_reply']}")

def text_chat(lang='en'):
    """Multi-turn text chat"""
    coach.set_user_context(lang=lang)
    print(f"\n💬 TEXT CHAT")
    print("Commands: 'lang' (change language), 'quit' (exit)\n")
    
    while True:
        print(f"[Lang: {lang}]", end=" ")
        msg = input("💭 You: ").strip()
        
        if msg.lower() == 'quit':
            break
        elif msg.lower() == 'lang':
            new_lang = input("Language (en/hi/pt): ").strip()
            if new_lang in ['en', 'hi', 'pt']:
                lang = new_lang
                coach.set_user_context(lang=lang)
                print(f"✅ Language changed to {lang}\n")
            else:
                print("❌ Invalid language\n")
        elif msg:
            response = coach.process_text(msg, lang=lang)
            print(f"💬 Coach: {response['coach_reply']}\n")

def show_stats():
    """Show session statistics"""
    stats = coach.get_stats()
    print("\n" + "="*50)
    print("📊 SESSION STATS")
    print("="*50)
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Languages: {', '.join(stats['languages_used']) if stats['languages_used'] else 'None'}")
    print(f"Current Language: {stats['current_language']}")
    print(f"Preferred Voice: {stats['preferred_voice']}")
    print(f"Session Start: {stats['session_start']}")

if __name__ == "__main__":
    try:
        while True:
            print("\n" + "="*50)
            print("💬 COACH AI - TEXT TESTING")
            print("="*50)
            print("1. Single Text Message")
            print("2. Text Chat (Multi-turn)")
            print("3. View Stats")
            print("4. Exit")
            print("-"*50)
            
            choice = input("Choose (1-4): ").strip()
            
            if choice == '1':
                text = input("Your message: ").strip()
                lang = input("Language (en/hi/pt) [en]: ").strip() or 'en'
                if text and lang in ['en', 'hi', 'pt']:
                    test_text(text, lang)
                else:
                    print("❌ Invalid input")
            
            elif choice == '2':
                lang = input("Language (en/hi/pt) [en]: ").strip() or 'en'
                if lang in ['en', 'hi', 'pt']:
                    text_chat(lang)
                else:
                    print("❌ Invalid input")
            
            elif choice == '3':
                show_stats()
            
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n👋 Bye!")