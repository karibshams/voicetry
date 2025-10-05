import json
from typing import Dict, Optional
from openai_agent import OpenAIAgent
class AppGuide:
    """AI helper for app feature explanations"""
    
    def __init__(self, openai_agent: OpenAIAgent):
        self.openai_agent = openai_agent
        self.knowledge_base = self._load_knowledge_base()
    
    def get_help_response(self, query: str, language: str = 'en') -> Dict[str, any]:
        """Generate helpful response for app-related queries"""
        # Find relevant knowledge
        relevant_info = self._search_knowledge(query)
        
        # Generate contextual response
        if relevant_info:
            prompt = f"Explain this app feature simply: {relevant_info}"
            response = self.openai_agent.get_chat_response(prompt, [], language)
        else:
            response = self._get_general_help_response(query, language)
        
        return {
            'response_text': response,
            'category': self._categorize_query(query),
            'has_tutorial': bool(relevant_info)
        }
    
    def _load_knowledge_base(self) -> Dict:
        """Load app features knowledge base"""
        return {
            'journaling': {
                'description': 'Record voice journals, get AI feedback',
                'steps': ['Tap mic button', 'Speak freely', 'Listen to Juno\'s response']
            },
            'sos': {
                'description': 'Emergency grounding tools and crisis support',
                'steps': ['Access from main menu', 'Choose breathing exercise', 'Follow guided support']
            },
            'faith': {
                'description': 'Spiritual wellness and meditation guidance',
                'steps': ['Select faith mode', 'Choose prayer/meditation', 'Follow gentle guidance']
            },
            'music': {
                'description': 'Therapeutic music recommendations',
                'steps': ['Open music section', 'Select mood', 'Play curated playlist']
            }
        }
    
    def _search_knowledge(self, query: str) -> Optional[str]:
        """Search knowledge base for relevant information"""
        query_lower = query.lower()
        for feature, info in self.knowledge_base.items():
            if feature in query_lower or any(word in query_lower for word in feature.split()):
                return f"{info['description']}. Steps: {', '.join(info['steps'])}"
        return None
    
    def _categorize_query(self, query: str) -> str:
        """Categorize user query for analytics"""
        categories = ['journaling', 'sos', 'faith', 'music', 'general']
        query_lower = query.lower()
        for category in categories:
            if category in query_lower:
                return category
        return 'general'
    
    def _get_general_help_response(self, query: str, language: str) -> str:
        """Generic helpful response when no specific knowledge found"""
        responses = {
            'en': "I'm here to help! Can you tell me more about what you'd like to do in the app?",
            'hi': "मैं मदद के लिए यहाँ हूँ! क्या आप बता सकते हैं कि आप ऐप में क्या करना चाहते हैं?",
            'pt': "Estou aqui para ajudar! Pode me dizer mais sobre o que gostaria de fazer no app?"
        }
        return responses.get(language, responses['en'])