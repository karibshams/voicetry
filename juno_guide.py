class JunoGuide:
    """App feature knowledge base and guide AI system"""
    
    PAGE_GUIDES = {
        'ProfilePage': {
            'overview': 'Your personal profile with mood tracking, streaks, and check-in reminders',
            'features': [
                'Profile header with picture, name, and settings',
                'About Me cards showing age, gender, country, occupation',
                'My Progress card that navigates to Gamification page',
                'Personal motivational quote display',
                'This Week Mood Journey showing daily mood emojis (? for future days)',
                'User streak tracking to celebrate consistency',
                'Morning, afternoon, and evening check-in reminders with toggle on/off',
                'Customize check-in schedule with time preferences'
            ]
        },
        
        'SubscriptionPage': {
            'overview': 'Premium subscription plans to unlock full AI features',
            'features': [
                '3-day FREE trial with voice journaling, AI guidance, prayers, mood tracking, cloud storage',
                'Monthly plan at $9.99/month with full access to all features',
                'Annual plan at $79.99/year (saves 2 months) with lifetime cloud, habit tracking, biometric security',
                'Easy subscription: pick a plan and tap the button to start',
                'All plans include Juno AI guidance and meditation support'
            ]
        },
        
        'ChatbotPage': {
            'overview': 'Chat with Juno - your AI wellness companion for journaling and support',
            'features': [
                'Voice journaling companion powered by AI',
                'Chat interface with your messages (right side) and Juno replies (left with avatar)',
                'Scrollable conversation history to review past chats',
                'Text input field with send button',
                'Automatic keyboard handling for smooth typing',
                'Empty state with introduction and motivational prompts when starting'
            ]
        },
        
        'NotificationPage': {
            'overview': 'Stay updated with wellness reminders and app notifications',
            'features': [
                'List of notifications with title, message, and time',
                'Swipe to delete notifications you no longer need',
                'Back navigation to return to previous screen'
            ]
        },
        
        'GamificationPage': {
            'overview': 'Track your wellness journey with badges and achievements',
            'features': [
                'Display badges you have earned',
                'Consistency percentage showing your dedication',
                'Weekly progress bar chart visualization',
                'Recent achievements with name, description, and icons',
                'Locked status for achievements not yet unlocked',
                'Create custom badges with name, goal, and privacy settings (Private/Public)'
            ]
        },
        
        'AccountPage': {
            'overview': 'Manage your account settings and profile information',
            'features': [
                'View and edit profile picture (circular avatar)',
                'Edit your user name',
                'Edit your email address',
                'Delete account option (use carefully)',
                'Back navigation to return to previous screen'
            ]
        },
        
        'CreateJournalPage': {
            'overview': 'Create new journal entries with feelings, voice, and photos',
            'features': [
                'Select your current feeling with emoji labels',
                'Add journal title and content',
                'Record voice notes with audio recorder',
                'Add photos or images to your entry',
                'Preview recorded audio before saving',
                'Lock journal entry for privacy',
                'Save journal entry to your collection',
                'Back button to return to journal list'
            ]
        },
        
        'JournalPage': {
            'overview': 'View and manage all your journal entries',
            'features': [
                'View journal entries filtered by selected date',
                'Select date from current week to filter journals',
                'Create new journal button for quick entry',
                'Share journals via email or export as PDF',
                'Delete journals with confirmation',
                'Lock/unlock journal entries (locked cannot be edited or shared)',
                'Shows "No journals found" if none exist for selected date',
                'Uses Bloc for managing journal data and CRUD operations'
            ]
        },
        
        'VisualsPage': {
            'overview': 'Relaxing visual content and videos for mindfulness',
            'features': [
                'Video player showing selected visual with title',
                'Play/pause controls for videos',
                'Scrollable grid of visuals (2 per row)',
                'Thumbnails with play overlay icon',
                'Blue border highlights selected visual',
                'Tap visual to auto-select and update player',
                'Easy visual selection with immediate feedback'
            ]
        },
        
        'AffirmationPage': {
            'overview': 'Daily positive affirmations for motivation and mindset',
            'features': [
                'Daily affirmation with decorative emoji',
                'Bold, italicized text for emphasis',
                'Motivational subtext explaining affirmation purpose',
                'Generate button to create new affirmation',
                'Mark as Read button to acknowledge current affirmation',
                'Centered card design for focused interaction'
            ]
        },
        
        'NowPlayingPage': {
            'overview': 'Music player for therapy tracks with full controls',
            'features': [
                'Large centered album art with gradient and shadow',
                'Track title and artist display',
                'Favorite button to mark/unmark track',
                'Add to playlist option',
                'Play/Pause with prominent circular button',
                'Skip to next/previous track',
                'Shuffle and repeat buttons',
                'Interactive progress bar with seek slider',
                'Time indicators showing elapsed and total duration',
                'Clean minimalistic design with soothing colors'
            ]
        },
        
        'MusicTherapyPage': {
            'overview': 'Therapy music library with calming tracks for wellness',
            'features': [
                'Music library with therapy tracks',
                'Category tabs: All, Favorites, Sleep, Alone, Focus',
                'Music cards showing artwork, title, duration',
                'Favorite toggle on each card',
                'Tap card to go to Now Playing screen',
                'Soothing light purple background',
                'Rounded corners for soft visual effect',
                'Grid layout for easy track scanning'
            ]
        },
        
        'GroundingPage': {
            'overview': '5-4-3-2-1 grounding technique to reconnect with present moment',
            'features': [
                'Guided grounding exercise using 5 senses',
                'Step 1: Name 5 things you can see',
                'Step 2: Notice 4 things you can feel',
                'Step 3: Identify 3 things you can hear',
                'Step 4: Find 2 things you can smell',
                'Step 5: Focus on 1 thing you can taste',
                'Completion celebration with "Well done!" message',
                'Horizontal category tabs with visual indicator'
            ]
        },
        
        'BreathingPage': {
            'overview': 'Guided breathing exercises with animation and audio',
            'features': [
                'Central circular animation that expands (inhale) and contracts (exhale)',
                'Circle changes color and opacity for breath phases',
                'Text-to-speech audio guidance for breathing instructions',
                'Timer showing elapsed/total duration in MM:SS format',
                'Play/Pause button to control session',
                'Stop/Exit button to end session',
                'Animated microwave/wave icon for immersive feel',
                'Clear "Breath In.." / "Breath Out.." instructions',
                'Gradient background with calming UI'
            ]
        },
        
        'MindToolsPage': {
            'overview': 'Collection of quick wellness tools for stress relief',
            'features': [
                'Breathing Timer: Sync breath with calming animations',
                '5-4-3-2-1 Grounding: Sensory awareness exercise',
                'Mirror Talk: Self-compassion and positive self-talk',
                'Music Therapy: Curated relaxation music',
                'Affirmations: Daily positive mindset encouragement',
                'Visuals: Immersive exercises to relax and recenter',
                'Interactive navigation to each tool page'
            ]
        },
        
        'FaithPage': {
            'overview': 'Spiritual wellness with scripture, prayer, and affirmations',
            'features': [
                'Faith card prompting spiritual reflection',
                'Daily scripture verse with reference',
                'Audio icon for text-to-speech scripture playback',
                'Guided voice prayer sessions with Start Session button',
                'Session progress visual indicators',
                'Daily affirmations for positive mindset',
                'Generate new affirmations or Mark as Read buttons',
                'Back navigation to previous screen'
            ]
        },
        
        'FeaturesPage': {
            'overview': 'Overview of all main app features and tools',
            'features': [
                'Journal: Record thoughts, get AI insights, chat with coach',
                'Faith: Track faith and wellness goals with motivation',
                'Life Coach: Access crisis resources and guidance',
                'Mind Tools: Quick interactive tools for stress reduction',
                'Back navigation to previous screen'
            ]
        },
        
        'HomePage': {
            'overview': 'Main dashboard with quick access to all wellness features',
            'features': [
                'User avatar and greeting text',
                'Notification icon for alerts',
                '"Silence Juno" toggle to mute/activate voice assistant',
                'Feeling selector: Happy, Calm, Okay, Stressed, Angry',
                'Daily scripture for reflection',
                'Quick access shortcuts: Journal, Spiritual, Coach',
                'Recommended section with music/meditation based on preferences',
                'Daily wellness and mindfulness tips'
            ]
        }
    }
    
    def get_page_info(self, query: str, lang: str = 'en') -> str:
        """Find and return page information based on query"""
        query_lower = query.lower()
        
        # Search for exact page match
        for page_name, page_data in self.PAGE_GUIDES.items():
            page_key = page_name.lower().replace('page', '')
            if page_key in query_lower:
                features_text = '\n'.join([f"• {f}" for f in page_data['features']])
                return f"{page_data['overview']}\n\n{features_text}"
        
        # Search in features
        matching_features = []
        for page_name, page_data in self.PAGE_GUIDES.items():
            for feature in page_data['features']:
                if any(word in feature.lower() for word in query_lower.split() if len(word) > 3):
                    matching_features.append(f"{page_name.replace('Page', '')}: {feature}")
        
        if matching_features:
            return '\n'.join([f"• {f}" for f in matching_features[:5]])
        
        return None
    
    def get_all_features_summary(self) -> str:
        """Return summary of all app features"""
        summary = []
        for page_name, page_data in self.PAGE_GUIDES.items():
            summary.append(f"{page_name.replace('Page', '')}: {page_data['overview']}")
        return '\n'.join(summary)


# ==========================================
# TEST CODE FOR juno_guide.py
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("TESTING: JunoGuide Module")
    print("=" * 50)
    
    try:
        guide = JunoGuide()
        print(f"✅ JunoGuide initialized with {len(guide.PAGE_GUIDES)} pages")
        
        # Test page search
        test_queries = [
            "How do I use the profile page?",
            "Tell me about subscription",
            "What is journaling?",
            "breathing exercise"
        ]
        
        for query in test_queries:
            result = guide.get_page_info(query)
            if result:
                print(f"\n✅ Query: '{query}'")
                print(f"   Found: {result[:80]}...")
            else:
                print(f"\n⚠️  Query: '{query}' - No specific match")
        
        # Test all features summary
        summary = guide.get_all_features_summary()
        print(f"\n✅ Features summary: {len(summary)} characters")
        
        print("\n✅ ALL TESTS PASSED for juno_guide.py")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("=" * 50)