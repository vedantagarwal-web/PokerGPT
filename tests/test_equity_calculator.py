import pytest
import os
from src.core.equity_calculator import EquityCalculator, EquityResult
from src.core.poker import Card, Hand, Board, Suit, Rank

@pytest.fixture
def setup_test_data(tmp_path):
    """Create a temporary directory for test data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def equity_calculator(setup_test_data):
    """Create an EquityCalculator instance with test data."""
    cache_path = setup_test_data / "equity_cache.json"
    return EquityCalculator(str(cache_path))

def test_equity_calculation(equity_calculator):
    """Test basic equity calculations."""
    # Test with a strong hand
    hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    board = Board()
    opponent_range = "random"
    
    result = equity_calculator.calculate_equity(hand, opponent_range, board)
    assert isinstance(result, EquityResult)
    assert 0 <= result.equity <= 1
    assert result.outs >= 0
    assert result.hand_type is not None

def test_equity_with_board(equity_calculator):
    """Test equity calculations with different board states."""
    # Test preflop
    hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    board = Board()
    opponent_range = "random"
    
    preflop_result = equity_calculator.calculate_equity(hand, opponent_range, board)
    
    # Test flop
    board.add_card(Card(Suit.DIAMONDS, Rank.QUEEN))
    board.add_card(Card(Suit.CLUBS, Rank.JACK))
    board.add_card(Card(Suit.HEARTS, Rank.TEN))
    
    flop_result = equity_calculator.calculate_equity(hand, opponent_range, board)
    assert flop_result.equity != preflop_result.equity  # Should be different

def test_equity_with_different_ranges(equity_calculator):
    """Test equity calculations against different opponent ranges."""
    hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    board = Board()
    
    # Test against random range
    random_result = equity_calculator.calculate_equity(hand, "random", board)
    
    # Test against tight range
    tight_result = equity_calculator.calculate_equity(hand, "tight", board)
    assert tight_result.equity <= random_result.equity  # Should be lower against tight range
    
    # Test against loose range
    loose_result = equity_calculator.calculate_equity(hand, "loose", board)
    assert loose_result.equity >= random_result.equity  # Should be higher against loose range

def test_equity_with_different_hands(equity_calculator):
    """Test equity calculations with different starting hands."""
    board = Board()
    opponent_range = "random"
    
    # Test with premium hand
    premium_hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    premium_result = equity_calculator.calculate_equity(premium_hand, opponent_range, board)
    
    # Test with medium hand
    medium_hand = Hand(Card(Suit.DIAMONDS, Rank.QUEEN), Card(Suit.CLUBS, Rank.JACK))
    medium_result = equity_calculator.calculate_equity(medium_hand, opponent_range, board)
    assert premium_result.equity > medium_result.equity  # Premium hand should have higher equity
    
    # Test with weak hand
    weak_hand = Hand(Card(Suit.HEARTS, Rank.SEVEN), Card(Suit.SPADES, Rank.TWO))
    weak_result = equity_calculator.calculate_equity(weak_hand, opponent_range, board)
    assert medium_result.equity > weak_result.equity  # Medium hand should have higher equity

def test_equity_caching(equity_calculator, setup_test_data):
    """Test that equity calculations are cached correctly."""
    hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    board = Board()
    opponent_range = "random"
    
    # First calculation
    result1 = equity_calculator.calculate_equity(hand, opponent_range, board)
    
    # Create new calculator instance
    new_cache_path = setup_test_data / "equity_cache.json"
    new_calculator = EquityCalculator(str(new_cache_path))
    
    # Second calculation should be faster and give same result
    result2 = new_calculator.calculate_equity(hand, opponent_range, board)
    assert result1.equity == result2.equity
    assert result1.outs == result2.outs
    assert result1.hand_type == result2.hand_type

def test_equity_with_draws(equity_calculator):
    """Test equity calculations with drawing hands."""
    # Test with flush draw
    hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.HEARTS, Rank.KING))
    board = Board()
    board.add_card(Card(Suit.HEARTS, Rank.QUEEN))
    board.add_card(Card(Suit.HEARTS, Rank.JACK))
    board.add_card(Card(Suit.DIAMONDS, Rank.TEN))
    
    flush_result = equity_calculator.calculate_equity(hand, "random", board)
    assert flush_result.outs > 0  # Should have outs for flush
    
    # Test with straight draw
    hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    board = Board()
    board.add_card(Card(Suit.DIAMONDS, Rank.QUEEN))
    board.add_card(Card(Suit.CLUBS, Rank.JACK))
    board.add_card(Card(Suit.HEARTS, Rank.TEN))
    
    straight_result = equity_calculator.calculate_equity(hand, "random", board)
    assert straight_result.outs > 0  # Should have outs for straight

def test_equity_with_made_hands(equity_calculator):
    """Test equity calculations with made hands."""
    # Test with pair
    hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.ACE))
    board = Board()
    pair_result = equity_calculator.calculate_equity(hand, "random", board)
    assert pair_result.hand_type == "pair"
    
    # Test with two pair
    board.add_card(Card(Suit.DIAMONDS, Rank.KING))
    board.add_card(Card(Suit.CLUBS, Rank.KING))
    two_pair_result = equity_calculator.calculate_equity(hand, "random", board)
    assert two_pair_result.hand_type == "two_pair"
    
    # Test with three of a kind
    board.add_card(Card(Suit.HEARTS, Rank.ACE))
    three_of_a_kind_result = equity_calculator.calculate_equity(hand, "random", board)
    assert three_of_a_kind_result.hand_type == "three_of_a_kind"

def test_equity_edge_cases(equity_calculator):
    """Test equity calculations in edge cases."""
    # Test with empty board
    hand = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    board = Board()
    result = equity_calculator.calculate_equity(hand, "random", board)
    assert result.equity > 0
    
    # Test with full board
    board.add_card(Card(Suit.DIAMONDS, Rank.QUEEN))
    board.add_card(Card(Suit.CLUBS, Rank.JACK))
    board.add_card(Card(Suit.HEARTS, Rank.TEN))
    board.add_card(Card(Suit.SPADES, Rank.NINE))
    board.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
    result = equity_calculator.calculate_equity(hand, "random", board)
    assert result.equity > 0
    
    # Test with invalid hand
    with pytest.raises(ValueError):
        equity_calculator.calculate_equity(None, "random", board) 