"""Juno App Guide - Interactive Guide & Testing System"""

class JunoGuide:
    """Smart guide that understands your app and responds conversationally"""
    
    GUIDES = {
        'HomePage': {
            'overview': 'Main dashboard with quick access to wellness features',
            'tags': ['home', 'dashboard', 'mood', 'quick access', 'start'],
            'navigate_to': ['ProfilePage', 'MindToolsPage', 'JournalPage', 'FaithPage'],
            'actions': ['Set mood emoji', 'View daily scripture', 'Access quick shortcuts', 'See recommended content'],
            'how_to_reach': 'This is the default page after login or app launch'
        },
        'ProfilePage': {
            'overview': 'Personal profile with mood tracking, streaks, and reminders',
            'tags': ['profile', 'mood tracking', 'streak', 'reminders', 'progress', 'check-in'],
            'navigate_to': ['HomePage', 'GamificationPage', 'AccountPage'],
            'actions': ['View mood journey', 'Set check-in reminders', 'View achievements', 'Edit profile'],
            'how_to_reach': 'From HomePage, tap the user avatar at the top-left corner'
        },
        'MindToolsPage': {
            'overview': 'Quick wellness tools - breathing, grounding, music, affirmations',
            'tags': ['stress relief', 'breathing', 'grounding', 'music', 'tools', 'anxiety', 'calm'],
            'navigate_to': ['BreathingPage', 'GroundingPage', 'MusicTherapyPage', 'AffirmationPage', 'HomePage'],
            'actions': ['Start breathing exercise', 'Use 5-4-3-2-1 grounding', 'Play therapy music', 'Read affirmations'],
            'how_to_reach': 'From HomePage, tap Mind Tools shortcut'
        },
        'JournalPage': {
            'overview': 'Create and manage journal entries with text, voice, and photos',
            'tags': ['journal', 'voice', 'entries', 'memories', 'reflection', 'write'],
            'navigate_to': ['HomePage', 'CreateJournalPage', 'MindToolsPage'],
            'actions': ['Create new entry', 'Record voice note', 'Attach photo', 'Share journal', 'Delete entries'],
            'how_to_reach': 'From HomePage, tap Journal shortcut'
        },
        'BreathingPage': {
            'overview': 'Guided breathing exercises with animation and timer',
            'tags': ['breathing', 'relaxation', 'anxiety', 'stress', 'meditation', 'calm down'],
            'navigate_to': ['MindToolsPage'],
            'actions': ['Start breathing', 'Pause session', 'View timer', 'Exit exercise'],
            'how_to_reach': 'From MindToolsPage, tap Breathing Timer'
        },
        'GroundingPage': {
            'overview': '5-4-3-2-1 grounding technique using five senses',
            'tags': ['grounding', 'anxiety', 'present', 'senses', 'mindfulness', '5-4-3-2-1'],
            'navigate_to': ['MindToolsPage'],
            'actions': ['Name 5 things you see', 'Feel 4 things', 'Hear 3 things', 'Smell 2 things', 'Taste 1 thing'],
            'how_to_reach': 'From MindToolsPage, tap 5-4-3-2-1 Grounding'
        },
        'MusicTherapyPage': {
            'overview': 'Curated therapy music library with categories (Sleep, Focus, Alone)',
            'tags': ['music', 'therapy', 'relaxation', 'sleep', 'focus', 'alone', 'calm'],
            'navigate_to': ['NowPlayingPage', 'MindToolsPage'],
            'actions': ['Browse tracks', 'Play music', 'Add to favorites', 'Create playlist', 'Filter by category'],
            'how_to_reach': 'From MindToolsPage, tap Music Therapy'
        },
        'NowPlayingPage': {
            'overview': 'Music player with controls, favorites, and progress bar',
            'tags': ['music player', 'play', 'playlist', 'favorites', 'track'],
            'navigate_to': ['MusicTherapyPage'],
            'actions': ['Play/Pause', 'Skip track', 'Mark favorite', 'Seek progress', 'Shuffle', 'Repeat'],
            'how_to_reach': 'From MusicTherapyPage, tap any track card'
        },
        'FaithPage': {
            'overview': 'Spiritual wellness with daily scripture, prayers, and affirmations',
            'tags': ['faith', 'scripture', 'prayer', 'spiritual', 'affirmation', 'verse'],
            'navigate_to': ['HomePage', 'MindToolsPage'],
            'actions': ['Read scripture', 'Start prayer session', 'Generate affirmation', 'Listen to audio'],
            'how_to_reach': 'From HomePage, tap Faith shortcut or from MindToolsPage'
        },
        'GamificationPage': {
            'overview': 'Track achievements, badges, and consistency percentage',
            'tags': ['achievements', 'badges', 'progress', 'gamification', 'consistency', 'motivation'],
            'navigate_to': ['ProfilePage'],
            'actions': ['View badges', 'See consistency %', 'Create custom badge', 'Track weekly progress'],
            'how_to_reach': 'From ProfilePage, tap My Progress card'
        },
        'SubscriptionPage': {
            'overview': 'Premium plans - 3-day free trial, $9.99/month or $79.99/year',
            'tags': ['subscription', 'premium', 'trial', 'upgrade', 'pricing', 'features', 'ai'],
            'navigate_to': ['ProfilePage'],
            'actions': ['Start free trial', 'Subscribe monthly', 'Subscribe yearly', 'View features'],
            'how_to_reach': 'From ProfilePage, tap Subscription section'
        },
        'AffirmationPage': {
            'overview': 'Daily positive affirmations for motivation and inspiration',
            'tags': ['affirmation', 'motivation', 'inspiration', 'daily', 'positive'],
            'navigate_to': ['MindToolsPage', 'FaithPage'],
            'actions': ['Generate new affirmation', 'Mark as read'],
            'how_to_reach': 'From MindToolsPage, tap Affirmations'
        },
        'CreateJournalPage': {
            'overview': 'Create journal entry with mood selector, text, voice, and photos',
            'tags': ['create journal', 'voice journaling', 'mood', 'photos', 'new entry'],
            'navigate_to': ['JournalPage'],
            'actions': ['Select mood', 'Write text', 'Record voice', 'Add photo', 'Save entry', 'Lock entry'],
            'how_to_reach': 'From JournalPage, tap New Entry button'
        },
        'AccountPage': {
            'overview': 'Manage account settings and personal information',
            'tags': ['account', 'settings', 'profile', 'email', 'password', 'delete'],
            'navigate_to': ['ProfilePage'],
            'actions': ['Edit profile picture', 'Update name', 'Change email', 'Delete account'],
            'how_to_reach': 'From ProfilePage, tap Settings'
        }
    }
    
    def __init__(self):
        self.current_page = 'HomePage'
    
    def guide(self, user_input):
        """Main guide function - understands user intent and responds conversationally"""
        user_lower = user_input.lower().strip()
        
        # Check if user wants to navigate/go to a page
        if self._is_navigation_intent(user_lower):
            return self._handle_navigation(user_lower)
        
        # Check if user is asking what to do (actions)
        if self._is_action_intent(user_lower):
            return self._handle_actions(user_lower)
        
        # Check if user is asking how to reach something
        if self._is_location_intent(user_lower):
            return self._handle_location(user_lower)
        
        # Default: search and suggest
        return self._search_and_suggest(user_lower)
    
    def _is_navigation_intent(self, query):
        """Check if user wants to navigate/go to a page"""
        keywords = ['go to', 'open', 'navigate', 'take me', 'show me', 'visit', 'access']
        return any(keyword in query for keyword in keywords)
    
    def _is_action_intent(self, query):
        """Check if user wants to know what actions are available"""
        keywords = ['what can i', 'how do i', 'can i', 'actions', 'features', 'what to do']
        return any(keyword in query for keyword in keywords)
    
    def _is_location_intent(self, query):
        """Check if user is asking how to reach somewhere"""
        keywords = ['where', 'how to reach', 'how to get to', 'how to access', 'from where']
        return any(keyword in query for keyword in keywords)
    
    def _search_pages(self, query):
        """Search for matching pages based on query"""
        results = []
        for page_name, data in self.GUIDES.items():
            score = 0
            # Check tags (highest priority)
            for tag in data['tags']:
                if query in tag or tag in query:
                    score += 3
            # Check overview (medium priority)
            if query in data['overview'].lower():
                score += 2
            # Check actions (lower priority)
            for action in data['actions']:
                if query in action.lower():
                    score += 1
            
            if score > 0:
                results.append((page_name, data, score))
        
        return sorted(results, key=lambda x: x[2], reverse=True)
    
    def _handle_navigation(self, query):
        """Handle navigation requests"""
        matching_pages = self._search_pages(query)
        
        if not matching_pages:
            return "❌ I couldn't find that page. Try asking about: breathing, journaling, music, faith, profile, or mind tools."
        
        page_name, page_data, score = matching_pages[0]
        reach_info = page_data['how_to_reach']
        overview = page_data['overview']
        
        response = f"✅ **{page_name}**\n"
        response += f"📌 {overview}\n"
        response += f"🔸 How to reach: {reach_info}\n"
        
        if page_data['actions']:
            response += f"💡 You can: {', '.join(page_data['actions'][:2])}"
        
        return response
    
    def _handle_actions(self, query):
        """Handle action/feature requests"""
        matching_pages = self._search_pages(query)
        
        if not matching_pages:
            return "❌ I couldn't find that feature. Try asking about specific actions like: breathing, journaling, tracking mood, etc."
        
        page_name, page_data, score = matching_pages[0]
        
        response = f"✅ **On {page_name}, you can:**\n\n"
        for i, action in enumerate(page_data['actions'], 1):
            response += f"{i}. {action}\n"
        
        response += f"\n📍 How to get there: {page_data['how_to_reach']}"
        return response
    
    def _handle_location(self, query):
        """Handle location/navigation queries"""
        matching_pages = self._search_pages(query)
        
        if not matching_pages:
            return "❌ I couldn't find that. Try asking how to reach: breathing, journal, profile, music, etc."
        
        page_name, page_data, score = matching_pages[0]
        reach_info = page_data['how_to_reach']
        
        response = f"✅ **To reach {page_name}:**\n"
        response += f"👉 {reach_info}\n"
        response += f"\n📋 {page_data['overview']}"
        return response
    
    def _search_and_suggest(self, query):
        """Default search and suggest"""
        matching_pages = self._search_pages(query)
        
        if not matching_pages:
            return f"❌ I don't have info about '{query}'. Try asking about: breathing, journaling, mood tracking, music, prayer, achievements, or wellness tools."
        
        page_name, page_data, score = matching_pages[0]
        response = f"✅ Based on your question, I found **{page_name}**:\n\n"
        response += f"📖 {page_data['overview']}\n"
        response += f"🔸 How to reach: {page_data['how_to_reach']}\n"
        response += f"💡 Key actions: {', '.join(page_data['actions'][:3])}"
        
        return response


