from openai import OpenAI
from textblob import TextBlob
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Suppress httpx logging
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR)


class PhaseConfig:
    """Configuration for journal phases."""
    
    PHASES = {
        'feel': {
            'en': "You are a gentle, emotionally safe companion. The user is sharing their feelings. Listen deeply and validate without judgment. Show warmth and care. Ask ONE simple reflective question. Keep response under 70 words. Be warm, safe, calm. No dramatic language.",
            'hi': "आप एक कोमल, भावनात्मक रूप से सुरक्षित साथी हैं। उपयोगकर्ता अपनी भावनाएं साझा कर रहे हैं। गहराई से सुनें और मान्य करें। ONE सरल प्रश्न पूछें। 70 शब्दों से कम। कोमल और शांत रहें।",
            'pt': "Você é um companheiro gentil e seguro. Ouça profundamente e valide sem julgamento. Faça UMA pergunta simples. Menos de 70 palavras. Seja gentil e calmo."
        },
        'understand': {
            'en': "You are a thoughtful, gentle guide in the UNDERSTAND phase. Ask ONE meaningful question to help them explore their feelings deeper. Keep response under 70 words. Be soft and supportive. No judgement. Direct and simple language only. After this phase comes RELIEVE where you will NOT ask questions.",
            'hi': "आप UNDERSTAND चरण में एक विचारशील, कोमल गाइड हैं। ONE प्रश्न पूछें। 70 शब्दों से कम। कोमल, सहायक, सरल भाषा। अगले चरण में कोई सवाल नहीं।",
            'pt': "Você é um guia atencioso e gentil na fase UNDERSTAND. Faça UMA pergunta significativa. Menos de 70 palavras. Seja gentil e direto. Na próxima fase sem perguntas."
        },
        'relieve': {
            'en': "You are a calm, supportive guide in the RELIEVE phase. Acknowledge their pain with warmth. Suggest ONE simple coping practice (breathing, stillness, reflection, grounding, or self-care). ABSOLUTELY NO QUESTIONS - not a single question mark. Only comfort, reassurance, and practice suggestions. Keep under 80 words. Vary the coping practice suggestions. Simple, direct language.",
            'hi': "आप RELIEVE चरण में एक शांत, सहायक गाइड हैं। उनकी भावनाओं को स्वीकार करें। एक सरल प्रथा सुझाएं। कोई सवाल नहीं - कोई प्रश्न चिह्न नहीं। सिर्फ आराम, आश्वासन और प्रथा। 80 शब्दों से कम। विविध सुझाव दें।",
            'pt': "Você é um guia calmo e solidário na fase RELIEVE. Reconheça seus sentimentos. Sugira uma prática simples. SEM PERGUNTAS - nenhum ponto de interrogação. Apenas conforto, reasseguramento e sugestões de práticas. Menos de 80 palavras. Varie as sugestões."
        }
    }
    
    PHASES_ORDER = ['feel', 'understand', 'relieve']
    SUPPORTED_LANGUAGES = ['en', 'hi', 'pt']


