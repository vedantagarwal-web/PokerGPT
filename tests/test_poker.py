import pytest
from src.core.poker import Card, Deck, Hand, Board, Suit, Rank, create_deck

def test_card_creation():
    """Test creating cards with different suits and ranks."""
    # Test creating a card
    card = Card(Suit.SPADES, Rank.ACE)
    assert card.suit == Suit.SPADES
    assert card.rank == Rank.ACE
    
    # Test string representation
    assert str(card) == 'As'
    
    # Test equality
    card2 = Card(Suit.SPADES, Rank.ACE)
    assert card == card2
    
    # Test inequality
    card3 = Card(Suit.HEARTS, Rank.ACE)
    assert card != card3

def test_deck_creation():
    """Test creating and manipulating a deck."""
    # Test creating a deck
    deck = Deck()
    assert len(deck.cards) == 52
    
    # Test shuffling
    original_cards = deck.cards.copy()
    deck.shuffle()
    assert deck.cards != original_cards
    assert len(deck.cards) == 52
    
    # Test drawing cards
    card = deck.draw_card()
    assert isinstance(card, Card)
    assert len(deck.cards) == 51
    
    # Test resetting deck
    deck.reset()
    assert len(deck.cards) == 52

def test_hand_creation():
    """Test creating and manipulating hands."""
    # Test creating a hand
    hand = Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING))
    assert len(hand.cards) == 2
    assert hand.cards[0].suit == Suit.SPADES
    assert hand.cards[0].rank == Rank.ACE
    assert hand.cards[1].suit == Suit.HEARTS
    assert hand.cards[1].rank == Rank.KING
    
    # Test string representation
    assert str(hand) == 'As Kh'
    
    # Test equality
    hand2 = Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING))
    assert hand == hand2
    
    # Test inequality
    hand3 = Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.QUEEN))
    assert hand != hand3

def test_board_creation():
    """Test creating and manipulating boards."""
    # Test creating an empty board
    board = Board([])
    assert len(board.cards) == 0
    
    # Test creating a flop
    flop = Board([
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.QUEEN)
    ])
    assert len(flop.cards) == 3
    
    # Test creating a turn
    turn = Board([
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.QUEEN),
        Card(Suit.HEARTS, Rank.JACK)
    ])
    assert len(turn.cards) == 4
    
    # Test creating a river
    river = Board([
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.QUEEN),
        Card(Suit.HEARTS, Rank.JACK),
        Card(Suit.DIAMONDS, Rank.TEN)
    ])
    assert len(river.cards) == 5
    
    # Test string representation
    assert str(flop) == 'Ad Kc Qs'
    
    # Test equality
    flop2 = Board([
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.QUEEN)
    ])
    assert flop == flop2
    
    # Test inequality
    flop3 = Board([
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.JACK)
    ])
    assert flop != flop3

def test_create_deck():
    """Test creating a deck with excluded cards."""
    # Test creating a full deck
    deck = create_deck()
    assert len(deck.cards) == 52
    
    # Test creating a deck with excluded cards
    excluded_cards = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.KING)
    ]
    deck = create_deck(excluded_cards)
    assert len(deck.cards) == 50
    assert Card(Suit.SPADES, Rank.ACE) not in deck.cards
    assert Card(Suit.HEARTS, Rank.KING) not in deck.cards

def test_card_hash():
    """Test card hashing for use in sets and dictionaries."""
    # Create two identical cards
    card1 = Card(Suit.SPADES, Rank.ACE)
    card2 = Card(Suit.SPADES, Rank.ACE)
    
    # Test that they have the same hash
    assert hash(card1) == hash(card2)
    
    # Test that they can be used in a set
    card_set = {card1, card2}
    assert len(card_set) == 1
    
    # Test that they can be used as dictionary keys
    card_dict = {card1: 'value'}
    assert card_dict[card2] == 'value'

def test_hand_hash():
    """Test hand hashing for use in sets and dictionaries."""
    # Create two identical hands
    hand1 = Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING))
    hand2 = Hand(Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING))
    
    # Test that they have the same hash
    assert hash(hand1) == hash(hand2)
    
    # Test that they can be used in a set
    hand_set = {hand1, hand2}
    assert len(hand_set) == 1
    
    # Test that they can be used as dictionary keys
    hand_dict = {hand1: 'value'}
    assert hand_dict[hand2] == 'value'

