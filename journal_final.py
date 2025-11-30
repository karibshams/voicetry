from openai import OpenAI
from textblob import TextBlob
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class JournalAI:
    """FEEL → UNDERSTAND → RELIEVE Journaling AI"""

    PHASES = {
        'feel': {
            'en': "You are a gentle, emotionally safe companion. The user is sharing their feelings. Listen deeply and validate without judgment. Show warmth and care. Ask ONE simple reflective question. Keep response under 70 words. Be warm, safe, calm. No dramatic language.",
            'hi': "आप एक कोमल, भावनात्मक रूप से सुरक्षित साथी हैं। उपयोगकर्ता अपनी भावनाएं साझा कर रहे हैं। गहराई से सुनें और मान्य करें। ONE सरल प्रश्न पूछें। 70 शब्दों से कम। कोमल और शांत रहें।",
            'pt': "Você é um companheiro gentil e seguro. Ouça profundamente e valide sem julgamento. Faça UMA pergunta simples. Menos de 70 palavras. Seja gentil e calmo."
        },
        'understand': {
            'en': "You are a thoughtful, gentle guide. Ask ONE meaningful question to help them explore their feelings deeper. Keep response under 70 words. Be soft and supportive. No judgement. Direct and simple language only.",
            'hi': "आप एक विचारशील, कोमल गाइड हैं। ONE प्रश्न पूछें। 70 शब्दों से कम। कोमल, सहायक, सरल भाषा।",
            'pt': "Você é um guia atencioso e gentil. Faça UMA pergunta significativa. Menos de 70 palavras. Seja gentil e direto."
        },
        'relieve': {
            'en': "You are a calm, supportive guide in the RELIEVE phase. Acknowledge their pain with warmth. Suggest ONE simple coping practice (breathing, stillness, reflection). ABSOLUTELY NO QUESTIONS - just comfort and practice. Keep under 80 words. Simple, direct language. End with gentle reassurance that help is available.",
            'hi': "आप RELIEVE चरण में एक शांत, सहायक गाइड हैं। उनकी भावनाओं को स्वीकार करें। एक सरल प्रथा सुझाएं। कोई सवाल नहीं - सिर्फ आराम और प्रथा। 80 शब्दों से कम। सरल भाषा।",
            'pt': "Você é um guia calmo e solidário na fase RELIEVE. Reconheça seus sentimentos. Sugira uma prática simples. SEM PERGUNTAS - apenas conforto. Menos de 80 palavras."
        }
    }

    
    CRISIS_KEYWORDS = [
    # Direct self-harm intent
    "suicide", "kill myself", "end it all", "end my life", "take my life",
    "hurt myself", "self harm", "self-harm", "cutting", "cut myself",
    "i want to die", "want to die", "i want to end everything",
    "better off dead", "no point living", "life is meaningless",
    "i hate my life", "i hate myself", "i don't want to live",
    "i’m done with life", "life is pointless",

    # Indirect suicidal statements
    "wish i was dead", "wish i could disappear", "i don’t care anymore",
    "i can’t do this anymore", "i can’t go on", "i want it to stop",
    "i feel empty", "i’m tired of everything", "i’m giving up",
    "i feel hopeless", "i feel useless", "nothing matters",
    "nobody cares", "i’m a burden", "everyone is better without me",

    # Severe depression markers
    "i’m worthless", "worthless", "nothing will change",
    "i have no reason to live", "no hope", "hopeless", "lifeless",
    "constant pain", "i’m stuck", "i can’t escape",

    # Harm ideation (non-graphic)
    "hurt myself", "harm myself", "i deserve pain",
    "i want to feel something", "pain feels better",
    
    # Crisis emotional states
    "i’m overwhelmed", "i’m broken", "i’m shattered",
    "i feel dead inside", "i’m not okay", "i’m losing control",
    "i’m going through too much", "i feel trapped",

    # Surrender expressions
    "i give up", "i surrender", "i’m tired of fighting",
    "i don’t want to try anymore", "i can’t keep going",

    # Isolation indicators
    "i’m completely alone", "nobody understands me",
    "i have no one", "i feel abandoned",

    # Additional caution phrases
    "dark thoughts", "ending things", "ending myself",
    "last day", "final goodbye", "goodbye forever",
    "i’m at my limit", "i can’t take this pain",]

    

    CRISIS_SYSTEM_PROMPT = {
        'en': "You are a compassionate crisis support responder. Keep response to EXACTLY 30-40 words. Be direct, caring, and urgent. Mention crisis helpline. No filler words. Respond based on what user said, not generic template.",
        'hi': "आप संकट सहायता प्रदाता हैं। बिल्कुल 30-40 शब्द। सीधे और देखभालपूर्ण रहें। क्राइसिस लाइन का उल्लेख करें। जो उपयोगकर्ता ने कहा उस पर आधारित रहें।",
        'pt': "Você é um respondente de apoio em crise. EXATAMENTE 30-40 palavras. Seja direto e compassivo. Mencione linha de crise. Responda ao que o usuário disse."
    }

    FINAL_RESPONSE = {
        'en': "Thank you for sharing your thoughts and feelings with me. Remember to be kind to yourself. You've done beautiful work today, and I'm honored to have been part of your journey.",
        'hi': "मेरे साथ अपने विचार और भावनाएं साझा करने के लिए धन्यवाद। अपने प्रति दयालु होना याद रखें। आपने आज सुंदर काम किया है।",
        'pt': "Obrigado por compartilhar seus pensamentos e sentimentos comigo. Lembre-se de ser gentil consigo mesmo. Você fez um trabalho lindo hoje."
    }

    PHASES_ORDER = ['feel', 'understand', 'relieve']

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
        
        self.client = OpenAI(api_key=api_key)
        self.language = 'en'
        self.clear_memory()

    def start_chat(self, language: str = 'en') -> dict:
        """Generate a welcome message to start the chat"""
        if language not in self.PHASES:
            language = 'en'
        
        self.language = language
        
        welcome_messages = {
            'en': "Welcome to your journal. This is a safe space for you to express your thoughts and feelings. How are you feeling today?",
            'hi': "आपकी पत्रिका में आपका स्वागत है। यह आपके विचारों और भावनाओं को व्यक्त करने के लिए एक सुरक्षित स्थान है। आप आज कैसा महसूस कर रहे हैं?",
            'pt': "Bem-vindo ao seu diário. Este é um espaço seguro para você expressar seus pensamentos e sentimentos. Como você está se sentindo hoje?"
        }
        
        welcome_text = welcome_messages.get(language, welcome_messages['en'])
        
        return {
            'response': welcome_text,
            'language': language,
            'phase': self.phase
        }

    def process_text(self, patient_text: str, language: str = None) -> dict:
        """Process text input"""
        if language and language in self.PHASES:
            self.language = language
        
        response_text = self._generate_response(patient_text)
        
        response_data = {
            'patient_input': patient_text,
            'response': response_text,
            'language': self.language,
            'phase': self.phase,
            'is_crisis': False,
            'session_complete': False
        }
        
        return response_data

    def _generate_response(self, patient_text: str) -> str:
        """Generate response based on current phase"""
        
        # Check for crisis
        if self._is_crisis(patient_text):
            return self._handle_crisis(patient_text)
        
        # Normal response
        sentiment = self._analyze_sentiment(patient_text)
        self.memory.append({
            'role': 'patient',
            'text': patient_text,
            'sentiment': sentiment,
            'phase': self.phase
        })
        
        conversation_context = self._build_context()
        system_msg = self.PHASES[self.phase].get(self.language, self.PHASES[self.phase]['en'])
        
        messages = [
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': f"Respond in {self.language_name()}. Conversation:\n{conversation_context}"}
        ]
        
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=160,
            temperature=0.7
        )
        
        therapist_reply = response.choices[0].message.content
        
        self.memory.append({
            'role': 'therapist',
            'text': therapist_reply,
            'phase': self.phase
        })
        
        self._advance_phase()
        
        return therapist_reply

    def language_name(self) -> str:
        """Get language name for AI instructions"""
        lang_map = {
            'en': 'English',
            'hi': 'Hindi',
            'pt': 'Portuguese'
        }
        return lang_map.get(self.language, 'English')

    def _build_context(self) -> str:
        """Build conversation context from recent memory"""
        return "\n".join([
            f"{m['role'].capitalize()}: {m['text']}"
            for m in self.memory[-6:]
        ])

    def _advance_phase(self):
        """Move to next phase"""
        current_idx = self.PHASES_ORDER.index(self.phase)
        if current_idx < len(self.PHASES_ORDER) - 1:
            self.phase = self.PHASES_ORDER[current_idx + 1]

    def _generate_final_summary(self) -> str:
        """Generate a final summary of the conversation"""
        conversation_history = "\n".join([
            f"{m['role'].capitalize()}: {m['text']}"
            for m in self.memory
        ])
        
        summary_prompts = {
            'en': "Based on the following conversation, provide a concise and compassionate summary of the user's feelings and journey. End with a message of hope and encouragement.",
            'hi': "निम्नलिखित बातचीत के आधार पर, उपयोगकर्ता की भावनाओं और यात्रा का एक संक्षिप्त और दयालु सारांश प्रदान करें।",
            'pt': "Com base na conversa a seguir, forneça um resumo conciso e compassivo dos sentimentos e da jornada do usuário."
        }
        
        summary_prompt = summary_prompts.get(self.language, summary_prompts['en'])
        
        messages = [
            {'role': 'system', 'content': "You are a caring summarizer. Provide a warm and encouraging summary."},
            {'role': 'user', 'content': f"{summary_prompt}\n\nConversation:\n{conversation_history}"}
        ]
        
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=250,
            temperature=0.6
        )
        
        return response.choices[0].message.content

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.3:
            return 'positive'
        elif polarity > 0:
            return 'neutral'
        elif polarity > -0.3:
            return 'slightly_negative'
        return 'negative'

    def _handle_crisis(self, patient_text: str) -> str:
        """Generate dynamic crisis response in user's language"""
        system_msg = self.CRISIS_SYSTEM_PROMPT.get(self.language, self.CRISIS_SYSTEM_PROMPT['en'])
        
        messages = [
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': f"User said: {patient_text}\n\nRespond in {self.language_name()}. EXACTLY 30-40 words. Include crisis helpline. Be specific to what they said."}
        ]
        
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=60,
            temperature=0.7
        )
        
        crisis_msg = response.choices[0].message.content
        
        self.memory.append({
            'role': 'patient',
            'text': patient_text,
            'sentiment': 'crisis',
            'phase': 'crisis'
        })
        self.memory.append({
            'role': 'therapist',
            'text': crisis_msg,
            'phase': 'crisis'
        })
        
        return crisis_msg

    def _is_crisis(self, text: str) -> bool:
        """Check for crisis keywords"""
        return any(keyword in text.lower() for keyword in self.CRISIS_KEYWORDS)

    def end_session(self) -> dict:
        """End session and generate summary"""
        summary = self._generate_final_summary()
        final_msg = self.FINAL_RESPONSE.get(self.language, self.FINAL_RESPONSE['en'])
        
        return {
            'summary': summary,
            'final_message': final_msg,
            'completed': True,
            'total_messages': len(self.memory),
            'started_at': self.entry_start.isoformat()
        }

    def get_memory(self) -> list:
        """Get full conversation memory"""
        return self.memory

    def clear_memory(self):
        """Clear memory for new journal entry"""
        self.memory = []
        self.phase = self.PHASES_ORDER[0]
        self.entry_start = datetime.now()

    def get_entry_summary(self) -> dict:
        """Get current entry summary"""
        return {
            'phase': self.phase,
            'messages': len(self.memory),
            'started_at': self.entry_start.isoformat(),
            'memory': self.memory
        }


def main():
    """Live chat with JournalAI in terminal"""
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
    
    language_map = {'1': 'en', '2': 'hi', '3': 'pt'}
    language = language_map.get(lang_choice, 'en')
    
    welcome = journal.start_chat(language)
    print(f"\n🤖 {welcome['response']}\n")
    
    while True:
        user_input = input("👤 You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye! Take care of yourself.\n")
            break
        
        if user_input.lower() == 'summary' or user_input.lower() == 'done':
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
        
        response = journal.process_text(user_input, language)
        print(f"\n🤖 JournalAI [{response['phase'].upper()}]:\n{response['response']}\n")


if __name__ == "__main__":
    main()