class CrisisConfig:
    """Crisis detection and response configuration."""
    
    KEYWORDS = [
        "suicide", "kill myself", "end it all", "end my life", "take my life",
        "hurt myself", "self harm", "self-harm", "cutting", "cut myself",
        "i want to die", "want to die", "i want to end everything",
        "better off dead", "no point living", "life is meaningless",
        "i hate my life", "i hate myself", "i don't want to live",
        "i'm done with life", "life is pointless", "wish i was dead",
        "wish i could disappear", "i don't care anymore", "i can't do this anymore",
        "i can't go on", "i want it to stop", "i feel empty", "i'm tired of everything",
        "i'm giving up", "i feel hopeless", "i feel useless", "nothing matters",
        "nobody cares", "i'm a burden", "everyone is better without me",
        "i'm worthless", "worthless", "nothing will change", "i have no reason to live",
        "no hope", "hopeless", "lifeless", "constant pain", "i'm stuck",
        "i can't escape", "harm myself", "i deserve pain", "i want to feel something",
        "pain feels better", "i'm overwhelmed", "i'm broken", "i'm shattered",
        "i feel dead inside", "i'm not okay", "i'm losing control", "i'm going through too much",
        "i feel trapped", "i give up", "i surrender", "i'm tired of fighting",
        "i don't want to try anymore", "i can't keep going", "i'm completely alone",
        "nobody understands me", "i have no one", "i feel abandoned", "dark thoughts",
        "ending things", "ending myself", "last day", "final goodbye", "goodbye forever",
        "i'm at my limit", "i can't take this pain"
    ]
    
    CRISIS_PATTERNS = ['suicid', 'kill', 'die', 'self harm', 'cut myself', 'harm', 'hopeless', 'worthless', 'burden', 'alone', 'end my']
    
    SYSTEM_PROMPT = {
        'en': "You are a compassionate crisis support responder. Keep response to EXACTLY 30-40 words. Be direct, caring, and urgent. Mention crisis helpline. No filler words. Respond based on what user said, not generic template.",
        'hi': "आप संकट सहायता प्रदाता हैं। बिल्कुल 30-40 शब्द। सीधे और देखभालपूर्ण रहें। क्राइसिस लाइन का उल्लेख करें। जो उपयोगकर्ता ने कहा उस पर आधारित रहें।",
        'pt': "Você é um respondente de apoio em crise. EXATAMENTE 30-40 palavras. Seja direto e compassivo. Mencione linha de crise. Responda ao que o usuário disse."
    }


class TextProcessor:
    """Handle text processing utilities."""
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    @staticmethod
    def analyze_sentiment(text: str, is_crisis: bool = False) -> str:
        """Analyze sentiment using TextBlob."""
        if is_crisis:
            return 'crisis'
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.3:
                return 'positive'
            elif polarity > 0:
                return 'neutral'
            elif polarity > -0.3:
                return 'slightly_negative'
            return 'negative'
        except Exception:
            return 'neutral'
    
    @staticmethod
    def is_crisis(text: str) -> bool:
        """Detect crisis with exact and fuzzy matching."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in CrisisConfig.KEYWORDS):
            return True
        
        return any(pattern in text_lower for pattern in CrisisConfig.CRISIS_PATTERNS)


class AIClient:
    """Manage OpenAI API interactions."""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env!")
        self.client = OpenAI(api_key=api_key)
    
    def generate_response(self, system_msg: str, user_msg: str, max_tokens: int = 160, temperature: float = 0.7) -> str:
        """Generate response from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system_msg},
                    {'role': 'user', 'content': user_msg}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"API call failed: {e}")
            return ""


class LanguageManager:
    """Manage multilingual support."""
    
    LANGUAGE_NAMES = {
        'en': 'English',
        'hi': 'Hindi',
        'pt': 'Portuguese'
    }
    
    WELCOME_MESSAGES = {
        'en': "Welcome to your journal. This is a safe space for you to express your thoughts and feelings. How are you feeling today?",
        'hi': "आपकी पत्रिका में आपका स्वागत है। यह आपके विचारों और भावनाओं को व्यक्त करने के लिए एक सुरक्षित स्थान है। आप आज कैसा महसूस कर रहे हैं?",
        'pt': "Bem-vindo ao seu diário. Este é um espaço seguro para você expressar seus pensamentos e sentimentos. Como você está se sentindo hoje?"
    }
    
    FINAL_MESSAGES = {
        'en': "Thank you for sharing your thoughts and feelings with me. Remember to be kind to yourself. You've done beautiful work today, and I'm honored to have been part of your journey.",
        'hi': "मेरे साथ अपने विचार और भावनाएं साझा करने के लिए धन्यवाद। अपने प्रति दयालु होना याद रखें। आपने आज सुंदर काम किया है।",
        'pt': "Obrigado por compartilhar seus pensamentos e sentimentos comigo. Lembre-se de ser gentil consigo mesmo. Você fez um trabalho lindo hoje."
    }
    
    ERROR_MESSAGES = {
        'en': "I'm sorry — I'm having trouble right now. Can you tell me more about how you're feeling?",
        'hi': "माफ़ कीजिए — अभी कुछ दिक्कत हो रही है। क्या आप मुझे और बता सकते हैं कि आप कैसा महसूस कर रहे हैं?",
        'pt': "Sinto muito — estou com dificuldades agora. Pode me contar mais sobre como está se sentindo?"
    }
    
    CRISIS_FALLBACK = {
        'en': "I'm deeply concerned. Please call a crisis helpline or emergency services immediately. You are not alone and help is available.",
        'hi': "मुझे गहरी चिंता है। कृपया तुरंत संकट हेल्पलाइन या आपातकालीन सेवाओं को कॉल करें। आप अकेले नहीं हैं।",
        'pt': "Estou muito preocupado. Ligue imediatamente para uma linha de crise ou serviços de emergência. Você não está sozinho."
    }
    
    SUMMARY_PROMPTS = {
        'en': "Based on the conversation, provide a concise compassionate summary of the user's journey. End with hope and encouragement.",
        'hi': "बातचीत के आधार पर, उपयोगकर्ता की यात्रा का एक संक्षिप्त और दयालु सारांश प्रदान करें। अंत में आशा और प्रोत्साहन के साथ समाप्त करें।",
        'pt': "Com base na conversa, forneça um resumo conciso e compassivo da jornada do usuário. Termine com esperança e incentivo."
    }
    
    @staticmethod
    def get_language_name(lang: str) -> str:
        """Get human-readable language name."""
        return LanguageManager.LANGUAGE_NAMES.get(lang, 'English')
    
    @staticmethod
    def get_message(key: str, lang: str) -> str:
        """Get localized message."""
        messages = {
            'welcome': LanguageManager.WELCOME_MESSAGES,
            'final': LanguageManager.FINAL_MESSAGES,
            'error': LanguageManager.ERROR_MESSAGES,
            'crisis': LanguageManager.CRISIS_FALLBACK,
            'summary': LanguageManager.SUMMARY_PROMPTS
        }
        return messages.get(key, {}).get(lang, messages.get(key, {}).get('en', ''))


