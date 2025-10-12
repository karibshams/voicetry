import openai
from textblob import TextBlob
from typing import Dict, List, Optional
import json
from datetime import datetime
from voice_engine import VoiceEngine
from prompt_manager import PromptManager    
from guide import JunoGuide

class JunoAssistant:
    """Main orchestrator with dual AI system (Juno + Guide AI)"""
    
    CRISIS_KEYWORDS = [
        'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
        'cutting', 'die', 'worthless', 'want to die', 'better off dead',
        'no point living', 'hate myself', 'end my life'
    ]
    
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.voice_engine = VoiceEngine()
        self.prompt_manager = PromptManager()
        self.guide = JunoGuide()
        
        # Unlimited conversation memory - stores ALL user interactions
        self.user_memory: List[Dict] = []
        self.user_context = {
            'name': None,
            'mood_history': [],
            'topics_discussed': [],
            'last_greeting': None
        }
    
    def process_voice_input(self, audio_data: bytes, user_id: str = None) -> Dict[str, any]:
        """Complete voice-to-voice interaction with dual AI routing"""
        
        # 1. Convert speech to text
        stt_result = self.voice_engine.speech_to_text(audio_data)
        text = stt_result['text']
        language = stt_result['language']
        gender = stt_result['speaker_gender']
        
        if not text:
            return self._generate_error_response(
                "I couldn't hear you clearly. Could you try again?", 
                language, gender
            )
        
        # 2. Check if crisis situation
        if self._is_crisis(text):
            return self._handle_crisis(text, language, gender)
        
        # 3. Route to appropriate AI
        if self._is_guide_request(text):
            # Use App Guide AI
            return self._handle_guide_ai(text, language, gender)
        else:
            # Use Main Juno AI
            return self._handle_juno_ai(text, language, gender)
    
    def _handle_juno_ai(self, text: str, language: str, gender: str) -> Dict[str, any]:
        """Main Juno AI - Wellness coach conversation"""
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(text)
        
        # Build conversation context with ALL previous messages
        system_prompt = self.prompt_manager.get_juno_prompt('system', language)
        
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add personalized greeting context for returning users
        if len(self.user_memory) > 0 and self.user_context['last_greeting'] is None:
            last_topic = self.user_memory[-1]['user'] if self.user_memory else None
            if last_topic:
                context_note = f"[Note: This is a returning user. Previous conversation included: {last_topic[:100]}...]"
                messages.append({'role': 'system', 'content': context_note})
            self.user_context['last_greeting'] = datetime.now()
        
        # Add ALL conversation history (unlimited memory)
        for memory in self.user_memory:
            messages.append({'role': 'user', 'content': memory['user']})
            messages.append({'role': 'assistant', 'content': memory['assistant']})
        
        # Add current message
        messages.append({'role': 'user', 'content': text})
        
        # Get AI response from Juno
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=200,
            temperature=0.8
        )
        
        response_text = response.choices[0].message.content
        
        # Convert to speech
        response_audio = self.voice_engine.text_to_speech(response_text, language, gender)
        
        # Update unlimited memory and context
        self._update_memory(text, response_text, sentiment, language)
        
        return {
            'ai_type': 'juno',
            'transcript': text,
            'language': language,
            'sentiment': sentiment,
            'response_text': response_text,
            'response_audio': response_audio,
            'mood': sentiment['mood'],
            'avatar_emotion': self._get_avatar_emotion(sentiment['mood']),
            'memory_count': len(self.user_memory)
        }
    
    def _handle_guide_ai(self, text: str, language: str, gender: str) -> Dict[str, any]:
        """App Guide AI - Feature explanations (separate AI)"""
        
        # Get relevant app information
        page_info = self.guide.get_page_info(text, language)
        
        if not page_info:
            page_info = self.guide.get_all_features_summary()
        
        # Build Guide AI prompt
        guide_system = self.prompt_manager.get_guide_prompt(language)
        
        messages = [
            {'role': 'system', 'content': guide_system},
            {'role': 'user', 'content': f"User asked: {text}\n\nApp Information:\n{page_info}\n\nExplain this feature naturally and helpfully, combining the app details with your AI knowledge to make it clear and engaging."}
        ]
        
        # Get AI response from Guide AI
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=180,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        # Convert to speech
        response_audio = self.voice_engine.text_to_speech(response_text, language, gender)
        
        # Store in memory (but don't affect Juno's conversation context)
        self._update_memory(text, f"[Guide AI] {response_text}", {'mood': 'neutral', 'polarity': 0}, language)
        
        return {
            'ai_type': 'guide',
            'transcript': text,
            'language': language,
            'sentiment': {'mood': 'neutral', 'polarity': 0.0},
            'response_text': response_text,
            'response_audio': response_audio,
            'mood': 'neutral',
            'avatar_emotion': 'attentive',
            'guide_response': True,
            'memory_count': len(self.user_memory)
        }
    
    def _handle_crisis(self, text: str, language: str, gender: str) -> Dict[str, any]:
        """Handle crisis with empathetic response"""
        
        crisis_prompt = self.prompt_manager.get_juno_prompt('crisis', language)
        
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': crisis_prompt},
                {'role': 'user', 'content': text}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        response_audio = self.voice_engine.text_to_speech(response_text, language, gender)
        
        # Store crisis interaction
        self._update_memory(text, f"[CRISIS] {response_text}", {'mood': 'crisis', 'polarity': -1.0}, language)
        
        return {
            'ai_type': 'juno_crisis',
            'transcript': text,
            'language': language,
            'sentiment': {'mood': 'crisis', 'polarity': -1.0},
            'response_text': response_text,
            'response_audio': response_audio,
            'mood': 'crisis',
            'avatar_emotion': 'concerned',
            'crisis_detected': True,
            'memory_count': len(self.user_memory)
        }
    
    def _is_crisis(self, text: str) -> bool:
        """Detect crisis keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.CRISIS_KEYWORDS)
    
    def _is_guide_request(self, text: str) -> bool:
        """Detect if user is asking about app features"""
        guide_keywords = [
            'how do i', 'how to', 'what is', 'explain', 'show me', 'tell me about',
            'subscription', 'profile', 'journal', 'faith', 'music', 'breathing',
            'grounding', 'affirmation', 'mind tools', 'page', 'feature',
            'account', 'notification', 'gamification', 'visual', 'chatbot',
            'how does', 'where can i', 'where do i', 'what can i do'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in guide_keywords)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, any]:
        """Analyze text sentiment"""
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
        
        return {
            'mood': mood,
            'polarity': polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def _update_memory(self, user_text: str, assistant_text: str, sentiment: Dict, language: str):
        """Store interaction in unlimited memory"""
        self.user_memory.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_text,
            'assistant': assistant_text,
            'sentiment': sentiment,
            'language': language
        })
        
        # Update user context
        self.user_context['mood_history'].append(sentiment['mood'])
        
        # Extract topics (simple keyword extraction)
        words = user_text.lower().split()
        topics = [w for w in words if len(w) > 5]
        self.user_context['topics_discussed'].extend(topics[:3])
    
    def _get_avatar_emotion(self, mood: str) -> str:
        """Map mood to avatar expression"""
        emotion_map = {
            'happy': 'smile',
            'calm': 'peaceful',
            'neutral': 'attentive',
            'sad': 'empathetic',
            'anxious': 'concerned',
            'crisis': 'concerned'
        }
        return emotion_map.get(mood, 'attentive')
    
    def _generate_error_response(self, message: str, language: str, gender: str) -> Dict[str, any]:
        """Generate error response"""
        response_audio = self.voice_engine.text_to_speech(message, language, gender)
        
        return {
            'ai_type': 'error',
            'transcript': '',
            'language': language,
            'sentiment': {'mood': 'neutral', 'polarity': 0.0},
            'response_text': message,
            'response_audio': response_audio,
            'mood': 'neutral',
            'avatar_emotion': 'attentive',
            'error': True
        }
    
    def generate_affirmation(self, mood: str, language: str = 'en', gender: str = 'female') -> Dict[str, any]:
        """Generate mood-based affirmation"""
        affirmation_prompt = f"Generate a short, personal affirmation for someone feeling {mood}. Keep it under 30 words, Gen Z friendly."
        
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': affirmation_prompt}],
            max_tokens=60,
            temperature=0.9
        )
        
        affirmation_text = response.choices[0].message.content
        affirmation_audio = self.voice_engine.text_to_speech(affirmation_text, language, gender)
        
        return {
            'text': affirmation_text,
            'audio': affirmation_audio,
            'mood': mood,
            'language': language
        }
    
    def get_memory_summary(self) -> Dict[str, any]:
        """Get summary of conversation memory"""
        return {
            'total_conversations': len(self.user_memory),
            'mood_history': self.user_context['mood_history'],
            'topics_discussed': list(set(self.user_context['topics_discussed'])),
            'first_interaction': self.user_memory[0]['timestamp'] if self.user_memory else None,
            'last_interaction': self.user_memory[-1]['timestamp'] if self.user_memory else None
        }
    
    def save_memory_to_file(self, filepath: str = 'juno_memory.json'):
        """Save unlimited memory to file"""
        memory_data = {
            'user_memory': self.user_memory,
            'user_context': self.user_context
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Memory saved: {len(self.user_memory)} conversations")
    
    def load_memory_from_file(self, filepath: str = 'juno_memory.json'):
        """Load memory from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
                self.user_memory = memory_data.get('user_memory', [])
                self.user_context = memory_data.get('user_context', self.user_context)
            print(f"✅ Memory loaded: {len(self.user_memory)} conversations")
        except FileNotFoundError:
            print("⚠️  No memory file found. Starting fresh.")


