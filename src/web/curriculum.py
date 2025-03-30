from typing import Dict, List, Optional

class Curriculum:
    def __init__(self):
        self.paths = {
            'fundamentals': {
                'name': 'Poker Fundamentals',
                'level': 'beginner',
                'description': 'Master the basic concepts of poker to build a solid foundation for your poker journey.',
                'lessons': [
                    {
                        'title': 'Introduction to Poker',
                        'description': 'Learn the basic rules, hand rankings, and fundamental concepts of poker.',
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
                        ''',
                        'quiz_questions': [
                            {
                                'question': 'Which hand is ranked highest in poker?',
                                'options': ['Four of a Kind', 'Full House', 'Royal Flush', 'Straight Flush', 'Flush'],
                                'answer': 'Royal Flush',
                                'explanation': 'A Royal Flush is the highest-ranking hand in poker, consisting of A-K-Q-J-10 all of the same suit.'
                            },
                            {
                                'question': 'What is the primary goal in poker?',
                                'options': [
                                    'Always have the best hand',
                                    'Win money by having the best hand or making others fold',
                                    'Bluff on every hand',
                                    'Force others to fold',
                                    'Play every hand to the river'
                                ],
                                'answer': 'Win money by having the best hand or making others fold',
                                'explanation': 'The goal of poker is to win money, which can be achieved either by showing down the best hand at showdown or by getting your opponents to fold before showdown.'
                            },
                            {
                                'question': 'Which of the following is NOT a common poker variant?',
                                'options': ['Texas Hold\'em', 'Omaha', 'Seven-card Stud', 'Poker Run', 'Razz'],
                                'answer': 'Poker Run',
                                'explanation': 'Poker Run is not a poker variant but an organized event where participants travel between checkpoints, collecting playing cards. Texas Hold\'em, Omaha, Seven-card Stud, and Razz are all legitimate poker variants.'
                            }
                        ]
                    },
                    {
                        'title': 'Position and Its Importance',
                        'description': 'Understand why position is one of the most powerful advantages in poker and how to leverage it.',
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
                        ''',
                        'quiz_questions': [
                            {
                                'question': 'Which position is considered the best in poker?',
                                'options': ['Under the Gun (UTG)', 'Cutoff (CO)', 'Button (BTN)', 'Small Blind (SB)', 'Big Blind (BB)'],
                                'answer': 'Button (BTN)',
                                'explanation': 'The Button (BTN) is considered the best position because you act last on all post-flop streets, giving you maximum information before making your decisions.'
                            },
                            {
                                'question': 'Why is position so important in poker?',
                                'options': [
                                    'It determines the order of receiving cards',
                                    'It gives you an information advantage when acting later',
                                    'It increases your starting hand value',
                                    'It lets you see the flop for free',
                                    'It forces other players to fold'
                                ],
                                'answer': 'It gives you an information advantage when acting later',
                                'explanation': 'Position is crucial because acting later gives you more information about your opponents\' actions, allowing you to make more informed decisions.'
                            },
                            {
                                'question': 'Which statement about position is TRUE?',
                                'options': [
                                    'You should play more hands from early position',
                                    'The Small Blind has the best post-flop position',
                                    'Position advantage disappears after the flop',
                                    'You should play tighter from early positions',
                                    'Position doesn\'t affect bluffing success'
                                ],
                                'answer': 'You should play tighter from early positions',
                                'explanation': 'When in early position, you should play tighter (fewer hands) because you\'ll have to act first on all post-flop streets with less information about your opponents\' holdings.'
                            }
                        ]
                    },
                    {
                        'title': 'Starting Hand Selection',
                        'description': 'Learn which hands to play and which to fold based on position and game context.',
                        'content': '''
                        # Starting Hand Selection
                        
                        Choosing the right starting hands is fundamental to profitable poker. Not all hands are created equal.
                        
                        ## Hand Categories:
                        1. **Premium Hands**: AA, KK, QQ, AK
                        2. **Strong Hands**: JJ, TT, AQ, AJ, KQ
                        3. **Speculative Hands**: Small pairs, suited connectors
                        4. **Marginal Hands**: Weak aces, offsuit connectors
                        5. **Trash Hands**: Unsuited, unconnected low cards
                        
                        ## Position-Based Selection:
                        - **Early Position**: Play only premium and strong hands
                        - **Middle Position**: Add some strong speculative hands
                        - **Late Position**: Widen range with more speculative hands
                        - **Blinds**: Defend with wider range but be cautious
                        
                        ## Other Factors to Consider:
                        - Table dynamics and player tendencies
                        - Stack sizes (deep vs. short)
                        - Tournament stage or cash game context
                        - Number of players who have entered the pot
                        ''',
                        'quiz_questions': [
                            {
                                'question': 'Which of these starting hands is considered "premium"?',
                                'options': ['JJ', 'AQ', 'T9 suited', 'AA', '76 suited'],
                                'answer': 'AA',
                                'explanation': 'AA (pocket aces) is considered a premium hand in poker, while JJ and AQ are strong hands, and T9s and 76s are speculative hands.'
                            },
                            {
                                'question': 'How should your starting hand selection change based on position?',
                                'options': [
                                    'Play more hands from early position',
                                    'Play the same hands regardless of position',
                                    'Play fewer hands from late position',
                                    'Play more hands from late position',
                                    'Position doesn\'t affect hand selection'
                                ],
                                'answer': 'Play more hands from late position',
                                'explanation': 'You should play more hands from late position because you have the advantage of acting after most players post-flop, allowing you to play more marginal hands profitably.'
                            },
                            {
                                'question': 'Which factor is LEAST important when selecting starting hands?',
                                'options': [
                                    'Your position at the table',
                                    'The color of the cards in your hand',
                                    'Stack sizes',
                                    'Number of players in the pot',
                                    'Player tendencies'
                                ],
                                'answer': 'The color of the cards in your hand',
                                'explanation': 'The color of the cards (red or black) has no relevance to hand selection. What matters is the rank and whether they are suited (same suit) or offsuit (different suits), not the actual color of the cards.'
                            }
                        ]
                    }
                ]
            },
            'basic_math': {
                'name': 'Basic Poker Math',
                'level': 'beginner',
                'description': 'Learn the essential mathematical concepts that form the foundation of profitable poker decision-making.',
                'lessons': [
                    {
                        'title': 'Pot Odds and Basic Probability',
                        'description': 'Master the fundamental calculations needed to make profitable calls in poker.',
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
                        ''',
                        'quiz_questions': [
                            {
                                'question': 'If the pot is $50 and your opponent bets $25, what are your pot odds?',
                                'options': ['3:1', '2:1', '1:1', '4:1', '5:2'],
                                'answer': '3:1',
                                'explanation': 'When your opponent bets $25, the new pot size is $75 ($50 + $25). Your pot odds are $75:$25, which simplifies to 3:1.'
                            },
                            {
                                'question': 'How many outs do you have with a flush draw after the flop?',
                                'options': ['4', '8', '9', '12', '15'],
                                'answer': '9',
                                'explanation': 'With a flush draw after the flop, you have 9 outs. There are 13 cards of each suit, and you already have 4 cards of that suit (2 in your hand and 2 on the flop), leaving 9 cards that will complete your flush.'
                            },
                            {
                                'question': 'Using the Rule of 4 and 2, what is the approximate probability of hitting an open-ended straight draw from the flop to the river?',
                                'options': ['8%', '16%', '32%', '40%', '50%'],
                                'answer': '32%',
                                'explanation': 'An open-ended straight draw has 8 outs. Using the Rule of 4 for two cards to come, 8 × 4 = 32%, which is your approximate probability of hitting your straight from flop to river.'
                            }
                        ]
                    },
                    {
                        'title': 'Expected Value (EV)',
                        'description': 'Learn how to calculate the profitability of poker decisions over the long run.',
                        'content': '''
                        # Expected Value (EV) in Poker
                        
                        Expected Value is a fundamental concept that helps determine the profitability of poker decisions over the long term.
                        
                        ## What is EV?
                        - **Definition**: The average amount you expect to win or lose on a bet over the long run
                        - **Formula**: EV = (Probability of Winning × Amount Won) - (Probability of Losing × Amount Lost)
                        
                        ## Calculating EV:
                        1. Determine your equity in the pot
                        2. Calculate potential winnings and losses
                        3. Multiply winnings by win probability
                        4. Multiply losses by loss probability
                        5. Subtract the expected loss from the expected win
                        
                        ## EV Examples:
                        - **Positive EV (+EV)**: Profitable decision over the long run
                        - **Negative EV (-EV)**: Unprofitable decision over the long run
                        - **Example Calculation**: If you have a 30% chance to win a $100 pot by calling $20, your EV is:
                          (0.3 × $100) - (0.7 × $20) = $30 - $14 = $16
                        ''',
                        'quiz_questions': [
                            {
                                'question': 'What does a positive expected value (EV) decision mean in poker?',
                                'options': [
                                    'You will definitely win the hand',
                                    'The decision will be profitable over the long run',
                                    'Your hand has more than 50% equity',
                                    'You have position advantage',
                                    'The pot is large'
                                ],
                                'answer': 'The decision will be profitable over the long run',
                                'explanation': 'A positive EV decision means that, on average, you expect to profit from making this decision repeatedly over the long run, even though you might lose in individual instances.'
                            },
                            {
                                'question': 'If you have a 25% chance to win a $200 pot and need to call $30, what is your EV?',
                                'options': ['$17.50', '$-5', '$20', '$50', '$-30'],
                                'answer': '$20',
                                'explanation': 'EV = (Probability of Winning × Amount Won) - (Probability of Losing × Amount Lost). You have a 25% chance to win $200, and a 75% chance to lose $30. EV = (0.25 × $200) - (0.75 × $30) = $50 - $22.50 = $27.50. When you call $30, your net win is $170 ($200 - $30), so the actual calculation is (0.25 × $170) - (0.75 × $30) = $42.50 - $22.50 = $20.'
                            },
                            {
                                'question': 'Which of these is NOT an essential component for calculating EV in poker?',
                                'options': [
                                    'Probability of winning',
                                    'Amount you can win',
                                    'Probability of losing',
                                    'Amount you can lose',
                                    'The time of day you are playing'
                                ],
                                'answer': 'The time of day you are playing',
                                'explanation': 'The time of day you are playing has no direct mathematical relevance to calculating expected value. EV calculation requires only the probabilities of different outcomes and the amount you win or lose in each case.'
                            }
                        ]
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