class JournalAI:
    """Main journaling AI class."""
    
    def __init__(self):
        self.ai_client = AIClient()
        self.language = 'en'
        self.clear_memory()
    
    def start_chat(self, language: str = 'en') -> dict:
        """Start chat session."""
        if language not in PhaseConfig.SUPPORTED_LANGUAGES:
            language = 'en'
        
        self.language = language
        return {
            'response': LanguageManager.get_message('welcome', language),
            'language': language,
            'phase': self.phase
        }
    
    def process_text(self, patient_text: str, language: str = None) -> dict:
        """Process user input."""
        if language and language in PhaseConfig.SUPPORTED_LANGUAGES:
            self.language = language
        
        response_text = self._generate_response(patient_text)
        
        return {
            'patient_input': patient_text,
            'response': response_text,
            'language': self.language,
            'phase': self.phase,
            'is_crisis': TextProcessor.is_crisis(patient_text),
            'session_complete': False
        }
    
    def _generate_response(self, patient_text: str) -> str:
        """Generate response based on phase."""
        if TextProcessor.is_crisis(patient_text):
            return self._handle_crisis(patient_text)
        
        sentiment = TextProcessor.analyze_sentiment(patient_text)
        
        self.memory.append({
            'role': 'patient',
            'text': patient_text,
            'sentiment': sentiment,
            'phase': self.phase,
            'timestamp': datetime.now().isoformat()
        })
        
        system_msg = PhaseConfig.PHASES.get(self.phase, {}).get(self.language, PhaseConfig.PHASES[self.phase]['en'])
        context = self._build_context()
        
        user_instruction = f"Respond in {LanguageManager.get_language_name(self.language)} only. Conversation:\n{context}\n\nLatest: {patient_text}"
        
        therapist_reply = self.ai_client.generate_response(system_msg, user_instruction, max_tokens=160, temperature=0.7)
        
        if not therapist_reply:
            therapist_reply = LanguageManager.get_message('error', self.language)
        
        self.memory.append({
            'role': 'therapist',
            'text': therapist_reply,
            'phase': self.phase,
            'timestamp': datetime.now().isoformat()
        })
        
        self._advance_phase()
        return therapist_reply
    
    def _handle_crisis(self, patient_text: str) -> str:
        """Handle crisis response."""
        system_msg = CrisisConfig.SYSTEM_PROMPT.get(self.language, CrisisConfig.SYSTEM_PROMPT['en'])
        user_content = f"User said: {patient_text}\n\nRespond in {LanguageManager.get_language_name(self.language)}. EXACTLY 30-40 words. Include crisis helpline. Be specific to what they said."
        
        crisis_msg = self.ai_client.generate_response(system_msg, user_content, max_tokens=80, temperature=0.3)
        
        if not crisis_msg or TextProcessor.count_words(crisis_msg) > 45:
            crisis_msg = LanguageManager.get_message('crisis', self.language)
        
        self.memory.append({
            'role': 'patient',
            'text': patient_text,
            'sentiment': 'crisis',
            'phase': 'crisis',
            'timestamp': datetime.now().isoformat()
        })
        self.memory.append({
            'role': 'therapist',
            'text': crisis_msg,
            'phase': 'crisis',
            'timestamp': datetime.now().isoformat()
        })
        
        return crisis_msg
    
    def _build_context(self) -> str:
        """Build conversation context."""
        return "\n".join([
            f"{m['role'].capitalize()} ({m.get('phase','')}): {m['text']}"
            for m in self.memory[-6:]
        ])
    
    def _advance_phase(self):
        """Advance to next phase."""
        try:
            idx = PhaseConfig.PHASES_ORDER.index(self.phase)
            if idx < len(PhaseConfig.PHASES_ORDER) - 1:
                self.phase = PhaseConfig.PHASES_ORDER[idx + 1]
        except ValueError:
            self.phase = PhaseConfig.PHASES_ORDER[0]
    
    def _generate_final_summary(self) -> str:
        """Generate session summary."""
        history = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in self.memory])
        summary_prompt = LanguageManager.get_message('summary', self.language)
        system_msg = f"You are a caring summarizer. Respond in {LanguageManager.get_language_name(self.language)} only. Be warm and encouraging."
        user_content = f"{summary_prompt}\n\nConversation:\n{history}"
        
        summary = self.ai_client.generate_response(system_msg, user_content, max_tokens=220, temperature=0.6)
        return summary if summary else LanguageManager.get_message('final', self.language)
    
    def end_session(self) -> dict:
        """End session and generate summary."""
        return {
            'summary': self._generate_final_summary(),
            'final_message': LanguageManager.get_message('final', self.language),
            'completed': True,
            'total_messages': len(self.memory),
            'started_at': self.entry_start.isoformat()
        }
    
    def get_memory(self) -> list:
        """Get conversation memory."""
        return self.memory
    
    def clear_memory(self):
        """Clear memory for new session."""
        self.memory = []
        self.phase = PhaseConfig.PHASES_ORDER[0]
        self.entry_start = datetime.now()
    
    def get_entry_summary(self) -> dict:
        """Get entry state."""
        return {
            'phase': self.phase,
            'messages': len(self.memory),
            'started_at': self.entry_start.isoformat(),
            'language': self.language
        }


