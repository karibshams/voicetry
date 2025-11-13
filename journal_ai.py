import os
from openai import OpenAI
from textblob import TextBlob
from dotenv import load_dotenv
from voice import VoiceEngine
from prompt import Prompts

load_dotenv()


class JournalAI:
    """Professional AI Therapist - Voice and Text Support"""

    SUPPORTED_LANGUAGES = {
        'en': 'english',
        'hi': 'hindi',
        'pt': 'portuguese'
    }

    THERAPIST_PROMPTS = {
        'en': "You are Dr. juno, a compassionate and professional AI therapist with 15+ years clinical experience. Ask thoughtful diagnostic questions to understand patient's physical, emotional, and mental health. Ask 5-9 questions one at a time. After gathering sufficient information, provide clinical assessment and evidence-based treatment recommendations. Be warm, professional, and never minimize concerns. Keep responses under 130 words.",
        'hi': "आप डॉ. जूनो हैं, एक सहानुभूतिपूर्ण और पेशेवर एआई चिकित्सक। रोगी के स्वास्थ्य को समझने के लिए 5-9 विचारशील प्रश्न पूछें। एक बार में एक प्रश्न पूछें। पर्याप्त जानकारी के बाद, क्लिनिकल मूल्यांकन और उपचार सुझाएं। गर्म, पेशेवर रहें। 130 शब्दों से कम रखें।",
        'pt': "Você é Dra. juno, uma terapeuta de IA compassiva e profissional com 15+ anos de experiência clínica. Faça 5-9 perguntas diagnósticas para entender a saúde do paciente. Uma pergunta por vez. Após coletar informações, forneça avaliação clínica e recomendações de tratamento. Seja calorosa e profissional. Máximo 130 palavras."
    }

    def __init__(self):
        """Initialize therapist with API clients"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
        
        self.client = OpenAI(api_key=api_key)
        self.voice = VoiceEngine()
        self.memory = []
        self.questions_asked = 0
        self.diagnosis_done = False
        print("✅ JournalAI Therapist initialized")

    def process_voice(self, audio_data: bytes, language: str = 'en', gender: str = 'female') -> dict:
        """
        Process voice input from patient
        
        Args:
            audio_data: Audio bytes from STT
            language: 'en', 'hi', or 'pt'
            gender: 'male' or 'female' for voice response
        
        Returns:
            dict: Response with text and audio
        """
        if language not in self.SUPPORTED_LANGUAGES:
            language = 'en'

        # Speech to Text
        stt_result = self.voice.speech_to_text(audio_data)
        patient_text = stt_result['text']
        
        if not patient_text:
            error_msg = "I couldn't hear you clearly. Could you please repeat?"
            audio = self.voice.text_to_speech(error_msg, language, gender)
            return {'text': error_msg, 'audio': audio, 'language': language}

        # Process text and get response
        response_text = self._generate_response(patient_text, language)

        # Text to Speech
        response_audio = self.voice.text_to_speech(response_text, language, gender)

        return {
            'patient_input': patient_text,
            'response': response_text,
            'audio': response_audio,
            'language': language,
            'questions_asked': self.questions_asked,
            'diagnosis_done': self.diagnosis_done
        }

    def process_text(self, patient_text: str, language: str = 'en') -> dict:
        """
        Process text input from patient
        
        Args:
            patient_text: Patient's message as text
            language: 'en', 'hi', or 'pt'
        
        Returns:
            dict: Response text
        """
        if language not in self.SUPPORTED_LANGUAGES:
            language = 'en'

        response_text = self._generate_response(patient_text, language)

        return {
            'patient_input': patient_text,
            'response': response_text,
            'language': language,
            'questions_asked': self.questions_asked,
            'diagnosis_done': self.diagnosis_done
        }

    def _generate_response(self, patient_text: str, language: str) -> str:
        """Generate therapist response based on conversation phase"""
        
        # Store in memory
        sentiment = self._analyze_sentiment(patient_text)
        self.memory.append({
            'role': 'patient',
            'text': patient_text,
            'sentiment': sentiment
        })

        # Build conversation context
        conversation_context = "\n".join([
            f"{m['role'].capitalize()}: {m['text']}"
            for m in self.memory[-6:]
        ])

        # Determine response phase
        if self.questions_asked < 9 and not self.diagnosis_done:
            system_msg = f"{self.THERAPIST_PROMPTS[language]} You have asked {self.questions_asked} questions so far. Ask a thoughtful diagnostic question."
        elif not self.diagnosis_done:
            system_msg = f"{self.THERAPIST_PROMPTS[language]} You have gathered sufficient information. Now provide a professional clinical assessment and evidence-based treatment recommendations."
            self.diagnosis_done = True
        else:
            system_msg = f"{self.THERAPIST_PROMPTS[language]} Patient has received recommendations. Provide supportive follow-up guidance."

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

        # Store response in memory
        self.memory.append({
            'role': 'therapist',
            'text': therapist_reply
        })

        if not self.diagnosis_done or self.questions_asked < 9:
            self.questions_asked += 1

        return therapist_reply

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze patient sentiment"""
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
        """Clear memory for new patient session"""
        self.memory = []
        self.questions_asked = 0
        self.diagnosis_done = False
        print("✅ Memory cleared - Ready for new patient")


def main():
    """Test JournalAI with text input"""
    therapist = JournalAI()
    
    print("\n🏥 JournalAI Therapist - Test Mode")
    print("=" * 50)
    print("Type 'exit' to quit | 'memory' to see history\n")
    
    while True:
        try:
            patient_input = input("👤 You: ").strip()
            
            if patient_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            
            if patient_input.lower() == 'memory':
                print("\n📋 Conversation Memory:")
                for msg in therapist.get_memory():
                    print(f"{msg['role'].upper()}: {msg['text']}\n")
                continue
            
            if not patient_input:
                continue
            
            # Process text input
            result = therapist.process_text(patient_input, language='en')
            
            print(f"\n🤖 Dr. juno: {result['response']}")
            print(f"📊 Questions asked: {result['questions_asked']} | Diagnosis done: {result['diagnosis_done']}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Session ended!")
            break

if __name__ == "__main__":
    main()