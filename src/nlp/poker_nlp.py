from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import os
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from enum import Enum

class ActionType(Enum):
    FOLD = "fold"
    CALL = "call"
    CHECK = "check"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"

@dataclass
class PokerSituation:
    hand: Tuple[str, str]
    position: str
    effective_stack: int
    board: List[str]
    action_history: List[Tuple[str, str, Optional[float]]]
    tournament: bool
    blinds: Tuple[float, float]
    pot_size: float
    opponent_count: int

class PokerNLP:
    """Natural Language Processing module for poker-related tasks."""
    
    def __init__(self, model_path: str):
        """Initialize the NLP module.
        
        Args:
            model_path: Path to the directory containing the model files.
        """
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained model and tokenizer."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to a basic implementation
            self.tokenizer = None
            self.model = None
    
    def describe_action(self, hand: str, board: str, action: str, position: str) -> str:
        """Generate a natural language description of a poker action.
        
        Args:
            hand: The player's hand (e.g., "Ah Kd")
            board: The community cards (e.g., "2h 3h 4h")
            action: The action taken (e.g., "raise", "call", "fold")
            position: The player's position (e.g., "BTN", "BB", "UTG")
            
        Returns:
            A natural language description of the action.
        """
        if self.model and self.tokenizer:
            # Use the model to generate a description
            inputs = self.tokenizer(
                f"Hand: {hand} Board: {board} Action: {action} Position: {position}",
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            outputs = self.model.generate(**inputs, max_length=100)
            description = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        else:
            # Fallback to template-based generation
            description = (
                f"With {hand} in {position} position, "
                f"facing a {board} board, "
                f"the optimal play is to {action}."
            )
        
        return description
    
    def parse_hand_description(self, description: str) -> Dict:
        """Parse a natural language hand description into structured data.
        
        Args:
            description: A natural language description of a poker hand.
            
        Returns:
            A dictionary containing the parsed information.
        """
        if self.model and self.tokenizer:
            # Use the model to parse the description
            inputs = self.tokenizer(
                description,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            outputs = self.model(**inputs)
            parsed = self._process_model_outputs(outputs)
        else:
            # Fallback to basic parsing
            parsed = self._basic_parse(description)
        
        return parsed
    
    def _process_model_outputs(self, outputs) -> Dict:
        """Process the model outputs into structured data.
        
        Args:
            outputs: The outputs from the model.
            
        Returns:
            A dictionary containing the processed information.
        """
        # This is a placeholder for actual model output processing
        # In a real implementation, you would process the model's outputs
        # to extract relevant information about the hand
        return {
            'hand': None,
            'board': None,
            'position': None,
            'action': None,
            'stack_size': None,
            'opponents': None
        }
    
    def _basic_parse(self, description: str) -> Dict:
        """Basic parsing of hand descriptions using string manipulation.
        
        Args:
            description: A natural language description of a poker hand.
            
        Returns:
            A dictionary containing the parsed information.
        """
        # This is a simple implementation that looks for common patterns
        # In a real application, you would want more robust parsing
        parsed = {
            'hand': None,
            'board': None,
            'position': None,
            'action': None,
            'stack_size': None,
            'opponents': None
        }
        
        # Look for position
        positions = ['UTG', 'MP', 'CO', 'BTN', 'SB', 'BB']
        for pos in positions:
            if pos in description:
                parsed['position'] = pos
                break
        
        # Look for stack size
        import re
        stack_match = re.search(r'(\d+)\s*BB', description)
        if stack_match:
            parsed['stack_size'] = int(stack_match.group(1))
        
        # Look for number of opponents
        opp_match = re.search(r'(\d+)\s*opponents?', description)
        if opp_match:
            parsed['opponents'] = int(opp_match.group(1))
        
        return parsed
    
    def generate_explanation(self, concept: str, difficulty: str = 'intermediate') -> str:
        """Generate an explanation of a poker concept.
        
        Args:
            concept: The concept to explain (e.g., "3-betting", "floating")
            difficulty: The desired difficulty level ('beginner', 'intermediate', 'advanced')
            
        Returns:
            A natural language explanation of the concept.
        """
        if self.model and self.tokenizer:
            # Use the model to generate an explanation
            inputs = self.tokenizer(
                f"Concept: {concept} Difficulty: {difficulty}",
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            outputs = self.model.generate(**inputs, max_length=200)
            explanation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        else:
            # Fallback to template-based generation
            explanation = (
                f"Here's a {difficulty}-level explanation of {concept}: "
                f"This is a placeholder explanation. "
                f"In a real implementation, you would have detailed explanations "
                f"for each concept at different difficulty levels."
            )
        
        return explanation
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from poker-related text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            A list of relevant keywords.
        """
        if self.model and self.tokenizer:
            # Use the model to extract keywords
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            outputs = self.model(**inputs)
            keywords = self._process_keywords(outputs)
        else:
            # Fallback to basic keyword extraction
            keywords = self._basic_keyword_extraction(text)
        
        return keywords
    
    def _process_keywords(self, outputs) -> List[str]:
        """Process the model outputs to extract keywords.
        
        Args:
            outputs: The outputs from the model.
            
        Returns:
            A list of keywords.
        """
        # This is a placeholder for actual keyword extraction
        # In a real implementation, you would process the model's outputs
        # to extract relevant keywords
        return []
    
    def _basic_keyword_extraction(self, text: str) -> List[str]:
        """Basic keyword extraction using string manipulation.
        
        Args:
            text: The text to analyze.
            
        Returns:
            A list of keywords.
        """
        # This is a simple implementation that looks for common poker terms
        # In a real application, you would want more sophisticated keyword extraction
        common_terms = {
            'actions': ['raise', 'call', 'fold', 'check', 'bet'],
            'positions': ['UTG', 'MP', 'CO', 'BTN', 'SB', 'BB'],
            'concepts': ['3-bet', '4-bet', 'float', 'c-bet', 'donk bet'],
            'hand_types': ['pair', 'two pair', 'three of a kind', 'straight', 'flush', 'full house']
        }
        
        keywords = []
        text = text.lower()
        
        for category in common_terms.values():
            for term in category:
                if term.lower() in text:
                    keywords.append(term)
        
        return keywords
    
    def parse_situation(self, query: str) -> PokerSituation:
        """Parse a natural language query into a structured poker situation."""
        # Extract hand
        hand_match = re.search(self.patterns['hand_pattern'], query)
        if not hand_match:
            raise ValueError("Could not find hand in query")
        hand = (hand_match.group('card1'), hand_match.group('card2'))
        
        # Extract position
        position_match = re.search(self.patterns['position_pattern'], query)
        if not position_match:
            raise ValueError("Could not find position in query")
        position = self.vocabulary['positions'][position_match.group('position')]
        
        # Extract stack size
        stack_match = re.search(self.patterns['stack_pattern'], query)
        if not stack_match:
            raise ValueError("Could not find stack size in query")
        effective_stack = int(stack_match.group('size'))
        
        # Extract board
        board_match = re.search(self.patterns['board_pattern'], query)
        board = []
        if board_match:
            board = [
                board_match.group('flop1'),
                board_match.group('flop2'),
                board_match.group('flop3')
            ]
        
        # Extract action history
        action_history = []
        for match in re.finditer(self.patterns['action_sequence_pattern'], query):
            action_history.append((
                match.group('player'),
                match.group('action'),
                float(match.group('size')) if match.group('size') else None
            ))
        
        # Extract tournament info
        tournament = bool(re.search(r'tournament', query.lower()))
        
        # Extract blinds
        blinds_match = re.search(self.patterns['blinds_pattern'], query)
        if not blinds_match:
            raise ValueError("Could not find blinds in query")
        blinds = (
            float(blinds_match.group('small')),
            float(blinds_match.group('big'))
        )
        
        # Extract pot size
        pot_match = re.search(self.patterns['pot_size_pattern'], query)
        pot_size = float(pot_match.group('size')) if pot_match else 0.0
        
        # Extract opponent count
        opponent_match = re.search(self.patterns['player_count_pattern'], query)
        opponent_count = int(opponent_match.group('count')) if opponent_match else 9
        
        return PokerSituation(
            hand=hand,
            position=position,
            effective_stack=effective_stack,
            board=board,
            action_history=action_history,
            tournament=tournament,
            blinds=blinds,
            pot_size=pot_size,
            opponent_count=opponent_count
        )
    
    def extract_action(self, text: str) -> Tuple[ActionType, Optional[float]]:
        """Extract action and size from text."""
        match = re.search(self.patterns['bet_pattern'], text)
        if not match:
            return ActionType.FOLD, None
        
        action = match.group('action')
        size = float(match.group('size')) if match.group('size') else None
        
        if action == 'all in':
            return ActionType.ALL_IN, None
        elif action == 'raise':
            return ActionType.RAISE, size
        elif action == 'bet':
            return ActionType.BET, size
        elif action == 'call':
            return ActionType.CALL, size
        elif action == 'check':
            return ActionType.CHECK, None
        else:
            return ActionType.FOLD, None
    
    def extract_position(self, text: str) -> str:
        """Extract position from text."""
        match = re.search(self.patterns['position_pattern'], text)
        if not match:
            raise ValueError("Could not find position in text")
        return self.vocabulary['positions'][match.group('position')]
    
    def extract_hand_type(self, text: str) -> str:
        """Extract hand type from text."""
        match = re.search(self.patterns['hand_type_pattern'], text)
        if not match:
            return "high card"
        return match.group('type')
    
    def extract_board_texture(self, text: str) -> str:
        """Extract board texture from text."""
        match = re.search(self.patterns['board_texture_pattern'], text)
        if not match:
            return "neutral"
        return match.group('texture')
    
    def extract_stack_size(self, text: str) -> str:
        """Extract stack size description from text."""
        match = re.search(self.patterns['stack_size_pattern'], text)
        if not match:
            return "medium"
        return match.group('size')
    
    def generate_question(self, concept: str) -> str:
        """Generate a practice question about a concept."""
        # This is a simplified version. In a real implementation,
        # you would want to use a more sophisticated language model
        # to generate natural questions.
        
        return f"What is the optimal play for {concept}?"
    
    def generate_feedback(self, answer: str, correct_answer: str) -> str:
        """Generate feedback on a user's answer."""
        # This is a simplified version. In a real implementation,
        # you would want to use a more sophisticated language model
        # to generate natural feedback.
        
        return "That's correct!" if answer == correct_answer else "That's not quite right. Try again!" 