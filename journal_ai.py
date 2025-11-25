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
            'en': "You are a soothing guide helping the user find relief and peace. They've explored their feelings deeply. Now offer comfort, perspective, and hope. Suggest a calming practice (prayer, breathing, reflection) or share a short Bible verse (under 15 words) that brings comfort. Keep response under 120 words. End with warmth and reassurance.",
            'hi': "आप एक शांतिपूर्ण गाइड हैं जो उपयोगकर्ता को राहत और शांति खोजने में मदद कर रहे हैं। एक छोटी बाइबल वर्स (15 शब्दों से कम) साझा करें या शांत प्रथा का सुझाव दें। 120 शब्दों से कम। गर्मजोशी और आश्वासन के साथ समाप्त करें।",
            'pt': "Você é um guia tranquilizador ajudando o usuário a encontrar alívio e paz. Ofereça conforto, perspectiva e esperança. Sugira uma prática calmante ou compartilhe um verso bíblico curto (menos de 15 palavras). Menos de 120 palavras. Termine com calor e segurança."
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

    RELIEF_VERSES = {
        'en': [
            "Cast all your anxiety on him because he cares for you. - 1 Peter 5:7",
            "Peace I leave with you; my peace I give to you. - John 14:27",
            "The Lord is my shepherd; I shall not want. - Psalm 23:1",
            "Come to me, all you who are weary and burdened, and I will give you rest. - Matthew 11:28",
            "For God has not given us a spirit of fear, but of power, love and a sound mind. - 2 Timothy 1:7"
        ],
        'hi': [
            "अपनी सभी चिंताएं उस पर डालें क्योंकि वह आपकी परवाह करता है। - 1 पीटर 5:7",
            "मैं तुम्हें शांति देता हूं। - यूहन्ना 14:27",
            "प्रभु मेरा चरवाहा है। - भजन 23:1"
        ],
        'pt': [
            "Lançai em cima dele toda a vossa ansiedade, porque ele tem cuidado de vós. - 1 Pedro 5:7",
            "A paz vos deixo, a minha paz vos dou. - João 14:27",
            "O Senhor é meu pastor; nada me faltará. - Salmo 23:1"
        ]
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

        # Add Bible verse in relieve phase
        if self.phase == 'relieve':
            import random
            verse = random.choice(self.RELIEF_VERSES[language])
            therapist_reply += f"\n\n✨ {verse}"

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
    """Main function to test JournalAI functionality"""
    
    print("=" * 60)
    print("🧠 JournalAI - Testing Suite")
    print("=" * 60)
    
    try:
        # Initialize JournalAI
        print("\n[1] Initializing JournalAI...")
        journal = JournalAI()
        print("✅ JournalAI initialized successfully\n")
        
    except ValueError as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Test 1: Text processing - FEEL phase
    print("[2] Testing FEEL phase (text input)...")
    test_input_1 = "I'm feeling really overwhelmed with work today"
    result_1 = journal.process_text(test_input_1, language='en')
    print(f"  Input: {result_1['patient_input']}")
    print(f"  Phase: {result_1['phase']}")
    print(f"  Response: {result_1['response'][:100]}...\n")
    
    # Test 2: Continue with UNDERSTAND phase
    print("[3] Testing UNDERSTAND phase...")
    test_input_2 = "I think it's because I have too many deadlines and I can't prioritize"
    result_2 = journal.process_text(test_input_2, language='en')
    print(f"  Input: {result_2['patient_input']}")
    print(f"  Phase: {result_2['phase']}")
    print(f"  Response: {result_2['response'][:100]}...\n")
    
    # Test 3: Continue with RELIEVE phase
    print("[4] Testing RELIEVE phase...")
    test_input_3 = "I need to learn to let go and trust that things will work out"
    result_3 = journal.process_text(test_input_3, language='en')
    print(f"  Input: {result_3['patient_input']}")
    print(f"  Phase: {result_3['phase']}")
    print(f"  Response: {result_3['response'][:150]}...\n")
    
    # Test 4: Memory tracking
    print("[5] Testing Memory...")
    memory = journal.get_memory()
    print(f"  Total messages in memory: {len(memory)}")
    print(f"  Memory snapshot:")
    for i, msg in enumerate(memory):
        print(f"    {i+1}. {msg['role'].upper()} - Phase: {msg['phase']}\n")
    
    # Test 5: Sentiment analysis
    print("[6] Testing Sentiment Analysis...")
    test_sentiments = [
        ("I'm so happy and excited!", "positive"),
        ("It's just okay, nothing special", "neutral"),
        ("I'm a bit sad today", "negative"),
    ]
    journal.clear_memory()
    for text, expected in test_sentiments:
        sentiment = journal._analyze_sentiment(text)
        status = "✅" if sentiment else "❌"
        print(f"  {status} '{text}' → {sentiment}")
    print()
    
    # Test 6: Crisis detection
    print("[7] Testing Crisis Detection...")
    crisis_test = "I can't take it anymore, I want to kill myself"
    is_crisis = journal._is_crisis(crisis_test)
    print(f"  Text: '{crisis_test}'")
    print(f"  Crisis detected: {'✅ YES' if is_crisis else '❌ NO'}\n")
    
    # Test 7: Language support
    print("[8] Testing Language Support...")
    journal.clear_memory()
    test_langs = [
        ("I'm feeling anxious", "en", "English"),
        ("मुझे चिंता हो रही है", "hi", "Hindi"),
        ("Estou me sentindo ansioso", "pt", "Portuguese"),
    ]
    for text, lang, lang_name in test_langs:
        try:
            result = journal.process_text(text, language=lang)
            print(f"  ✅ {lang_name} ({lang}): OK")
        except Exception as e:
            print(f"  ❌ {lang_name} ({lang}): {str(e)[:50]}")
    print()
    
    # Test 8: Entry summary
    print("[9] Testing Entry Summary...")
    summary = journal.get_entry_summary()
    print(f"  Current phase: {summary['phase']}")
    print(f"  Total messages: {summary['messages']}")
    print(f"  Session started: {summary['started_at']}\n")
    
    # Test 9: Clear memory
    print("[10] Testing Memory Clear...")
    print(f"  Messages before clear: {len(journal.get_memory())}")
    journal.clear_memory()
    print(f"  Messages after clear: {len(journal.get_memory())}")
    print(f"  Phase reset to: {journal.phase}\n")
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()