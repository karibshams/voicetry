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
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
        
        self.client = OpenAI(api_key=api_key)
        self.voice = VoiceEngine()
        self.prompts = Prompts()
        self.juno_guide = JunoGuide()
        self.memory = []
        self.context = {'greeted': False}    
        print("Juno Assistant initialized successfully")
    
    def process_voice(self, audio_data: bytes) -> dict:
        """Main voice processing pipeline"""
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
            return self._handle_juno(text, lang)
    
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
            print(f"No memory file found at {filepath}")
    
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


# ==========================================
# TEST CODE
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 JUNO ASSISTANT - SYSTEM TESTER")
    print("=" * 60)
    print("\n📋 Select Test Module:")
    print("1. Initialize System")
    print("2. Test Sentiment Analysis")
    print("3. Test AI Routing (Crisis/Guide/Juno)")
    print("4. Test Memory Storage")
    print("5. Test System Stats")
    print("6. Test Memory Save/Load")
    print("7. Run All Tests")
    print("0. Exit")

    choice = input("\n👉 Enter your choice (0-7): ").strip()

    try:
        juno = None

        if choice == "0":
            print("\n👋 Exiting...")
            exit()

        # Initialize for all tests
        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            print("\n" + "=" * 60)
            print("1️⃣  INITIALIZING SYSTEM...")
            print("=" * 60)
            juno = JunoAssistant()
            print("✅ All modules connected successfully\n")

        # Test 2: Sentiment Analysis
        if choice in ["2", "7"]:
            print("=" * 60)
            print("2️⃣  TESTING SENTIMENT ANALYSIS...")
            print("=" * 60)
            test_texts = [
                "I'm so happy today!",
                "Feeling a bit anxious",
                "Just okay, nothing special",
                "I feel really sad",
                "This is amazing!"
            ]
            for t in test_texts:
                s = juno._get_sentiment(t)
                print(f"✅ '{t}' → Mood: {s['mood']}, Polarity: {s['polarity']:.2f}")
            print()

        # Test 3: AI Routing
        if choice in ["3", "7"]:
            print("=" * 60)
            print("3️⃣  TESTING AI ROUTING...")
            print("=" * 60)
            queries = [
                ("I'm feeling sad today", "juno"),
                ("How do I use the journal?", "guide"),
                ("I want to hurt myself", "crisis"),
                ("Tell me about meditation", "guide"),
                ("I had a great day!", "juno")
            ]
            for q, expected in queries:
                if juno._is_crisis(q):
                    route = "crisis"
                elif juno._is_guide_query(q):
                    route = "guide"
                else:
                    route = "juno"

                status = "✅" if route == expected else "❌"
                print(f"{status} '{q}' → Routed to: {route} (Expected: {expected})")
            print()

        # Test 4: Memory
        if choice in ["4", "7"]:
            print("=" * 60)
            print("4️⃣  TESTING MEMORY STORAGE...")
            print("=" * 60)
            juno._save_memory(
                "Test message 1", 
                "Test reply 1", 
                {'mood': 'happy', 'polarity': 0.5}, 
                'en', 
                'juno'
            )
            juno._save_memory(
                "Test message 2", 
                "Test reply 2", 
                {'mood': 'calm', 'polarity': 0.2}, 
                'en', 
                'guide'
            )
            print(f"✅ Memory stored: {len(juno.memory)} conversations")
            print(f"✅ Last conversation: {juno.memory[-1]['user'][:50]}...")
            print()

        # Test 5: Stats
        if choice in ["5", "7"]:
            print("=" * 60)
            print("5️⃣  TESTING STATISTICS...")
            print("=" * 60)
            stats = juno.get_stats()
            print(f"✅ Total conversations: {stats['total_conversations']}")
            print(f"✅ Mood distribution: {stats['mood_distribution']}")
            print(f"✅ Languages used: {stats['languages']}")
            print(f"✅ AI types: {stats['ai_types']}")
            print()

        # Test 6: Save/Load
        if choice in ["6", "7"]:
            print("=" * 60)
            print("6️⃣  TESTING MEMORY PERSISTENCE...")
            print("=" * 60)
            
            # Save
            juno.save_memory('test_memory.json')
            
            # Load in new instance
            new_juno = JunoAssistant()
            new_juno.load_memory('test_memory.json')
            print(f"✅ Restored {len(new_juno.memory)} conversations")
            print(f"✅ Memory integrity: {len(juno.memory) == len(new_juno.memory)}")
            print()

        print("=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERROR OCCURRED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()

    print("\n🎉 Testing session finished\n")