def test_board_hash():
    """Test board hashing for use in sets and dictionaries."""
    # Create two identical boards
    board1 = Board([
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.QUEEN)
    ])
    board2 = Board([
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.QUEEN)
    ])
    
    # Test that they have the same hash
    assert hash(board1) == hash(board2)
    
    # Test that they can be used in a set
    board_set = {board1, board2}
    assert len(board_set) == 1
    
    # Test that they can be used as dictionary keys
    board_dict = {board1: 'value'}
    assert board_dict[board2] == 'value'

def test_card_equality():
    """Test card equality and hashing."""
    # Test identical cards
    card1 = Card(Suit.HEARTS, Rank.ACE)
    card2 = Card(Suit.HEARTS, Rank.ACE)
    assert card1 == card2
    
    # Test different cards
    card3 = Card(Suit.SPADES, Rank.ACE)
    card4 = Card(Suit.HEARTS, Rank.KING)
    assert card1 != card3
    assert card1 != card4
    
    # Test hashing
    cards = {card1, card2, card3, card4}
    assert len(cards) == 3  # card1 and card2 are identical

def test_deck_shuffling():
    """Test deck shuffling."""
    # Create two decks
    deck1 = Deck()
    deck2 = Deck()
    
    # Shuffle one deck
    deck1.shuffle()
    
    # Compare the decks
    assert deck1.cards != deck2.cards  # Should be different after shuffling
    assert len(deck1.cards) == len(deck2.cards)  # Should have same number of cards

def test_board_validation():
    """Test board validation rules."""
    # Test adding too many cards
    board = Board()
    for _ in range(5):
        board.add_card(Card(Suit.HEARTS, Rank.ACE))
    
    with pytest.raises(ValueError):
        board.add_card(Card(Suit.SPADES, Rank.KING))

def test_card_comparison():
    """Test card comparison operations."""
    # Test rank comparison
    ace = Card(Suit.HEARTS, Rank.ACE)
    king = Card(Suit.SPADES, Rank.KING)
    queen = Card(Suit.DIAMONDS, Rank.QUEEN)
    
    assert ace > king
    assert king > queen
    assert ace > queen
    
    # Test same rank, different suit
    ace_hearts = Card(Suit.HEARTS, Rank.ACE)
    ace_spades = Card(Suit.SPADES, Rank.ACE)
    assert ace_hearts == ace_spades  # Suits don't matter for comparison

def test_hand_comparison():
    """Test hand comparison operations."""
    # Create hands with different ranks
    high_ace = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    high_king = Hand(Card(Suit.DIAMONDS, Rank.KING), Card(Suit.CLUBS, Rank.QUEEN))
    
    assert high_ace > high_king
    
    # Create hands with same high card
    ace_king = Hand(Card(Suit.HEARTS, Rank.ACE), Card(Suit.SPADES, Rank.KING))
    ace_queen = Hand(Card(Suit.DIAMONDS, Rank.ACE), Card(Suit.CLUBS, Rank.QUEEN))
    
    assert ace_king > ace_queen

def test_board_state():
    """Test board state transitions."""
    board = Board()
    
    # Test flop
    board.add_card(Card(Suit.HEARTS, Rank.ACE))
    board.add_card(Card(Suit.SPADES, Rank.KING))
    board.add_card(Card(Suit.DIAMONDS, Rank.QUEEN))
    assert board.is_flop()
    
    # Test turn
    board.add_card(Card(Suit.CLUBS, Rank.JACK))
    assert board.is_turn()
    
    # Test river
    board.add_card(Card(Suit.HEARTS, Rank.TEN))
    assert board.is_river()

def test_deck_drawing():
    """Test deck drawing operations."""
    deck = Deck()
    
    # Test drawing single card
    card = deck.draw_card()
    assert isinstance(card, Card)
    assert len(deck.cards) == 51
    
    # Test drawing multiple cards
    cards = deck.draw_cards(5)
    assert len(cards) == 5
    assert len(deck.cards) == 46
    
    # Test drawing too many cards
    with pytest.raises(ValueError):
        deck.draw_cards(47) 