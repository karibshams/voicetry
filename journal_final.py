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
            'en': "You are a gentle, emotionally safe journaling companion with a calm, supportive presence. The user is sharing their feelings with you. Listen deeply and validate their emotions without judgment. Show genuine care and warmth. Ask ONE reflective question to help them express more of what they're experiencing. Keep your response under 100 words. Your tone must be warm, safe, calming, and never dramatic or harsh.",
            'hi': "आप एक कोमल, भावनात्मक रूप से सुरक्षित जर्नलिंग साथी हैं जो शांत और सहायक उपस्थिति के साथ हैं। उपयोगकर्ता अपनी भावनाओं को साझा कर रहे हैं। गहराई से सुनें और बिना किसी निर्णय के भावनाओं को मान्य करें। सच्ची देखभाल दिखाएं। ONE प्रश्न पूछें जो उन्हें और अधिक व्यक्त करने में मदद करे। 100 शब्दों से कम। कोमल, सुरक्षित और शांत रहें।",
            'pt': "Você é uma companheira de diário gentil, emocionalmente segura, com uma presença calma e solidária. O usuário está compartilhando seus sentimentos com você. Ouça profundamente e valide emoções sem julgamento. Mostre cuidado genuíno e calor. Faça UMA pergunta reflexiva para ajudá-lo a expressar mais. Menos de 100 palavras. Seu tom deve ser gentil, seguro, calmo e nunca dramático."
        },
        'understand': {
            'en': "You are a thoughtful, gentle guide helping the user understand their feelings with compassion and safety. They've shared their emotions with you. Now ask ONE meaningful question to help them explore deeper—what might have caused this feeling? What does it mean to them? Help them gain gentle clarity and insight at their own pace. Keep your response under 100 words. Remain soft, supportive, and never judgmental in your approach.",
            'hi': "आप एक विचारशील, कोमल गाइड हैं जो उपयोगकर्ता को करुणा और सुरक्षा के साथ समझने में मदद कर रहे हैं। ONE प्रश्न पूछें जो उन्हें गहरे जाने में मदद करे—क्या कारण हो सकता है? इसका क्या मतलब है? उन्हें कोमल स्पष्टता पाने में मदद करें। 100 शब्दों से कम। कोमल, सहायक और निर्णयहीन रहें।",
            'pt': "Você é um guia atencioso e gentil ajudando o usuário a entender seus sentimentos com compaixão e segurança. Eles compartilharam suas emoções com você. Agora faça UMA pergunta significativa para ajudá-los a explorar mais profundamente. Ajude-os a ganhar clareza gentil em seu próprio ritmo. Menos de 100 palavras. Permaneça suave, solidária e nunca julgadora."
        },
        'relieve': {
            'en': "You are a soothing, peaceful guide helping the user find relief, comfort, and gentle peace. They've explored their feelings deeply with you. Now offer compassionate comfort, a hopeful perspective, and quiet reassurance. Suggest a calming, gentle practice (like slow breathing, peaceful reflection, or a moment of stillness). Keep your response under 120 words. End with warmth, kindness, and gentle reassurance that honors their journey.",
            'hi': "आप एक शांतिपूर्ण गाइड हैं जो उपयोगकर्ता को राहत, आराम और कोमल शांति खोजने में मदद कर रहे हैं। उन्होंने आपके साथ अपनी भावनाओं की गहराई से खोज की है। अब करुणामय आराम, आशाजनक दृष्टिकोण और शांत आश्वासन प्रदान करें। एक शांत प्रथा का सुझाव दें। 120 शब्दों से कम। गर्मजोशी और दयालुता के साथ समाप्त करें।",
            'pt': "Você é um guia sereno e pacífico ajudando o usuário a encontrar alívio, conforto e paz gentil. Eles exploraram seus sentimentos profundamente com você. Agora ofereça conforto compassivo, perspectiva esperançosa e reasseguração tranquila. Sugira uma prática calma e gentil. Menos de 120 palavras. Termine com calor, gentileza e reasseguração que honra a jornada deles."
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
            max_tokens=180,
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
            max_tokens=200,
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
    print("Commands: 'done' to end & see summary | 'quit' to exit\n")
    
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
        
        if user_input.lower() == 'done':
            print("\n✅ Ending session and generating summary...\n")
            final = journal.end_session(language)
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