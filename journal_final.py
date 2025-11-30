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
            'en': "You are a gentle, emotionally safe companion. The user is sharing their feelings. Listen deeply and validate without judgment. Show warmth and care. Ask ONE simple reflective question to help them share more. Keep response under 70 words. Be warm, safe, and calm. Avoid being poetic or dramatic.",
            'hi': "आप एक कोमल, भावनात्मक रूप से सुरक्षित साथी हैं। उपयोगकर्ता अपनी भावनाएं साझा कर रहे हैं। गहराई से सुनें और बिना निर्णय के मान्य करें। ONE सरल प्रश्न पूछें। 70 शब्दों से कम। कोमल और शांत रहें।",
            'pt': "Você é um companheiro gentil e seguro. O usuário está compartilhando seus sentimentos. Ouça profundamente e valide sem julgamento. Faça UMA pergunta simples. Menos de 70 palavras. Seja gentil e calmo."
        },
        'understand': {
            'en': "You are a thoughtful, gentle guide helping the user understand their feelings. Ask ONE meaningful question to help them explore—what might have caused this? What does it mean? Help them gain clarity. Keep response under 70 words. Be soft and supportive, never judgmental. Avoid poetic language.",
            'hi': "आप एक विचारशील, कोमल गाइड हैं। ONE प्रश्न पूछें जो उन्हें गहराई से समझने में मदद करे। 70 शब्दों से कम। कोमल और सहायक रहें।",
            'pt': "Você é um guia atencioso e gentil. Faça UMA pergunta para ajudá-los a explorar mais profundamente. Menos de 70 palavras. Seja gentil e solidária."
        },
        'relieve': {
            'en': "You are a calm guide offering comfort and relief. Acknowledge their feelings with warmth. Offer one simple, practical coping practice (like breathing or a moment of peace). Be brief, kind, and encouraging. Keep response under 80 words. No flowery language—be simple and direct with genuine warmth.",
            'hi': "आप एक शांत गाइड हैं जो आराम प्रदान करते हैं। उनकी भावनाओं को स्वीकार करें। एक सरल प्रथा सुझाएं। 80 शब्दों से कम। सरल और प्रत्यक्ष रहें।",
            'pt': "Você é um guia calmo oferecendo conforto. Reconheça seus sentimentos com ternura. Sugira uma prática simples. Menos de 80 palavras. Seja direto e gentil."
        }
    }

    CRISIS_KEYWORDS = [
        'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
        'cutting', 'die', 'worthless', 'want to die', 'better off dead',
        'no point living', 'hate myself', 'end my life'
    ]

    CRISIS_RESPONSE = {
        'en': "I hear you, and I'm truly concerned about you. What you're feeling is real, and you matter deeply. You're not alone in this pain. Please reach out immediately to someone you trust or contact a crisis helpline. Your life has value. Would you like to try a calming breathing exercise together?",
        'hi': "मैं आपकी बात सुन रहा हूं और आपके बारे में चिंतित हूं। आप जो महसूस कर रहे हैं वह वास्तविक है। कृपया तुरंत किसी भरोसेमंद से संपर्क करें। आप अकेले नहीं हैं। क्या आप श्वास व्यायाम करना चाहेंगे?",
        'pt': "Eu ouço você e estou realmente preocupado. O que você está sentindo é real, e você é importante. Entre em contato imediatamente com alguém de confiança. Você não está sozinho. Gostaria de tentar um exercício de respiração?"
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
        self.clear_memory()

    def start_chat(self, language: str = 'en') -> dict:
        """Generate a welcome message to start the chat"""
        if language not in self.PHASES:
            language = 'en'
        
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

    def process_text(self, patient_text: str, language: str = 'en') -> dict:
        """Process text input"""
        if language not in self.PHASES:
            language = 'en'
        
        response_text = self._generate_response(patient_text, language)
        
        response_data = {
            'patient_input': patient_text,
            'response': response_text,
            'language': language,
            'phase': self.phase,
            'completed': False
        }
        
        return response_data

    def _generate_response(self, patient_text: str, language: str) -> str:
        """Generate response based on current phase"""
        
        if self._is_crisis(patient_text):
            return self._handle_crisis(patient_text, language)
        
        sentiment = self._analyze_sentiment(patient_text)
        self.memory.append({
            'role': 'patient',
            'text': patient_text,
            'sentiment': sentiment,
            'phase': self.phase
        })
        
        conversation_context = self._build_context()
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
        
        therapist_reply = response.choices[0].message.content
        
        self.memory.append({
            'role': 'therapist',
            'text': therapist_reply,
            'phase': self.phase
        })
        
        self._advance_phase()
        
        return therapist_reply

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

    def _generate_final_summary(self, language: str) -> str:
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
        
        summary_prompt = summary_prompts.get(language, summary_prompts['en'])
        
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

    def _is_crisis(self, text: str) -> bool:
        """Check for crisis keywords"""
        return any(keyword in text.lower() for keyword in self.CRISIS_KEYWORDS)

    def _handle_crisis(self, patient_text: str, language: str) -> str:
        """Handle crisis situation"""
        crisis_msg = self.CRISIS_RESPONSE.get(language, self.CRISIS_RESPONSE['en'])
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

    def end_session(self, language: str = 'en') -> dict:
        """End session and generate summary"""
        summary = self._generate_final_summary(language)
        final_msg = self.FINAL_RESPONSE.get(language, self.FINAL_RESPONSE['en'])
        
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
    print("Type 'quit' to exit\n")
    
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
        
        response = journal.process_text(user_input, language)
        print(f"\n🤖 JournalAI [{response['phase'].upper()}]:\n{response['response']}\n")


if __name__ == "__main__":
    main()