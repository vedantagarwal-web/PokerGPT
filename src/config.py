import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask settings
FLASK_APP = os.getenv('FLASK_APP', 'src/web/app.py')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/pokergpt.db')

# Model settings
MODEL_PATH = os.getenv('MODEL_PATH', 'data/models')
LANGUAGE_MODEL = os.getenv('LANGUAGE_MODEL', 'bert-base-uncased')

# API settings
API_KEY = os.getenv('API_KEY')

# Cache settings
CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))

# File paths
DATA_DIR = 'data'
SOLUTIONS_PATH = os.path.join(DATA_DIR, 'solutions.json')
KNOWLEDGE_PATH = os.path.join(DATA_DIR, 'knowledge.json')
EQUITY_CACHE_PATH = os.path.join(DATA_DIR, 'equity_cache.json')
USER_PROFILES_DIR = os.path.join(DATA_DIR, 'profiles')
SRS_DIR = os.path.join(DATA_DIR, 'srs')

# Learning settings
DEFAULT_DETAIL_LEVEL = 'intermediate'
XP_PER_CONCEPT = 100
XP_PER_PRACTICE = 50
XP_PER_ACHIEVEMENT = 200

# Spaced repetition settings
INITIAL_INTERVAL = 1
INITIAL_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3
MAX_EASE_FACTOR = 2.5

# Achievement settings
ACHIEVEMENTS = {
    'first_concept': {
        'id': 'first_concept',
        'name': 'First Steps',
        'description': 'Complete your first concept',
        'icon': '🎯'
    },
    'streak_7': {
        'id': 'streak_7',
        'name': 'Consistent Learner',
        'description': 'Maintain a 7-day study streak',
        'icon': '🔥'
    },
    'master_10': {
        'id': 'master_10',
        'name': 'Knowledge Master',
        'description': 'Master 10 concepts',
        'icon': '🏆'
    },
    'perfect_practice': {
        'id': 'perfect_practice',
        'name': 'Perfect Practice',
        'description': 'Score 100% on a practice session',
        'icon': '⭐'
    }
}

# Learning paths
LEARNING_PATHS = {
    'preflop': {
        'id': 'preflop',
        'name': 'Preflop Fundamentals',
        'description': 'Master the basics of preflop play',
        'concepts': [
            'preflop_position',
            'range_construction',
            'betting_strategy',
            'game_theory'
        ]
    },
    'postflop': {
        'id': 'postflop',
        'name': 'Postflop Play',
        'description': 'Advanced postflop strategies',
        'concepts': [
            'pot_odds',
            'implied_odds',
            'betting_strategy',
            'game_theory'
        ]
    },
    'tournament': {
        'id': 'tournament',
        'name': 'Tournament Strategy',
        'description': 'Tournament-specific concepts',
        'concepts': [
            'icm',
            'bubble_play',
            'final_table',
            'tournament_structure'
        ]
    }
}

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(USER_PROFILES_DIR, exist_ok=True)
os.makedirs(SRS_DIR, exist_ok=True)
os.makedirs(MODEL_PATH, exist_ok=True) 