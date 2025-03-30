import pytest
import os
from src.nlp.poker_nlp import PokerNLP
from src.core.poker import Card, Hand, Board, Suit, Rank

@pytest.fixture
def setup_test_data(tmp_path):
    """Create a temporary directory for test data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def poker_nlp(setup_test_data):
    """Create a PokerNLP instance with test data."""
    model_path = setup_test_data / "nlp_model"
    return PokerNLP(str(model_path))

def test_describe_action(poker_nlp):
    """Test generating action descriptions."""
    # Test with valid inputs
    description = poker_nlp.describe_action(
        hand="Ah Kd",
        board="2h 3h 4h",
        action="raise",
        position="BTN"
    )
    assert isinstance(description, str)
    assert "Ah Kd" in description
    assert "BTN" in description
    assert "raise" in description
    
    # Test with different position
    description = poker_nlp.describe_action(
        hand="Ah Kd",
        board="2h 3h 4h",
        action="fold",
        position="BB"
    )
    assert "BB" in description
    assert "fold" in description

def test_parse_hand_description(poker_nlp):
    """Test parsing hand descriptions."""
    # Test with valid description
    description = "I have Ah Kd in BTN position with 100BB stack"
    parsed = poker_nlp.parse_hand_description(description)
    assert isinstance(parsed, dict)
    assert parsed['position'] == 'BTN'
    assert parsed['stack_size'] == 100
    
    # Test with different description
    description = "UTG position with 2 opponents"
    parsed = poker_nlp.parse_hand_description(description)
    assert parsed['position'] == 'UTG'
    assert parsed['opponents'] == 2

def test_generate_explanation(poker_nlp):
    """Test generating concept explanations."""
    # Test with different difficulty levels
    for difficulty in ['beginner', 'intermediate', 'advanced']:
        explanation = poker_nlp.generate_explanation(
            concept="3-betting",
            difficulty=difficulty
        )
        assert isinstance(explanation, str)
        assert "3-betting" in explanation
        assert difficulty in explanation.lower()

def test_extract_keywords(poker_nlp):
    """Test extracting keywords from text."""
    # Test with poker-specific terms
    text = "I'm in UTG position and considering a 3-bet with Ah Kd"
    keywords = poker_nlp.extract_keywords(text)
    assert isinstance(keywords, list)
    assert "UTG" in keywords
    assert "3-bet" in keywords
    
    # Test with different text
    text = "The board shows 2h 3h 4h, giving me a flush draw"
    keywords = poker_nlp.extract_keywords(text)
    assert "flush" in keywords

def test_model_loading_failure(poker_nlp):
    """Test handling of model loading failure."""
    # The model should fall back to basic implementation
    # when model loading fails
    description = poker_nlp.describe_action(
        hand="Ah Kd",
        board="2h 3h 4h",
        action="raise",
        position="BTN"
    )
    assert isinstance(description, str)
    assert "Ah Kd" in description
    assert "BTN" in description
    assert "raise" in description

def test_invalid_inputs(poker_nlp):
    """Test handling of invalid inputs."""
    # Test with empty strings
    description = poker_nlp.describe_action("", "", "", "")
    assert isinstance(description, str)
    
    # Test with None values
    description = poker_nlp.describe_action(None, None, None, None)
    assert isinstance(description, str)
    
    # Test with invalid position
    description = poker_nlp.describe_action(
        hand="Ah Kd",
        board="2h 3h 4h",
        action="raise",
        position="INVALID"
    )
    assert isinstance(description, str)

def test_complex_hand_description(poker_nlp):
    """Test parsing complex hand descriptions."""
    description = (
        "I'm in CO position with 150BB stack, facing a raise from UTG "
        "and a 3-bet from BTN. The board is 2h 3h 4h and I have Ah Kd."
    )
    parsed = poker_nlp.parse_hand_description(description)
    assert parsed['position'] == 'CO'
    assert parsed['stack_size'] == 150
    assert parsed['opponents'] == 2

def test_concept_explanation_difficulty(poker_nlp):
    """Test that explanations adapt to difficulty level."""
    # Test beginner explanation
    beginner_explanation = poker_nlp.generate_explanation(
        concept="3-betting",
        difficulty="beginner"
    )
    assert "basic" in beginner_explanation.lower()
    assert "simple" in beginner_explanation.lower()
    
    # Test advanced explanation
    advanced_explanation = poker_nlp.generate_explanation(
        concept="3-betting",
        difficulty="advanced"
    )
    assert "advanced" in advanced_explanation.lower()
    assert "complex" in advanced_explanation.lower()

def test_keyword_extraction_complexity(poker_nlp):
    """Test keyword extraction with complex poker scenarios."""
    text = (
        "I'm in MP position with 100BB stack. The UTG player opens to 3BB, "
        "and I'm considering a 3-bet with Ah Kd. The BTN player has been "
        "aggressive with his 4-bets lately."
    )
    keywords = poker_nlp.extract_keywords(text)
    assert "MP" in keywords
    assert "UTG" in keywords
    assert "BTN" in keywords
    assert "3-bet" in keywords
    assert "4-bet" in keywords

def test_hand_description(nlp):
    """Test generating hand descriptions."""
    hand = Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING))
    description = nlp.describe_hand(hand)
    assert isinstance(description, str)
    assert 'Ace' in description
    assert 'King' in description
    assert 'suited' not in description.lower()

def test_hand_description_suited(nlp):
    """Test generating descriptions for suited hands."""
    hand = Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    description = nlp.describe_hand(hand)
    assert isinstance(description, str)
    assert 'Ace' in description
    assert 'King' in description
    assert 'suited' in description.lower()

def test_board_description(nlp):
    """Test generating board descriptions."""
    board = Board([
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.QUEEN)
    ])
    description = nlp.describe_board(board)
    assert isinstance(description, str)
    assert 'Ace' in description
    assert 'King' in description
    assert 'Queen' in description

def test_hand_analysis(nlp):
    """Test analyzing hand strength and context."""
    hand = Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING))
    board = Board([])
    position = "BTN"
    
    analysis = nlp.analyze_hand(hand, board, position)
    assert isinstance(analysis, dict)
    assert 'strength' in analysis
    assert 'context' in analysis
    assert 'recommendations' in analysis

def test_practice_question_generation(nlp):
    """Test generating practice questions."""
    concept_id = "preflop_position"
    difficulty = "beginner"
    
    question = nlp.generate_practice_question(concept_id, difficulty)
    assert isinstance(question, dict)
    assert 'question' in question
    assert 'options' in question
    assert 'correct_answer' in question
    assert 'explanation' in question

def test_hand_history_analysis(nlp):
    """Test analyzing hand history."""
    hand_history = [
        {
            'hand': Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)),
            'board': Board([]),
            'position': 'BTN',
            'action': 'raise',
            'result': 'win'
        }
    ]
    
    analysis = nlp.analyze_hand_history(hand_history)
    assert isinstance(analysis, dict)
    assert 'patterns' in analysis
    assert 'recommendations' in analysis
    assert 'improvements' in analysis

def test_concept_relationship_analysis(nlp):
    """Test analyzing relationships between concepts."""
    concept_ids = ["preflop_position", "range_construction"]
    
    analysis = nlp.analyze_concept_relationships(concept_ids)
    assert isinstance(analysis, dict)
    assert 'relationships' in analysis
    assert 'prerequisites' in analysis
    assert 'learning_path' in analysis

def test_difficulty_adaptation(nlp):
    """Test adapting content difficulty."""
    concept_id = "preflop_position"
    
    # Test beginner level
    beginner_content = nlp.adapt_difficulty(concept_id, "beginner")
    assert isinstance(beginner_content, str)
    assert len(beginner_content) > 0
    
    # Test intermediate level
    intermediate_content = nlp.adapt_difficulty(concept_id, "intermediate")
    assert isinstance(intermediate_content, str)
    assert len(intermediate_content) > 0
    
    # Test advanced level
    advanced_content = nlp.adapt_difficulty(concept_id, "advanced")
    assert isinstance(advanced_content, str)
    assert len(advanced_content) > 0
    
    # Content should be different for different difficulty levels
    assert beginner_content != intermediate_content
    assert intermediate_content != advanced_content 