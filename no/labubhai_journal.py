from openai import OpenAI
from textblob import TextBlob
from datetime import datetime
import os
from dotenv import load_dotenv
from voice import VoiceEngine
from prompt import Prompts

load_dotenv()


class JournalAI:
    """FEEL → UNDERSTAND → RELIEVE Journaling AI"""

    PHASES = {
        'feel': {
            'en': "You are a compassionate journaling companion. The user is sharing their feelings. Listen deeply and validate their emotions without judgment. Show genuine care. Ask ONE reflective question to help them express more. Keep response under 100 words. Be warm, safe, and calming.",
            'hi': "आप एक दयालु जर्नलिंग साथी हैं। उपयोगकर्ता अपनी भावनाओं को साझा कर रहे हैं। गहराई से सुनें और बिना किसी निर्णय के भावनाओं को मान्य करें। ONE प्रश्न पूछें। 100 शब्दों से कम। गर्म, सुरक्षित और शांत रहें।",
            'pt': "Você é uma companheira de diário compassiva. O usuário está compartilhando seus sentimentos. Ouça profundamente e valide emoções sem julgamento. Faça UMA pergunta reflexiva. Menos de 100 palavras. Seja calorosa, segura e calma."
        },
        'understand': {
            'en': "You are a thoughtful counselor helping the user understand their feelings. They've shared emotions. Now ask ONE meaningful question to help them explore deeper - what caused this? What does it mean? Help them gain clarity and insight. Keep response under 100 words. Be gentle and supportive.",
            'hi': "आप एक विचारशील परामर्शदाता हैं जो उपयोगकर्ता को उनकी भावनाओं को समझने में मदद कर रहे हैं। ONE प्रश्न पूछें जो उन्हें गहरे जाने में मदद करे। क्या कारण है? इसका क्या मतलब है? उन्हें स्पष्टता पाने में मदद करें। 100 शब्दों से कम। कोमल और सहायक रहें।",
            'pt': "Você é uma conselheira atenciosa ajudando o usuário a entender seus sentimentos. Eles compartilharam emoções. Agora faça UMA pergunta significativa para ajudá-los a explorar mais profundamente. Menos de 100 palavras. Seja gentil e solidária."
        },
        'relieve': {
            'en': "You are a soothing guide helping the user find relief and peace. They've explored their feelings deeply. Now offer comfort, perspective, and hope. Suggest a calming practice (prayer, breathing, reflection). Keep response under 120 words. End with warmth and reassurance.",
            'hi': "आप एक शांतिपूर्ण गाइड हैं जो उपयोगकर्ता को राहत और शांति खोजने में मदद कर रहे हैं। एक शांत प्रथा का सुझाव दें। 120 शब्दों से कम। गर्मजोशी और आश्वासन के साथ समाप्त करें।",
            'pt': "Você é um guia tranquilizador ajudando o usuário a encontrar alívio e paz. Ofereça conforto, perspectiva e esperança. Sugira uma prática calmante. Menos de 120 palavras. Termine com calor e segurança."
        }
    }

    CRISIS_KEYWORDS = [
        'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
        'cutting', 'die', 'worthless', 'want to die', 'better off dead',
        'no point living', 'hate myself', 'end my life'
    ]

    CRISIS_RESPONSE = {
        'en': "I hear you, and I'm truly concerned about you. What you're feeling is real, and you matter deeply to God and to me. You're not alone in this pain. Please reach out immediately to someone you trust - a pastor, counselor, or trusted adult - or contact a crisis helpline. God's heart breaks with yours. Would you like to try a calming breathing exercise together?",
        'hi': "मैं आपकी बात सुन रहा हूं और आपके बारे में चिंतित हूं। आप जो महसूस कर रहे हैं वह वास्तविक है। कृपया तुरंत किसी भरोसेमंद से संपर्क करें। आप अकेले नहीं हैं। क्या आप श्वास व्यायाम करना चाहेंगे?",
        'pt': "Eu ouço você e estou realmente preocupado. O que você está sentindo é real, e você é profundamente importante para Deus e para mim. Entre em contato imediatamente com alguém de confiança. Você não está sozinho. Gostaria de tentar um exercício de respiração?"
    }

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
        
        self.client = OpenAI(api_key=api_key)
        self.voice = VoiceEngine()
        self.memory = []
        self.phase = 'feel'
        self.entry_start = datetime.now()
        print("✅ JournalAI initialized - FEEL → UNDERSTAND → RELIEVE")

    def process_voice(self, audio_data: bytes, language: str = 'en', gender: str = 'female') -> dict:
        """Process voice input with STT → AI → TTS"""
        if language not in self.PHASES:
            language = 'en'

        stt_result = self.voice.speech_to_text(audio_data)
        patient_text = stt_result['text']
        
        if not patient_text:
            error_msg = "I couldn't hear you clearly. Could you please repeat?"
            audio = self.voice.text_to_speech(error_msg, language, gender)
            return {'text': error_msg, 'audio': audio, 'language': language, 'phase': self.phase}

        response_text = self._generate_response(patient_text, language)
        response_audio = self.voice.text_to_speech(response_text, language, gender)

        return {
            'patient_input': patient_text,
            'response': response_text,
            'audio': response_audio,
            'language': language,
            'phase': self.phase
        }

    def process_text(self, patient_text: str, language: str = 'en') -> dict:
        """Process text input"""
        if language not in self.PHASES:
            language = 'en'

        response_text = self._generate_response(patient_text, language)

        return {
            'patient_input': patient_text,
            'response': response_text,
            'language': language,
            'phase': self.phase
        }

    def _generate_response(self, patient_text: str, language: str) -> str:
        """Generate response based on current phase"""
        
        # Check for crisis
        if self._is_crisis(patient_text):
            return self._handle_crisis(patient_text, language)
        
        sentiment = self._analyze_sentiment(patient_text)
        self.memory.append({
            'role': 'patient',
            'text': patient_text,
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

        therapist_reply = response.choices[0].message.content

        self.memory.append({
            'role': 'therapist',
            'text': therapist_reply,
            'phase': self.phase
        })

        self._advance_phase()

        return therapist_reply

    def _advance_phase(self):
        """Move to next phase"""
        phases_order = ['feel', 'understand', 'relieve']
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
        """Clear memory for new journal entry"""
        self.memory = []
        self.phase = 'feel'
        self.entry_start = datetime.now()
        print("Memory cleared - Ready for new journal entry")

    def get_entry_summary(self) -> dict:
        """Get current entry summary"""
        return {
            'phase': self.phase,
            'messages': len(self.memory),
            'started_at': self.entry_start.isoformat(),
            'memory': self.memory
        }

    def _is_crisis(self, text: str) -> bool:
        """Check for crisis keywords"""
        return any(k in text.lower() for k in self.CRISIS_KEYWORDS)

    def _handle_crisis(self, patient_text: str, language: str) -> str:
        """Handle crisis situation"""
        crisis_msg = self.CRISIS_RESPONSE[language]
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


def main():
    """Simple main function for live chat with JournalAI"""
    
    print("\n" + "="*60)
    print("🧠 JournalAI - FEEL → UNDERSTAND → RELIEVE")
    print("="*60)
    print("Type 'quit' to exit | 'clear' to start new session | 'lang' to change language\n")
    
    try:
        journal = JournalAI()
    except ValueError as e:
        print(f"❌ Error: {e}")
        return
    
    language = 'en'
    
    while True:
        try:
            user_input = input(f"You ({journal.phase.upper()}): ").strip()
            
            if user_input.lower() == 'quit':
                print("\n👋 Thank you for sharing. Take care!\n")
                break
            
            if user_input.lower() == 'clear':
                journal.clear_memory()
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
            response = journal.process_text(user_input, language=language)
            
            print(f"\nAI ({response['phase'].upper()}): {response['response']}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session ended. Take care!\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()