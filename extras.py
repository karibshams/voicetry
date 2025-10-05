from typing import Dict, List
from datetime import datetime
import random

class JunoExtras:
    """Additional AI features: affirmations, badges, music, avatar"""
    
    def __init__(self, openai_agent):
        self.openai_agent = openai_agent
        self.badge_system = BadgeSystem()
        self.music_recommender = MusicRecommender()
        self.avatar_controller = AvatarController()
    
    def generate_daily_affirmation(self, mood: str, language: str = 'en') -> Dict[str, any]:
        """Generate personalized daily affirmation"""
        affirmation = self.openai_agent.generate_affirmation(mood, language)
        avatar_action = self.avatar_controller.get_affirmation_pose()
        
        return {
            'text': affirmation,
            'avatar_action': avatar_action,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_badges(self, user_activity: Dict) -> List[Dict]:
        """Check for earned badges and celebrations"""
        return self.badge_system.check_earned_badges(user_activity)
    
    def recommend_music(self, mood: str, language: str = 'en') -> Dict[str, any]:
        """Recommend therapeutic music based on mood"""
        return self.music_recommender.get_recommendations(mood, language)


class BadgeSystem:
    """Badge and achievement system"""
    
    def __init__(self):
        self.badges = {
            'first_journal': {'name': 'First Steps', 'trigger': 'journal_count_1'},
            'week_streak': {'name': 'Week Warrior', 'trigger': 'streak_7'},
            'mood_tracker': {'name': 'Mood Master', 'trigger': 'mood_entries_10'}
        }
    
    def check_earned_badges(self, activity: Dict) -> List[Dict]:
        """Check which badges user has earned"""
        earned = []
        for badge_id, badge_info in self.badges.items():
            if self._check_trigger(badge_info['trigger'], activity):
                earned.append({
                    'badge_id': badge_id,
                    'name': badge_info['name'],
                    'celebration': True
                })
        return earned
    
    def _check_trigger(self, trigger: str, activity: Dict) -> bool:
        """Check if badge trigger condition is met"""
        if trigger == 'journal_count_1':
            return activity.get('journal_count', 0) >= 1
        elif trigger == 'streak_7':
            return activity.get('streak_days', 0) >= 7
        elif trigger == 'mood_entries_10':
            return activity.get('mood_entries', 0) >= 10
        return False


class MusicRecommender:
    """Music therapy recommendation system"""
    
    def __init__(self):
        self.mood_playlists = {
            'sad': ['Healing Sounds', 'Gentle Rain', 'Peaceful Piano'],
            'anxious': ['Calm Breathing', 'Ocean Waves', 'Meditation'],
            'happy': ['Uplifting Vibes', 'Morning Energy', 'Positive Flow'],
            'calm': ['Zen Garden', 'Soft Instrumental', 'Nature Sounds']
        }
    
    def get_recommendations(self, mood: str, language: str = 'en') -> Dict[str, any]:
        """Get mood-based music recommendations"""
        playlists = self.mood_playlists.get(mood, self.mood_playlists['calm'])
        return {
            'recommended_playlists': playlists,
            'mood': mood,
            'explanation': f"Music selected for {mood} mood"
        }


class AvatarController:
    """Avatar expressions and animations controller"""
    
    def __init__(self):
        self.expressions = {
            'happy': {'animation': 'smile', 'glow': 'warm_yellow'},
            'sad': {'animation': 'empathetic_nod', 'glow': 'soft_blue'},
            'anxious': {'animation': 'concerned_tilt', 'glow': 'gentle_purple'},
            'calm': {'animation': 'peaceful_breathe', 'glow': 'mint_green'},
            'celebrating': {'animation': 'celebration_dance', 'glow': 'rainbow'}
        }
    
    def get_expression(self, emotion: str) -> Dict[str, str]:
        """Get avatar expression for emotion"""
        return self.expressions.get(emotion, self.expressions['calm'])
    
    def get_affirmation_pose(self) -> Dict[str, str]:
        """Special pose for affirmations"""
        return {'animation': 'encouraging_gesture', 'glow': 'inspiring_gold'}