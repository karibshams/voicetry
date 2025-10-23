from openai import OpenAI
from textblob import TextBlob
import json
from datetime import datetime
import os
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv
load_dotenv()
from voice import VoiceEngine
from prompt import Prompts
from juno_guide import JunoGuide

class JunoAssistant:
    """Main AI orchestrator with dual AI and unlimited memory"""
    CRISIS_KEYWORDS = [
        'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
        'cutting', 'die', 'worthless', 'want to die', 'better off dead',
        'no point living', 'hate myself', 'end my life'
    ]
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file!")
        
        self.client = OpenAI(api_key=api_key)
        self.voice = VoiceEngine()
        self.prompts = Prompts()
        self.juno_guide = JunoGuide()
        self.memory = []
        self.context = {'greeted': False}    
        print(" Juno Assistant initialized successfully")
    
    def process_voice(self, audio_data: bytes, context: str = 'juno') -> dict:
        """
        Main voice processing pipeline with context awareness
        
        Args:
            audio_data: Audio bytes from user
            context: 'juno' (default), 'coach', or 'journal'
        
        Returns:
            dict: Response with text, audio, mood, etc.
        """
        stt = self.voice.speech_to_text(audio_data)
        text = stt['text']
        lang = stt['language']

        if not text:
            return self._error("I couldn't hear you clearly", lang)
        
        if self._is_crisis(text):
            return self._handle_crisis(text, lang)
        elif self._is_guide_query(text):
            return self._handle_guide(text, lang)
        else:

            return self._handle_contextual(text, lang, context)
    
    def _handle_juno(self, text: str, lang: str) -> dict:
        """Main Juno AI - Wellness conversations"""
        
        sentiment = self._get_sentiment(text)
        system_prompt = self.prompts.get('juno', lang)
        messages = [{'role': 'system', 'content': system_prompt}]

        if self.memory and not self.context['greeted']:
            last = self.memory[-1]['user'][:80]
            messages.append({
                'role': 'system', 
                'content': f"Returning user. Last talked about: {last}"
            })
            self.context['greeted'] = True

        for m in self.memory[-10:]:
            messages.append({'role': 'user', 'content': m['user']})
            messages.append({'role': 'assistant', 'content': m['assistant']})
        
        messages.append({'role': 'user', 'content': text})
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=250,
            temperature=0.8
        )
        
        reply = response.choices[0].message.content
        audio = self.voice.text_to_speech(reply, lang, 'female')
        
        self._save_memory(text, reply, sentiment, lang, 'juno')
        
        return {
            'type': 'juno',
            'text': text,
            'reply': reply,
            'audio': audio,
            'mood': sentiment['mood'],
            'lang': lang
        }
    
    def _handle_guide(self, text: str, lang: str) -> dict:
        """Guide AI - App features"""
        app_info = self.juno_guide.search(text)
        system_prompt = self.prompts.get('guide', lang)
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Question: {text}\n\nApp Info:\n{app_info}\n\nExplain using both app details and your AI knowledge."}
        ]
        
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=180,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        audio = self.voice.text_to_speech(reply, lang, 'female')
        
        self._save_memory(text, f"[Guide] {reply}", {'mood': 'neutral'}, lang, 'guide')
        
        return {
            'type': 'guide',
            'text': text,
            'reply': reply,
            'audio': audio,
            'mood': 'neutral',
            'lang': lang
        }
    
    def _handle_crisis(self, text: str, lang: str) -> dict:
        """Crisis response"""
        
        reply = self.prompts.get('crisis', lang)
        audio = self.voice.text_to_speech(reply, lang, 'female')
        
        self._save_memory(text, f"[Crisis] {reply}", {'mood': 'crisis'}, lang, 'crisis')
        
        return {
            'type': 'crisis',
            'text': text,
            'reply': reply,
            'audio': audio,
            'mood': 'crisis',
            'lang': lang,
            'crisis': True
        }
    
    def _is_crisis(self, text: str) -> bool:
        """Check for crisis keywords"""
        return any(k in text.lower() for k in self.CRISIS_KEYWORDS)
    
    def _is_guide_query(self, text: str) -> bool:
        """Check if asking about app features"""
        keywords = [
            'how do i', 'how to', 'what is', 'explain', 'tell me about', 
            'subscription', 'profile', 'journal', 'page', 'feature',
            'use', 'work', 'setup', 'configure'
        ]
        return any(k in text.lower() for k in keywords)
    
    def _get_sentiment(self, text: str) -> dict:
        """Analyze sentiment"""
        blob = TextBlob(text)
        p = blob.sentiment.polarity
        
        if p > 0.3: mood = 'happy'
        elif p > 0: mood = 'calm'
        elif p > -0.3: mood = 'neutral'
        elif p > -0.6: mood = 'sad'
        else: mood = 'anxious'
        
        return {'mood': mood, 'polarity': p}
    
    def _save_memory(self, user: str, assistant: str, sentiment: dict, lang: str, ai_type: str):
        """Store in unlimited memory"""
        self.memory.append({
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'assistant': assistant,
            'sentiment': sentiment,
            'lang': lang,
            'ai_type': ai_type
        })
    
    def _error(self, msg: str, lang: str) -> dict:
        """Error response"""
        audio = self.voice.text_to_speech(msg, lang, 'female')
        return {'type': 'error', 'reply': msg, 'audio': audio, 'lang': lang}
    
    def save_memory(self, filepath: str = 'juno_memory.json'):
        """Save memory to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'memory': self.memory, 'context': self.context}, f, indent=2)
        print(f"Saved {len(self.memory)} conversations to {filepath}")
    
    def load_memory(self, filepath: str = 'juno_memory.json'):
        """Load memory from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.memory = data.get('memory', [])
                self.context = data.get('context', {'greeted': False})
            print(f"Loaded {len(self.memory)} conversations from {filepath}")
        except FileNotFoundError:
            print(f" No memory file found at {filepath}")
    
    def get_stats(self) -> dict:
        """Get memory statistics"""
        moods = [m['sentiment']['mood'] for m in self.memory if 'sentiment' in m]
        
        return {
            'total_conversations': len(self.memory),
            'moods': moods,
            'mood_distribution': {
                'happy': moods.count('happy'),
                'calm': moods.count('calm'),
                'neutral': moods.count('neutral'),
                'sad': moods.count('sad'),
                'anxious': moods.count('anxious'),
                'crisis': moods.count('crisis')
            },
            'languages': list(set(m['lang'] for m in self.memory)),
            'ai_types': list(set(m['ai_type'] for m in self.memory))
        }


