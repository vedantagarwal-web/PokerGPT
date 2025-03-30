from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from typing import Dict, Optional
from datetime import datetime
import json
import random

# Import local modules - using absolute imports
try:
    from core.equity_calculator import EquityCalculator
    from core.gto_solver import GtoSolver, GameState, Position, Action
    from knowledge.poker_knowledge import PokerKnowledge
    from personalization.user_profile import UserProfile
    from personalization.spaced_repetition import SpacedRepetition
    from core.hand_evaluator import Card, Suit, Rank, HandEvaluator, HandRank
except ImportError:
    # Mock objects for when modules can't be imported
    EquityCalculator = None
    GtoSolver, GameState, Position, Action = None, None, None, None
    PokerKnowledge = None
    UserProfile = None
    SpacedRepetition = None
    Card, Suit, Rank, HandEvaluator, HandRank = None, None, None, None, None

from .routes import bp as routes_bp

app = Flask(__name__, 
            static_folder='static',
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['SECRET_KEY'] = 'your-secret-key' # This should be more secure in production
app.config['DEBUG'] = True  # Enable debug mode to auto-reload templates

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize paths
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Create mock classes if imports failed
# Create a mock EquityCalculator if the real one couldn't be imported
if EquityCalculator is None:
    class EquityCalculator:
        def __init__(self, cache_path):
            self.cache_path = cache_path
            print(f"Using mock EquityCalculator with cache path: {cache_path}")
        
        def calculate_equity(self, *args, **kwargs):
            return {"player1": 0.5, "player2": 0.5}  # Mock equity calculation

# Similarly create other mock classes as needed
if GtoSolver is None:
    class GtoSolver:
        def __init__(self, *args, **kwargs):
            pass
        
    class GameState:
        def __init__(self, *args, **kwargs):
            pass
    
    class Position:
        UTG = "UTG"
        MP = "MP"
        CO = "CO"
        BTN = "BTN"
        SB = "SB"
        BB = "BB"
    
    class Action:
        FOLD = "FOLD"
        CHECK = "CHECK"
        CALL = "CALL"
        BET = "BET"
        RAISE = "RAISE"

if UserProfile is None:
    class UserProfile:
        profiles = {}
        
        def __init__(self, user_id):
            self.user_id = user_id
            self.name = "Mock User"
            self.skill_level = "beginner"
            self.learning_paths = []  # Already initialized as empty list
            self.hands_played = 0
            self._is_authenticated = True
            self.is_active = True  # Required by Flask-Login
            self.is_anonymous = False  # Required by Flask-Login
            self.last_study_date = None
            self.study_streak = 0
            self.total_study_time = 0
            
        def get_id(self):  # Required by Flask-Login
            return str(self.user_id)
            
        @property
        def is_authenticated(self):
            return self._is_authenticated
            
        @is_authenticated.setter
        def is_authenticated(self, value):
            self._is_authenticated = value
            
        @classmethod
        def set_profiles_file(cls, file_path):
            print(f"Setting mock profiles file path: {file_path}")
            cls.profiles_file = file_path
            
        @classmethod
        def get_profile(cls, user_id):
            if user_id not in cls.profiles:
                cls.profiles[user_id] = UserProfile(user_id)
            return cls.profiles[user_id]
            
        def check_password(self, password):
            return True
            
        def update_profile(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            return True
            
        def get_learning_stats(self):
            return {
                "completed": 0,
                "in_progress": 0,
                "total_concepts": 0
            }
            
        @classmethod
        def create_profile(cls, username, email, password):
            if username in cls.profiles:
                return False
            cls.profiles[username] = UserProfile(username)
            return True

if PokerKnowledge is None:
    class PokerKnowledge:
        def __init__(self, knowledge_base_path=None):
            self.knowledge_base = {}
        
        def get_concept(self, concept_id):
            return {"id": concept_id, "title": "Mock Concept", "content": "Mock content"}

if SpacedRepetition is None:
    class SpacedRepetition:
        def __init__(self, reviews_file_path):
            self.reviews_file_path = reviews_file_path
            self.reviews = {}
            print(f"Using mock SpacedRepetition with file path: {reviews_file_path}")
            
        def add_review(self, user_id, review_data):
            if user_id not in self.reviews:
                self.reviews[user_id] = []
            self.reviews[user_id].append(review_data)
            return review_data
            
        def get_review_stats(self, user_id):
            if user_id is None:
                return {
                    "total_reviews": 0,
                    "average_rating": 0,
                    "next_review": None,
                    "mastery_level": 0,
                    "due_count": 0,
                    "completion_rate": 0
                }
            
            return {
                "total_reviews": len(self.reviews.get(user_id, [])),
                "average_rating": 3.0,
                "next_review": datetime.now().strftime('%Y-%m-%d'),
                "mastery_level": 25.0,
                "due_count": 1,
                "completion_rate": 0.75
            }
        
        def get_due_reviews(self, user_id):
            return self.reviews.get(user_id, [])

# Initialize components with proper mocks
# Initialize UserProfile
if hasattr(UserProfile, 'set_profiles_file'):
    UserProfile.set_profiles_file(os.path.join(data_dir, 'profiles.json'))

# Initialize EquityCalculator
equity_calculator = EquityCalculator(os.path.join(data_dir, 'equity_cache'))

# Initialize other components
gto_solver = GtoSolver(os.path.join(data_dir, 'gto_solutions.json'))
poker_knowledge = PokerKnowledge(os.path.join(data_dir, 'knowledge.json'))
spaced_repetition = SpacedRepetition(os.path.join(data_dir, 'reviews.json'))

# Learning paths data
LEARNING_PATHS = {
    'preflop': {
        'id': 'preflop',
        'name': 'Preflop Fundamentals',
        'description': 'Master the basics of preflop play, positions, and starting hand selection.',
        'concepts': [
            {
                'id': 'positions',
                'title': 'Understanding Positions',
                'content': '''
                    <h4>Position in Poker</h4>
                    <p>Position is one of the most important concepts in poker. It refers to where you sit relative to the dealer button.</p>
                    <h5>Key Positions:</h5>
                    <ul>
                        <li><strong>Early Position (UTG)</strong>: First to act, most disadvantageous</li>
                        <li><strong>Middle Position</strong>: Better than early, but still challenging</li>
                        <li><strong>Late Position (CO, BTN)</strong>: Most advantageous, you see others act first</li>
                        <li><strong>Blinds (SB, BB)</strong>: Forced bets, play carefully</li>
                    </ul>
                    <h5>Positional Advantages:</h5>
                    <ul>
                        <li>Information advantage: Acting last gives you more information</li>
                        <li>Control: Better control over pot size and betting rounds</li>
                        <li>Bluffing: More effective bluffing opportunities</li>
                        <li>Value betting: Better opportunities for thin value</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'Which position is generally considered the most advantageous?',
                        'options': ['UTG', 'Middle Position', 'Button', 'Small Blind'],
                        'correct': 'Button'
                    },
                    {
                        'question': 'Why is position important in poker?',
                        'options': [
                            'It determines the order of betting',
                            'You get to act after seeing what others do',
                            'It affects your starting hand selection',
                            'All of the above'
                        ],
                        'correct': 'All of the above'
                    }
                ]
            },
            {
                'id': 'starting_hands',
                'title': 'Starting Hand Selection',
                'content': '''
                    <h4>Starting Hand Selection</h4>
                    <p>Choosing the right hands to play is crucial for long-term success in poker.</p>
                    <h5>Hand Categories:</h5>
                    <ul>
                        <li><strong>Premium Hands</strong>: AA, KK, QQ, AK</li>
                        <li><strong>Strong Hands</strong>: JJ, TT, AQ, AJ</li>
                        <li><strong>Medium Hands</strong>: 99, 88, AT, KQ</li>
                        <li><strong>Speculative Hands</strong>: Suited connectors, small pairs</li>
                    </ul>
                    <h5>Position-Based Hand Selection:</h5>
                    <ul>
                        <li>Early Position: Play tighter, focus on premium hands</li>
                        <li>Middle Position: Add strong hands to your range</li>
                        <li>Late Position: Play wider, include speculative hands</li>
                        <li>Blinds: Defend wider, especially against late position raises</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'Which of these is considered a premium starting hand?',
                        'options': ['KQ', 'JJ', 'AT', '99'],
                        'correct': 'JJ'
                    },
                    {
                        'question': 'In early position, you should:',
                        'options': [
                            'Play very loose',
                            'Play very tight',
                            'Play medium strength hands',
                            'Play any two cards'
                        ],
                        'correct': 'Play very tight'
                    }
                ]
            }
        ]
    },
    'postflop': {
        'id': 'postflop',
        'name': 'Postflop Strategy',
        'description': 'Learn advanced concepts of postflop play, including bet sizing and hand reading.',
        'concepts': [
            {
                'id': 'betting',
                'title': 'Postflop Bet Sizing',
                'content': '''
                    <h4>Bet Sizing in Poker</h4>
                    <p>Proper bet sizing is crucial for maximizing value and minimizing losses.</p>
                    <h5>Common Bet Sizes:</h5>
                    <ul>
                        <li><strong>Small (25-33% pot)</strong>: For value betting thin or blocking</li>
                        <li><strong>Medium (50-75% pot)</strong>: Standard value bet or semi-bluff</li>
                        <li><strong>Large (100%+ pot)</strong>: Strong hands or polarized ranges</li>
                    </ul>
                    <h5>Bet Sizing Factors:</h5>
                    <ul>
                        <li>Board texture</li>
                        <li>Opponent tendencies</li>
                        <li>Stack depth</li>
                        <li>Position</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'When might you use a small bet size (25-33% pot)?',
                        'options': [
                            'With very strong hands',
                            'When bluffing',
                            'For thin value bets',
                            'When all-in'
                        ],
                        'correct': 'For thin value bets'
                    },
                    {
                        'question': 'What factors influence bet sizing?',
                        'options': [
                            'Only your hand strength',
                            'Only the pot size',
                            'Board texture, opponent tendencies, stack depth, and position',
                            'Only your position'
                        ],
                        'correct': 'Board texture, opponent tendencies, stack depth, and position'
                    }
                ]
            },
            {
                'id': 'hand_reading',
                'title': 'Hand Reading',
                'content': '''
                    <h4>Hand Reading</h4>
                    <p>Understanding how to read your opponent\'s hand is crucial for making good decisions.</p>
                    <h5>Hand Reading Process:</h5>
                    <ul>
                        <li>Consider preflop action</li>
                        <li>Analyze betting patterns</li>
                        <li>Look for tells</li>
                        <li>Consider opponent\'s range</li>
                    </ul>
                    <h5>Range Analysis:</h5>
                    <ul>
                        <li>Value hands</li>
                        <li>Drawing hands</li>
                        <li>Bluffing hands</li>
                        <li>Mixed strategies</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'What is the first step in hand reading?',
                        'options': [
                            'Looking for tells',
                            'Considering preflop action',
                            'Analyzing betting patterns',
                            'Guessing the hand'
                        ],
                        'correct': 'Considering preflop action'
                    },
                    {
                        'question': 'What should you consider when analyzing an opponent\'s range?',
                        'options': [
                            'Only their current bet',
                            'Their position, betting patterns, and previous actions',
                            'Only their position',
                            'Only their previous actions'
                        ],
                        'correct': 'Their position, betting patterns, and previous actions'
                    }
                ]
            }
        ]
    },
    'gto': {
        'id': 'gto',
        'name': 'GTO Concepts',
        'description': 'Explore Game Theory Optimal play and balanced strategies.',
        'concepts': [
            {
                'id': 'ranges',
                'title': 'Range-Based Thinking',
                'content': '''
                    <h4>Understanding Ranges</h4>
                    <p>Instead of putting opponents on specific hands, think in terms of ranges of hands.</p>
                    <h5>Key Range Concepts:</h5>
                    <ul>
                        <li><strong>Polarized Range</strong>: Very strong hands and bluffs</li>
                        <li><strong>Linear Range</strong>: Connected hands of varying strength</li>
                        <li><strong>Merged Range</strong>: Medium to strong hands</li>
                    </ul>
                    <h5>Range Construction:</h5>
                    <ul>
                        <li>Value hands</li>
                        <li>Bluffing hands</li>
                        <li>Mixed strategies</li>
                        <li>Frequency-based decisions</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'What is a polarized range?',
                        'options': [
                            'Only medium strength hands',
                            'Strong hands and bluffs',
                            'Only premium hands',
                            'Connected hands'
                        ],
                        'correct': 'Strong hands and bluffs'
                    },
                    {
                        'question': 'Why is range-based thinking important?',
                        'options': [
                            'It\'s easier than hand reading',
                            'It helps make more accurate decisions',
                            'It\'s required by poker rules',
                            'It makes the game faster'
                        ],
                        'correct': 'It helps make more accurate decisions'
                    }
                ]
            }
        ]
    },
    'poker_math': {
        'id': 'poker_math',
        'name': 'Intermediate: Poker Mathematics',
        'description': 'Master the mathematical concepts that form the foundation of winning poker strategies.',
        'concepts': [
            {
                'id': 'pot_odds',
                'title': 'Pot Odds & Equity',
                'content': '''
                    <h4>Understanding Pot Odds</h4>
                    <p>Pot odds are the ratio of the current pot size to the cost of a contemplated call. This concept is fundamental to making mathematically correct decisions.</p>
                    
                    <h5>Calculating Pot Odds:</h5>
                    <p>Pot odds = Cost to call / (Current pot + Cost to call)</p>
                    <p>Example: If the pot is $100 and your opponent bets $50, the pot odds are:</p>
                    <p>$50 / ($100 + $50) = $50 / $150 = 1/3 or 33%</p>
                    
                    <h5>Converting to Percentages:</h5>
                    <ul>
                        <li>4-to-1 odds = 20% equity needed</li>
                        <li>3-to-1 odds = 25% equity needed</li>
                        <li>2-to-1 odds = 33% equity needed</li>
                        <li>1-to-1 odds = 50% equity needed</li>
                    </ul>
                    
                    <h5>Pot Odds vs. Equity:</h5>
                    <p>The fundamental principle: Call if your equity exceeds the pot odds percentage.</p>
                    <p>Example: If your pot odds are 33%, you need at least 33% equity to call profitably.</p>
                ''',
                'questions': [
                    {
                        'question': 'If the pot is $80 and your opponent bets $40, what are your pot odds?',
                        'options': [
                            '33%',
                            '50%',
                            '25%',
                            '40%'
                        ],
                        'correct': '33%'
                    },
                    {
                        'question': 'With 8 outs after the flop, what is your approximate equity?',
                        'options': [
                            '16%',
                            '24%',
                            '32%',
                            '8%'
                        ],
                        'correct': '32%'
                    }
                ]
            },
            {
                'id': 'expected_value',
                'title': 'Expected Value & Decision Making',
                'content': '''
                    <h4>Expected Value (EV) in Poker</h4>
                    <p>Expected Value is the average result of a decision if it were made repeatedly over a large sample size. It's the cornerstone of profitable poker decision-making.</p>
                    
                    <h5>Mathematical Foundation:</h5>
                    <p>EV = (Probability of Outcome 1 × Result 1) + (Probability of Outcome 2 × Result 2) + ...</p>
                    
                    <h5>Simple EV Example:</h5>
                    <p>Flipping a coin with $10 payoff for heads and $5 loss for tails:</p>
                    <p>EV = (0.5 × $10) + (0.5 × -$5) = $5 - $2.50 = $2.50</p>
                    <p>Each flip is worth $2.50 on average.</p>
                ''',
                'questions': [
                    {
                        'question': 'If you have a 40% chance to win $100 and a 60% chance to lose $50, what is your EV?',
                        'options': [
                            '+$10',
                            '+$20',
                            '-$10',
                            '+$40'
                        ],
                        'correct': '+$10'
                    },
                    {
                        'question': 'Which of these is a correct principle regarding EV?',
                        'options': [
                            'Always make the decision with lowest variance',
                            'The highest EV play is always the most aggressive',
                            'You should always choose the option with highest EV',
                            'EV calculations are only relevant in tournament play'
                        ],
                        'correct': 'You should always choose the option with highest EV'
                    }
                ]
            }
        ]
    },
    'exploitative_play': {
        'id': 'exploitative_play',
        'name': 'Advanced: Exploitative Strategies',
        'description': 'Learn how to deviate from GTO principles to exploit specific opponents and maximize profitability.',
        'concepts': [
            {
                'id': 'player_profiling',
                'title': 'Player Profiling & Typing',
                'content': '''
                    <h4>Player Profiling: The Key to Exploitation</h4>
                    <p>Player profiling involves categorizing opponents based on their tendencies, allowing you to make precise adjustments to counter their strategies.</p>
                    
                    <h5>Traditional Player Types:</h5>
                    <ul>
                        <li><strong>TAG (Tight-Aggressive):</strong> Plays few hands but plays them aggressively</li>
                        <li><strong>LAG (Loose-Aggressive):</strong> Plays many hands aggressively, often applying pressure</li>
                        <li><strong>Nit/Rock:</strong> Extremely tight player who only plays premium hands</li>
                        <li><strong>Calling Station:</strong> Calls too frequently, rarely folds once committed</li>
                        <li><strong>Maniac:</strong> Hyper-aggressive player who bets and raises constantly</li>
                        <li><strong>Passive Fish:</strong> Loose-passive player who calls too much and rarely raises</li>
                    </ul>
                    
                    <h5>Modern Frequency-Based Profiling:</h5>
                    <ul>
                        <li><strong>VPIP (Voluntarily Put $ In Pot):</strong> Percentage of hands played</li>
                        <li><strong>PFR (Preflop Raise):</strong> Percentage of hands raised preflop</li>
                        <li><strong>3-Bet %:</strong> Frequency of re-raising preflop</li>
                        <li><strong>Fold to 3-Bet %:</strong> How often they surrender to a re-raise</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'What adjustment should you make against a calling station?',
                        'options': [
                            'Bluff more frequently',
                            'Value bet thinner',
                            'Fold more often to their bets',
                            'Play fewer hands against them'
                        ],
                        'correct': 'Value bet thinner'
                    },
                    {
                        'question': 'A player with VPIP: 15% and PFR: 12% would be classified as:',
                        'options': [
                            'Loose-Aggressive (LAG)',
                            'Tight-Aggressive (TAG)',
                            'Loose-Passive Fish',
                            'Maniac'
                        ],
                        'correct': 'Tight-Aggressive (TAG)'
                    }
                ]
            },
            {
                'id': 'advanced_exploitation',
                'title': 'Exploitation Techniques & Frequencies',
                'content': '''
                    <h4>Advanced Exploitation Techniques</h4>
                    <p>Exploitation involves deliberately deviating from GTO frequencies to target specific weaknesses in opponents' strategies.</p>
                    
                    <h5>Fundamental Exploitative Adjustments:</h5>
                    <ul>
                        <li><strong>Overfolding Exploitation:</strong> Bluff more frequently against players who fold too much</li>
                        <li><strong>Overcalling Exploitation:</strong> Value bet thinner and reduce bluffs against calling stations</li>
                        <li><strong>Passive Exploitation:</strong> Bet more frequently and aggressively when opponents check too often</li>
                        <li><strong>Aggressive Exploitation:</strong> Trap and induce bluffs against overly aggressive players</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'Against an opponent who folds too much on the river, you should:',
                        'options': [
                            'Value bet thinner',
                            'Increase your bluffing frequency',
                            'Check more often with your medium-strength hands',
                            'Always check-call the river'
                        ],
                        'correct': 'Increase your bluffing frequency'
                    },
                    {
                        'question': 'What does "merging" your betting range mean?',
                        'options': [
                            'Betting only the nuts and air',
                            'Betting with a range containing mostly medium-strength hands',
                            'Checking all hands',
                            'Using the same bet size with all hands'
                        ],
                        'correct': 'Betting with a range containing mostly medium-strength hands'
                    }
                ]
            }
        ]
    },
    'tournament_strategy': {
        'id': 'tournament_strategy',
        'name': 'Advanced: Tournament Strategy',
        'description': 'Master the unique dynamics of tournament poker, from ICM considerations to final table strategy.',
        'concepts': [
            {
                'id': 'icm_basics',
                'title': 'ICM Theory & Applications',
                'content': '''
                    <h4>Independent Chip Model (ICM)</h4>
                    <p>ICM is a mathematical model that converts tournament chip counts into their actual cash equity value, accounting for the payout structure.</p>
                    
                    <h5>Fundamental ICM Principles:</h5>
                    <ul>
                        <li>Chips have non-linear value in tournaments (diminishing marginal value)</li>
                        <li>Survival value increases as you approach pay jumps</li>
                        <li>Risk/reward calculations differ significantly from cash games</li>
                        <li>ICM pressure affects optimal strategy, particularly calling ranges</li>
                    </ul>
                    
                    <h5>ICM Mathematics:</h5>
                    <p>The ICM model calculates the probability of each finishing position based on current chip distributions:</p>
                    <ul>
                        <li>Probability of finishing in each position is proportional to chip stack</li>
                        <li>Each position has an associated prize value</li>
                        <li>$EV = Sum of (probability of each position × prize value)</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'In ICM terms, which stack has the most pressure to fold in a bubble situation?',
                        'options': [
                            'Chip leader',
                            'Medium stack',
                            'Shortest stack',
                            'Average stack'
                        ],
                        'correct': 'Medium stack'
                    },
                    {
                        'question': 'As the big stack on the bubble, you should:',
                        'options': [
                            'Tighten up to secure your position',
                            'Apply pressure to medium stacks who cannot call correctly',
                            'Only play premium hands',
                            'Focus on eliminating the chip leader'
                        ],
                        'correct': 'Apply pressure to medium stacks who cannot call correctly'
                    }
                ]
            },
            {
                'id': 'stack_dynamics',
                'title': 'Tournament Stack Dynamics',
                'content': '''
                    <h4>Tournament Stack Dynamics & Adaptations</h4>
                    <p>Understanding how to adapt your strategy based on stack sizes is critical for tournament success.</p>
                    
                    <h5>Stack Size Categories:</h5>
                    <ul>
                        <li><strong>Big Stack (>100 BB):</strong> Maximum flexibility and pressure potential</li>
                        <li><strong>Deep Stack (40-100 BB):</strong> Standard full strategy possible</li>
                        <li><strong>Middle Stack (25-40 BB):</strong> Transitional strategy required</li>
                        <li><strong>Shallow Stack (15-25 BB):</strong> Simplified strategy, commitment decisions</li>
                        <li><strong>Short Stack (10-15 BB):</strong> Push/fold considerations begin</li>
                        <li><strong>Critical Stack (<10 BB):</strong> Primarily push/fold strategy</li>
                        <li><strong>Micro Stack (<5 BB):</strong> Desperate push/fold with any reasonable hand</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'At what approximate stack depth should you begin considering a push/fold strategy?',
                        'options': [
                            '40 BBs',
                            '25 BBs',
                            '15 BBs',
                            '5 BBs'
                        ],
                        'correct': '15 BBs'
                    },
                    {
                        'question': 'With a 12 BB stack, which position is most advantageous for attempting to steal the blinds?',
                        'options': [
                            'UTG (Under the Gun)',
                            'Middle Position',
                            'Button',
                            'Small Blind'
                        ],
                        'correct': 'Button'
                    }
                ]
            }
        ]
    }
}

# Register the blueprint
app.register_blueprint(routes_bp)

@login_manager.user_loader
def load_user(user_id):
    """Load user from session."""
    if not user_id:
        print(f"User ID is None or empty, cannot load user")
        return None
    
    user = UserProfile.get_profile(user_id)
    if not user:
        print(f"Failed to load user with ID: {user_id}")
    else:
        print(f"Successfully loaded user: {user_id}")
    return user

def get_current_user():
    """Get the current user's profile."""
    if current_user.is_authenticated:
        # Check for username attribute first (real implementation)
        if hasattr(current_user, 'username'):
            return UserProfile.get_profile(current_user.username)
        # Fall back to user_id for mock implementation
        elif hasattr(current_user, 'user_id'):
            return UserProfile.get_profile(current_user.user_id)
    return None

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'GET':
        next_url = request.args.get('next', '/')
        return render_template('login.html', next_url=next_url)
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    next_url = data.get('next', '/')
    
    if not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get user profile
    user = UserProfile.get_profile(username)
    if user and user.check_password(password):
        login_user(user)
        # Explicitly set user_id in session to ensure it's synchronized
        session['user_id'] = user.get_id()
        # Validate the next URL to prevent open redirects
        if not next_url or not next_url.startswith('/'):
            next_url = '/'
        return jsonify({'success': True, 'next': next_url})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create user profile
    if UserProfile.create_profile(username, email, password):
        return jsonify({'success': True})
    return jsonify({'error': 'Username already exists'}), 400

@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Handle hand analysis requests."""
    if request.method == 'GET':
        return render_template('analyze.html')
    
    data = request.get_json()
    hand = data.get('hand', '')
    board = data.get('board', '')
    position = data.get('position', '')
    opponents = int(data.get('opponents', 1))
    stack_size = int(data.get('stack_size', 100))
    
    # Create game state
    game_state = GameState(
        hand=hand,
        position=position,
        opponents=opponents,
        action_history=[],
        effective_stack=stack_size,
        board=board,
        tournament=False
    )
    
    # Get optimal action
    action, frequency, ev = gto_solver.get_action(game_state)
    
    # Calculate equity
    equity_result = equity_calculator.calculate_equity(
        hand=hand,
        opponent_range=gto_solver.get_range(position, stack_size),
        board=board
    )
    
    # Generate explanation (without NLP)
    explanation = f"Based on GTO analysis, you should {action} in this spot."
    
    return jsonify({
        'action': action,
        'frequency': frequency,
        'ev': ev,
        'equity': equity_result.equity,
        'outs': equity_result.outs,
        'hand_type': equity_result.hand_type,
        'explanation': explanation
    })

@app.route('/learn')
def learn():
    """Render the learning page."""
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.url))
    
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Get user's learning progress
    learning_paths = list(LEARNING_PATHS.values())
    print(f"DEBUG - LEARNING_PATHS: {LEARNING_PATHS}")
    print(f"DEBUG - learning_paths list: {learning_paths}")
    
    # Initialize user's learning paths if they don't exist
    if not hasattr(user, 'learning_paths') or user.learning_paths is None:
        user.learning_paths = []
    
    # Create a default progress entry for each path
    user_progress = {
        path['id']: {'completed': False, 'score': 0}
        for path in learning_paths
    }
    
    # Update with actual progress if it exists
    for progress in user.learning_paths:
        path_id = progress.get('path_id')
        if path_id and path_id in user_progress:
            user_progress[path_id] = progress
    
    print(f"DEBUG - user_progress: {user_progress}")
    
    return render_template('learn.html', learning_paths=learning_paths, user_progress=user_progress)

@app.route('/learn/path/<path_id>')
def learn_path(path_id):
    """Render a specific learning path."""
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.url))
    
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Check if the path exists
    if path_id not in LEARNING_PATHS:
        flash('Learning path not found.', 'error')
        return redirect(url_for('learn'))
    
    path = LEARNING_PATHS[path_id]
    
    # Get user's progress for this path
    user_progress = next(
        (p for p in user.learning_paths if p.get('path_id') == path_id),
        {'completed': False, 'score': 0, 'concepts': {}}
    )
    
    # Get concept progress
    concept_progress = {}
    for concept in path['concepts']:
        concept_progress[concept['id']] = next(
            (p for p in user.learning_paths if p.get('concept_id') == concept['id']),
            {'completed': False, 'score': 0}
        )
    
    return render_template(
        'learn_path.html', 
        path=path, 
        user_progress=user_progress,
        concept_progress=concept_progress
    )

@app.route('/learn/concept/<concept_id>')
def learn_concept(concept_id):
    """Render a specific concept page."""
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.url))
    
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Find the concept in all learning paths
    found_concept = None
    source_path = None
    
    for path_id, path in LEARNING_PATHS.items():
        for concept in path['concepts']:
            if concept['id'] == concept_id:
                found_concept = concept
                source_path = path
                break
        if found_concept:
            break
    
    if not found_concept:
        flash('Concept not found.', 'error')
        return redirect(url_for('learn'))
    
    # Get user's progress for this concept
    concept_progress = next(
        (p for p in user.learning_paths if p.get('concept_id') == concept_id),
        {'completed': False, 'score': 0}
    )
    
    return render_template(
        'learn_path.html',  # Reuse the learn_path template with a single concept
        path={
            'id': source_path['id'],
            'name': found_concept['title'],
            'description': source_path['description'],
            'concepts': [found_concept]
        },
        user_progress={'completed': concept_progress.get('completed', False), 'score': concept_progress.get('score', 0)},
        concept_progress={found_concept['id']: concept_progress},
        single_concept=True,
        source_path=source_path
    )

@app.route('/profile')
def profile():
    """Render the user profile page."""
    # Check if user is logged in properly
    if not current_user.is_authenticated or not hasattr(current_user, 'get_id'):
        print("User not authenticated or missing get_id method")
        return redirect(url_for('login', next=request.url))
    
    # Get the user ID from the current_user object
    user_id = current_user.get_id()
    
    # Double-check the session also has this user_id
    if 'user_id' not in session or session['user_id'] != user_id:
        print(f"Session user_id mismatch: {session.get('user_id')} != {user_id}")
        # Fix the session
        session['user_id'] = user_id
    
    user = get_current_user()
    if not user:
        print(f"Failed to get current user despite being authenticated")
        logout_user()
        session.clear()
        return redirect(url_for('login', next=request.url))
    
    # Get learning statistics
    stats = user.get_learning_stats()
    
    # Get review statistics
    user_id = user.username if hasattr(user, 'username') else user.user_id
    review_stats = spaced_repetition.get_review_stats(user_id)
    
    # Prepare template variables
    context = {
        'username': user_id,
        'join_date': datetime.now().strftime('%B %d, %Y'),
        'skill_level': getattr(user, 'skill_level', 'Beginner'),
        'status': 'Active',
        'study_streak': getattr(user, 'study_streak', 0),
        'study_hours': getattr(user, 'total_study_time', 0),
        'lessons_completed': stats.get('completed', 0),
        'quizzes_passed': stats.get('completed', 0) // 2,
        'achievements': stats.get('completed', 0) // 3,
        'cards_reviewed': review_stats.get('total_reviews', 0),
        'accuracy_rate': int(review_stats.get('completion_rate', 0) * 100),
        'retention_rate': 85,
        'activities': [
            {'description': 'Completed lesson on position', 'time': '2 days ago'},
            {'description': 'Reviewed pot odds concept', 'time': '3 days ago'},
            {'description': 'Analyzed hand history', 'time': '5 days ago'}
        ]
    }
    
    return render_template('profile.html', **context)

@app.route('/api/logout')
def api_logout():
    """Handle user logout API request."""
    logout_user()
    session.clear()
    response = jsonify({'success': True})
    response.delete_cookie('session')
    response.set_cookie('session', '', expires=0)
    print("API logout: User logged out successfully, session cleared")
    return response

@app.route('/logout')
def logout():
    """Handle user logout."""
    # Log out the user
    logout_user()
    # Clear all session data
    session.clear()
    # Create redirect response
    response = redirect(url_for('home'))
    # Force expire all cookies related to authentication
    response.delete_cookie('session')
    # Also set an expired session cookie
    response.set_cookie('session', '', expires=0)
    # Log the logout
    print("User logged out successfully, session cleared")
    return response

@app.route('/api/learn/progress', methods=['POST'])
@login_required
def update_learning_progress():
    """Update user's learning progress."""
    data = request.get_json()
    concept_id = data.get('concept_id')
    answers = data.get('answers', [])
    
    if not concept_id:
        return jsonify({'error': 'Missing concept ID'}), 400
    
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find the concept and check answers
    path_id = None
    concept = None
    for p_id, path in LEARNING_PATHS.items():
        for c in path['concepts']:
            if c['id'] == concept_id:
                path_id = p_id
                concept = c
                break
        if path_id:
            break
    
    if not path_id or not concept:
        return jsonify({'error': 'Invalid concept ID'}), 400
    
    # Check answers
    correct_answers = 0
    for i, q in enumerate(concept['questions']):
        if i < len(answers) and answers[i] == q['correct']:
            correct_answers += 1
    score = (correct_answers / len(concept['questions'])) * 100
    completed = score >= 70  # Pass if score >= 70%
    
    # Create progress data
    progress_data = {
        'concept_id': concept_id,
        'path_id': path_id,
        'completed': completed,
        'score': score,
        'answers': answers,
        'timestamp': datetime.now().isoformat()
    }
    
    # Update user's learning paths
    if not hasattr(user, 'learning_paths'):
        user.learning_paths = []
    
    # Find and update existing progress or add new progress
    found = False
    for i, p in enumerate(user.learning_paths):
        if p.get('concept_id') == concept_id:
            user.learning_paths[i] = progress_data
            found = True
            break
    
    if not found:
        user.learning_paths.append(progress_data)
    
    # Update study streak
    now = datetime.now()
    if user.last_study_date:
        days_diff = (now - user.last_study_date).days
        if days_diff == 1:
            user.study_streak += 1
        elif days_diff > 1:
            user.study_streak = 1
    else:
        user.study_streak = 1
    
    user.last_study_date = now
    user.total_study_time += 10  # Assume 10 minutes per concept
    
    # Save user profile
    if not user.update_profile({
        'learning_paths': user.learning_paths,
        'last_study_date': user.last_study_date,
        'study_streak': user.study_streak,
        'total_study_time': user.total_study_time
    }):
        return jsonify({'error': 'Failed to update profile'}), 500
    
    return jsonify({
        'success': True,
        'score': score,
        'completed': completed
    })

@app.route('/api/review', methods=['POST'])
@login_required
def record_review():
    """Record a spaced repetition review."""
    data = request.get_json()
    concept_id = data.get('concept_id')
    difficulty = data.get('difficulty')
    next_review = data.get('next_review')
    
    if not concept_id or not difficulty or not next_review:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Add review
    review_data = {
        'concept_id': concept_id,
        'difficulty': difficulty,
        'next_review': next_review,
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    review = spaced_repetition.add_review(current_user.username, review_data)
    
    if not review:
        return jsonify({'error': 'Failed to record review'}), 500
    
    return jsonify({'success': True})

@app.route('/api/activity', methods=['POST'])
@login_required
def record_activity():
    """Record user activity."""
    data = request.get_json()
    activity_type = data.get('activity_type')
    concept_id = data.get('concept_id')
    duration = data.get('duration')
    
    if not activity_type or not concept_id or not duration:
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update study streak
    now = datetime.now()
    if user.last_study_date:
        days_diff = (now - user.last_study_date).days
        if days_diff == 1:
            user.study_streak += 1
        elif days_diff > 1:
            user.study_streak = 1
    else:
        user.study_streak = 1
    
    user.last_study_date = now
    user.total_study_time += duration
    
    # Save user profile
    if not user.update_profile({
        'last_study_date': user.last_study_date,
        'study_streak': user.study_streak,
        'total_study_time': user.total_study_time
    }):
        return jsonify({'error': 'Failed to update profile'}), 500
    
    return jsonify({'success': True})

@app.route('/api/learn/concept')
@login_required
def get_concept():
    path_id = request.args.get('path_id')
    if path_id not in LEARNING_PATHS:
        return jsonify({'error': 'Invalid learning path'}), 400
    
    # Get the first concept from the path
    # In a real app, this would track user progress and return the next concept
    concept = LEARNING_PATHS[path_id]['concepts'][0]
    return jsonify({
        'concept_id': concept['id'],
        'title': concept['title'],
        'content': concept['content'],
        'questions': [{'question': q['question'], 'options': q['options']} for q in concept['questions']]  # Don't send correct answers
    })

@app.route('/practice')
@login_required
def practice():
    """Render the practice page."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login', next=request.url))
    return render_template('practice.html')

@app.route('/api/practice/new_hand', methods=['POST'])
@login_required
def start_new_hand():
    """Start a new hand for practice mode."""
    try:
        # Generate random position
        positions = ['BTN', 'SB', 'BB']
        position = random.choice(positions)
        
        # Deal player cards
        player_cards = deal_cards(2)
        
        # Return initial game state
        return jsonify({
            'success': True,
            'position': position,
            'playerCards': player_cards,
            'message': f"New hand dealt! You're in position {position}"
        })
    except Exception as e:
        print(f"Error in start_new_hand: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/action', methods=['POST'])
@login_required
def handle_practice_action():
    try:
        data = request.get_json()
        action = data.get('action')
        amount = data.get('amount', 0)
        game_state = data.get('gameState')

        if not game_state:
            return jsonify({'error': 'Invalid game state'}), 400

        # Process the action using GTO solver
        player_hand = [string_to_card(c) for c in game_state.get('playerCards', [])]
        community_cards = [string_to_card(c) for c in game_state.get('communityCards', [])]
        
        # Get GTO advice for the current situation
        advice = gto_solver.get_advice(
            position=game_state['position'],
            hand=player_hand,
            community_cards=community_cards,
            pot=game_state['pot'],
            current_bet=game_state['currentBet'],
            stack=game_state['playerStack']
        )

        # Process bot actions based on GTO recommendations
        bot_actions = []
        if action != 'fold':
            for bot in ['bot1', 'bot2']:
                bot_action = gto_solver.get_bot_action(
                    position='BTN' if bot == 'bot1' else 'SB',
                    pot=game_state['pot'] + amount,
                    current_bet=amount or game_state['currentBet']
                )
                bot_actions.append({
                    'bot': bot,
                    'action': bot_action['action'],
                    'amount': bot_action['amount'],
                    'pot': game_state['pot'] + amount + bot_action['amount'],
                    'currentBet': bot_action['amount'] or game_state['currentBet']
                })

        # Update game state
        new_game_state = {
            'playerCards': game_state['playerCards'],
            'communityCards': game_state['communityCards'],
            'pot': game_state['pot'] + amount,
            'currentBet': amount or game_state['currentBet'],
            'position': game_state['position'],
            'playerStack': game_state['playerStack'] - amount,
            'bot1Stack': game_state['bot1Stack'],
            'bot2Stack': game_state['bot2Stack'],
            'phase': game_state['phase'],
            'handInProgress': True
        }

        # If it's preflop and all players have acted, deal flop
        if new_game_state['phase'] == 'preflop' and len(bot_actions) == 2:
            new_game_state['phase'] = 'flop'
            new_game_state['communityCards'] = deal_cards(3)
        # If it's flop and all players have acted, deal turn
        elif new_game_state['phase'] == 'flop' and len(bot_actions) == 2:
            new_game_state['phase'] = 'turn'
            new_game_state['communityCards'].append(deal_cards(1)[0])
        # If it's turn and all players have acted, deal river
        elif new_game_state['phase'] == 'turn' and len(bot_actions) == 2:
            new_game_state['phase'] = 'river'
            new_game_state['communityCards'].append(deal_cards(1)[0])
        # If it's river and all players have acted, evaluate hands
        elif new_game_state['phase'] == 'river' and len(bot_actions) == 2:
            # Evaluate hands and determine winner
            player_full_hand = player_hand + [string_to_card(c) for c in new_game_state['communityCards']]
            player_hand_value = hand_evaluator.evaluate_hand(player_full_hand)
            
            # Simulate bot hands (simplified for demo)
            bot1_hand = deal_cards(2)
            bot1_full_hand = [string_to_card(c) for c in bot1_hand] + [string_to_card(c) for c in new_game_state['communityCards']]
            bot1_hand_value = hand_evaluator.evaluate_hand(bot1_full_hand)
            
            bot2_hand = deal_cards(2)
            bot2_full_hand = [string_to_card(c) for c in bot2_hand] + [string_to_card(c) for c in new_game_state['communityCards']]
            bot2_hand_value = hand_evaluator.evaluate_hand(bot2_full_hand)
            
            # Determine winner
            is_winner = player_hand_value.rank.value > max(bot1_hand_value.rank.value, bot2_hand_value.rank.value)
            profit = new_game_state['pot'] if is_winner else -amount
            
            # Show bot cards in the final result
            new_game_state['bot1Cards'] = bot1_hand
            new_game_state['bot2Cards'] = bot2_hand
            
            return jsonify({
                'success': True,
                'gameState': new_game_state,
                'botActions': bot_actions,
                'handComplete': True,
                'result': {
                    'isWinner': is_winner,
                    'profit': profit,
                    'playerHandValue': str(player_hand_value.rank.name),
                    'bot1HandValue': str(bot1_hand_value.rank.name),
                    'bot2HandValue': str(bot2_hand_value.rank.name),
                    'gtoAnalysis': f"Your play was {'optimal' if is_winner else 'suboptimal'}. {advice['explanation']}"
                }
            })

        return jsonify({
            'success': True,
            'gameState': new_game_state,
            'botActions': bot_actions,
            'handComplete': False,
            'gtoAdvice': advice['explanation']
        })

    except Exception as e:
        print(f"Error in handle_practice_action: {str(e)}")
        return jsonify({'error': str(e)}), 500

def deal_cards(num_cards):
    """Helper function to deal random cards"""
    deck = []
    for suit in ['♠', '♥', '♦', '♣']:
        for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
            deck.append({'rank': rank, 'suit': suit})
    random.shuffle(deck)
    return deck[:num_cards]

@app.route('/api/practice/chat', methods=['POST'])
@login_required
def handle_practice_chat():
    try:
        data = request.get_json()
        message = data.get('message')
        game_state = data.get('gameState')

        if not message or not game_state:
            return jsonify({'error': 'Invalid request data'}), 400

        # Process the chat message and generate a response
        response = process_chat_message(message, game_state)

        return jsonify({
            'success': True,
            'response': response
        })

    except Exception as e:
        print(f"Error in handle_practice_chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_chat_message(message, game_state):
    """Process chat message and generate appropriate response"""
    message = message.lower()
    
    # Check for different types of questions/keywords
    if 'what should i do' in message or 'advice' in message:
        # Get GTO advice for current situation
        player_hand = [string_to_card(c) for c in game_state.get('playerCards', [])]
        community_cards = [string_to_card(c) for c in game_state.get('communityCards', [])]
        
        advice = gto_solver.get_advice(
            position=game_state['position'],
            hand=player_hand,
            community_cards=community_cards,
            pot=game_state['pot'],
            current_bet=game_state['currentBet'],
            stack=game_state['playerStack']
        )
        return f"Based on GTO principles, {advice['explanation']}"
    
    elif 'position' in message:
        return get_position_explanation(game_state['position'])
    
    elif 'equity' in message:
        player_hand = [string_to_card(c) for c in game_state.get('playerCards', [])]
        community_cards = [string_to_card(c) for c in game_state.get('communityCards', [])]
        equity = gto_solver.calculate_equity(player_hand, community_cards)
        return f"Your current equity is approximately {equity * 100:.1f}%"
    
    elif 'odds' in message or 'outs' in message:
        player_hand = [string_to_card(c) for c in game_state.get('playerCards', [])]
        community_cards = [string_to_card(c) for c in game_state.get('communityCards', [])]
        odds = gto_solver.calculate_odds(player_hand, community_cards)
        return f"Your pot odds are {odds['pot_odds']:.1f}% and you need {odds['outs']} outs to improve"
    
    else:
        return "I'm your AI poker coach! Ask me about your current hand, position, equity, or what action you should take."

def get_position_explanation(position):
    """Get detailed explanation for different positions"""
    explanations = {
        'BTN': "You're on the Button (BTN), the most advantageous position. You act last post-flop, giving you maximum information about your opponents' actions.",
        'SB': "You're in the Small Blind (SB). While you act first post-flop, you get to see one player's action pre-flop before making your decision.",
        'BB': "You're in the Big Blind (BB). You have the worst position but get to act last pre-flop and can often defend your blind with a wider range."
    }
    return explanations.get(position, "Unknown position")

@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access attempts."""
    if request.is_xhr:
        return jsonify({'error': 'Unauthorized'}), 401
    return redirect(url_for('login', next=request.url))

@app.route('/api/practice/gto_advice', methods=['POST'])
@login_required
def get_gto_advice():
    try:
        data = request.get_json()
        position = data.get('position')
        player_cards = data.get('playerCards', [])
        community_cards = data.get('communityCards', [])
        pot = data.get('pot', 0)
        current_bet = data.get('currentBet', 0)
        stack = data.get('stack', 1000)

        # Convert card data to Card objects
        player_hand = [string_to_card(c) for c in player_cards]
        comm_cards = [string_to_card(c) for c in community_cards]

        # Get GTO advice
        advice = gto_solver.get_advice(
            position=position,
            hand=player_hand,
            community_cards=comm_cards,
            pot=pot,
            current_bet=current_bet,
            stack=stack
        )

        # Calculate additional metrics
        equity = gto_solver.calculate_equity(player_hand, comm_cards)
        odds = gto_solver.calculate_odds(player_hand, comm_cards)

        return jsonify({
            'advice': advice['explanation'],
            'actions': advice['actions'],
            'equity': equity,
            'ev': advice['ev'],
            'odds': odds
        })

    except Exception as e:
        print(f"Error in get_gto_advice: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper function to convert suit and rank strings to Enum values
def string_to_card(card_dict):
    suit_map = {
        '♠': Suit.SPADES,
        '♥': Suit.HEARTS,
        '♦': Suit.DIAMONDS,
        '♣': Suit.CLUBS
    }
    
    rank_map = {
        '2': Rank.TWO,
        '3': Rank.THREE,
        '4': Rank.FOUR,
        '5': Rank.FIVE,
        '6': Rank.SIX,
        '7': Rank.SEVEN,
        '8': Rank.EIGHT,
        '9': Rank.NINE,
        '10': Rank.TEN,
        'J': Rank.JACK,
        'Q': Rank.QUEEN,
        'K': Rank.KING,
        'A': Rank.ACE
    }
    
    suit = suit_map.get(card_dict['suit'])
    rank = rank_map.get(card_dict['rank'])
    
    if not suit or not rank:
        raise ValueError(f"Invalid card: {card_dict}")
    
    return Card(suit=suit, rank=rank)

@app.route('/api/practice/debug', methods=['GET'])
def debug_practice():
    """Debug endpoint to check if the practice API is working."""
    try:
        # Test card creation
        test_card = string_to_card({'rank': 'A', 'suit': '♠'})
        
        # Test deal_cards
        dealt_cards = deal_cards(2)
        
        # Test GTO solver methods
        test_player_hand = [string_to_card(c) for c in dealt_cards]
        test_community_cards = [string_to_card(c) for c in deal_cards(3)]
        
        equity = gto_solver.calculate_equity(test_player_hand, test_community_cards)
        odds = gto_solver.calculate_odds(test_player_hand, test_community_cards)
        
        # Test hand evaluation
        test_full_hand = test_player_hand + test_community_cards
        hand_value = hand_evaluator.evaluate_hand(test_full_hand)
        
        return jsonify({
            'status': 'ok',
            'test_card': str(test_card),
            'dealt_cards': dealt_cards,
            'player_hand': [str(c) for c in test_player_hand],
            'community_cards': [str(c) for c in test_community_cards],
            'equity': equity,
            'odds': odds,
            'hand_value': str(hand_value.rank.name)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if Card is None or Suit is None or Rank is None or HandEvaluator is None or HandRank is None:
    class Suit:
        SPADES = "SPADES"
        HEARTS = "HEARTS"
        DIAMONDS = "DIAMONDS"
        CLUBS = "CLUBS"
    
    class Rank:
        TWO = "TWO"
        THREE = "THREE"
        FOUR = "FOUR"
        FIVE = "FIVE"
        SIX = "SIX"
        SEVEN = "SEVEN"
        EIGHT = "EIGHT"
        NINE = "NINE"
        TEN = "TEN"
        JACK = "JACK"
        QUEEN = "QUEEN"
        KING = "KING"
        ACE = "ACE"
    
    class HandRank:
        HIGH_CARD = "HIGH_CARD"
        PAIR = "PAIR"
        TWO_PAIR = "TWO_PAIR"
        THREE_OF_A_KIND = "THREE_OF_A_KIND"
        STRAIGHT = "STRAIGHT"
        FLUSH = "FLUSH"
        FULL_HOUSE = "FULL_HOUSE"
        FOUR_OF_A_KIND = "FOUR_OF_A_KIND"
        STRAIGHT_FLUSH = "STRAIGHT_FLUSH"
        ROYAL_FLUSH = "ROYAL_FLUSH"
        
        def __init__(self, name):
            self.name = name
            self.value = {"HIGH_CARD": 1, "PAIR": 2, "TWO_PAIR": 3, "THREE_OF_A_KIND": 4, 
                         "STRAIGHT": 5, "FLUSH": 6, "FULL_HOUSE": 7, "FOUR_OF_A_KIND": 8, 
                         "STRAIGHT_FLUSH": 9, "ROYAL_FLUSH": 10}[name]
    
    class Card:
        def __init__(self, suit, rank):
            self.suit = suit
            self.rank = rank
        
        def __str__(self):
            return f"{self.rank.name} of {self.suit.name}"
    
    class HandValue:
        def __init__(self, rank, cards):
            self.rank = rank
            self.cards = cards
    
    class HandEvaluator:
        @staticmethod
        def evaluate_hand(cards):
            # Simple mock implementation
            # Just return a random hand rank for demonstration
            import random
            ranks = [HandRank("HIGH_CARD"), HandRank("PAIR"), HandRank("TWO_PAIR"), 
                    HandRank("THREE_OF_A_KIND"), HandRank("STRAIGHT"), HandRank("FLUSH"),
                    HandRank("FULL_HOUSE"), HandRank("FOUR_OF_A_KIND"), 
                    HandRank("STRAIGHT_FLUSH"), HandRank("ROYAL_FLUSH")]
            
            # For demonstration, return a random hand rank
            # In a real implementation, this would evaluate the cards
            return HandValue(random.choice(ranks), cards)

# Create a global reference to the hand evaluator
hand_evaluator = HandEvaluator()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 