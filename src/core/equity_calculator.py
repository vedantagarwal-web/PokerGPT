from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import os
from .poker import Card, Deck, Hand, Board, create_deck

@dataclass
class EquityResult:
    equity: float
    hand_strength: float
    outs: List[Card]
    hand_type: str

class EquityCalculator:
    def __init__(self, cache_path: str):
        """Initialize equity calculator with a path to the equity cache."""
        self.cache_path = cache_path
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load equity calculations from cache."""
        if not os.path.exists(self.cache_path):
            return {}
        
        with open(self.cache_path, 'r') as f:
            return json.load(f)
    
    def _save_cache(self) -> None:
        """Save equity calculations to cache."""
        with open(self.cache_path, 'w') as f:
            json.dump(self.cache, f)
    
    def _get_cache_key(self, hand: Hand, opponent_range: Dict[str, float], 
                      board: Optional[Board] = None) -> str:
        """Generate a cache key for the current calculation."""
        hand_str = str(hand)
        range_str = json.dumps(opponent_range)
        board_str = str(board) if board else ""
        return f"{hand_str}:{range_str}:{board_str}"
    
    def calculate_equity(self, hand: Hand, opponent_range: Dict[str, float],
                        board: Optional[Board] = None) -> EquityResult:
        """Calculate equity against an opponent's range."""
        cache_key = self._get_cache_key(hand, opponent_range, board)
        
        if cache_key in self.cache:
            return EquityResult(**self.cache[cache_key])
        
        # Create a deck excluding known cards
        known_cards = hand.cards
        if board:
            known_cards.extend(board.cards)
        deck = create_deck(known_cards)
        
        # Run Monte Carlo simulation
        iterations = 10000
        wins = 0
        ties = 0
        total_strength = 0
        
        for _ in range(iterations):
            # Draw remaining board cards if needed
            current_board = board.cards if board else []
            if len(current_board) < 5:
                remaining_cards = deck.draw_multiple(5 - len(current_board))
                current_board.extend(remaining_cards)
            
            # Calculate hand strength
            hand_strength = self._calculate_hand_strength(hand.cards, current_board)
            total_strength += hand_strength
            
            # Compare against opponent's range
            opponent_hand = self._draw_opponent_hand(deck, opponent_range)
            if opponent_hand:
                opponent_strength = self._calculate_hand_strength(opponent_hand.cards, current_board)
                if hand_strength > opponent_strength:
                    wins += 1
                elif hand_strength == opponent_strength:
                    ties += 0.5
        
        # Calculate results
        equity = (wins + ties) / iterations
        avg_strength = total_strength / iterations
        outs = self._calculate_outs(hand.cards, current_board)
        hand_type = self._get_hand_type(hand.cards, current_board)
        
        result = EquityResult(
            equity=equity,
            hand_strength=avg_strength,
            outs=outs,
            hand_type=hand_type
        )
        
        # Cache the result
        self.cache[cache_key] = {
            'equity': equity,
            'hand_strength': avg_strength,
            'outs': [str(card) for card in outs],
            'hand_type': hand_type
        }
        self._save_cache()
        
        return result
    
    def _calculate_hand_strength(self, hand_cards: List[Card], 
                               board_cards: List[Card]) -> float:
        """Calculate the strength of a hand."""
        # This is a simplified version. In a real implementation,
        # you would want to use a proper hand evaluator that considers
        # all possible poker hand rankings.
        all_cards = hand_cards + board_cards
        return len(set(card.rank for card in all_cards)) / 13
    
    def _draw_opponent_hand(self, deck: Deck, 
                          opponent_range: Dict[str, float]) -> Optional[Hand]:
        """Draw a hand from the opponent's range."""
        # This is a simplified version. In a real implementation,
        # you would want to properly sample from the range based on
        # the frequencies provided.
        if not opponent_range:
            return None
        
        # For now, just draw two random cards
        cards = deck.draw_multiple(2)
        if len(cards) == 2:
            return Hand(cards)
        return None
    
    def _calculate_outs(self, hand_cards: List[Card], 
                       board_cards: List[Card]) -> List[Card]:
        """Calculate the number of outs for a hand."""
        # This is a simplified version. In a real implementation,
        # you would want to calculate actual outs based on the
        # current hand and board texture.
        return []
    
    def _get_hand_type(self, hand_cards: List[Card], 
                      board_cards: List[Card]) -> str:
        """Get the type of hand (e.g., 'pair', 'two pair', etc.)."""
        # This is a simplified version. In a real implementation,
        # you would want to properly evaluate the hand type.
        return "high card" 