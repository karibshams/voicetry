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
    
    TRAUMA_KEYWORDS = [
        'abuse', 'assault', 'sexually', 'raped', 'molested', 'attacked',
        'traumatized', 'violated', 'trauma'
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
        self.context = {'greeted': False, 'spiritual_tier': 1}    
        print("✅ Juno Assistant initialized successfully")
    
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
    
    def _handle_contextual(self, text: str, lang: str, context: str) -> dict:
        """Route to appropriate AI based on context"""
        if context == 'coach':
            return self._handle_coach(text, lang)
        else:
            return self._handle_juno(text, lang)
    
    def _handle_juno(self, text: str, lang: str) -> dict:
        """Main Juno AI - Christian wellness conversations with tiered responses"""
        
        sentiment = self._get_sentiment(text)
        tier = self._detect_spiritual_tier(text, sentiment)
        
        system_prompt = self.prompts.get('juno', lang)
        tier_guidance = self._get_tier_guidance(tier)
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'system', 'content': tier_guidance}
        ]

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
        
        self.context['spiritual_tier'] = max(self.context['spiritual_tier'], tier)
        self._save_memory(text, reply, sentiment, lang, 'juno', tier)
        
        return {
            'type': 'juno',
            'text': text,
            'reply': reply,
            'audio': audio,
            'mood': sentiment['mood'],
            'lang': lang,
            'tier': tier
        }
    
    def _handle_coach(self, text: str, lang: str) -> dict:
        """Life Coach AI - Christian motivational guidance"""
        
        sentiment = self._get_sentiment(text)
        system_prompt = self.prompts.get('coach', lang)
        
        messages = [{'role': 'system', 'content': system_prompt}]
        
        for m in self.memory[-5:]:
            if m.get('ai_type') == 'coach':
                messages.append({'role': 'user', 'content': m['user']})
                messages.append({'role': 'assistant', 'content': m['assistant']})
        
        messages.append({'role': 'user', 'content': text})
        
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=250,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        audio = self.voice.text_to_speech(reply, lang, 'male')
        
        self._save_memory(text, reply, sentiment, lang, 'coach', 5)
        
        return {
            'type': 'coach',
            'text': text,
            'reply': reply,
            'audio': audio,
            'mood': sentiment['mood'],
            'lang': lang
        }
    
    def _handle_guide(self, text: str, lang: str) -> dict:
        """Guide AI - App features"""
        app_info = self.juno_guide.guide(text)
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
        
        self._save_memory(text, f"[Guide] {reply}", {'mood': 'neutral'}, lang, 'guide', 0)
        
        return {
            'type': 'guide',
            'text': text,
            'reply': reply,
            'audio': audio,
            'mood': 'neutral',
            'lang': lang
        }
    
    def _handle_crisis(self, text: str, lang: str) -> dict:
        """Crisis response with Christian comfort"""
        
        reply = self.prompts.get('crisis', lang)
        audio = self.voice.text_to_speech(reply, lang, 'female')
        
        self._save_memory(text, f"[Crisis] {reply}", {'mood': 'crisis'}, lang, 'crisis', 1)
        
        return {
            'type': 'crisis',
            'text': text,
            'reply': reply,
            'audio': audio,
            'mood': 'crisis',
            'lang': lang,
            'crisis': True
        }
    
    def _detect_spiritual_tier(self, text: str, sentiment: dict) -> int:
        """
        Detect spiritual/emotional tier for response
        Tier 1: Comfort (pain, fear, trauma)
        Tier 2: Reflection (processing, confusion)
        Tier 3: Hope (starting to heal)
        Tier 4: Truth (open to spiritual guidance)
        Tier 5: Action (goal-setting, accountability)
        """
        text_lower = text.lower()
        
        if any(k in text_lower for k in self.TRAUMA_KEYWORDS):
            return 1
        
        if sentiment['mood'] in ['anxious', 'sad'] and sentiment['polarity'] < -0.4:
            return 1
        
        question_words = ['why', 'how', 'what', 'confused', 'understand', 'make sense']
        if any(w in text_lower for w in question_words):
            return 2
        
        hope_words = ['better', 'trying', 'want to', 'hope', 'maybe', 'starting']
        if any(w in text_lower for w in hope_words):
            return 3
        
        spiritual_words = ['god', 'pray', 'faith', 'bible', 'jesus', 'scripture', 'forgive']
        if any(w in text_lower for w in spiritual_words):
            return 4
        
        action_words = ['goal', 'plan', 'do', 'change', 'improve', 'grow', 'start']
        if any(w in text_lower for w in action_words):
            return 5
        
        return max(2, self.context['spiritual_tier'])
    
    def _get_tier_guidance(self, tier: int) -> str:
        """Get response guidance based on spiritual tier"""
        guidance = {
            1: "Tier 1 - COMFORT: Validate pain deeply. Never minimize trauma. Say 'What happened was not your fault. You are not alone.' Emphasize safety and worth. Encourage reaching out to pastor, counselor, or trusted adult. No Scripture yet - just compassion.",
            2: "Tier 2 - REFLECTION: Ask gentle reflective questions. Help process emotions. Listen more than advise. Begin subtle Christian perspective: 'God sees your struggle.' No pressure.",
            3: "Tier 3 - HOPE: Introduce gentle hope. 'God's heart breaks with yours. Healing is possible.' Build trust. Suggest prayer or journaling if appropriate.",
            4: "Tier 4 - TRUTH: User is ready for biblical truth. Introduce Scripture gently. Explain forgiveness as freedom, not obligation. 'God calls us to forgive - not to excuse pain, but to set us free.'",
            5: "Tier 5 - ACTION: Focus on practical faith-based steps. Break goals into small actions. Encourage prayer for strength. Celebrate progress. Build accountability."
        }
        return guidance.get(tier, guidance[2])
    
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
    
    def _save_memory(self, user: str, assistant: str, sentiment: dict, lang: str, ai_type: str, tier: int = 0):
        """Store in unlimited memory"""
        self.memory.append({
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'assistant': assistant,
            'sentiment': sentiment,
            'lang': lang,
            'ai_type': ai_type,
            'tier': tier
        })
    
    def _error(self, msg: str, lang: str) -> dict:
        """Error response"""
        audio = self.voice.text_to_speech(msg, lang, 'female')
        return {'type': 'error', 'reply': msg, 'audio': audio, 'lang': lang}
    
    def save_memory(self, filepath: str = 'juno_memory.json'):
        """Save memory to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'memory': self.memory, 'context': self.context}, f, indent=2)
        print(f"✅ Saved {len(self.memory)} conversations to {filepath}")
    
    def load_memory(self, filepath: str = 'juno_memory.json'):
        """Load memory from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.memory = data.get('memory', [])
                self.context = data.get('context', {'greeted': False, 'spiritual_tier': 1})
            print(f"Loaded {len(self.memory)} conversations from {filepath}")
        except FileNotFoundError:
            print(f"ℹNo memory file found at {filepath}")
    
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
            'ai_types': list(set(m['ai_type'] for m in self.memory)),
            'current_spiritual_tier': self.context.get('spiritual_tier', 1)
        }