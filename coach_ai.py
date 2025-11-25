from openai import OpenAI
from textblob import TextBlob
from datetime import datetime
import os
from dotenv import load_dotenv
from voice import VoiceEngine
from prompt import Prompts

load_dotenv()


class CoachAI:
    """IDENTIFY → ACT → RELIEVE Life Coach AI"""

    PHASES = {
        'identify': {
            'en': "You are a supportive life coach. The user is sharing a challenge or stuck point. Listen carefully and identify the core issue without judgment. Ask ONE clarifying question to understand the root cause better. Keep response under 100 words. Be direct, encouraging, and practical.",
            'hi': "आप एक सहायक जीवन कोच हैं। उपयोगकर्ता एक चुनौती साझा कर रहे हैं। मूल समस्या की पहचान करें। ONE स्पष्टीकरण प्रश्न पूछें। 100 शब्दों से कम। सीधे, प्रोत्साहक और व्यावहारिक रहें।",
            'pt': "Você é um treinador de vida solidário. O usuário está compartilhando um desafio. Identifique o problema central. Faça UMA pergunta de esclarecimento. Menos de 100 palavras. Seja direto, encorajador e prático."
        },
        'act': {
            'en': "You are a practical action coach. The user has identified their stuck point. Now suggest ONE tiny, specific action they can take right now or today. Make it so small they cannot fail. Focus on momentum and progress over perfection. Keep response under 100 words. Be specific, motivating, and realistic.",
            'hi': "आप एक व्यावहारिक कार्य कोच हैं। अब ONE छोटी, विशिष्ट कार्रवाई सुझाएं जो वे तुरंत ले सकें। इतनी छोटी कि वह असफल न हो सके। गति और प्रगति पर ध्यान दें। 100 शब्दों से कम। विशिष्ट, प्रेरणादायक और यथार्थवादी रहें।",
            'pt': "Você é um treinador de ação prático. Agora sugira UMA ação pequena e específica que ele possa fazer agora. Tão pequena que não possa falhar. Foco no momentum e progresso. Menos de 100 palavras. Seja específico, motivador e realista."
        },
        'relieve': {
            'en': "You are an encouraging guide helping the user celebrate progress and feel relief. Acknowledge their effort and small wins. Share a short Bible verse (under 15 words) about strength, progress, or capability that empowers them. Keep response under 120 words. End with acknowledgment of progress and confidence in their ability.",
            'hi': "आप एक प्रोत्साहक गाइड हैं जो प्रगति का जश्न मनाने में मदद कर रहे हैं। प्रयास को स्वीकार करें। एक छोटी बाइबल वर्स (15 शब्दों से कम) साझा करें। 120 शब्दों से कम। प्रगति और क्षमता की स्वीकृति के साथ समाप्त करें।",
            'pt': "Você é um guia encorajador ajudando o usuário a celebrar o progresso. Reconheça o esforço e pequenas vitórias. Compartilhe um verso bíblico curto (menos de 15 palavras). Menos de 120 palavras. Termine com reconhecimento do progresso."
        }
    }

    CRISIS_KEYWORDS = [
        'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
        'cutting', 'die', 'worthless', 'want to die', 'better off dead',
        'no point living', 'hate myself', 'end my life'
    ]

    CRISIS_RESPONSE = {
        'en': "I hear you, and I'm truly concerned about you. What you're feeling is real, and you matter deeply to God and to me. You're not alone in this struggle. Please reach out immediately to someone you trust - a pastor, counselor, or trusted adult - or contact a crisis helpline. Your life has purpose. Would you like to try a calming breathing exercise together?",
        'hi': "मैं आपकी बात सुन रहा हूं और आपके बारे में चिंतित हूं। आप जो महसूस कर रहे हैं वह वास्तविक है। कृपया तुरंत किसी भरोसेमंद से संपर्क करें। आप अकेले नहीं हैं। क्या आप श्वास व्यायाम करना चाहेंगे?",
        'pt': "Eu ouço você e estou realmente preocupado. O que você está sentindo é real, e você é profundamente importante. Entre em contato imediatamente com alguém de confiança. Você não está sozinho. Gostaria de tentar um exercício de respiração?"
    }

    EMPOWERMENT_VERSES = {
        'en': [
            "I can do all things through Christ who strengthens me. - Philippians 4:13",
            "For we are God's masterpiece. - Ephesians 2:10",
            "You are capable of more than you know. - Proverbs 31:25",
            "He gives strength to the weary. - Isaiah 40:29",
            "With God, all things are possible. - Matthew 19:26"
        ],
        'hi': [
            "मैं मसीह के माध्यम से सब कुछ कर सकता हूं। - फिलिप्पियों 4:13",
            "हम ईश्वर की कृति हैं। - इफिसियों 2:10",
            "थकों को वह शक्ति देता है। - यशायाह 40:29"
        ],
        'pt': [
            "Posso fazer todas as coisas através de Cristo. - Filipenses 4:13",
            "Somos obra-prima de Deus. - Efésios 2:10",
            "Ele dá força aos cansados. - Isaías 40:29"
        ]
    }

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
        
        self.client = OpenAI(api_key=api_key)
        self.voice = VoiceEngine()
        self.memory = []
        self.phase = 'identify'
        self.entry_start = datetime.now()
        print("✅ CoachAI initialized - IDENTIFY → ACT → RELIEVE")

    def process_voice(self, audio_data: bytes, language: str = 'en', gender: str = 'female') -> dict:
        """Process voice input with STT → AI → TTS"""
        if language not in self.PHASES:
            language = 'en'

        stt_result = self.voice.speech_to_text(audio_data)
        user_text = stt_result['text']
        
        if not user_text:
            error_msg = "I couldn't hear you clearly. Could you please repeat?"
            audio = self.voice.text_to_speech(error_msg, language, gender)
            return {'text': error_msg, 'audio': audio, 'language': language, 'phase': self.phase}

        response_text = self._generate_response(user_text, language)
        response_audio = self.voice.text_to_speech(response_text, language, gender)

        return {
            'user_input': user_text,
            'response': response_text,
            'audio': response_audio,
            'language': language,
            'phase': self.phase
        }

    def process_text(self, user_text: str, language: str = 'en') -> dict:
        """Process text input"""
        if language not in self.PHASES:
            language = 'en'

        response_text = self._generate_response(user_text, language)

        return {
            'user_input': user_text,
            'response': response_text,
            'language': language,
            'phase': self.phase
        }

    def _generate_response(self, user_text: str, language: str) -> str:
        """Generate response based on current phase"""
        
        # Check for crisis
        if self._is_crisis(user_text):
            return self._handle_crisis(user_text, language)
        
        sentiment = self._analyze_sentiment(user_text)
        self.memory.append({
            'role': 'user',
            'text': user_text,
            'sentiment': sentiment,
            'phase': self.phase
        })

        conversation_context = "\n".join([
            f"{m['role'].capitalize()}: {m['text']}"
            for m in self.memory[-6:]
        ])

        system_msg = self.PHASES[self.phase][language]

        messages = [
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': f"Conversation:\n{conversation_context}"}
        ]

        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )

        coach_reply = response.choices[0].message.content

        # Add Bible verse in relieve phase
        if self.phase == 'relieve':
            import random
            verse = random.choice(self.EMPOWERMENT_VERSES[language])
            coach_reply += f"\n\n✨ {verse}"

        self.memory.append({
            'role': 'coach',
            'text': coach_reply,
            'phase': self.phase
        })

        self._advance_phase()

        return coach_reply

    def _advance_phase(self):
        """Move to next phase"""
        phases_order = ['identify', 'act', 'relieve']
        current_idx = phases_order.index(self.phase)
        if current_idx < len(phases_order) - 1:
            self.phase = phases_order[current_idx + 1]

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.3:
            return 'positive'
        elif polarity > 0:
            return 'neutral'
        elif polarity > -0.3:
            return 'slightly_negative'
        return 'negative'

    def get_memory(self) -> list:
        """Get full conversation memory"""
        return self.memory

    def clear_memory(self):
        """Clear memory for new coaching session"""
        self.memory = []
        self.phase = 'identify'
        self.entry_start = datetime.now()
        print("Memory cleared - Ready for new coaching session")

    def get_session_summary(self) -> dict:
        """Get current session summary"""
        return {
            'phase': self.phase,
            'messages': len(self.memory),
            'started_at': self.entry_start.isoformat(),
            'memory': self.memory
        }

    def _is_crisis(self, text: str) -> bool:
        """Check for crisis keywords"""
        return any(k in text.lower() for k in self.CRISIS_KEYWORDS)

    def _handle_crisis(self, user_text: str, language: str) -> str:
        """Handle crisis situation"""
        crisis_msg = self.CRISIS_RESPONSE[language]
        self.memory.append({
            'role': 'user',
            'text': user_text,
            'sentiment': 'crisis',
            'phase': 'crisis'
        })
        self.memory.append({
            'role': 'coach',
            'text': crisis_msg,
            'phase': 'crisis'
        })
        return crisis_msg


