from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

class Suit(Enum):
    SPADES = '♠'
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'

class Rank(Enum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'

@dataclass
class Card:
    suit: Suit
    rank: Rank

    def __init__(self, suit, rank):
        """Initialize a card with either Enum values or strings."""
        if isinstance(suit, str):
            suit_map = {
                '♠': Suit.SPADES,
                '♥': Suit.HEARTS,
                '♦': Suit.DIAMONDS,
                '♣': Suit.CLUBS
            }
            self.suit = suit_map.get(suit, suit)
        else:
            self.suit = suit
            
        if isinstance(rank, str):
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
            self.rank = rank_map.get(rank, rank)
        else:
            self.rank = rank

    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"

class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

@dataclass
class Hand:
    cards: List[Card]
    rank: HandRank
    kickers: List[Card]

    def __str__(self) -> str:
        return f"{self.rank.name} - {', '.join(str(card) for card in self.cards)}"

class HandEvaluator:
    def __init__(self):
        self.rank_values = {rank: idx for idx, rank in enumerate(Rank)}
        self.rank_values[Rank.ACE] = 14  # Ace high

    def evaluate_hand(self, cards: List[Card]) -> Hand:
        """Evaluate the best possible hand from the given cards."""
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate a hand")

        # Try each hand rank from highest to lowest
        evaluators = [
            self._evaluate_royal_flush,
            self._evaluate_straight_flush,
            self._evaluate_four_of_a_kind,
            self._evaluate_full_house,
            self._evaluate_flush,
            self._evaluate_straight,
            self._evaluate_three_of_a_kind,
            self._evaluate_two_pair,
            self._evaluate_pair,
            self._evaluate_high_card
        ]

        for evaluator in evaluators:
            result = evaluator(cards)
            if result:
                return result

        # If no hand is found, return high card
        return self._evaluate_high_card(cards)

    def _evaluate_royal_flush(self, cards: List[Card]) -> Hand:
        """Evaluate for Royal Flush."""
        straight_flush = self._evaluate_straight_flush(cards)
        if straight_flush and straight_flush.cards[0].rank == Rank.ACE:
            return Hand(straight_flush.cards, HandRank.ROYAL_FLUSH, [])
        return None

    def _evaluate_straight_flush(self, cards: List[Card]) -> Hand:
        """Evaluate for Straight Flush."""
        flush = self._evaluate_flush(cards)
        if flush:
            straight = self._evaluate_straight(flush.cards)
            if straight:
                return Hand(straight.cards, HandRank.STRAIGHT_FLUSH, [])
        return None

    def _evaluate_four_of_a_kind(self, cards: List[Card]) -> Hand:
        """Evaluate for Four of a Kind."""
        rank_groups = self._group_by_rank(cards)
        for rank, group in rank_groups.items():
            if len(group) >= 4:
                four_cards = sorted(group, key=lambda c: self.rank_values[c.rank], reverse=True)[:4]
                kickers = sorted([c for c in cards if c not in four_cards],
                               key=lambda c: self.rank_values[c.rank], reverse=True)[:1]
                return Hand(four_cards, HandRank.FOUR_OF_A_KIND, kickers)
        return None

    def _evaluate_full_house(self, cards: List[Card]) -> Hand:
        """Evaluate for Full House."""
        three_of_a_kind = self._evaluate_three_of_a_kind(cards)
        if three_of_a_kind:
            remaining_cards = [c for c in cards if c not in three_of_a_kind.cards]
            pair = self._evaluate_pair(remaining_cards)
            if pair:
                return Hand(three_of_a_kind.cards + pair.cards, HandRank.FULL_HOUSE, [])
        return None

    def _evaluate_flush(self, cards: List[Card]) -> Hand:
        """Evaluate for Flush."""
        suit_groups = self._group_by_suit(cards)
        for suit, group in suit_groups.items():
            if len(group) >= 5:
                flush_cards = sorted(group, key=lambda c: self.rank_values[c.rank], reverse=True)[:5]
                return Hand(flush_cards, HandRank.FLUSH, [])
        return None

    def _evaluate_straight(self, cards: List[Card]) -> Hand:
        """Evaluate for Straight."""
        # Handle Ace-low straight (A-2-3-4-5)
        ranks = sorted(set(self.rank_values[c.rank] for c in cards), reverse=True)
        if 14 in ranks:  # Ace
            ranks.append(1)

        for i in range(len(ranks) - 4):
            if ranks[i] - ranks[i + 4] == 4:
                straight_cards = []
                for rank_value in range(ranks[i], ranks[i + 4] - 1, -1):
                    for card in cards:
                        if self.rank_values[card.rank] == rank_value:
                            straight_cards.append(card)
                            break
                return Hand(straight_cards, HandRank.STRAIGHT, [])
        return None

    def _evaluate_three_of_a_kind(self, cards: List[Card]) -> Hand:
        """Evaluate for Three of a Kind."""
        rank_groups = self._group_by_rank(cards)
        for rank, group in rank_groups.items():
            if len(group) >= 3:
                three_cards = sorted(group, key=lambda c: self.rank_values[c.rank], reverse=True)[:3]
                kickers = sorted([c for c in cards if c not in three_cards],
                               key=lambda c: self.rank_values[c.rank], reverse=True)[:2]
                return Hand(three_cards, HandRank.THREE_OF_A_KIND, kickers)
        return None

    def _evaluate_two_pair(self, cards: List[Card]) -> Hand:
        """Evaluate for Two Pair."""
        rank_groups = self._group_by_rank(cards)
        pairs = []
        for rank, group in rank_groups.items():
            if len(group) >= 2:
                pairs.append(sorted(group, key=lambda c: self.rank_values[c.rank], reverse=True)[:2])
        if len(pairs) >= 2:
            pairs.sort(key=lambda p: self.rank_values[p[0].rank], reverse=True)
            two_pair_cards = pairs[0] + pairs[1]
            kickers = sorted([c for c in cards if c not in two_pair_cards],
                           key=lambda c: self.rank_values[c.rank], reverse=True)[:1]
            return Hand(two_pair_cards, HandRank.TWO_PAIR, kickers)
        return None

    def _evaluate_pair(self, cards: List[Card]) -> Hand:
        """Evaluate for Pair."""
        rank_groups = self._group_by_rank(cards)
        for rank, group in rank_groups.items():
            if len(group) >= 2:
                pair_cards = sorted(group, key=lambda c: self.rank_values[c.rank], reverse=True)[:2]
                kickers = sorted([c for c in cards if c not in pair_cards],
                               key=lambda c: self.rank_values[c.rank], reverse=True)[:3]
                return Hand(pair_cards, HandRank.PAIR, kickers)
        return None

    def _evaluate_high_card(self, cards: List[Card]) -> Hand:
        """Evaluate for High Card."""
        high_cards = sorted(cards, key=lambda c: self.rank_values[c.rank], reverse=True)[:5]
        return Hand(high_cards, HandRank.HIGH_CARD, [])

    def _group_by_rank(self, cards: List[Card]) -> Dict[Rank, List[Card]]:
        """Group cards by rank."""
        groups = {}
        for card in cards:
            if card.rank not in groups:
                groups[card.rank] = []
            groups[card.rank].append(card)
        return groups

    def _group_by_suit(self, cards: List[Card]) -> Dict[Suit, List[Card]]:
        """Group cards by suit."""
        groups = {}
        for card in cards:
            if card.suit not in groups:
                groups[card.suit] = []
            groups[card.suit].append(card)
        return groups

    def compare_hands(self, hand1: Hand, hand2: Hand) -> int:
        """Compare two hands and return 1 if hand1 wins, -1 if hand2 wins, 0 if tie."""
        if hand1.rank.value != hand2.rank.value:
            return 1 if hand1.rank.value > hand2.rank.value else -1

        # Compare main cards
        for c1, c2 in zip(hand1.cards, hand2.cards):
            if self.rank_values[c1.rank] != self.rank_values[c2.rank]:
                return 1 if self.rank_values[c1.rank] > self.rank_values[c2.rank] else -1

        # Compare kickers
        for k1, k2 in zip(hand1.kickers, hand2.kickers):
            if self.rank_values[k1.rank] != self.rank_values[k2.rank]:
                return 1 if self.rank_values[k1.rank] > self.rank_values[k2.rank] else -1

        return 0  # Tie 