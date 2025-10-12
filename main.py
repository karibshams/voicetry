import openai
from textblob import TextBlob
import json
from datetime import datetime
import os
from typing import List, Dict, Optional, Union
from voice import VoiceEngine
from prompt import Prompts
from guide import AppGuide
class JunoAssistant:
    """Main AI orchestrator with dual AI and unlimited memory"""
    
    CRISIS_KEYWORDS = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
        'cutting', 'die', 'worthless', 'want to die', 'better off dead',
        'no point living', 'hate myself', 'end my life']
    
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.voice = VoiceEngine()
        self.prompts = Prompts()
        self.guide = AppGuide()
        
        # Unlimited memory
        self.memory = []
        self.context = {'greeted': False}
    
    def process_voice(self, audio_data: bytes) -> dict:
        """Main voice processing pipeline"""
        
        # 1. Speech to text
        stt = self.voice.speech_to_text(audio_data)
        text = stt['text']
        lang = stt['language']
        
        if not text:
            return self._error("I couldn't hear you clearly", lang)
        
        # 2. Route to appropriate AI
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
        
        # Build messages with ALL memory
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add greeting context for returning users
        if self.memory and not self.context['greeted']:
            last = self.memory[-1]['user'][:80]
            messages.append({'role': 'system', 'content': f"Returning user. Last talked about: {last}"})
            self.context['greeted'] = True
        
        # Add full conversation history
        for m in self.memory:
            messages.append({'role': 'user', 'content': m['user']})
            messages.append({'role': 'assistant', 'content': m['assistant']})
        
        messages.append({'role': 'user', 'content': text})
        
        # Get AI response
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=200,
            temperature=0.8
        )
        
        reply = response.choices[0].message.content
        audio = self.voice.text_to_speech(reply, lang, 'female')
        
        # Store in memory
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
        
        app_info = self.guide.search(text)
        system_prompt = self.prompts.get('guide', lang)
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Question: {text}\n\nApp Info:\n{app_info}\n\nExplain using both app details and your AI knowledge."}
        ]
        
        response = openai.ChatCompletion.create(
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
        keywords = ['how do i', 'how to', 'what is', 'explain', 'tell me about', 
                   'subscription', 'profile', 'journal', 'page', 'feature']
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
        print(f"✅ Saved {len(self.memory)} conversations")
    
    def load_memory(self, filepath: str = 'juno_memory.json'):
        """Load memory from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.memory = data.get('memory', [])
                self.context = data.get('context', {'greeted': False})
            print(f"✅ Loaded {len(self.memory)} conversations")
        except FileNotFoundError:
            print("⚠️  No memory file found")
    
    def get_stats(self) -> dict:
        """Get memory statistics"""
        return {
            'total': len(self.memory),
            'moods': [m['sentiment']['mood'] for m in self.memory if 'sentiment' in m],
            'languages': list(set(m['lang'] for m in self.memory)),
            'ai_types': list(set(m['ai_type'] for m in self.memory))
        }


# ==========================================
# TEST CODE
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("🧠 Juno Assistant System Tester")
    print("=" * 50)
    print("\nSelect what you want to test:")
    print("1. Initialize System")
    print("2. Test Sentiment Analysis")
    print("3. Test Query Routing")
    print("4. Test Memory Storage")
    print("5. Test System Stats")
    print("6. Test Memory Save/Load")
    print("7. Run All Tests")
    print("0. Exit")

    choice = input("\n👉 Enter your choice (0–7): ").strip()

    try:
        juno = None

        if choice == "0":
            print("\n👋 Exiting...")
            exit()

        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            print("\n1. Initializing...")
            juno = JunoAssistant()
            print("✅ All modules connected")

        if choice in ["2", "7"]:
            print("\n2. Testing sentiment...")
            test_texts = ["I'm so happy!", "I feel anxious", "Just okay"]
            for t in test_texts:
                s = juno._get_sentiment(t)
                print(f"✅ '{t}' → {s['mood']}")

        if choice in ["3", "7"]:
            print("\n3. Testing AI routing...")
            queries = [
                ("I'm feeling sad", "juno"),
                ("How do I use journal?", "guide"),
                ("I want to hurt myself", "crisis")
            ]
            for q, expected in queries:
                if juno._is_crisis(q):
                    route = "crisis"
                elif juno._is_guide_query(q):
                    route = "guide"
                else:
                    route = "juno"

                status = "✅" if route == expected else "❌"
                print(f"{status} '{q}' → {route}")

        if choice in ["4", "7"]:
            print("\n4. Testing memory...")
            juno._save_memory("Test message", "Test reply", {'mood': 'happy'}, 'en', 'juno')
            print(f"✅ Memory: {len(juno.memory)} conversations")

        if choice in ["5", "7"]:
            print("\n5. Testing stats...")
            stats = juno.get_stats()
            print(f"✅ Stats: {stats}")

        if choice in ["6", "7"]:
            print("\n6. Testing memory save/load...")
            juno.save_memory('test_memory.json')
            new_juno = JunoAssistant()
            new_juno.load_memory('test_memory.json')
            print(f"✅ Restored {len(new_juno.memory)} conversations")

        print("\n" + "=" * 50)
        print("✅ Test Complete")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 50)