def main():
    """Simple main function for live chat with CoachAI"""
    
    print("\n" + "="*60)
    print("🏆 CoachAI - IDENTIFY → ACT → RELIEVE")
    print("="*60)
    print("Type 'quit' to exit | 'clear' to start new session | 'lang' to change language\n")
    
    try:
        coach = CoachAI()
    except ValueError as e:
        print(f"❌ Error: {e}")
        return
    
    language = 'en'
    
    while True:
        try:
            user_input = input(f"You ({coach.phase.upper()}): ").strip()
            
            if user_input.lower() == 'quit':
                print("\n👋 Great work! Keep taking small steps!\n")
                break
            
            if user_input.lower() == 'clear':
                coach.clear_memory()
                print("🔄 Memory cleared - New session started!\n")
                continue
            
            if user_input.lower() == 'lang':
                print("Available languages: en (English), hi (Hindi), pt (Portuguese)")
                language = input("Choose language: ").strip().lower()
                if language not in ['en', 'hi', 'pt']:
                    language = 'en'
                    print("Invalid language. Using English.\n")
                continue
            
            if not user_input:
                continue
            
            # Get response from AI
            response = coach.process_text(user_input, language=language)
            
            print(f"\nCoach ({response['phase'].upper()}): {response['response']}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session ended. Keep moving forward!\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()