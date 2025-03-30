from typing import List, Tuple, Optional
from enum import Enum
import random

class Suit(Enum):
    HEARTS = 'h'
    DIAMONDS = 'd'
    CLUBS = 'c'
    SPADES = 's'

class Rank(Enum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = 'T'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    @classmethod
    def from_string(cls, card_str: str) -> 'Card':
        """Create a card from a string like 'As' or 'Kh'."""
        rank = Rank(card_str[0].upper())
        suit = Suit(card_str[1].lower())
        return cls(rank, suit)
    
    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

class Deck:
    def __init__(self):
        self.cards = [
            Card(rank, suit)
            for rank in Rank
            for suit in Suit
        ]
    
    def shuffle(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def draw(self) -> Optional[Card]:
        """Draw a card from the top of the deck."""
        if not self.cards:
            return None
        return self.cards.pop()
    
    def draw_multiple(self, count: int) -> List[Card]:
        """Draw multiple cards from the top of the deck."""
        return [self.draw() for _ in range(count)]
    
    def reset(self) -> None:
        """Reset the deck to its original state."""
        self.__init__()

class Hand:
    def __init__(self, cards: List[Card]):
        if len(cards) != 2:
            raise ValueError("A poker hand must contain exactly 2 cards")
        self.cards = cards
    
    @classmethod
    def from_string(cls, hand_str: str) -> 'Hand':
        """Create a hand from a string like 'As Kh'."""
        cards = [Card.from_string(card) for card in hand_str.split()]
        return cls(cards)
    
    def __str__(self) -> str:
        return " ".join(str(card) for card in self.cards)
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        return set(self.cards) == set(other.cards)
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.cards, key=lambda x: (x.rank.value, x.suit.value))))

class Board:
    def __init__(self, cards: List[Card]):
        if len(cards) not in [0, 3, 4, 5]:
            raise ValueError("Board must have 0, 3, 4, or 5 cards")
        self.cards = cards
    
    @classmethod
    def from_string(cls, board_str: str) -> 'Board':
        """Create a board from a string like 'Jh 9d 2c'."""
        if not board_str:
            return cls([])
        cards = [Card.from_string(card) for card in board_str.split()]
        return cls(cards)
    
    def __str__(self) -> str:
        return " ".join(str(card) for card in self.cards)
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Board):
            return NotImplemented
        return set(self.cards) == set(other.cards)
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.cards, key=lambda x: (x.rank.value, x.suit.value))))

def create_deck(exclude_cards: List[Card] = None) -> Deck:
    """Create a deck excluding specified cards."""
    deck = Deck()
    if exclude_cards:
        deck.cards = [card for card in deck.cards if card not in exclude_cards]
    return deck 