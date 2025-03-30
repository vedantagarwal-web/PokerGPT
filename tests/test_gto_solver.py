import pytest
import os
from src.core.gto_solver import GtoSolver, GameState
from src.core.poker import Card, Hand, Board, Suit, Rank

@pytest.fixture
def gto_solver():
    """Create a test GTO solver instance."""
    test_data_path = os.path.join(os.path.dirname(__file__), 'data')
    solver = GtoSolver(os.path.join(test_data_path, 'gto_solutions.json'))
    return solver

def test_get_action_preflop(gto_solver):
    """Test getting optimal action preflop."""
    game_state = GameState(
        hand=Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)),
        position="BTN",
        opponents=1,
        action_history=["fold", "fold"],
        effective_stack=100,
        board=Board([]),
        tournament=False
    )
    
    action, frequency, ev = gto_solver.get_action(game_state)
    assert action in ["fold", "call", "raise"]
    assert 0 <= frequency <= 1
    assert ev is not None

def test_get_action_postflop(gto_solver):
    """Test getting optimal action postflop."""
    game_state = GameState(
        hand=Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)),
        position="BTN",
        opponents=1,
        action_history=["fold", "fold", "call", "check"],
        effective_stack=100,
        board=Board([
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.SPADES, Rank.QUEEN)
        ]),
        tournament=False
    )
    
    action, frequency, ev = gto_solver.get_action(game_state)
    assert action in ["fold", "call", "raise", "check"]
    assert 0 <= frequency <= 1
    assert ev is not None

def test_get_range(gto_solver):
    """Test getting optimal ranges for different positions."""
    # Test BTN range
    btn_range = gto_solver.get_range("BTN", 100)
    assert len(btn_range) > 0
    assert "AA" in btn_range
    assert "AKs" in btn_range
    
    # Test UTG range
    utg_range = gto_solver.get_range("UTG", 100)
    assert len(utg_range) > 0
    assert "AA" in utg_range
    assert len(utg_range) < len(btn_range)  # UTG range should be tighter

def test_solution_caching(gto_solver):
    """Test caching of GTO solutions."""
    game_state = GameState(
        hand=Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)),
        position="BTN",
        opponents=1,
        action_history=["fold", "fold"],
        effective_stack=100,
        board=Board([]),
        tournament=False
    )
    
    # First calculation
    action1, freq1, ev1 = gto_solver.get_action(game_state)
    
    # Second calculation should use cache
    action2, freq2, ev2 = gto_solver.get_action(game_state)
    
    assert action1 == action2
    assert freq1 == freq2
    assert ev1 == ev2

def test_different_stack_sizes(gto_solver):
    """Test GTO solutions with different stack sizes."""
    game_state_shallow = GameState(
        hand=Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)),
        position="BTN",
        opponents=1,
        action_history=["fold", "fold"],
        effective_stack=20,
        board=Board([]),
        tournament=False
    )
    
    game_state_deep = GameState(
        hand=Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)),
        position="BTN",
        opponents=1,
        action_history=["fold", "fold"],
        effective_stack=200,
        board=Board([]),
        tournament=False
    )
    
    action_shallow, freq_shallow, ev_shallow = gto_solver.get_action(game_state_shallow)
    action_deep, freq_deep, ev_deep = gto_solver.get_action(game_state_deep)
    
    # Solutions should be different for different stack sizes
    assert (action_shallow, freq_shallow) != (action_deep, freq_deep)

def test_tournament_vs_cash(gto_solver):
    """Test GTO solutions in tournament vs cash game contexts."""
    game_state_tournament = GameState(
        hand=Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)),
        position="BTN",
        opponents=1,
        action_history=["fold", "fold"],
        effective_stack=20,
        board=Board([]),
        tournament=True
    )
    
    game_state_cash = GameState(
        hand=Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)),
        position="BTN",
        opponents=1,
        action_history=["fold", "fold"],
        effective_stack=20,
        board=Board([]),
        tournament=False
    )
    
    action_tournament, freq_tournament, ev_tournament = gto_solver.get_action(game_state_tournament)
    action_cash, freq_cash, ev_cash = gto_solver.get_action(game_state_cash)
    
    # Solutions should be different for tournament vs cash
    assert (action_tournament, freq_tournament) != (action_cash, freq_cash) 