def main():
    """Main CLI interface."""
    print("\n" + "="*60)
    print("🌿 VoiceMind Journal AI - Live Chat")
    print("="*60)
    print("Type 'quit' to exit | 'summary' to end & get summary\n")
    
    journal = JournalAI()
    
    print("Select Language:")
    print("1. English (en)")
    print("2. Hindi (hi)")
    print("3. Portuguese (pt)")
    lang_choice = input("Enter choice (1-3): ").strip()
    
    language = {'1': 'en', '2': 'hi', '3': 'pt'}.get(lang_choice, 'en')
    
    welcome = journal.start_chat(language)
    print(f"\n🤖 {welcome['response']}\n")
    
    while True:
        user_input = input("👤 You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye! Take care of yourself.\n")
            break
        
        if user_input.lower() in ('summary', 'done'):
            if len(journal.memory) == 0:
                print("\n⚠️  Please share something first before getting summary.\n")
                continue
            print("\n✅ Generating summary...\n")
            final = journal.end_session()
            print("="*60)
            print("📝 CONVERSATION SUMMARY")
            print("="*60)
            print(f"\n{final['summary']}\n")
            print("="*60)
            print(f"💫 {final['final_message']}")
            print("="*60 + "\n")
            break
        
        response = journal.process_text(user_input)
        print(f"\n🤖 JournalAI [{response['phase'].upper()}]:\n{response['response']}\n")


if __name__ == "__main__":
    main()