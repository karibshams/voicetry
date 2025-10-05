import openai
from typing import Dict, List, Optional

class OpenAIAgent:
    """OpenAI API wrapper for all AI operations"""
    
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.model = "gpt-4"
        self.language_prompts = {
            'en': 'Respond in English',
            'hi': 'Respond in Hindi',
            'pt': 'Respond in Portuguese'
        }
    
    def summarize_journal(self, text: str, language: str = 'en') -> str:
        """Summarize voice journal entry"""
        prompt = f"""
        {self.language_prompts[language]}. Act as an empathetic wellness coach.
        Summarize this journal entry with gentle advice:
        
        "{text}"
        
        Keep response warm, supportive, and under 100 words.
        """
        return self._get_completion(prompt)
    
    def get_chat_response(self, message: str, context: List[Dict], language: str = 'en') -> str:
        """Generate contextual chat response"""
        prompt = f"""
        {self.language_prompts[language]}. You are Juno, a Gen Z AI wellness friend.
        
        Context: {context}
        User message: "{message}"
        
        Respond naturally, warmly, and supportively.
        """
        return self._get_completion(prompt)
    
    def generate_affirmation(self, mood: str, language: str = 'en') -> str:
        """Generate mood-based affirmation"""
        prompt = f"""
        {self.language_prompts[language]}. Create a positive affirmation for someone feeling {mood}.
        Make it personal, uplifting, and Gen Z friendly.
        """
        return self._get_completion(prompt)
    
    def _get_completion(self, prompt: str) -> str:
        """Private method for OpenAI API calls"""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()