from openai import OpenAI
from textblob import TextBlob
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class JournalAI:
    """FEEL → UNDERSTAND → RELIEVE Journaling AI (Compact & Accurate)"""
    
    PROMPTS = {
        'feel': {
            'en': "You are a gentle companion. The user is sharing feelings. Listen deeply and validate without judgment. Ask ONE simple reflective question. Keep response under 70 words. Be warm, safe, calm.",
            'hi': "आप एक कोमल साथी हैं। उपयोगकर्ता अपनी भावनाएं साझा कर रहे हैं। गहराई से सुनें और बिना निर्णय के मान्य करें। ONE सरल प्रश्न पूछें। 70 शब्दों से कम। कोमल, सुरक्षित, शांत रहें।",
            'pt': "Você é um companheiro gentil. O usuário está compartilhando seus sentimentos. Ouça profundamente e valide sem julgamento. Faça UMA pergunta simples. Menos de 70 palavras. Seja gentil, seguro, calmo."
        },
        'understand': {
            'en': "You are a thoughtful guide. Ask ONE meaningful question to help them explore their feelings deeper. Keep response under 70 words. Be soft and supportive. Direct and simple language only.",
            'hi': "आप एक विचारशील गाइड हैं। ONE अर्थपूर्ण प्रश्न पूछें जो उन्हें गहरे जाने में मदद करे। 70 शब्दों से कम। कोमल और सहायक रहें। सरल भाषा।",
            'pt': "Você é um guia atencioso. Faça UMA pergunta significativa para ajudá-los a explorar mais profundamente. Menos de 70 palavras. Seja gentil e solidário. Linguagem simples e direta."
        },
        'relieve': {
            'en': "RELIEVE PHASE - NO QUESTIONS ALLOWED. You are a calm guide. Acknowledge their pain. Suggest ONE simple coping practice (breathing/stillness/grounding/reflection). Use max 80 words. Be warm and direct. NEVER ask a question - not even one.",
            'hi': "RELIEVE चरण - कोई सवाल नहीं। शांत गाइड बनें। दर्द को स्वीकार करें। ONE सरल प्रथा सुझाएं। 80 शब्द से कम। कभी कोई सवाल न पूछें।",
            'pt': "Fase RELIEVE - SEM PERGUNTAS. Seja um guia calmo. Reconheça a dor. Sugira UMA prática simples. Menos de 80 palavras. NUNCA faça uma pergunta."
        }
    }
    
    CRISIS_KEYWORDS = ['suicid', 'kill', 'die', 'self harm', 'hopeless', 'worthless', 'burden', 'end my', 'harm myself', 'alone', 'pain']
    
    CRISIS_PROMPT = {
        'en': "You are a compassionate crisis support responder. Keep response to EXACTLY 30-40 words. Be direct, caring, and urgent. Mention crisis helpline. Respond specifically to what they said, not generic.",
        'hi': "आप एक संकट सहायता प्रदाता हैं। बिल्कुल 30-40 शब्द। सीधे, देखभालपूर्ण और तत्काल रहें। संकट हेल्पलाइन का उल्लेख करें। जो उन्होंने कहा उस पर विशेष रूप से प्रतिक्रिया दें।",
        'pt': "Você é um respondente de apoio em crise. EXATAMENTE 30-40 palavras. Seja direto, compassivo e urgente. Mencione linha de crise. Responda especificamente ao que eles disseram."
    }
    
    MESSAGES = {
        'welcome': {
            'en': "Welcome to your journal. This is a safe space for you to express your thoughts and feelings. How are you feeling today?",
            'hi': "आपकी पत्रिका में स्वागत है। यह आपके विचारों और भावनाओं को व्यक्त करने के लिए एक सुरक्षित स्थान है। आप आज कैसा महसूस कर रहे हैं?",
            'pt': "Bem-vindo ao seu diário. Este é um espaço seguro para você expressar seus pensamentos e sentimentos. Como você está se sentindo hoje?"
        },
        'final': {
            'en': "Thank you for sharing your thoughts and feelings with me. Remember to be kind to yourself. You've done beautiful work today.",
            'hi': "मेरे साथ अपने विचार और भावनाएं साझा करने के लिए धन्यवाद। अपने प्रति दयालु होना याद रखें। आपने आज सुंदर काम किया है।",
            'pt': "Obrigado por compartilhar seus pensamentos e sentimentos comigo. Lembre-se de ser gentil consigo mesmo. Você fez um trabalho lindo hoje."
        }
    }
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found!")
        self.client = OpenAI(api_key=api_key)
        self.language = 'en'
        self.clear_memory()
    
    def start_chat(self, language='en'):
        if language not in self.PROMPTS['feel']:
            language = 'en'
        self.language = language
        return {'response': self.MESSAGES['welcome'][language], 'language': language, 'phase': self.phase}
    
    def process_text(self, text, language=None):
        if language and language in self.PROMPTS['feel']:
            self.language = language
        response = self._generate_response(text)
        return {'response': response, 'language': self.language, 'phase': self.phase, 'is_crisis': self._is_crisis(text)}
    
    def _generate_response(self, text):
        is_crisis = self._is_crisis(text)
        if is_crisis:
            return self._crisis_response(text)
        
        sentiment = TextBlob(text).sentiment.polarity
        sentiment_label = 'positive' if sentiment > 0.3 else 'negative' if sentiment < -0.3 else 'neutral'
        
        self.memory.append({'role': 'patient', 'text': text, 'sentiment': sentiment_label, 'phase': self.phase})
        
        context = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in self.memory[-6:]])
        system = self.PROMPTS[self.phase][self.language]
        user_msg = f"Conversation:\n{context}\n\nLatest: {text}"
        
        try:
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user_msg}],
                max_tokens=160, temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            
            # RELIEVE phase: remove any questions
            if self.phase == 'relieve' and '?' in reply:
                reply = reply.replace('?', '.').replace('Can you', 'You can').replace('What do', 'Consider')
        except:
            reply = "I'm here to listen. Tell me more."
        
        self.memory.append({'role': 'therapist', 'text': reply, 'phase': self.phase})
        self._advance_phase()
        return reply
    
    def _crisis_response(self, text):
        # Include recent conversation history for varied responses
        history = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in self.memory[-4:]])
        
        system = self.CRISIS_PROMPT[self.language]
        user_msg = f"Recent conversation:\n{history}\n\nUser now said: {text}\n\nRespond in {self._lang_name()}. EXACTLY 30-40 words. Different response - not a repetition. Be specific to their exact words and situation. Include crisis helpline. Show you understand their specific pain. Be unique and varied."
        
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user_msg}],
            max_tokens=100, temperature=0.9
        )
        reply = response.choices[0].message.content.strip()
        
        self.memory.append({'role': 'patient', 'text': text, 'sentiment': 'crisis', 'phase': 'crisis'})
        self.memory.append({'role': 'therapist', 'text': reply, 'phase': 'crisis'})
        return reply
    
    def _is_crisis(self, text):
        t = text.lower()
        # Exact keywords
        if any(kw in t for kw in self.CRISIS_KEYWORDS):
            return True
        # Pattern matching for typos and variations
        crisis_patterns = ['suicid', 'kill', 'die', 'self harm', 'hopeless', 'worthless', 'burden', 'end my', 'harm myself', 'want to d', 'no reason', 'better off']
        return any(pattern in t for pattern in crisis_patterns)
    
    def _lang_name(self):
        return {'en': 'English', 'hi': 'Hindi', 'pt': 'Portuguese'}[self.language]
    
    def _advance_phase(self):
        phases = ['feel', 'understand', 'relieve']
        idx = phases.index(self.phase)
        self.phase = phases[min(idx + 1, 2)]
    
    def _generate_summary(self):
        history = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in self.memory])
        system = f"Summarize compassionately. Respond in {self._lang_name()}."
        user_msg = f"Conversation:\n{history}"
        
        try:
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user_msg}],
                max_tokens=200, temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except:
            return "Session complete. Thank you for sharing."
    
    def end_session(self):
        return {'summary': self._generate_summary(), 'final_message': self.MESSAGES['final'][self.language], 'total_messages': len(self.memory)}
    
    def clear_memory(self):
        self.memory, self.phase, self.entry_start = [], 'feel', datetime.now()
    
    def get_memory(self):
        return self.memory


def main():
    print("\n" + "="*60)
    print("🌿 VoiceMind Journal AI - Live Chat")
    print("="*60)
    print("Type 'quit' to exit | 'summary' to end\n")
    
    journal = JournalAI()
    print("Select Language: 1=English, 2=Hindi, 3=Portuguese")
    lang = {'1': 'en', '2': 'hi', '3': 'pt'}.get(input("Choice (1-3): ").strip(), 'en')
    
    welcome = journal.start_chat(lang)
    print(f"\n🤖 {welcome['response']}\n")
    
    while True:
        user_input = input("👤 You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye!\n")
            break
        if user_input.lower() in ('summary', 'done'):
            if not journal.memory:
                print("\n⚠️  Share something first.\n")
                continue
            print("\n✅ Generating summary...\n")
            final = journal.end_session()
            print("="*60)
            print(f"{final['summary']}\n")
            print(f"💫 {final['final_message']}")
            print("="*60 + "\n")
            break
        
        response = journal.process_text(user_input)
        print(f"\n🤖 [{response['phase'].upper()}]: {response['response']}\n")


if __name__ == "__main__":
    main()