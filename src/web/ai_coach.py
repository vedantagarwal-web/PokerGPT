from typing import Dict, List, Optional, Union
import json
import os
import random

class PokerCoach:
    def __init__(self):
        # Load poker knowledge base
        self.knowledge_base = self._load_knowledge_base()
        
        # Pre-defined coaching contexts
        self.contexts = {
            'preflop': 'Analyze preflop decision making based on position and hand strength',
            'flop': 'Analyze flop play including continuation betting and board texture',
            'turn': 'Evaluate turn play focusing on pot control and value betting',
            'river': 'Analyze river decision making including value betting and bluffing spots'
        }
        
        # Hand rankings and terminology
        self.hand_rankings = {
            'premium': ['AA', 'KK', 'QQ', 'AKs'],
            'strong': ['JJ', 'TT', 'AQs', 'AQo', 'AJs', 'KQs'],
            'playable': ['99', '88', 'ATs', 'KJs', 'QJs', 'AJo'],
            'speculative': ['77', '66', 'KTs', 'QTs', 'JTs', 'T9s', 'A9s']
        }
        
        # Position explanations
        self.position_explanations = {
            'UTG': 'Under the Gun (UTG) is the tightest position. Play only premium hands.',
            'MP': 'Middle Position (MP) allows for slightly wider play, but still tight.',
            'CO': 'Cutoff (CO) is a late position where you can play more hands due to positional advantage.',
            'BTN': 'Button (BTN) is the best position. You can play your widest range here.',
            'SB': 'Small Blind (SB) acts first postflop, requiring caution despite late position preflop.',
            'BB': 'Big Blind (BB) gets a discount to see the flop, allowing wider defense.'
        }

    def _load_knowledge_base(self) -> Dict:
        """Load poker knowledge base from file or create default if not found"""
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Path to knowledge base file
            knowledge_file = os.path.join(data_dir, 'poker_knowledge.json')
            
            # Check if file exists
            if os.path.exists(knowledge_file):
                with open(knowledge_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default knowledge base
                default_kb = self._create_default_knowledge_base()
                
                # Save default knowledge base
                with open(knowledge_file, 'w') as f:
                    json.dump(default_kb, f, indent=4)
                
                return default_kb
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return self._create_default_knowledge_base()
    
    def _create_default_knowledge_base(self) -> Dict:
        """Create a default knowledge base with basic poker concepts"""
        return {
            "concepts": {
                "position": {
                    "name": "Position",
                    "difficulty": "beginner",
                    "prerequisites": [],
                    "explanations": {
                        "beginner": "Position refers to where you are seated relative to the dealer button. Later positions (closer to the button) are more advantageous because you get to act after other players.",
                        "intermediate": "Position is crucial in poker. In later positions, you have more information about other players' actions and can make better decisions. This allows you to play more hands profitably.",
                        "advanced": "Positional advantage allows for more complex strategies like floating, check-raising, and value betting thinner. Understanding position-based ranges and frequencies is essential for GTO play."
                    }
                },
                "pot_odds": {
                    "name": "Pot Odds",
                    "difficulty": "beginner",
                    "prerequisites": ["position"],
                    "explanations": {
                        "beginner": "Pot odds are the ratio of the current pot size to the cost of calling. If the pot is $100 and it costs $20 to call, your pot odds are 5:1.",
                        "intermediate": "Pot odds help determine if a call is profitable. Compare your pot odds to your hand's equity to make mathematically correct decisions.",
                        "advanced": "Advanced players consider implied odds, reverse implied odds, and stack-to-pot ratios when making decisions based on pot odds."
                    }
                },
                "preflop_ranges": {
                    "name": "Preflop Ranges",
                    "difficulty": "intermediate",
                    "prerequisites": ["position", "pot_odds"],
                    "explanations": {
                        "beginner": "Different positions have different starting hand requirements. Early positions should play tighter ranges than late positions.",
                        "intermediate": "Understanding position-based ranges is crucial. The button can play wider ranges than UTG because of positional advantage.",
                        "advanced": "GTO preflop ranges are carefully balanced between value hands and bluffs, with specific frequencies for each action."
                    }
                },
                "board_texture": {
                    "name": "Board Texture",
                    "difficulty": "intermediate",
                    "prerequisites": ["preflop_ranges"],
                    "explanations": {
                        "beginner": "Board texture refers to how the community cards interact with each other. Wet boards have many straight and flush possibilities, while dry boards don't.",
                        "intermediate": "Understanding how a board hits different ranges helps with betting strategy. Boards that favor your range are good for continuation betting.",
                        "advanced": "GTO players adapt their strategies to different board textures, considering range advantage, nuts advantage, and removal effects."
                    }
                },
                "hand_reading": {
                    "name": "Hand Reading",
                    "difficulty": "advanced",
                    "prerequisites": ["board_texture", "preflop_ranges"],
                    "explanations": {
                        "beginner": "Hand reading is the process of narrowing down your opponent's possible holdings based on their actions.",
                        "intermediate": "Effective hand reading involves considering preflop action, position, and how they play different streets.",
                        "advanced": "Advanced hand reading requires understanding player tendencies, bet sizing tells, and the entire action sequence across all streets."
                    }
                }
            },
            "learning_paths": {
                "beginner": ["position", "pot_odds"],
                "intermediate": ["position", "pot_odds", "preflop_ranges", "board_texture"],
                "advanced": ["position", "pot_odds", "preflop_ranges", "board_texture", "hand_reading"]
            },
            "preflop_charts": {
                "UTG": {
                    "raise": ["AA", "KK", "QQ", "JJ", "TT", "99", "AKs", "AQs", "AJs", "ATs", "KQs", "KJs", "AKo", "AQo"],
                    "call": [],
                    "fold": "everything else"
                },
                "MP": {
                    "raise": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "AKs", "AQs", "AJs", "ATs", "A9s", "KQs", "KJs", "KTs", "QJs", "QTs", "JTs", "AKo", "AQo", "AJo", "KQo"],
                    "call": [],
                    "fold": "everything else"
                },
                "CO": {
                    "raise": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "KQs", "KJs", "KTs", "K9s", "QJs", "QTs", "Q9s", "JTs", "J9s", "T9s", "98s", "AKo", "AQo", "AJo", "ATo", "KQo", "KJo", "QJo"],
                    "call": [],
                    "fold": "everything else"
                },
                "BTN": {
                    "raise": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22", "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "QJs", "QTs", "Q9s", "Q8s", "JTs", "J9s", "J8s", "T9s", "T8s", "98s", "97s", "87s", "76s", "65s", "AKo", "AQo", "AJo", "ATo", "A9o", "KQo", "KJo", "KTo", "QJo", "QTo", "JTo"],
                    "call": [],
                    "fold": "everything else"
                },
                "SB": {
                    "raise": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "KQs", "KJs", "KTs", "K9s", "QJs", "QTs", "JTs", "AKo", "AQo", "AJo", "ATo", "KQo", "KJo"],
                    "call": [],
                    "fold": "everything else"
                },
                "BB": {
                    "raise": [],
                    "call": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22", "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s", "QJs", "QTs", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s", "JTs", "J9s", "J8s", "J7s", "J6s", "J5s", "T9s", "T8s", "T7s", "98s", "97s", "87s", "76s", "65s", "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o", "KQo", "KJo", "KTo", "K9o", "QJo", "QTo", "JTo"],
                    "fold": "everything else"
                }
            }
        }

    def get_advice(self, position: str, phase: str, pot: float, current_bet: float, 
                player_cards: List[Dict], community_cards: List[Dict], bets: Dict) -> str:
        """Generate strategic advice based on the current game state"""
        try:
            # Format hand and board for readability
            hand_str = self._format_cards(player_cards)
            board_str = self._format_cards(community_cards) if community_cards else ""
            
            # Generate appropriate advice based on game phase
            if phase == 'preflop':
                return self._get_preflop_advice(position, hand_str, pot, current_bet, bets)
            elif phase == 'flop':
                return self._get_flop_advice(position, hand_str, board_str, pot, current_bet, bets)
            elif phase == 'turn':
                return self._get_turn_advice(position, hand_str, board_str, pot, current_bet, bets)
            elif phase == 'river':
                return self._get_river_advice(position, hand_str, board_str, pot, current_bet, bets)
            else:
                return "I'm not sure what phase of the hand we're in. Could you clarify?"
                
        except Exception as e:
            # Provide a fallback response if anything fails
            print(f"Error generating advice: {e}")
            
            # Create a basic response based on the phase
            fallback_advice = {
                'preflop': "In preflop, consider your position and starting hand strength. Play tighter in early positions and looser in late positions.",
                'flop': "On the flop, evaluate how well your hand connects with the board. Consider continuation betting if you were the preflop aggressor.",
                'turn': "On the turn, re-evaluate your hand and look for potential draws. Think about pot odds and implied odds for drawing hands.",
                'river': "On the river, make your best value bet with strong hands and consider well-timed bluffs with missed draws."
            }
            
            return fallback_advice.get(phase, "Consider your hand strength and position when making decisions.")

    def _format_cards(self, cards: List[Dict]) -> str:
        """Format cards for display"""
        return " ".join([f"{card['rank']}{card['suit']}" for card in cards])
    
    def _get_hand_category(self, hand: str) -> str:
        """Determine hand category based on shorthand notation"""
        for category, hands in self.hand_rankings.items():
            if hand in hands:
                return category
        return "weak"
    
    def _get_preflop_advice(self, position: str, hand: str, pot: float, current_bet: float, bets: Dict) -> str:
        """Generate preflop advice"""
        # Parse hand to shorthand notation
        cards = hand.split()
        rank1 = cards[0][0]
        rank2 = cards[1][0]
        suited = cards[0][1] == cards[1][1]
        
        # Convert 10 to T for notation
        if rank1 == '1': rank1 = 'T'
        if rank2 == '1': rank2 = 'T'
        
        # Format hand in standard notation
        if rank1 == rank2:
            hand_notation = f"{rank1}{rank1}"  # Pair
        else:
            # Check which rank is higher
            ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
            if ranks.index(rank1) < ranks.index(rank2):
                hand_notation = f"{rank1}{rank2}"
            else:
                hand_notation = f"{rank2}{rank1}"
                
            # Add suited or offsuit designation
            if suited:
                hand_notation += "s"
            else:
                hand_notation += "o"
        
        # Check preflop chart
        chart = self.knowledge_base["preflop_charts"].get(position, self.knowledge_base["preflop_charts"]["MP"])
        
        if hand_notation in chart["raise"]:
            action = "raise"
            explanation = f"{hand_notation} is a raising hand from {position}. Consider raising to 2.5-3BB."
        elif hand_notation in chart["call"]:
            action = "call"
            explanation = f"{hand_notation} is a calling hand from {position}. Call the current bet if reasonable."
        else:
            action = "fold"
            explanation = f"{hand_notation} is generally a folding hand from {position} according to standard charts."
        
        # Add position context
        position_context = self.position_explanations.get(position, "")
        
        # Add pot odds if facing a bet
        pot_odds_context = ""
        call_amount = current_bet - bets.get(position, 0)
        if call_amount > 0:
            pot_odds = call_amount / (pot + call_amount)
            pot_odds_context = f"\n\nYou need to call {call_amount} BB into a {pot} BB pot, giving you pot odds of {pot_odds:.0%}."
        
        return f"Preflop with {hand} in {position}:\n\nRecommended action: {action.upper()}\n\n{explanation}\n\n{position_context}{pot_odds_context}"
    
    def _get_flop_advice(self, position: str, hand: str, board: str, pot: float, current_bet: float, bets: Dict) -> str:
        """Generate flop advice"""
        # Analyze board texture
        board_cards = board.split()
        is_paired = len(board_cards) >= 2 and any(board_cards[i][0] == board_cards[j][0] for i in range(len(board_cards)) for j in range(i+1, len(board_cards)))
        is_connected = len(board_cards) >= 2 and self._is_connected(board_cards)
        is_suited = len(board_cards) >= 2 and self._is_suited(board_cards)
        
        board_texture = "dry"
        if is_paired:
            board_texture = "paired"
        elif is_connected and is_suited:
            board_texture = "very wet"
        elif is_connected or is_suited:
            board_texture = "semi-wet"
        
        # Generate advice based on board texture
        advice = f"Flop: {board}\n\nThe board texture is {board_texture}. "
        
        if board_texture == "dry":
            advice += "This is a good board for continuation betting as it likely missed your opponent's range. Consider betting 50-60% of the pot with your entire range."
        elif board_texture == "paired":
            advice += "Paired boards are good for the player with more strong hands and overpairs in their range. Be cautious with marginal made hands."
        elif board_texture == "very wet":
            advice += "This is a very coordinated board with straight and flush possibilities. Be cautious with single pair hands and consider checking more frequently."
        else:  # semi-wet
            advice += "This board has some drawing possibilities. Balance your continuation betting range and consider betting smaller (around 33-50% pot)."
        
        # Add pot odds if facing a bet
        call_amount = current_bet - bets.get(position, 0)
        if call_amount > 0:
            pot_odds = call_amount / (pot + call_amount)
            advice += f"\n\nYou're facing a bet of {current_bet} BB. You need to call {call_amount} BB into a {pot} BB pot, giving you pot odds of {pot_odds:.0%}. Consider if your hand has enough equity against villain's range to continue."
        
        return advice
    
    def _get_turn_advice(self, position: str, hand: str, board: str, pot: float, current_bet: float, bets: Dict) -> str:
        """Generate turn advice"""
        # By the turn, pot control becomes more important
        advice = f"Turn: {board}\n\nOn the turn, it's important to start planning your river strategy. "
        advice += "Strong made hands should usually bet for value, while draws need to consider if they're getting the right odds to continue."
        
        # Add pot odds if facing a bet
        call_amount = current_bet - bets.get(position, 0)
        if call_amount > 0:
            pot_odds = call_amount / (pot + call_amount)
            advice += f"\n\nYou're facing a bet of {current_bet} BB. You need to call {call_amount} BB into a {pot} BB pot, giving you pot odds of {pot_odds:.0%}. Your hand needs at least {pot_odds:.0%} equity to make a profitable call."
        
        return advice
    
    def _get_river_advice(self, position: str, hand: str, board: str, pot: float, current_bet: float, bets: Dict) -> str:
        """Generate river advice"""
        # On the river, it's all about value betting and bluffing
        advice = f"River: {board}\n\nOn the river, your hand has reached its final value. "
        advice += "With strong hands, you should be value betting. With missed draws or weak hands, consider whether a bluff would be profitable."
        
        # Add pot odds if facing a bet
        call_amount = current_bet - bets.get(position, 0)
        if call_amount > 0:
            pot_odds = call_amount / (pot + call_amount)
            advice += f"\n\nYou're facing a bet of {current_bet} BB. You need to call {call_amount} BB into a {pot} BB pot, giving you pot odds of {pot_odds:.0%}. Since this is the river, your equity is either 0% or 100% - you either have the best hand or you don't. Consider if your hand is likely to be best against villain's betting range."
        
        return advice
    
    def _is_connected(self, cards: List[str]) -> bool:
        """Check if cards are connected (potential straight draws)"""
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        card_ranks = [c[0] for c in cards]
        # Convert 10 to T if needed
        card_ranks = ['T' if r == '1' else r for r in card_ranks]
        
        # Get rank indices
        rank_indices = [ranks.index(r) for r in card_ranks if r in ranks]
        rank_indices.sort()
        
        # Check for at most 2 gaps in consecutive cards
        for i in range(len(rank_indices) - 1):
            if rank_indices[i+1] - rank_indices[i] <= 3:
                return True
        return False
    
    def _is_suited(self, cards: List[str]) -> bool:
        """Check if cards are suited (potential flush draws)"""
        suits = [c[-1] for c in cards]
        return len(set(suits)) < len(suits)
    
    def get_learning_path(self, skill_level: str) -> list:
        """Get list of concept IDs for a given skill level"""
        # Ensure valid skill level
        if skill_level not in self.knowledge_base['learning_paths']:
            # Default to beginner if skill level not found
            skill_level = 'beginner'
        
        return self.knowledge_base['learning_paths'][skill_level]
    
    def get_concept_explanation(self, concept_id: str, detail_level: str = 'beginner') -> str:
        """Get explanation for a specific concept"""
        if concept_id in self.knowledge_base['concepts']:
            concept = self.knowledge_base['concepts'][concept_id]
            return {
                'name': concept['name'],
                'difficulty': concept['difficulty'],
                'explanation': concept['explanations'].get(detail_level, concept['explanations']['beginner'])
            }
        return {'name': 'Unknown Concept', 'difficulty': 'beginner', 'explanation': 'Concept not found.'}
    
    def get_coaching_advice(self, game_state: Dict, question: str, context: str = 'general', skill_level: str = 'intermediate') -> str:
        """
        Get personalized coaching advice based on the current game state and question.
        Simplified version that returns pre-written advice based on the context.
        """
        # Get basic advice based on context
        basic_advice = {
            'preflop': "Focus on position and hand strength. Play tighter ranges from early positions and wider from later positions.",
            'flop': "Evaluate how the board connects with your hand and your range. C-bet on boards that favor your range.",
            'turn': "On the turn, pot control becomes important. Value bet your strong hands and consider pot odds for draws.",
            'river': "On the river, polarize your range - value bet with strong hands and bluff with missed draws or blockers.",
            'general': "The most fundamental concepts in poker are position, pot odds, and hand selection. Master these first."
        }
        
        # Enhance advice based on skill level
        if skill_level == 'beginner':
            return f"Beginner advice: {basic_advice.get(context, basic_advice['general'])} Start by focusing on playing tight and learning hand values."
        elif skill_level == 'advanced':
            return f"Advanced advice: {basic_advice.get(context, basic_advice['general'])} Consider range vs range analysis and look for spots where your opponents are making mistakes."
        else:  # intermediate
            return f"Intermediate advice: {basic_advice.get(context, basic_advice['general'])} Balance your ranges and pay attention to player tendencies to exploit them."
    
    def analyze_hand_history(self, hand_history: List[Dict], focus_area: Optional[str] = None) -> str:
        """
        Simplified hand history analysis that returns pre-written advice.
        """
        focus_areas = {
            'preflop': "Your preflop strategy should focus on playing position-appropriate ranges. Avoid calling too much - either raise or fold most hands.",
            'bet_sizing': "Bet sizing should vary based on board texture and your range advantage. Use smaller bets (30-40%) on wet boards and larger bets (60-75%) on dry boards.",
            'hand_reading': "Hand reading requires tracking the full hand history and understanding what hands your opponent would play this way. Consider their range at each decision point.",
            'bluffing': "Effective bluffing requires identifying good bluff spots: having blockers, on boards that favor your range, against opponents who can fold, and with appropriate bet sizing.",
            None: "Overall, focus on playing solid fundamental poker. Identify leaks in your game and work on one aspect at a time."
        }
        
        return focus_areas.get(focus_area, focus_areas[None]) 