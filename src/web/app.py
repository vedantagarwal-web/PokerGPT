from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from typing import Dict, Optional
from datetime import datetime
import json
import random

from ..core.equity_calculator import EquityCalculator
from ..core.gto_solver import GtoSolver, GameState, Position, Action
from ..knowledge.poker_knowledge import PokerKnowledge
from ..personalization.user_profile import UserProfile
from ..personalization.spaced_repetition import SpacedRepetition
from ..core.hand_evaluator import Card, Suit, Rank, HandEvaluator, HandRank
from .routes import bp as routes_bp

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize paths
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Initialize EquityCalculator
equity_calculator = EquityCalculator(os.path.join(data_dir, 'equity_cache'))

# Initialize UserProfile
UserProfile.set_profiles_file(os.path.join(data_dir, 'profiles.json'))

# Initialize components
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
                    },
                    {
                        'question': 'What is the main advantage of playing in position?',
                        'options': [
                            'You can see other players\' actions first',
                            'You can control the pot size better',
                            'You can bluff more effectively',
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
            },
            {
                'id': 'preflop_actions',
                'title': 'Preflop Actions',
                'content': '''
                    <h4>Preflop Actions</h4>
                    <p>Understanding when to raise, call, or fold preflop is essential.</p>
                    <h5>Common Preflop Actions:</h5>
                    <ul>
                        <li><strong>Open Raise</strong>: First to enter the pot</li>
                        <li><strong>3-Bet</strong>: Re-raising an initial raise</li>
                        <li><strong>4-Bet</strong>: Re-raising a 3-bet</li>
                        <li><strong>Call</strong>: Matching the current bet</li>
                        <li><strong>Fold</strong>: Discarding your hand</li>
                    </ul>
                    <h5>Bet Sizing:</h5>
                    <ul>
                        <li>Standard open: 2.5-3x the big blind</li>
                        <li>3-bet: 2.5-3x the initial raise</li>
                        <li>4-bet: 2.2-2.5x the 3-bet</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'What is a standard preflop open raise size?',
                        'options': ['1x BB', '2.5-3x BB', '5x BB', '10x BB'],
                        'correct': '2.5-3x BB'
                    },
                    {
                        'question': 'When should you consider 3-betting?',
                        'options': [
                            'With any two cards',
                            'With premium hands or as a bluff',
                            'Only with AA or KK',
                            'Never 3-bet'
                        ],
                        'correct': 'With premium hands or as a bluff'
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
            },
            {
                'id': 'board_texture',
                'title': 'Board Texture',
                'content': '''
                    <h4>Understanding Board Texture</h4>
                    <p>Board texture refers to the characteristics of the community cards and how they interact.</p>
                    <h5>Types of Board Textures:</h5>
                    <ul>
                        <li><strong>Dry Boards</strong>: No draws, paired, or connected cards</li>
                        <li><strong>Wet Boards</strong>: Multiple draws, connected cards</li>
                        <li><strong>Paired Boards</strong>: Two or more cards of the same rank</li>
                        <li><strong>Monotone Boards</strong>: Three or more cards of the same suit</li>
                    </ul>
                    <h5>Strategy Adjustments:</h5>
                    <ul>
                        <li>Bet sizing based on texture</li>
                        <li>Range construction</li>
                        <li>Bluffing frequency</li>
                        <li>Value betting approach</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'What is a dry board?',
                        'options': [
                            'A board with many draws',
                            'A board with no draws, paired, or connected cards',
                            'A board with three of the same suit',
                            'A board with three connected cards'
                        ],
                        'correct': 'A board with no draws, paired, or connected cards'
                    },
                    {
                        'question': 'How should you adjust your betting on a wet board?',
                        'options': [
                            'Bet smaller',
                            'Bet larger',
                            'Never bet',
                            'Only check'
                        ],
                        'correct': 'Bet larger'
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
            },
            {
                'id': 'balanced_strategy',
                'title': 'Balanced Strategy',
                'content': '''
                    <h4>Balanced Strategy</h4>
                    <p>A balanced strategy includes both value bets and bluffs in the correct proportions.</p>
                    <h5>Key Components:</h5>
                    <ul>
                        <li><strong>Value Betting</strong>: Betting strong hands for value</li>
                        <li><strong>Bluffing</strong>: Betting weak hands to win pots</li>
                        <li><strong>Mixed Strategies</strong>: Using multiple actions with the same hand</li>
                        <li><strong>Frequency-Based Play</strong>: Making decisions based on optimal frequencies</li>
                    </ul>
                    <h5>Balance Considerations:</h5>
                    <ul>
                        <li>Pot odds</li>
                        <li>Stack depth</li>
                        <li>Position</li>
                        <li>Opponent tendencies</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'What is a balanced strategy?',
                        'options': [
                            'Only betting strong hands',
                            'Only bluffing',
                            'A mix of value bets and bluffs',
                            'Never betting'
                        ],
                        'correct': 'A mix of value bets and bluffs'
                    },
                    {
                        'question': 'Why is balance important in poker?',
                        'options': [
                            'It makes the game more fun',
                            'It makes you unpredictable',
                            'It\'s required by poker rules',
                            'It makes the game faster'
                        ],
                        'correct': 'It makes you unpredictable'
                    }
                ]
            },
            {
                'id': 'ev_calculations',
                'title': 'Expected Value Calculations',
                'content': '''
                    <h4>Expected Value (EV) Calculations</h4>
                    <p>Understanding EV helps make profitable decisions in poker.</p>
                    <h5>EV Components:</h5>
                    <ul>
                        <li><strong>Probability</strong>: Chance of winning</li>
                        <li><strong>Pot Size</strong>: Amount to win</li>
                        <li><strong>Cost</strong>: Amount to call or bet</li>
                    </ul>
                    <h5>EV Formula:</h5>
                    <p>EV = (Probability × Pot Size) - Cost</p>
                    <h5>Applications:</h5>
                    <ul>
                        <li>Calling decisions</li>
                        <li>Betting decisions</li>
                        <li>Bluffing decisions</li>
                        <li>Range construction</li>
                    </ul>
                ''',
                'questions': [
                    {
                        'question': 'What is Expected Value (EV)?',
                        'options': [
                            'The amount you win in a hand',
                            'The average profit/loss of a decision',
                            'The size of the pot',
                            'The amount you bet'
                        ],
                        'correct': 'The average profit/loss of a decision'
                    },
                    {
                        'question': 'What components are needed to calculate EV?',
                        'options': [
                            'Only the pot size',
                            'Probability, pot size, and cost',
                            'Only the probability',
                            'Only the cost'
                        ],
                        'correct': 'Probability, pot size, and cost'
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
    return UserProfile.get_profile(user_id)

def get_current_user():
    """Get the current user's profile."""
    if current_user.is_authenticated:
        return UserProfile.get_profile(current_user.username)
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
@login_required
def learn():
    """Render the learning page."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Get user's learning progress
    learning_paths = list(LEARNING_PATHS.values())
    user_progress = {
        path['id']: next(
            (p for p in user.learning_paths if p.get('path_id') == path['id']),
            {'completed': False, 'score': 0}
        )
        for path in learning_paths
    }
    
    return render_template('learn.html', learning_paths=learning_paths, user_progress=user_progress)

@app.route('/profile')
@login_required
def profile():
    """Render the user profile page."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Get learning statistics
    stats = user.get_learning_stats()
    
    # Get review statistics
    review_stats = spaced_repetition.get_review_stats(user.username)
    
    return render_template('profile.html', user=user, stats=stats, review_stats=review_stats)

@app.route('/api/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return jsonify({'success': True})

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 