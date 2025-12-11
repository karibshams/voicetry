from openai import OpenAI
from textblob import TextBlob
from datetime import datetime
import os
from dotenv import load_dotenv
import re
import random

load_dotenv()

class JournalAI:
    """FEEL → UNDERSTAND → RELIEVE Journaling AI (Updated: warmer, faster, smarter crisis detection)"""
    
    PROMPTS = {
        'feel': {
            'en': (
                "You are a warm, close friend listening to someone. When they share a feeling, "
                "acknowledge it naturally and ask ONE gentle question. Keep it short (30-40 words), "
                "casual, and genuinely curious—like you really care. No techniques, no breathing exercises."
            ),
            'hi': (
                "आप एक गर्म, करीबी दोस्त हैं। जब कोई अपनी भावना साझा करे, "
                "स्वाभाविक रूप से उसे स्वीकारें और एक हल्का सवाल पूछें। 30-40 शब्दों में रखें, "
                "आरामदायक और सच में जिज्ञासु। कोई अभ्यास या तकनीक नहीं।"
            ),
            'pt': (
                "Você é um amigo caloroso e próximo escutando alguém. Quando compartilham um sentimento, "
                "reconheça naturalmente e faça UMA pergunta suave. Mantenha curto (30-40 palavras), "
                "casual e genuinamente curioso. Sem técnicas ou exercícios."
            )
        },

        'understand': {
            'en': (
                "You are their friend helping them go deeper. Ask ONE reflective question that shows "
                "you really listened. Keep it warm and short (30-40 words). No coping techniques, no advice. "
                "Just genuine curiosity about what they're experiencing."
            ),
            'hi': (
                "आप उनके दोस्त हैं जो गहरी समझ में मदद करते हैं। एक सवाल पूछें जो दिखाए कि आपने सुना है। "
                "गर्म और छोटा रखें (30-40 शब्द)। कोई सलाह नहीं, कोई तकनीक नहीं।"
            ),
            'pt': (
                "Você é seu amigo ajudando a aprofundar. Faça UMA pergunta que mostre que você realmente ouviu. "
                "Mantenha caloroso e curto (30-40 palavras). Sem técnicas ou conselhos."
            )
        },

        'relieve': {
            'en': (
                "You are a warm friend offering a gentle perspective. Acknowledge what they're going through "
                "with real warmth. Offer ONE soft insight or reframe—nothing commanding. No questions. "
                "Keep it short (35-45 words) and honest."
            ),
            'hi': (
                "आप एक गर्म दोस्त हैं जो कोमल दृष्टिकोण देते हैं। उनके अनुभव को सच्ची गर्मजोशी से स्वीकारें। "
                "एक हल्का दृष्टिकोण दें। कोई आदेश नहीं, कोई सवाल नहीं। 35-45 शब्दों में।"
            ),
            'pt': (
                "Você é um amigo caloroso oferecendo perspectiva suave. Reconheça o que estão vivendo "
                "com genuína calidez. Ofereça UMA percepção suave—nada comandante. Sem perguntas. "
                "Mantenha curto (35-45 palavras)."
            )
        }
    }

    CRISIS_KEYWORDS = [
        'suicide', 'suicid', 'kill myself', 'want to die', 'want to suicid',
        'end my life', 'harm myself', 'cant go on', 'can\'t go on', 'i want to die',
        'worthless', 'hopeless', 'no reason to live', 'better off dead',
        'going to kill', 'going to end', 'plan to', 'will kill'
    ]

    NEGATION_WORDS = ['don\'t', 'dont', 'didn\'t', 'didnt', 'not', 'no', 'won\'t', 'wont', 'never', 'wouldn\'t', 'wouldnt']

    CRISIS_TEMPLATE = ("I'm really glad you told me this. I can hear how much pain you're in. "
                       "Please reach out to {helpline} right now. You deserve support, and help is real. "
                       "You matter, and you're not alone.")

    MESSAGES = {
        'welcome': {
            'en': "Hey, welcome. This is your space to just... be honest about how you're really feeling. No judgment. What's on your mind?",
            'hi': "अरे, स्वागत है। यह तुम्हारी जगह है—अपने असली विचारों को साझा करने के लिए। कोई फैसला नहीं। क्या है तुम्हारे मन में?",
            'pt': "Oi, bem-vindo. Este é seu espaço para ser honesto sobre como você realmente está se sentindo. Sem julgamento. O que está em sua mente?"
        },
        'final': {
            'en': "Thank you for trusting me with this. You've been really brave today. Be kind to yourself, okay?",
            'hi': "मुझ पर विश्वास करने के लिए धन्यवाद। तुमने आज बहुत हिम्मत दिखाई है। अपने साथ दयालु रहना।",
            'pt': "Obrigado por confiar em mim. Você foi muito corajoso hoje. Seja gentil consigo mesmo, certo?"
        }
    }

    DEFAULT_RESPONSES = {
        'feel': [
            "That sounds really hard. What do you think made today especially tough?",
            "I hear you. That's a lot to carry. What's the heaviest part of this for you?",
            "Yeah, that makes sense. How long have you been feeling this way?",
            "That's heavy. What does it feel like in your body right now?"
        ],
        'understand': [
            "So it sounds like [specific thing they mentioned] is really hitting you. Why do you think that is?",
            "Tell me more about that. When you think about it, what comes up?",
            "I'm trying to understand—what would it look like if this felt even a little bit better?",
            "What's the hardest part about all this for you?"
        ],
        'relieve': [
            "It sounds like you've been carrying this alone for a while. That's a lot. But you're here, talking about it—that's real.",
            "This is heavy, and it makes total sense that you feel this way. Your feelings are valid.",
            "You've been through something, and you're still here. That takes strength, even if it doesn't feel like it.",
            "This is painful, and it's okay to feel exactly what you're feeling. You don't have to be okay right now."
        ]
    }

    def __init__(self, api_key=None, language='en'):
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Using fallback responses.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
        self.language = language if language in self.PROMPTS['feel'] else 'en'
        self.clear_memory()
        self.analysis = []

    def start_chat(self, language='en'):
        if language not in self.PROMPTS['feel']:
            language = 'en'
        self.language = language
        return {'response': self.MESSAGES['welcome'][language], 'language': language, 'phase': self.phase}

    def process_text(self, text, language=None):
        if language and language in self.PROMPTS['feel']:
            self.language = language

        # Check for crisis—with negation awareness
        is_crisis = self._is_crisis(text)
        if is_crisis:
            response = self._crisis_response(text)
            return {'response': response, 'language': self.language, 'phase': self.phase, 'is_crisis': True, 'analysis': None}

        # Generate response
        response = self._generate_response(text)
        
        # Generate analysis (silent, for panel only)
        analysis = self._generate_analysis(text)

        return {
            'response': response,
            'language': self.language,
            'phase': self.phase,
            'is_crisis': False,
            'analysis': analysis
        }

    def _is_crisis(self, text):
        """
        Smart crisis detection that understands negation.
        "didn't want to die" or "don't want to kill myself" = NOT crisis
        "want to die" or "going to kill myself" = CRISIS
        """
        if not text or not isinstance(text, str):
            return False

        t = text.lower().strip()

        # Check for negation first
        for neg in self.NEGATION_WORDS:
            if re.search(r'\b' + re.escape(neg) + r'\b.*\b(die|kill|suicide|suicid|end my life|harm)\b', t):
                return False  # Negated statement = NOT crisis

        # Explicit crisis phrases (without negation)
        explicit_phrases = [
            "i want to die", "i want to kill myself", "i want to suicide",
            "i'm going to kill myself", "i'm going to end my life",
            "i'm going to die", "i plan to kill", "will kill myself"
        ]
        for phrase in explicit_phrases:
            if phrase in t:
                return True

        # Keyword matching
        for kw in self.CRISIS_KEYWORDS:
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, t):
                return True

        return False

    def _generate_response(self, text):
        """Generate warm, short response like a close friend."""
        try:
            polarity = TextBlob(text).sentiment.polarity
        except Exception:
            polarity = 0.0

        sentiment_label = 'positive' if polarity > 0.3 else 'negative' if polarity < -0.3 else 'neutral'
        self.memory.append({'role': 'user', 'text': text, 'sentiment': sentiment_label, 'phase': self.phase})

        # Build context from last few messages
        context = "\n".join([f"{m['role'].title()}: {m['text']}" for m in self.memory[-6:]])
        system = self.PROMPTS.get(self.phase, {}).get(self.language, self.PROMPTS['feel']['en'])
        user_msg = f"Conversation so far:\n{context}\n\nRespond warmly and shortly (30-45 words max)."

        reply = None

        # Try API first
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[
                        {'role': 'system', 'content': system},
                        {'role': 'user', 'content': user_msg}
                    ],
                    max_tokens=100,
                    temperature=0.8
                )
                reply = response.choices[0].message.content.strip()

                # Ensure it's short and doesn't have commanding language
                reply = self._clean_response(reply)

            except Exception as e:
                print(f"API error (using fallback): {e}")
                reply = None

        # Fallback if API fails or no client
        if not reply:
            reply = random.choice(self.DEFAULT_RESPONSES.get(self.phase, self.DEFAULT_RESPONSES['feel']))

        self.memory.append({'role': 'therapist', 'text': reply, 'phase': self.phase})
        self._advance_phase()

        return reply

    def _clean_response(self, text):
        """Remove commanding language, trim to 45 words, ensure warmth."""
        # Remove commanding phrases
        text = re.sub(r'\b(You must|You should|You need to|Try to|You have to)\b', 'Consider', text, flags=re.IGNORECASE)

        # Remove therapy/diagnosis language
        text = re.sub(r'\b(diagnosed|condition|symptom|therapy|treatment|mental health issue)\b', '', text, flags=re.IGNORECASE)

        # Remove questions that shouldn't be there
        if text.count('?') > 1:
            sentences = text.split('.')
            text = '.'.join(sentences[:-1]) + '.'

        # Trim to 45 words
        words = text.split()
        if len(words) > 45:
            text = ' '.join(words[:45]) + '...'

        return text.strip()

    def _generate_analysis(self, text):
        """
        Generate deeper emotional analysis in the background.
        This is shown in analysis panel, NOT in chat.
        Returns sentiment, emotional depth, themes, etc.
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Determine emotional tone
            if polarity < -0.5:
                tone = 'deeply distressed'
            elif polarity < -0.2:
                tone = 'sad/troubled'
            elif polarity < 0:
                tone = 'concerned'
            elif polarity == 0:
                tone = 'neutral'
            else:
                tone = 'positive/hopeful'

            # Extract key themes
            themes = []
            theme_keywords = {
                'loneliness': ['alone', 'lonely', 'isolated', 'no one', 'by myself'],
                'loss/grief': ['lost', 'missing', 'miss', 'gone', 'breakup', 'break up'],
                'overwhelm': ['overwhelm', 'too much', 'can\'t handle', 'drowning', 'exhausted'],
                'uncertainty': ['don\'t know', 'confused', 'unsure', 'lost'],
                'self-worth': ['worthless', 'not good enough', 'failure', 'stupid']
            }

            text_lower = text.lower()
            for theme, keywords in theme_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    themes.append(theme)

            return {
                'emotional_tone': tone,
                'intensity': 'high' if abs(polarity) > 0.6 else 'moderate' if abs(polarity) > 0.3 else 'mild',
                'subjectivity': 'very personal' if subjectivity > 0.7 else 'balanced' if subjectivity > 0.4 else 'objective',
                'themes': themes,
                'polarity_score': round(polarity, 2)
            }

        except Exception:
            return {
                'emotional_tone': 'unknown',
                'intensity': 'unknown',
                'subjectivity': 'unknown',
                'themes': [],
                'polarity_score': 0
            }

    def _crisis_response(self, text):
        """Deterministic, warm crisis response."""
        self.phase = 'crisis'
        self.memory.append({'role': 'user', 'text': text, 'sentiment': 'crisis', 'phase': 'crisis'})

        helpline_text = self.crisis_helpline.strip() if self.crisis_helpline else "your local crisis helpline or emergency services"
        reply = self.CRISIS_TEMPLATE.format(helpline=helpline_text)

        self.memory.append({'role': 'therapist', 'text': reply, 'phase': 'crisis'})

        # Add crisis analysis
        self.analysis.append({
            'type': 'crisis',
            'detected_at': datetime.now().isoformat(),
            'severity': 'high'
        })

        return reply

    def _advance_phase(self):
        """Move through FEEL → UNDERSTAND → RELIEVE."""
        if self.phase == 'crisis':
            return

        phases = ['feel', 'understand', 'relieve']
        idx = phases.index(self.phase) if self.phase in phases else 0

        # After 2 exchanges in each phase, move to next
        phase_count = sum(1 for m in self.memory if m.get('phase') == self.phase)
        if phase_count >= 4:  # 2 user + 2 therapist exchanges
            self.phase = phases[min(idx + 1, len(phases) - 1)]

    def _generate_summary(self):
        """Generate brief, warm summary of the session."""
        if not self.memory:
            return "No messages recorded."

        # Extract key themes from all messages
        themes = []
        for m in self.memory:
            if m.get('role') == 'user':
                analysis = self._generate_analysis(m['text'])
                themes.extend(analysis.get('themes', []))

        theme_str = ', '.join(set(themes)) if themes else "their feelings"

        if self.client:
            try:
                history = "\n".join([f"{m['role'].title()}: {m['text']}" for m in self.memory])
                system = f"Write a brief, warm summary (60 words max) of this journal session in {self._lang_name()}. Be compassionate and human."
                user_msg = f"Session:\n{history}"

                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[
                        {'role': 'system', 'content': system},
                        {'role': 'user', 'content': user_msg}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass

        # Fallback summary
        return f"You opened up about {theme_str} today. That took courage. You're doing the right thing by being honest with yourself."

    def end_session(self):
        """End session and return summary + analysis data."""
        summary = self._generate_summary()

        return {
            'summary': summary,
            'final_message': self.MESSAGES['final'][self.language],
            'total_exchanges': len([m for m in self.memory if m['role'] == 'user']),
            'analysis_data': self.analysis  # Can be used by frontend for analytics
        }

    def clear_memory(self):
        self.memory = []
        self.phase = 'feel'
        self.entry_start = datetime.now()

    def get_memory(self):
        return self.memory

    def _lang_name(self):
        return {'en': 'English', 'hi': 'Hindi', 'pt': 'Portuguese'}.get(self.language, 'English')


# CLI Interface
def main():
    print("\n" + "="*60)
    print("🌿 VoiceMind Journal - Your Safe Space")
    print("="*60)
    print("Type 'quit' to exit | 'done' to finish session\n")

    journal = JournalAI()

    print("Pick a language: 1=English, 2=Hindi, 3=Portuguese")
    lang = {'1': 'en', '2': 'hi', '3': 'pt'}.get(input("Choice (1-3): ").strip(), 'en')

    welcome = journal.start_chat(lang)
    print(f"\n💭 {welcome['response']}\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            print("\n👋 Take care of yourself.\n")
            break

        if user_input.lower() == 'done':
            if not journal.memory:
                print("\n⚠️ Share something first.\n")
                continue

            print("\n✨ Wrapping up...\n")
            final = journal.end_session()

            print("="*60)
            print(f"\n{final['summary']}\n")
            print(f"💫 {final['final_message']}")
            print("="*60 + "\n")
            break

        result = journal.process_text(user_input)

        # Show warm response
        print(f"\n💭 {result['response']}\n")

        # Analysis is stored but not shown in chat (for frontend panel)
        if result.get('analysis'):
            # Uncomment to debug analysis:
            # print(f"[Analysis (hidden): {result['analysis']}]\n")
            pass


if __name__ == "__main__":
    main()