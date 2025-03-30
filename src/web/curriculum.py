from typing import Dict, List, Optional

class Curriculum:
    def __init__(self):
        self.paths = {
            'fundamentals': {
                'name': 'Poker Fundamentals',
                'level': 'beginner',
                'lessons': [
                    {
                        'title': 'Introduction to Poker',
                        'content': '''
                        # Introduction to Poker
                        
                        Poker is a family of card games that combines gambling, strategy, and skill. The game involves players wagering over which hand is best according to specific game rules.
                        
                        ## Key Concepts:
                        1. **The Goal**: Win money by either having the best hand or making other players fold
                        2. **Basic Flow**: Players are dealt cards and bet in rounds
                        3. **Decision Making**: Choose to bet, call, raise, or fold based on your hand strength
                        
                        ## Hand Rankings (from highest to lowest):
                        1. Royal Flush
                        2. Straight Flush
                        3. Four of a Kind
                        4. Full House
                        5. Flush
                        6. Straight
                        7. Three of a Kind
                        8. Two Pair
                        9. One Pair
                        10. High Card
                        
                        ## Common Variants:
                        - Texas Hold'em (most popular)
                        - Omaha
                        - Seven-card Stud
                        '''
                    },
                    {
                        'title': 'Position and Its Importance',
                        'content': '''
                        # Understanding Position in Poker
                        
                        Position is one of the most crucial concepts in poker. It refers to where you sit relative to the dealer button.
                        
                        ## Why Position Matters:
                        1. **Information Advantage**: Act after seeing what opponents do
                        2. **Control**: Better ability to control pot size
                        3. **Bluffing Opportunity**: More effective bluffs from late position
                        
                        ## Positions in 6-max:
                        1. **Button (BTN)**: Best position, acts last post-flop
                        2. **Cutoff (CO)**: Second-best position
                        3. **Middle Position (MP)**: Middle position
                        4. **Under the Gun (UTG)**: First to act
                        5. **Small Blind (SB)**: Forced bet, bad position
                        6. **Big Blind (BB)**: Forced bet, acts last pre-flop
                        
                        ## Strategic Implications:
                        - Play tighter from early positions
                        - Play more hands from late positions
                        - Use position to control pot size
                        '''
                    }
                ]
            },
            'basic_math': {
                'name': 'Basic Poker Math',
                'level': 'beginner',
                'lessons': [
                    {
                        'title': 'Pot Odds and Basic Probability',
                        'content': '''
                        # Pot Odds and Basic Probability
                        
                        Understanding poker math is crucial for making profitable decisions.
                        
                        ## Pot Odds:
                        - **Definition**: The ratio of the current pot size to the cost of a contemplated call
                        - **Formula**: (Pot Size) : (Call Amount)
                        - **Example**: If pot is $100 and call is $20, pot odds are 100:20 or 5:1
                        
                        ## Calculating Outs:
                        - **Definition**: Cards that will improve your hand
                        - **Rule of 2 and 4**:
                          - On the flop: Multiply outs by 4 for two cards
                          - On the turn: Multiply outs by 2 for one card
                        
                        ## Common Scenarios:
                        1. Flush Draw: 9 outs (19% on turn, 35% on flop)
                        2. Open-Ended Straight Draw: 8 outs (17% on turn, 32% on flop)
                        3. Pair to Set: 2 outs (4% on turn, 8% on flop)
                        '''
                    }
                ]
            },
            'hand_reading': {
                'name': 'Hand Reading',
                'level': 'intermediate',
                'lessons': [
                    {
                        'title': 'Introduction to Hand Reading',
                        'content': '''
                        # Hand Reading in Poker
                        
                        Hand reading is the art of deducing your opponent's possible holdings based on their actions.
                        
                        ## Key Concepts:
                        1. **Range-Based Thinking**: Think in terms of hand ranges, not specific hands
                        2. **Action-Based Narrowing**: Use opponent's actions to narrow their range
                        3. **Position-Based Ranges**: Consider position when assigning ranges
                        
                        ## Hand Reading Process:
                        1. **Pre-flop Range**: Based on position and action
                        2. **Flop Actions**: Narrow range based on board and betting
                        3. **Turn Play**: Further narrow based on action and board changes
                        4. **River Decisions**: Final range assessment
                        
                        ## Common Tells and Patterns:
                        - Bet sizing tells
                        - Timing tells
                        - Betting patterns
                        - Position-based tendencies
                        '''
                    }
                ]
            },
            'gto_basics': {
                'name': 'GTO Fundamentals',
                'level': 'advanced',
                'lessons': [
                    {
                        'title': 'Introduction to GTO',
                        'content': '''
                        # Game Theory Optimal (GTO) Poker
                        
                        GTO poker refers to a theoretically perfect strategy that cannot be exploited.
                        
                        ## Core Concepts:
                        1. **Nash Equilibrium**: A strategy where no player can unilaterally improve
                        2. **Balance**: Having the right ratio of value bets to bluffs
                        3. **Minimum Defense Frequency**: Required calling frequency to prevent exploitation
                        
                        ## Key Principles:
                        1. **Bet Sizing**: Choose sizes that work for entire range
                        2. **Range Construction**: Build balanced ranges for all actions
                        3. **Frequency-Based Decisions**: Use correct frequencies for actions
                        
                        ## Practical Application:
                        - Mixed strategies
                        - Balanced betting ranges
                        - Protection concepts
                        - Range advantage
                        '''
                    }
                ]
            },
            'advanced_gto': {
                'name': 'Advanced GTO',
                'level': 'pro',
                'lessons': [
                    {
                        'title': 'Advanced GTO Concepts',
                        'content': '''
                        # Advanced Game Theory Concepts
                        
                        Deep dive into complex GTO principles and their practical application.
                        
                        ## Advanced Topics:
                        1. **Multi-Street Game Trees**: Understanding decision nodes and EV calculations
                        2. **Range Construction**: Building perfectly balanced ranges
                        3. **Exploitative Adjustments**: When and how to deviate from GTO
                        
                        ## Complex Concepts:
                        - **Polarized vs. Linear Ranges**
                        - **Blockers and Removal Effects**
                        - **ICM Implications on GTO**
                        - **Mixed Strategy Implementation**
                        
                        ## Solver Integration:
                        - Using solvers effectively
                        - Interpreting solver solutions
                        - Implementing solver findings
                        - Building custom scenarios
                        '''
                    }
                ]
            }
        }
    
    def get_path(self, path_id: str) -> Optional[Dict]:
        """Get a learning path by ID."""
        return self.paths.get(path_id)
    
    def get_lesson(self, path_id: str, lesson_index: int) -> Optional[Dict]:
        """Get a specific lesson from a path."""
        path = self.get_path(path_id)
        if path and 0 <= lesson_index < len(path['lessons']):
            return path['lessons'][lesson_index]
        return None
    
    def get_paths_by_level(self, level: str) -> List[Dict]:
        """Get all learning paths for a specific skill level."""
        return [
            {'id': path_id, **path_data}
            for path_id, path_data in self.paths.items()
            if path_data['level'] == level
        ] 