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
            raise ValueError("OPENAI_API_KEY not found in .env file!")
        
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
        print("CoachAI initialized successfully")
    
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
        
        self._save_conversation(user_text, coach_reply, lang, 'voice', sentiment['mood'])
        
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
        coach_reply = self._generate_coach_response(user_text, lang)
        audio_reply = self.voice.text_to_speech(coach_reply, lang, gender)
        sentiment = self._get_sentiment(user_text)
        
        self._save_conversation(user_text, coach_reply, lang, 'text', sentiment['mood'])
        
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
        system_prompt = Prompts.get('coach', lang)
        
        messages = [{'role': 'system', 'content': system_prompt}]
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

from coach_ai import CoachAI

coach = CoachAI()

def test_text(text, lang='en'):
    """Test text input"""
    response = coach.process_text(text, lang=lang)
    
    print(f"\n💭 You: {response['text_input']}")
    print(f"💬 Coach: {response['coach_reply']}")
    print(f"😊 Mood: {response['sentiment']}")

def text_chat():
    """Multi-turn text chat"""
    lang = 'en'
    
    coach.set_user_context(lang=lang)
    print(f"\n💬 TEXT CHAT | Lang: {lang}")
    print("Commands: 'lang' (change language), 'quit' (exit)")
    
    while True:
        msg = input("\n💭 You: ").strip()
        
        if msg.lower() == 'quit':
            break
        elif msg.lower() == 'lang':
            lang = input("Language (en/hi/pt): ").strip()
            if lang in ['en', 'hi', 'pt']:
                coach.set_user_context(lang=lang)
                print(f"✅ Language changed to {lang}")
        elif msg:
            response = coach.process_text(msg, lang=lang)
            print(f"💬 Coach: {response['coach_reply']}")
            print(f"😊 Mood: {response['sentiment']}")

def show_stats():
    """Show session statistics"""
    stats = coach.get_stats()
    print("\n" + "="*50)
    print("📊 SESSION STATS")
    print("="*50)
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Moods: {', '.join(stats['moods']) if stats['moods'] else 'None'}")
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
                    text_chat()
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