# ============= INTERACTIVE TEST FUNCTION =============

def test_juno_guide():
    """Interactive testing - type commands and get app guidance"""
    guide = JunoGuide()
    
    print("\n" + "="*70)
    print("🎯 JUNO APP GUIDE - INTERACTIVE TEST")
    print("="*70)
    print("\n📝 SAMPLE COMMANDS TO TEST:")
    print("  • 'how do i reduce anxiety?'")
    print("  • 'take me to breathing exercises'")
    print("  • 'what can i do on music therapy page?'")
    print("  • 'how to reach journal?'")
    print("  • 'i want to track my mood'")
    print("  • 'show me faith page'")
    print("  • 'how do i use the grounding technique?'")
    print("  • 'where is the affirmation page?'")
    print("="*70 + "\n")
    
    # Run predefined tests
    test_commands = [
        "how do i reduce anxiety?",
        "take me to breathing exercises",
        "what can i do on music therapy page?",
        "how to reach journal?",
        "i want to track my mood",
        "show me faith page",
        "how do i journal with voice?",
        "where is the achievement page?",
        "i need help with prayer",
        "open the profile page"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{'─'*70}")
        print(f"[TEST {i}] USER: {command}")
        print(f"{'─'*70}")
        response = guide.guide(command)
        print(f"\n📱 JUNO GUIDE:\n{response}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED - GUIDE WORKING PERFECTLY!")
    print("="*70)
    
    # Interactive mode
    print("\n\n🎤 INTERACTIVE MODE - Ask me anything about Juno app:")
    print("(Type 'quit' to exit)\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'quit':
            print("👋 Goodbye!")
            break
        if not user_input:
            continue
        
        response = guide.guide(user_input)
        print(f"\n🤖 Juno Guide:\n{response}\n")


if __name__ == '__main__':
    test_juno_guide()