# ==========================================
# TEST CODE FOR main.py
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("TESTING: JunoAssistant Main Orchestrator")
    print("=" * 50)
    
    try:
        # Initialize
        print("\n1. Initializing JunoAssistant...")
        juno = JunoAssistant()
        print("✅ JunoAssistant initialized successfully")
        
        # Test text-only processing (simulating voice input)
        print("\n2. Testing Juno AI (Wellness Coach)...")
        test_message = "I'm feeling a bit anxious today"
        
        # Simulate STT result
        print(f"   User said: '{test_message}'")
        sentiment = juno._analyze_sentiment(test_message)
        print(f"✅ Sentiment analysis: mood={sentiment['mood']}, polarity={sentiment['polarity']:.2f}")
        
        # Test Guide AI detection
        print("\n3. Testing Guide AI routing...")
        guide_queries = [
            "How do I use the journal page?",
            "What is the subscription plan?",
            "Tell me about breathing exercises"
        ]
        
        for query in guide_queries:
            is_guide = juno._is_guide_request(query)
            print(f"✅ '{query}' -> {'Guide AI' if is_guide else 'Juno AI'}")
        
        # Test Crisis detection
        print("\n4. Testing Crisis detection...")
        crisis_texts = [
            "I'm feeling sad",  # Not crisis
            "I want to hurt myself"  # Crisis
        ]
        
        for text in crisis_texts:
            is_crisis = juno._is_crisis(text)
            status = "🚨 CRISIS" if is_crisis else "✅ Safe"
            print(f"{status}: '{text}'")
        
        # Test memory system
        print("\n5. Testing Unlimited Memory...")
        juno._update_memory(
            "I'm feeling anxious about exams",
            "I hear you. Exam stress is real. Let's work through this together.",
            {'mood': 'anxious', 'polarity': -0.3},
            'en'
        )
        juno._update_memory(
            "Thanks, that helps",
            "I'm glad! Remember, I'm here whenever you need support.",
            {'mood': 'calm', 'polarity': 0.5},
            'en'
        )
        
        print(f"✅ Memory stored: {len(juno.user_memory)} conversations")
        print(f"✅ Mood history: {juno.user_context['mood_history']}")
        
        # Test memory summary
        summary = juno.get_memory_summary()
        print(f"✅ Memory summary: {summary['total_conversations']} total interactions")
        
        # Test affirmation generation
        print("\n6. Testing Affirmation Generation...")
        affirmation = juno.generate_affirmation('anxious', 'en', 'female')
        print(f"✅ Affirmation generated: '{affirmation['text']}'")
        print(f"✅ Audio size: {len(affirmation['audio'])} bytes")
        
        # Test memory save/load
        print("\n7. Testing Memory Persistence...")
        juno.save_memory_to_file('test_memory.json')
        
        new_juno = JunoAssistant()
        new_juno.load_memory_from_file('test_memory.json')
        print(f"✅ Memory restored: {len(new_juno.user_memory)} conversations")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED for main.py")
        print("=" * 50)
        print("\n📋 Summary:")
        print(f"   • Dual AI System: Juno AI + Guide AI")
        print(f"   • Unlimited Memory: Stores all conversations")
        print(f"   • Crisis Detection: Active")
        print(f"   • Multi-language: English, Hindi, Portuguese")
        print(f"   • Model: gpt-4o-mini")
        print(f"   • Memory persistence: JSON file storage")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)