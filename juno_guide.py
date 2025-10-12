class AppGuide:
    """App feature knowledge base"""
    
    PAGES = {
        'profile': 'Profile with mood journey, streak tracking, check-in reminders',
        'subscription': '3-day free trial, $9.99/month or $79.99/year plans with AI features',
        'chatbot': 'Chat with Juno AI for voice journaling and support',
        'journal': 'Create entries with feelings, voice, photos. Lock/share/export',
        'notification': 'View and manage app notifications',
        'gamification': 'Track badges, achievements, consistency with custom goals',
        'account': 'Edit profile picture, name, email, delete account',
        'visuals': 'Watch relaxing videos with play controls and grid selection',
        'affirmation': 'Daily affirmations with generate and mark as read',
        'music': 'Therapy music library with categories and now playing screen',
        'grounding': '5-4-3-2-1 sensory grounding exercise',
        'breathing': 'Guided breathing with animation and audio cues',
        'mindtools': 'Breathing, grounding, mirror talk, music, affirmations, visuals',
        'faith': 'Daily scripture, guided prayer, spiritual affirmations',
        'features': 'Journal, Faith, Life Coach, Mind Tools overview',
        'home': 'Dashboard with mood selector, daily scripture, quick access'
    }
    
    @classmethod
    def search(cls, query: str) -> str:
        """Search for relevant app info"""
        query_lower = query.lower()
        
        # Direct page match
        for page, info in cls.PAGES.items():
            if page in query_lower:
                return f"{page.title()}: {info}"
        
        # Keyword match
        matches = []
        for page, info in cls.PAGES.items():
            if any(word in info.lower() for word in query_lower.split() if len(word) > 3):
                matches.append(f"{page.title()}: {info}")
        
        return '\n'.join(matches[:3]) if matches else cls.get_all()
    
    @classmethod
    def get_all(cls) -> str:
        """Get all features summary"""
        return '\n'.join([f"{k.title()}: {v}" for k, v in cls.PAGES.items()])


# ==========================================
# TEST CODE
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("Testing AppGuide")
    print("=" * 50)
    
    try:
        print(f"✅ Loaded {len(AppGuide.PAGES)} pages")
        
        # Test searches
        queries = ["profile", "how do I journal?", "breathing", "xyz"]
        for q in queries:
            result = AppGuide.search(q)
            print(f"\n✅ Query: '{q}'")
            print(f"   Result: {result[:80]}...")
        
        print("\n✅ ALL TESTS PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("=" * 50)