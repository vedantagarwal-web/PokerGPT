from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import os
from .poker import Hand, Board
from enum import Enum
from .hand_evaluator import Card, Hand, HandEvaluator, HandRank
import random

@dataclass
class GameState:
    hand: Tuple[str, str]
    position: str
    opponents: List[str]
    action_history: List[Tuple[str, str, Optional[float]]]
    effective_stack: int
    board: List[str]
    tournament: bool

class Position(Enum):
    UTG = "UTG"  # Under the Gun
    MP = "MP"    # Middle Position
    CO = "CO"    # Cut Off
    BTN = "BTN"  # Button
    SB = "SB"    # Small Blind
    BB = "BB"    # Big Blind

class Action(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all-in"

@dataclass
class GTOAction:
    action: Action
    size: float = 0.0  # For raise sizes
    frequency: float = 1.0  # Probability of taking this action

@dataclass
class GTOAdvice:
    actions: List[GTOAction]
    explanation: str
    equity: float
    ev: float  # Expected value

class GtoSolver:
    def __init__(self, solutions_path: str):
        """Initialize GTO solver with a path to the solutions database."""
        self.solutions_path = solutions_path
        self.solutions = self._load_solutions()
        self.hand_evaluator = HandEvaluator()
        self.preflop_ranges = self._load_preflop_ranges()
        self.postflop_strategies = self._load_postflop_strategies()
    
    def _load_solutions(self) -> Dict:
        """Load GTO solutions from database."""
        if not os.path.exists(self.solutions_path):
            return {}
        
        with open(self.solutions_path, 'r') as f:
            return json.load(f)
    
    def _save_solutions(self) -> None:
        """Save GTO solutions to database."""
        with open(self.solutions_path, 'w') as f:
            json.dump(self.solutions, f)
    
    def _get_solution_key(self, game_state: GameState) -> str:
        """Generate a key for looking up solutions."""
        hand = "".join(game_state.hand)
        board = "".join(game_state.board) if game_state.board else ""
        position = game_state.position
        return f"{position}_{hand}_{board}"
    
    def get_action(self, game_state: GameState) -> Tuple[str, float, float]:
        """
        Get optimal action for the current game state.
        
        Returns:
            Tuple of (action, frequency, expected_value)
        """
        solution_key = self._get_solution_key(game_state)
        
        if solution_key in self.solutions:
            solution = self.solutions[solution_key]
            return solution['action'], solution['frequency'], solution['ev']
        
        # If no solution exists, calculate one
        action, frequency, ev = self._calculate_solution(game_state)
        
        # Cache the solution
        self.solutions[solution_key] = {
            'action': action,
            'frequency': frequency,
            'ev': ev
        }
        self._save_solutions()
        
        return action, frequency, ev
    
    def _calculate_solution(self, game_state: GameState) -> Tuple[str, float, float]:
        """Calculate optimal action for a game state."""
        # This is a simplified version. In a real implementation,
        # you would want to use a proper GTO solver that considers:
        # - Hand strength
        # - Position
        # - Stack depth
        # - Opponent tendencies
        # - Tournament vs cash game
        # - Action history
        # - Board texture
        
        # For now, return some reasonable defaults
        if not game_state.board:  # Preflop
            if game_state.position in ['BTN', 'CO']:
                return 'raise', 1.0, 0.85
            elif game_state.position in ['BB', 'SB']:
                return 'raise', 1.0, 0.95
            else:
                return 'raise', 0.8, 0.65
        else:  # Postflop
            if game_state.position in ['BTN', 'CO']:
                return 'bet', 0.8, 0.95
            elif game_state.position in ['BB', 'SB']:
                return 'bet', 0.9, 1.05
            else:
                return 'bet', 0.6, 0.75
    
    def get_range(self, position: str, stack_depth: int) -> Dict[str, float]:
        """Get optimal preflop range for a position and stack depth."""
        # This is a simplified version. In a real implementation,
        # you would want to use a proper range solver that considers:
        # - Position
        # - Stack depth
        # - Tournament vs cash game
        # - Opponent tendencies
        
        ranges = {
            'UTG': {
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0,
                'JJ': 0.9, 'TT': 0.8, '99': 0.7,
                'AKs': 1.0, 'AKo': 1.0,
                'AQs': 0.9, 'AQo': 0.8
            },
            'MP': {
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0,
                'JJ': 1.0, 'TT': 0.9, '99': 0.8,
                '88': 0.7, '77': 0.6,
                'AKs': 1.0, 'AKo': 1.0,
                'AQs': 1.0, 'AQo': 0.9,
                'AJs': 0.8, 'AJo': 0.7
            },
            'CO': {
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0,
                'JJ': 1.0, 'TT': 1.0, '99': 0.9,
                '88': 0.8, '77': 0.7, '66': 0.6,
                'AKs': 1.0, 'AKo': 1.0,
                'AQs': 1.0, 'AQo': 1.0,
                'AJs': 0.9, 'AJo': 0.8,
                'ATs': 0.7, 'ATo': 0.6
            },
            'BTN': {
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0,
                'JJ': 1.0, 'TT': 1.0, '99': 1.0,
                '88': 0.9, '77': 0.8, '66': 0.7,
                '55': 0.6, '44': 0.5,
                'AKs': 1.0, 'AKo': 1.0,
                'AQs': 1.0, 'AQo': 1.0,
                'AJs': 1.0, 'AJo': 0.9,
                'ATs': 0.8, 'ATo': 0.7,
                'A9s': 0.6, 'A8s': 0.5
            }
        }
        
        return ranges.get(position, {})

    def get_advice(self, 
                  position: str,
                  hand: List[Card],
                  community_cards: List[Card],
                  pot: float,
                  stack: float,
                  current_bet: float = 0) -> GTOAdvice:
        """Get GTO-based advice for the current situation."""
        if not community_cards:  # Preflop
            return self._get_preflop_advice(position, hand, stack, current_bet)
        else:  # Postflop
            return self._get_postflop_advice(position, hand, community_cards, pot, stack, current_bet)

    def _get_preflop_advice(self, 
                          position: str,
                          hand: List[Card],
                          stack: float,
                          current_bet: float) -> GTOAdvice:
        """Get preflop GTO advice."""
        # Since we use a simplified implementation for the demo
        # we'll return some basic advice based on hand strength and position
        
        # Calculate hand strength (pair, high cards, etc.)
        pair = hand[0].rank == hand[1].rank
        suited = hand[0].suit == hand[1].suit
        high_cards = sum(1 for card in hand if card.rank.value in ['A', 'K', 'Q', 'J', '10'])
        
        # Define position strength (BTN is strongest, BB is weakest)
        position_strength = {
            'BTN': 3,
            'SB': 2,
            'BB': 1
        }.get(position, 2)  # Default to middle strength
        
        # Generate explanation
        explanation = ""
        actions = []
        ev = 0
        
        if pair:
            explanation = f"You have a strong pair. "
            if position in ['BTN', 'SB']:
                explanation += "In position, you should raise to establish dominance."
                actions = [
                    {"action": "raise", "size": max(current_bet * 3, 30), "frequency": 0.8},
                    {"action": "call", "size": current_bet, "frequency": 0.2}
                ]
                ev = 15.5
            else:
                explanation += "Out of position, you should still play aggressively but be more cautious."
                actions = [
                    {"action": "raise", "size": max(current_bet * 2.5, 25), "frequency": 0.7},
                    {"action": "call", "size": current_bet, "frequency": 0.3}
                ]
                ev = 12.0
        elif suited and high_cards >= 1:
            explanation = f"You have a suited hand with high cards. "
            if position == 'BTN':
                explanation += "From the button, this is a good raising hand."
                actions = [
                    {"action": "raise", "size": max(current_bet * 2.5, 25), "frequency": 0.6},
                    {"action": "call", "size": current_bet, "frequency": 0.3},
                    {"action": "fold", "size": 0, "frequency": 0.1}
                ]
                ev = 8.0
            else:
                explanation += "Play cautiously from this position."
                actions = [
                    {"action": "call", "size": current_bet, "frequency": 0.5},
                    {"action": "fold", "size": 0, "frequency": 0.5}
                ]
                ev = 3.0
        elif high_cards >= 2:
            explanation = f"You have high cards. "
            if position == 'BTN':
                explanation += "This is a good raising hand from the button."
                actions = [
                    {"action": "raise", "size": max(current_bet * 2.5, 25), "frequency": 0.7},
                    {"action": "call", "size": current_bet, "frequency": 0.3}
                ]
                ev = 7.0
            else:
                explanation += "Consider the pot odds before continuing."
                actions = [
                    {"action": "call", "size": current_bet, "frequency": 0.4},
                    {"action": "fold", "size": 0, "frequency": 0.6}
                ]
                ev = 2.0
        else:
            explanation = f"You have a weak hand. "
            if position == 'BTN':
                explanation += "You might consider raising as a bluff from the button."
                actions = [
                    {"action": "raise", "size": max(current_bet * 2, 20), "frequency": 0.3},
                    {"action": "fold", "size": 0, "frequency": 0.7}
                ]
                ev = -1.0
            else:
                explanation += "This is a clear fold from your position."
                actions = [
                    {"action": "fold", "size": 0, "frequency": 1.0}
                ]
                ev = -5.0
        
        return {
            'actions': actions,
            'explanation': explanation,
            'equity': 0.5,  # Simplified
            'ev': ev
        }
    
    def _get_postflop_advice(self,
                           position: str,
                           hand: List[Card],
                           community_cards: List[Card],
                           pot: float,
                           stack: float,
                           current_bet: float) -> GTOAdvice:
        """Get postflop GTO advice."""
        # Simplified implementation for the demo
        # We'll just generate some advice based on hand strength and position
        
        # Evaluate hand strength
        all_cards = hand + community_cards
        strength = self._evaluate_hand_strength(all_cards)
        
        # Define position advantage
        position_advantage = position in ['BTN', 'CO']
        
        # Board texture analysis (simplified)
        flush_possible = len(set(card.suit for card in community_cards)) <= 3
        straight_possible = self._is_straight_possible(community_cards)
        
        # Generate advice
        explanation = ""
        actions = []
        ev = 0
        
        if strength > 0.8:  # Very strong hand
            explanation = "You have a very strong hand. "
            if position_advantage:
                explanation += "In position, you can extract maximum value with a strong bet."
                actions = [
                    {"action": "raise", "size": pot * 0.8, "frequency": 0.8},
                    {"action": "call", "size": current_bet, "frequency": 0.2}
                ]
                ev = pot * 0.7
            else:
                explanation += "Out of position, bet to protect your hand and build the pot."
                actions = [
                    {"action": "raise", "size": pot * 0.7, "frequency": 0.7},
                    {"action": "call", "size": current_bet, "frequency": 0.3}
                ]
                ev = pot * 0.5
        elif strength > 0.6:  # Strong hand
            explanation = "You have a strong hand. "
            if flush_possible or straight_possible:
                explanation += "Be cautious of the draw possibilities. "
                if position_advantage:
                    explanation += "Bet to protect your hand."
                    actions = [
                        {"action": "raise", "size": pot * 0.6, "frequency": 0.6},
                        {"action": "call", "size": current_bet, "frequency": 0.4}
                    ]
                    ev = pot * 0.3
                else:
                    explanation += "Consider check-raising to protect your hand."
                    actions = [
                        {"action": "raise", "size": pot * 0.7, "frequency": 0.4},
                        {"action": "call", "size": current_bet, "frequency": 0.6}
                    ]
                    ev = pot * 0.2
            else:
                explanation += "The board is relatively safe. "
                if position_advantage:
                    explanation += "Bet for value."
                    actions = [
                        {"action": "raise", "size": pot * 0.5, "frequency": 0.7},
                        {"action": "call", "size": current_bet, "frequency": 0.3}
                    ]
                    ev = pot * 0.4
                else:
                    explanation += "Lead with a medium-sized bet."
                    actions = [
                        {"action": "raise", "size": pot * 0.6, "frequency": 0.5},
                        {"action": "call", "size": current_bet, "frequency": 0.5}
                    ]
                    ev = pot * 0.3
        elif strength > 0.4:  # Medium hand
            explanation = "You have a medium-strength hand. "
            if position_advantage:
                explanation += "In position, you can control the pot size."
                actions = [
                    {"action": "call", "size": current_bet, "frequency": 0.7},
                    {"action": "raise", "size": pot * 0.4, "frequency": 0.2},
                    {"action": "fold", "size": 0, "frequency": 0.1}
                ]
                ev = pot * 0.1
            else:
                explanation += "Out of position, be cautious with this holding."
                actions = [
                    {"action": "call", "size": current_bet, "frequency": 0.5},
                    {"action": "fold", "size": 0, "frequency": 0.5}
                ]
                ev = -current_bet * 0.1
        else:  # Weak hand
            explanation = "You have a weak hand. "
            if position_advantage:
                explanation += "Consider bluffing occasionally in position."
                actions = [
                    {"action": "raise", "size": pot * 0.5, "frequency": 0.2},
                    {"action": "call", "size": current_bet, "frequency": 0.3},
                    {"action": "fold", "size": 0, "frequency": 0.5}
                ]
                ev = -current_bet * 0.3
            else:
                explanation += "This is mostly a folding situation out of position."
                actions = [
                    {"action": "fold", "size": 0, "frequency": 0.8},
                    {"action": "call", "size": current_bet, "frequency": 0.2}
                ]
                ev = -current_bet * 0.5
        
        return {
            'actions': actions,
            'explanation': explanation,
            'equity': strength,
            'ev': ev
        }

    def _evaluate_hand_strength(self, cards: List[Card]) -> float:
        """Evaluate hand strength (0-1)."""
        if len(cards) < 5:
            # Preflop hand strength
            ranks = [self.hand_evaluator.rank_values[card.rank] for card in cards]
            suited = cards[0].suit == cards[1].suit
            connected = abs(ranks[0] - ranks[1]) <= 2
            
            if ranks[0] == ranks[1]:  # Pocket pair
                return 0.7 + (ranks[0] / 14) * 0.3
            elif suited and connected:  # Suited connectors
                return 0.5 + (max(ranks) / 14) * 0.3
            else:  # High cards
                return (max(ranks) / 14) * 0.5
        else:
            # Postflop hand strength
            hand = self.hand_evaluator.evaluate_hand(cards)
            return hand.rank.value / 10.0

    def _get_position_value(self, position: Position) -> float:
        """Get position value (0-1)."""
        position_values = {
            Position.UTG: 0.3,
            Position.MP: 0.5,
            Position.CO: 0.7,
            Position.BTN: 0.9,
            Position.SB: 0.8,
            Position.BB: 0.6
        }
        return position_values[position]

    def _load_preflop_ranges(self) -> Dict[Position, List[Tuple[str, float]]]:
        """Load preflop ranges for different positions."""
        # This would typically load from a file or database
        return {}

    def _load_postflop_strategies(self) -> Dict[str, List[Tuple[str, float]]]:
        """Load postflop strategies for different board textures."""
        # This would typically load from a file or database
        return {}

    def get_bot_action(self, position: str, pot: float, current_bet: float) -> dict:
        """Get action for a bot based on position and pot size."""
        # Simplified version for demo purposes
        actions = ['fold', 'check', 'call', 'raise']
        action = random.choice(actions)
        
        if action == 'fold':
            return {'action': 'fold', 'amount': 0}
        elif action == 'check' or action == 'call':
            return {'action': 'call', 'amount': current_bet}
        else:  # raise
            min_raise = max(current_bet * 2, 20)
            max_raise = min(current_bet * 4, 100)
            amount = random.randint(min_raise, max_raise)
            return {'action': 'raise', 'amount': amount}
    
    def calculate_equity(self, hand: List[Card], community_cards: List[Card]) -> float:
        """Calculate equity for a hand against random opponents."""
        # Simplified version for demo purposes
        # In a real implementation, you would run a Monte Carlo simulation
        
        if not hand or len(hand) < 2:
            return 0.0
        
        # Get hand strength (0-1 scale)
        strength = self._evaluate_hand_strength(hand + community_cards)
        
        # Add some randomness for demo
        equity = strength + random.uniform(-0.1, 0.1)
        
        # Keep within bounds
        return max(0.0, min(1.0, equity))
    
    def calculate_odds(self, hand: List[Card], community_cards: List[Card]) -> dict:
        """Calculate pot odds and outs for a hand."""
        # Simplified version for demo purposes
        
        # Calculate random number of outs (0-15)
        outs = random.randint(0, 15)
        
        # Calculate pot odds based on outs
        # Rule of thumb: pot odds = outs * 4% (turn and river) or outs * 2% (river only)
        if len(community_cards) <= 3:  # Preflop or flop
            pot_odds = outs * 4
        else:  # Turn
            pot_odds = outs * 2
        
        return {
            'pot_odds': pot_odds,
            'outs': outs
        }

    def _is_straight_possible(self, community_cards: List[Card]) -> bool:
        """Check if a straight is possible with the given community cards."""
        if len(community_cards) < 3:
            return False
        
        # Get numerical values of ranks
        rank_values = {
            Rank.TWO: 2,
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13,
            Rank.ACE: 14
        }
        
        # Get unique ranks, sorted
        ranks = sorted(set(rank_values[card.rank] for card in community_cards))
        
        # Check for consecutive cards or close enough for a straight draw
        for i in range(len(ranks) - 1):
            if ranks[i + 1] - ranks[i] <= 4:
                return True
                
        # Check for A-2-3-4-5 possibility
        if Rank.ACE in [card.rank for card in community_cards]:
            low_straight = [2, 3, 4, 5]
            for rank in low_straight:
                if rank in ranks:
                    return True
                    
        return False 