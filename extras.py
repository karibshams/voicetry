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
    

from coach_ai import CoachAI

coach = CoachAI()

def test_text(text, lang='en'):
    """Test text input"""
    response = coach.process_text(text, lang=lang)
    
    print(f"\n💭 You: {response['text_input']}")
    print(f"💬 Coach: {response['coach_reply']}")

def text_chat(lang='en'):
    """Multi-turn text chat"""
    coach.set_user_context(lang=lang)
    print(f"\n💬 TEXT CHAT")
    print("Commands: 'lang' (change language), 'quit' (exit)\n")
    
    while True:
        print(f"[Lang: {lang}]", end=" ")
        msg = input("💭 You: ").strip()
        
        if msg.lower() == 'quit':
            break
        elif msg.lower() == 'lang':
            new_lang = input("Language (en/hi/pt): ").strip()
            if new_lang in ['en', 'hi', 'pt']:
                lang = new_lang
                coach.set_user_context(lang=lang)
                print(f"✅ Language changed to {lang}\n")
            else:
                print("❌ Invalid language\n")
        elif msg:
            response = coach.process_text(msg, lang=lang)
            print(f"💬 Coach: {response['coach_reply']}\n")

def show_stats():
    """Show session statistics"""
    stats = coach.get_stats()
    print("\n" + "="*50)
    print("📊 SESSION STATS")
    print("="*50)
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Languages: {', '.join(stats['languages_used']) if stats['languages_used'] else 'None'}")
    print(f"Current Language: {stats['current_language']}")
    print(f"Preferred Voice: {stats['preferred_voice']}")
    print(f"Session Start: {stats['session_start']}")

if __name__ == "__main__":
    try:
        while True:
            print("\n" + "="*50)
            print("💬 COACH AI - TEXT TESTING")
            print("="*50)
            print("1. Single Text Message")
            print("2. Text Chat (Multi-turn)")
            print("3. View Stats")
            print("4. Exit")
            print("-"*50)
            
            choice = input("Choose (1-4): ").strip()
            
            if choice == '1':
                text = input("Your message: ").strip()
                lang = input("Language (en/hi/pt) [en]: ").strip() or 'en'
                if text and lang in ['en', 'hi', 'pt']:
                    test_text(text, lang)
                else:
                    print("❌ Invalid input")
            
            elif choice == '2':
                lang = input("Language (en/hi/pt) [en]: ").strip() or 'en'
                if lang in ['en', 'hi', 'pt']:
                    text_chat(lang)
                else:
                    print("❌ Invalid input")
            
            elif choice == '3':
                show_stats()
            
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n👋 Bye!")
from journal_final import JournalAI
def main():
    print("\n" + "="*60)
    print("🌿 VoiceMind Journal AI - Live Chat (Fixed)")
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
        # Print phase label. If crisis, show CRISIS explicitly.
        phase_label = response['phase'].upper()
        print(f"\n🤖 [{phase_label}]: {response['response']}\n")


if __name__ == "__main__":
    main()
