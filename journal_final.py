# journal_final_fixed.py
from openai import OpenAI
from textblob import TextBlob
from datetime import datetime
import os
from dotenv import load_dotenv
import re
import random

load_dotenv()

class JournalAI:
    """FEEL → UNDERSTAND → RELIEVE Journaling AI (Fixed: crisis, phase, rotate practices)"""
    
    PROMPTS = {
    'feel': {
        'en': (
            "You are a calm, reflective journaling companion. When the user shares a feeling, "
            "validate it softly and ask ONE gentle reflective question. No exercises, no breathing, "
            "no grounding. Stay natural and under 70 words."
        ),
        'hi': (
            "आप एक शांत, चिंतनशील जर्नल साथी हैं। जब उपयोगकर्ता कोई भावना साझा करे, "
            "उसे कोमलता से स्वीकारें और ONE हल्का चिंतनशील प्रश्न पूछें। "
            "कोई ग्राउंडिंग, श्वास अभ्यास या मेडिटेशन न दें। 70 शब्दों से कम।"
        ),
        'pt': (
            "Você é um companheiro de diário calmo e reflexivo. Quando o usuário expressar um sentimento, "
            "valide suavemente e faça UMA pergunta reflexiva. Sem respiração, sem grounding, sem exercícios. "
            "Menos de 70 palavras."
        )
    },

    'understand': {
        'en': (
            "You are a gentle guide helping the user understand their emotions. Ask ONE deeper reflective "
            "question. No coping techniques, no breathing, no grounding. Keep it soft, simple, under 70 words."
        ),
        'hi': (
            "आप एक कोमल गाइड हैं जो उपयोगकर्ता को अपनी भावनाओं को समझने में मदद करते हैं। "
            "ONE गहरा चिंतनशील प्रश्न पूछें। कोई अभ्यास या श्वास तकनीक न दें। 70 शब्दों से कम।"
        ),
        'pt': (
            "Você é um guia gentil ajudando o usuário a compreender suas emoções. Faça UMA pergunta reflexiva "
            "mais profunda. Sem técnicas, sem respiração. Menos de 70 palavras."
        )
    },

    'relieve': {
        'en': (
            "RELIEVE PHASE — No exercises, no breathing, no grounding. You simply offer a calm emotional "
            "reflection acknowledging their difficulty, and give ONE gentle insight or perspective. "
            "Do NOT ask a question. Under 80 words."
        ),
        'hi': (
            "RELIEVE चरण — कोई अभ्यास, श्वास या ग्राउंडिंग नहीं। केवल शांत भावनात्मक प्रतिबिंब दें, "
            "उनके अनुभव को स्वीकारें और ONE हल्का दृष्टिकोण दें। कोई प्रश्न नहीं। 80 शब्दों से कम।"
        ),
        'pt': (
            "Fase RELIEVE — sem exercícios, respiração ou grounding. Ofereça apenas uma reflexão emocional calma, "
            "reconhecendo a dificuldade, com UMA perspectiva suave. Sem perguntas. Menos de 80 palavras."
        )
    }
}


    
    CRISIS_KEYWORDS = [
        'suicide', 'suicid', 'kill myself', 'want to die', 'want to suicid', 
        'end my life', 'harm myself', 'cant go on', 'can\'t go on', 'i want to die',
        'worthless', 'hopeless', 'no reason to live', 'better off dead'
    ]
    
    CRISIS_TEMPLATE = ("I'm very sorry you're feeling this way and I hear the depth of your pain. "
                       "Please contact immediate help — call {helpline} or your local emergency services now. "
                       "You are not alone; help is available.")

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
    
    DEFAULT_PRACTICES = [
        "Try a breathing cycle: inhale 4 counts, hold 4 counts, exhale 6 counts. Repeat a few times and notice your body settling.",
        "Grounding: notice five things you can see, four you can touch, three you can hear, two you can smell, one you can taste.",
        "Stillness: sit quietly for two minutes, softening shoulders, following the breath and letting thoughts pass without judgment.",
        "Reflection: write one short line about what you feel right now, then write one small thing you can do for yourself."
    ]
    
    def __init__(self, api_key=None, language='en'):
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Model calls will be skipped; fallback responses used.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
        self.language = language if language in self.PROMPTS['feel'] else 'en'
        self.clear_memory()
        self._practice_index = 0
        self._practices = list(self.DEFAULT_PRACTICES)
        random.shuffle(self._practices)
        self.crisis_helpline = os.getenv('CRISIS_HELPLINE', None)
    
    def start_chat(self, language='en'):
        if language not in self.PROMPTS['feel']:
            language = 'en'
        self.language = language
        return {'response': self.MESSAGES['welcome'][language], 'language': language, 'phase': self.phase}
    
    def process_text(self, text, language=None):
        if language and language in self.PROMPTS['feel']:
            self.language = language
        is_crisis = self._is_crisis(text)
        if is_crisis:
            response = self._crisis_response(text)
            return {'response': response, 'language': self.language, 'phase': self.phase, 'is_crisis': True}
        
        response = self._generate_response(text)
        return {'response': response, 'language': self.language, 'phase': self.phase, 'is_crisis': False}
    
    def _generate_response(self, text):
        try:
            polarity = TextBlob(text).sentiment.polarity
        except Exception:
            polarity = 0.0
        sentiment_label = 'positive' if polarity > 0.3 else 'negative' if polarity < -0.3 else 'neutral'
        self.memory.append({'role': 'patient', 'text': text, 'sentiment': sentiment_label, 'phase': self.phase})
        context = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in self.memory[-6:]])
        system = self.PROMPTS.get(self.phase, {}).get(self.language, self.PROMPTS['feel']['en'])
        user_msg = f"Conversation:\n{context}\n\nLatest: {text}"
        
        reply = None
        if not self.client:
            if self.phase == 'feel':
                reply = "Thank you for sharing. I hear you. What felt strongest about that experience for you?"
            elif self.phase == 'understand':
                reply = "I hear that. Tell me more about what that felt like in your body or day-to-day life."
            elif self.phase == 'relieve':
                reply = self._generate_relieve_reflection(text)
            else:
                reply = "I'm here to listen."
        else:
            try:
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user_msg}],
                    max_tokens=160, temperature=0.7
                )
                reply = response.choices[0].message.content.strip()
                if self.phase == 'relieve':
        
                    if '?' in reply:
                        reply = self._sanitize_relieve_reply(reply)
            except Exception:
    
                reply = "I'm here to listen. Tell me more."
        
        self.memory.append({'role': 'therapist', 'text': reply, 'phase': self.phase})
        self._advance_phase()
        return reply
    
    def _crisis_response(self, text):
        """
        Deterministic crisis reply using a template of 30-40 words.
        We set phase to 'crisis' and DO NOT call the model here.
        """
        self.phase = 'crisis'
        self.memory.append({'role': 'patient', 'text': text, 'sentiment': 'crisis', 'phase': 'crisis'})
        
        helpline_text = self.crisis_helpline.strip() if self.crisis_helpline else "your local emergency services or a trusted person"
        reply = self.CRISIS_TEMPLATE.format(helpline=helpline_text)
        word_count = len(reply.split())
        if word_count > 40:
            reply = self.CRISIS_TEMPLATE.format(helpline="local emergency services")
        self.memory.append({'role': 'therapist', 'text': reply, 'phase': 'crisis'})
        return reply
    
    def _is_crisis(self, text):
        """
        More robust matching: case-insensitive, word-boundary checks and some phrase checks.
        """
        if not text or not isinstance(text, str):
            return False
        t = text.lower().strip()
        explicit_phrases = [
            "i want to die", "i want to kill myself", "i want to suicide",
            "i want to end my life", "i'm going to kill myself", "i'm going to end my life"
        ]
        for phrase in explicit_phrases:
            if phrase in t:
                return True
        for kw in self.CRISIS_KEYWORDS:
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, t):
                return True
        if re.search(r'\b(suicid|suicidal|kill myself|harm myself)\b', t):
            return True
        return False
    
    def _generate_relieve_reflection(self, text):
        reflections = [
         "It sounds like this has been heavy on your heart. It's okay to slow down and take in what you're feeling.",
         "This feels like a lot to carry. You’ve made space for your feelings today, and that matters.",
         "You’ve been holding a lot inside. It’s alright to soften for a moment and simply notice what’s here.",
         "This moment seems overwhelming, but acknowledging it is already a meaningful step."
       ]
        return random.choice(reflections)

    
    def _sanitize_relieve_reply(self, text):
        """Remove questions and convert them into directive sentences for RELIEVE phase."""
        sanitized = text.replace('?', '.')
        sanitized = re.sub(r'\b(Can you|Could you|Would you|What do you)\b', 'Consider', sanitized, flags=re.IGNORECASE)
        words = sanitized.split()
        if len(words) > 80:
            sanitized = ' '.join(words[:80]) + '...'
        return sanitized
    
    def _lang_name(self):
        return {'en': 'English', 'hi': 'Hindi', 'pt': 'Portuguese'}.get(self.language, 'English')
    
    def _advance_phase(self):
        if self.phase == 'crisis':
            return  
        phases = ['feel', 'understand', 'relieve']
        idx = phases.index(self.phase) if self.phase in phases else 0
        self.phase = phases[min(idx + 1, len(phases) - 1)]

    
    def _generate_summary(self):
        history = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in self.memory])
        system = f"Summarize compassionately. Respond in {self._lang_name()}."
        user_msg = f"Conversation:\n{history}"
        
        if not self.client:
            return "Session complete. Thank you for sharing."
        try:
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user_msg}],
                max_tokens=200, temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Session complete. Thank you for sharing."
    
    def end_session(self):
        return {'summary': self._generate_summary(), 'final_message': self.MESSAGES['final'][self.language], 'total_messages': len(self.memory)}
    
    def clear_memory(self):
        self.memory, self.phase, self.entry_start = [], 'feel', datetime.now()
    
    def get_memory(self):
        return self.memory


