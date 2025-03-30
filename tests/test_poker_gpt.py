import pytest
import os
from datetime import datetime, timedelta
from src.core.gto_solver import GtoSolver, GameState
from src.core.equity_calculator import EquityCalculator
from src.core.poker import Card, Hand, Board, Suit, Rank
from src.knowledge.poker_knowledge import PokerKnowledge, DifficultyLevel
from src.nlp.poker_nlp import PokerNLP, PokerSituation, ActionType
from src.personalization.user_profile import UserProfile, Activity
from src.personalization.spaced_repetition import SpacedRepetition

# Test data paths
TEST_DATA_DIR = "tests/data"
GTO_SOLUTIONS_PATH = os.path.join(TEST_DATA_DIR, "solutions.json")
KNOWLEDGE_PATH = os.path.join(TEST_DATA_DIR, "knowledge.json")
EQUITY_CACHE_PATH = os.path.join(TEST_DATA_DIR, "equity_cache.json")
USER_PROFILE_PATH = os.path.join(TEST_DATA_DIR, "user_profile.json")
SRS_PATH = os.path.join(TEST_DATA_DIR, "srs.json")

@pytest.fixture
def setup_test_data():
    """Create test data directory and files."""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    yield
    # Cleanup after tests
    for file in os.listdir(TEST_DATA_DIR):
        os.remove(os.path.join(TEST_DATA_DIR, file))
    os.rmdir(TEST_DATA_DIR)

def test_gto_solver(setup_test_data):
    """Test GTO solver functionality."""
    solver = GtoSolver(GTO_SOLUTIONS_PATH)
    
    # Test preflop decision
    game_state = GameState(
        hand=('As', 'Kh'),
        position='BTN',
        opponents=['BB'],
        action_history=[('BB', 'fold', None)],
        effective_stack=100,
        board=[],
        tournament=False
    )
    
    action, frequency, ev = solver.get_action(game_state)
    assert action == 'raise'
    assert 0 <= frequency <= 1
    assert ev > 0
    
    # Test postflop decision
    game_state.board = ['Jh', '9d', '2c']
    action, frequency, ev = solver.get_action(game_state)
    assert action == 'bet'
    assert 0 <= frequency <= 1
    assert ev > 0

def test_equity_calculator(setup_test_data):
    """Test equity calculator functionality."""
    calculator = EquityCalculator(EQUITY_CACHE_PATH)
    
    # Test preflop equity
    hand = Hand.from_string("As Kh")
    opponent_range = {'AA': 1.0, 'KK': 1.0, 'QQ': 0.8}
    result = calculator.calculate_equity(hand, opponent_range)
    
    assert 0 <= result.equity <= 100
    assert 0 <= result.hand_strength <= 1
    assert len(result.outs) >= 0
    
    # Test postflop equity
    board = Board.from_string("Jh 9d 2c")
    result = calculator.calculate_equity(hand, opponent_range, board)
    
    assert 0 <= result.equity <= 100
    assert 0 <= result.hand_strength <= 1
    assert len(result.outs) >= 0

def test_poker_knowledge(setup_test_data):
    """Test poker knowledge base functionality."""
    knowledge = PokerKnowledge(KNOWLEDGE_PATH)
    
    # Test concept retrieval
    concept_id = "preflop_position"
    explanation = knowledge.get_explanation(concept_id, DifficultyLevel.BEGINNER)
    assert len(explanation) > 0
    
    # Test learning path
    path = knowledge.get_learning_path("preflop_position", "game_theory")
    assert len(path) > 0
    assert "preflop_position" in path
    assert "game_theory" in path
    
    # Test prerequisites
    prereqs = knowledge.get_prerequisites("game_theory")
    assert "range_construction" in prereqs
    assert "betting_strategy" in prereqs

def test_poker_nlp(setup_test_data):
    """Test NLP component functionality."""
    nlp = PokerNLP("data/models")
    
    # Test situation parsing
    query = "I have Ace of Spades and King of Hearts in the cutoff position. The button raised to 3BB, and I have 100BB effective stack."
    situation = nlp.parse_situation(query)
    
    assert situation.hand == ('As', 'Kh')
    assert situation.position == 'CO'
    assert situation.effective_stack == 100
    
    # Test action extraction
    action, size = nlp.extract_action("raise to 3BB")
    assert action == ActionType.RAISE
    assert size == 3.0
    
    # Test position extraction
    position = nlp.extract_position("I'm on the button")
    assert position == 'BTN'

def test_user_profile(setup_test_data):
    """Test user profile functionality."""
    profile = UserProfile("test_user", USER_PROFILE_PATH)
    
    # Test XP and leveling
    profile.add_xp(500)
    assert profile.profile['xp'] == 500
    assert profile.profile['level'] == 1
    
    profile.add_xp(600)
    assert profile.profile['level'] == 2
    assert profile.profile['xp'] == 100
    
    # Test activity tracking
    activity = Activity(
        id="test_activity",
        title="Completed Concept",
        description="Finished learning preflop position",
        timestamp=datetime.now(),
        type="concept_completed"
    )
    profile.add_activity(activity)
    assert len(profile.profile['recent_activity']) == 1
    
    # Test learning path update
    profile.update_learning_path(
        "preflop",
        0.5,
        ["preflop_position"],
        "range_construction"
    )
    assert len(profile.profile['learning_paths']) == 1
    assert profile.profile['learning_paths'][0]['progress'] == 0.5

def test_spaced_repetition(setup_test_data):
    """Test spaced repetition system functionality."""
    srs = SpacedRepetition("test_user", SRS_PATH)
    
    # Test adding concept
    concept_id = "preflop_position"
    srs.add_concept(concept_id)
    assert concept_id in srs.items
    
    # Test review
    srs.review_concept(concept_id, 5)
    stats = srs.get_concept_stats(concept_id)
    assert stats['repetitions'] == 1
    assert stats['interval'] == 6
    
    # Test mastery calculation
    mastery = srs.get_mastery_level(concept_id)
    assert 0 <= mastery <= 100
    
    # Test due reviews
    srs.items[concept_id].next_review = datetime.now() - timedelta(days=1)
    due_reviews = srs.get_due_reviews()
    assert concept_id in due_reviews 