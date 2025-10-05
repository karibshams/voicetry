from textblob import TextBlob
from typing import Dict, Tuple

class SentimentAnalyzer:
    """Emotion and mood detection from text"""
    
    def __init__(self):
        self.mood_map = {
            'positive_high': 'happy',
            'positive_low': 'calm',
            'negative_high': 'anxious',
            'negative_low': 'sad',
            'neutral': 'neutral'
        }
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'hurt myself',
            'self harm', 'cutting', 'die', 'worthless'
        ]
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """Analyze text sentiment and detect mood"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        mood = self._get_mood(polarity, subjectivity)
        crisis_detected = self._detect_crisis(text)
        
        return {
            'mood': mood,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'crisis_detected': crisis_detected,
            'confidence': abs(polarity)
        }
    
    def _get_mood(self, polarity: float, subjectivity: float) -> str:
        """Map sentiment to mood categories"""
        if polarity > 0.3:
            return 'happy' if subjectivity > 0.5 else 'calm'
        elif polarity < -0.3:
            return 'anxious' if subjectivity > 0.5 else 'sad'
        return 'neutral'
    
    def _detect_crisis(self, text: str) -> bool:
        """Detect crisis/self-harm keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crisis_keywords)