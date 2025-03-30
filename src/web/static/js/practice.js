// Game state
const gameState = {
    phase: 'preflop',
    positions: ['UTG', 'UTG1', 'MP', 'CO', 'BTN', 'SB', 'BB'],
    buttonIndex: 4, // BTN position
    activePosition: 'CO',  // Player is always in CO position
    pot: 1.5,
    currentBet: 1,
    lastRaise: 0,
    minRaise: 2,
    stacks: {
        'UTG': 100,
        'UTG1': 100,
        'MP': 100,
        'CO': 100,
        'BTN': 100,
        'SB': 99.5,
        'BB': 99
    },
    bets: {
        'UTG': 0,
        'UTG1': 0,
        'MP': 0,
        'CO': 0,
        'BTN': 0,
        'SB': 0.5,
        'BB': 1
    },
    communityCards: [],
    playerCards: [],
    handHistory: [],
    stats: {
        handsPlayed: 0,
        handsWon: 0,
        totalProfit: 0,
        vpip: 0,
        pfr: 0
    },
    handEquity: 0,
    handStrength: '',
    positionAdvice: ''
};

// DOM elements
let playerCardsEl, communityCardsEl, potDisplayEl, handHistoryEl;
let betSliderEl, betAmountEl, coachResponseEl, coachQuestionEl, askButtonEl;
let foldButtonEl, callButtonEl, raiseButtonEl, newHandButtonEl;
let statsElements = {};

// Card deck
const suits = ['♠', '♥', '♦', '♣'];
const suitColors = {'♠': 'black', '♥': 'red', '♦': 'red', '♣': 'black'};
const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

// Hand categories for evaluation
const handCategories = {
    premium: ['AA', 'KK', 'QQ', 'AKs', 'AKo'],
    strong: ['JJ', 'TT', 'AQs', 'AQo', 'AJs', 'KQs'],
    playable: ['99', '88', 'ATs', 'KJs', 'QJs', 'AJo', 'KQo'],
    speculative: ['77', '66', 'A9s', 'A8s', 'KTs', 'QTs', 'JTs', 'T9s']
};

// Position-based advice
const positionAdvice = {
    'UTG': 'Play only premium hands from UTG position. This is the tightest position at the table.',
    'UTG1': 'Play tight from UTG+1. This is still an early position requiring strong hands.',
    'MP': 'You can start widening your range in middle position, but still play relatively tight.',
    'CO': 'Cutoff is a late position where you can play more hands profitably due to positional advantage.',
    'BTN': 'Button is the best position. You can play your widest range here.',
    'SB': 'Small blind is a tricky position - you act first post-flop despite being near the button.',
    'BB': 'In the big blind, you get a discount to see the flop, which allows defending with a wider range.'
};

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    playerCardsEl = document.getElementById('player-cards');
    communityCardsEl = document.getElementById('community-cards');
    potDisplayEl = document.querySelector('.pot-display');
    handHistoryEl = document.getElementById('hand-history');
    betSliderEl = document.getElementById('bet-slider');
    betAmountEl = document.getElementById('bet-amount');
    coachResponseEl = document.getElementById('coach-response');
    coachQuestionEl = document.getElementById('coach-question');
    askButtonEl = document.getElementById('ask-button');
    foldButtonEl = document.getElementById('fold-button');
    callButtonEl = document.getElementById('call-button');
    raiseButtonEl = document.getElementById('raise-button');
    newHandButtonEl = document.getElementById('new-hand-button');
    
    statsElements = {
        handsPlayed: document.getElementById('hands-played'),
        vpip: document.getElementById('vpip'),
        pfr: document.getElementById('pfr'),
        profit: document.getElementById('profit')
    };

    // Set up event listeners
    if (foldButtonEl) {
        foldButtonEl.addEventListener('click', () => handleAction('fold'));
    }
    
    if (callButtonEl) {
        callButtonEl.addEventListener('click', () => handleAction('call'));
    }
    
    if (raiseButtonEl) {
        raiseButtonEl.addEventListener('click', () => handleAction('raise'));
    }
    
    if (newHandButtonEl) {
        newHandButtonEl.addEventListener('click', resetGame);
    }
    
    if (betSliderEl) {
        betSliderEl.addEventListener('input', (e) => {
            if (betAmountEl) {
                betAmountEl.textContent = `${e.target.value} BB`;
            }
        });
    }
    
    if (askButtonEl) {
        askButtonEl.addEventListener('click', () => {
            handleCoachQuestion();
        });
    }
    
    if (coachQuestionEl) {
        coachQuestionEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleCoachQuestion();
            }
        });
    }
    
    // Initialize the game
    resetGame();
});

// Create and shuffle deck
function createDeck() {
    let deck = [];
    for (let suit of suits) {
        for (let rank of ranks) {
            deck.push({
                suit, 
                rank, 
                color: suitColors[suit]
            });
        }
    }
    
    // Fisher-Yates shuffle
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    
    return deck;
}

// Deal initial cards
function dealInitialCards() {
    const deck = createDeck();
    
    // Deal player cards (to CO position)
    gameState.playerCards = [deck.pop(), deck.pop()];
    
    // Evaluate hand strength
    evaluateHandStrength();
}

// Evaluate hand strength
function evaluateHandStrength() {
    const card1 = gameState.playerCards[0];
    const card2 = gameState.playerCards[1];
    
    // Convert to shorthand notation
    let hand = '';
    if (card1.rank === card2.rank) {
        // Pair
        hand = card1.rank + card1.rank;
    } else {
        // Not a pair - higher card first
        const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
        const rank1Index = ranks.indexOf(card1.rank === '10' ? 'T' : card1.rank);
        const rank2Index = ranks.indexOf(card2.rank === '10' ? 'T' : card2.rank);
        
        if (rank1Index < rank2Index) {
            hand = (card1.rank === '10' ? 'T' : card1.rank) + (card2.rank === '10' ? 'T' : card2.rank);
        } else {
            hand = (card2.rank === '10' ? 'T' : card2.rank) + (card1.rank === '10' ? 'T' : card1.rank);
        }
        
        // Add suited or offsuit designation
        if (card1.suit === card2.suit) {
            hand += 's';
        } else {
            hand += 'o';
        }
    }
    
    // Determine hand category
    let category = '';
    for (const [cat, hands] of Object.entries(handCategories)) {
        if (hands.includes(hand)) {
            category = cat;
            break;
        }
    }
    
    if (!category) {
        category = 'weak';
    }
    
    // Set hand strength
    gameState.handStrength = category;
    
    // Calculate rough equity (simplified)
    switch(category) {
        case 'premium': gameState.handEquity = 0.65; break;
        case 'strong': gameState.handEquity = 0.55; break;
        case 'playable': gameState.handEquity = 0.45; break;
        case 'speculative': gameState.handEquity = 0.35; break;
        default: gameState.handEquity = 0.25;
    }
    
    // Set position-specific advice
    gameState.positionAdvice = positionAdvice[gameState.activePosition];
}

// Initialize game
function initGame() {
    // Clear game state
    gameState.communityCards = [];
    updateHandHistory("*** NEW HAND ***");
    
    // Deal cards
    dealInitialCards();
    
    // Update UI
    updateUI();
    
    // Provide initial advice
    provideInitialAdvice();
}

// Update UI
function updateUI() {
    // Update player cards
    if (playerCardsEl) {
        playerCardsEl.innerHTML = gameState.playerCards.map(card => 
            `<div class="card ${card.color}">${card.rank}${card.suit}</div>`
        ).join('');
    }
    
    // Update community cards
    if (communityCardsEl) {
        communityCardsEl.innerHTML = gameState.communityCards.map(card => 
            `<div class="card ${card.color}">${card.rank}${card.suit}</div>`
        ).join('');
    }
    
    // Update pot display
    if (potDisplayEl) {
        potDisplayEl.textContent = `Pot: ${gameState.pot.toFixed(1)} BB`;
    }
    
    // Update stacks
    for (const position of gameState.positions) {
        const stackEl = document.querySelector(`#${position.toLowerCase()}-position .player-stack`);
        if (stackEl) {
            stackEl.textContent = `${gameState.stacks[position].toFixed(1)} BB`;
        }
    }
    
    // Update active position highlighting
    document.querySelectorAll('.player-position').forEach(pos => {
        pos.classList.remove('active');
    });
    
    const activePos = document.querySelector(`#${gameState.activePosition.toLowerCase()}-position`);
    if (activePos) {
        activePos.classList.add('active');
    }
    
    // Update call button text
    if (callButtonEl) {
        const callAmount = gameState.currentBet - gameState.bets[gameState.activePosition];
        if (callAmount > 0) {
            callButtonEl.textContent = `Call ${callAmount.toFixed(1)} BB`;
        } else {
            callButtonEl.textContent = 'Check';
        }
    }
    
    // Update bet slider
    if (betSliderEl) {
        const minRaise = Math.max(gameState.minRaise, gameState.currentBet * 2);
        const maxRaise = gameState.stacks[gameState.activePosition];
        
        betSliderEl.min = minRaise;
        betSliderEl.max = maxRaise;
        betSliderEl.value = minRaise;
        
        if (betAmountEl) {
            betAmountEl.textContent = `${minRaise.toFixed(1)} BB`;
        }
    }
    
    // Update statistics
    updateStats();
}

// Update statistics
function updateStats() {
    if (statsElements.handsPlayed) {
        statsElements.handsPlayed.textContent = gameState.stats.handsPlayed;
    }
    
    if (statsElements.vpip) {
        statsElements.vpip.textContent = `${gameState.stats.vpip}%`;
    }
    
    if (statsElements.pfr) {
        statsElements.pfr.textContent = `${gameState.stats.pfr}%`;
    }
    
    if (statsElements.profit) {
        statsElements.profit.textContent = `${gameState.stats.totalProfit.toFixed(1)} BB`;
    }
}

// Update hand history
function updateHandHistory(entry) {
    gameState.handHistory.push(entry);
    
    if (handHistoryEl) {
        const entryEl = document.createElement('div');
        entryEl.className = 'history-entry';
        entryEl.textContent = entry;
        handHistoryEl.appendChild(entryEl);
        handHistoryEl.scrollTop = handHistoryEl.scrollHeight;
    }
}

// Handle player action
function handleAction(action) {
    switch (action) {
        case 'fold':
            updateHandHistory(`${gameState.activePosition} folds`);
            gameState.stats.handsPlayed++;
            gameState.stats.totalProfit -= gameState.bets[gameState.activePosition];
            disableActionButtons();
            updateCoachResponse("You folded. Click 'New Hand' to continue.");
            break;
            
        case 'call':
            const callAmount = gameState.currentBet - gameState.bets[gameState.activePosition];
            if (callAmount > 0) {
                gameState.stacks[gameState.activePosition] -= callAmount;
                gameState.bets[gameState.activePosition] += callAmount;
                gameState.pot += callAmount;
                updateHandHistory(`${gameState.activePosition} calls ${callAmount.toFixed(1)} BB`);
                
                // Update VPIP
                if (gameState.phase === 'preflop') {
                    updateVPIP();
                }
            } else {
                updateHandHistory(`${gameState.activePosition} checks`);
            }
            
            // Move to next street
            advanceToNextStreet();
            break;
            
        case 'raise':
            const raiseAmount = parseFloat(betSliderEl.value);
            const currentBet = gameState.bets[gameState.activePosition];
            const extraBet = raiseAmount - currentBet;
            
            gameState.stacks[gameState.activePosition] -= extraBet;
            gameState.bets[gameState.activePosition] = raiseAmount;
            gameState.pot += extraBet;
            gameState.currentBet = raiseAmount;
            gameState.lastRaise = raiseAmount - gameState.currentBet;
            gameState.minRaise = raiseAmount + gameState.lastRaise;
            
            updateHandHistory(`${gameState.activePosition} raises to ${raiseAmount.toFixed(1)} BB`);
            
            // Update VPIP and PFR
            if (gameState.phase === 'preflop') {
                updateVPIP();
                updatePFR();
            }
            
            // Move to next street
            advanceToNextStreet();
            break;
    }
    
    // Update the UI
    updateUI();
}

// Update VPIP
function updateVPIP() {
    // In a real implementation, this would track across many hands
    // For demo purposes, we'll just increase it by 10% per voluntarily played hand
    gameState.stats.vpip = Math.min(100, gameState.stats.vpip + 10);
}

// Update PFR
function updatePFR() {
    // Similar to VPIP, this is simplified
    gameState.stats.pfr = Math.min(100, gameState.stats.pfr + 10);
}

// Advance to next street
function advanceToNextStreet() {
    switch (gameState.phase) {
        case 'preflop':
            gameState.phase = 'flop';
            dealFlop();
            break;
            
        case 'flop':
            gameState.phase = 'turn';
            dealTurn();
            break;
            
        case 'turn':
            gameState.phase = 'river';
            dealRiver();
            break;
            
        case 'river':
            showdown();
            return;
    }
    
    // Reset bets for new street
    for (const position of gameState.positions) {
        gameState.bets[position] = 0;
    }
    gameState.currentBet = 0;
    
    // Update UI
    updateUI();
    
    // Provide new street advice
    provideStreetAdvice();
}

// Deal flop
function dealFlop() {
    const deck = createDeck();
    // Remove cards similar to player's cards
    const flop = [deck.pop(), deck.pop(), deck.pop()];
    gameState.communityCards = flop;
    
    updateHandHistory(`*** FLOP *** [${formatCards(flop)}]`);
}

// Deal turn
function dealTurn() {
    const deck = createDeck();
    const turn = deck.pop();
    gameState.communityCards.push(turn);
    
    updateHandHistory(`*** TURN *** [${formatCards(gameState.communityCards)}]`);
}

// Deal river
function dealRiver() {
    const deck = createDeck();
    const river = deck.pop();
    gameState.communityCards.push(river);
    
    updateHandHistory(`*** RIVER *** [${formatCards(gameState.communityCards)}]`);
}

// Format cards for display
function formatCards(cards) {
    return cards.map(card => `${card.rank}${card.suit}`).join(' ');
}

// Showdown - determine winner
function showdown() {
    // Simplified win logic based on preflop equity
    // In a real implementation, this would evaluate the actual hand strength
    const winProbability = gameState.handEquity * (1 + (gameState.communityCards.length * 0.05));
    const isWinner = Math.random() < winProbability;
    
    const winAmount = isWinner ? gameState.pot : 0;
    const profit = winAmount - gameState.bets[gameState.activePosition];
    
    // Update stats
    gameState.stats.handsPlayed++;
    gameState.stats.totalProfit += profit;
    
    if (isWinner) {
        gameState.stats.handsWon++;
        updateHandHistory(`${gameState.activePosition} wins ${winAmount.toFixed(1)} BB`);
        updateCoachResponse(`You won ${winAmount.toFixed(1)} BB! Your hand was strong enough to win at showdown. Click 'New Hand' to continue.`);
    } else {
        updateHandHistory(`${gameState.activePosition} loses`);
        updateCoachResponse(`You lost at showdown. Click 'New Hand' to play another hand.`);
    }
    
    // Disable action buttons
    disableActionButtons();
}

// Enable action buttons
function enableActionButtons() {
    if (foldButtonEl) foldButtonEl.disabled = false;
    if (callButtonEl) callButtonEl.disabled = false;
    if (raiseButtonEl) raiseButtonEl.disabled = false;
}

// Disable action buttons
function disableActionButtons() {
    if (foldButtonEl) foldButtonEl.disabled = true;
    if (callButtonEl) callButtonEl.disabled = true;
    if (raiseButtonEl) raiseButtonEl.disabled = true;
}

// Reset game
function resetGame() {
    // Reset stacks
    for (const position of gameState.positions) {
        gameState.stacks[position] = 100;
        gameState.bets[position] = 0;
    }
    
    // Post blinds
    gameState.stacks['SB'] -= 0.5;
    gameState.stacks['BB'] -= 1;
    gameState.bets['SB'] = 0.5;
    gameState.bets['BB'] = 1;
    
    // Reset game state
    gameState.pot = 1.5;
    gameState.currentBet = 1;
    gameState.lastRaise = 0;
    gameState.minRaise = 2;
    gameState.phase = 'preflop';
    gameState.activePosition = 'CO'; // Player is always in CO
    
    // Clear hand history
    if (handHistoryEl) {
        handHistoryEl.innerHTML = '';
    }
    
    // Enable action buttons
    enableActionButtons();
    
    // Initialize game
    initGame();
}

// Provide initial advice
function provideInitialAdvice() {
    const handCategory = gameState.handStrength;
    const position = gameState.activePosition;
    let advice = '';
    
    advice = `You're in the ${position} position with ${formatCards(gameState.playerCards)} (${handCategory}). `;
    
    switch (handCategory) {
        case 'premium':
            advice += `This is a premium hand that you should raise with from any position. Consider raising to 3BB.`;
            break;
        case 'strong':
            advice += `This is a strong hand that plays well from late positions like yours. A standard raise to 2.5-3BB is recommended.`;
            break;
        case 'playable':
            advice += `This hand is playable from late position. You can raise to 2.5BB or call if there's already been a raise.`;
            break;
        case 'speculative':
            advice += `This is a speculative hand with potential. From your position, you could raise to 2.5BB or fold if facing aggression.`;
            break;
        default:
            advice += `This hand is relatively weak. From your position, you could consider folding unless you want to mix your play.`;
    }
    
    advice += `\n\n${gameState.positionAdvice}`;
    
    updateCoachResponse(advice);
}

// Provide street-specific advice
function provideStreetAdvice() {
    let advice = '';
    
    switch (gameState.phase) {
        case 'flop':
            advice = `The flop is ${formatCards(gameState.communityCards)}. `;
            advice += `Look for connected cards, pairs, or flush/straight possibilities. `;
            advice += `With your ${gameState.handStrength} hand, consider how this board hits your range.`;
            break;
            
        case 'turn':
            advice = `The turn is ${gameState.communityCards[3].rank}${gameState.communityCards[3].suit}. `;
            advice += `Reevaluate your hand strength. If you have a strong hand, consider value betting. `;
            advice += `If your hand is marginal, pot control might be better.`;
            break;
            
        case 'river':
            advice = `The river is ${gameState.communityCards[4].rank}${gameState.communityCards[4].suit}. `;
            advice += `This is your last chance to extract value or bluff. `;
            advice += `Consider your opponent's likely holdings and whether your hand is strong enough to value bet.`;
            break;
    }
    
    updateCoachResponse(advice);
}

// Handle coach question
function handleCoachQuestion() {
    if (!coachQuestionEl || !coachQuestionEl.value.trim()) {
        return;
    }
    
    const question = coachQuestionEl.value.trim();
    coachQuestionEl.value = '';
    
    // Process the question
    const response = generateCoachResponse(question);
    updateCoachResponse(response);
}

// Generate coach response to user question
function generateCoachResponse(question) {
    // Convert question to lowercase for easier matching
    const lowerQuestion = question.toLowerCase();
    
    // Basic information about the current state
    const hand = formatCards(gameState.playerCards);
    const position = gameState.activePosition;
    const phase = gameState.phase;
    const board = gameState.communityCards.length > 0 ? formatCards(gameState.communityCards) : "not dealt yet";
    const pot = gameState.pot.toFixed(1);
    const callAmount = (gameState.currentBet - gameState.bets[position]).toFixed(1);
    
    // Question categories and responses
    if (lowerQuestion.includes("fold") || lowerQuestion.includes("should i fold")) {
        if (gameState.handStrength === 'premium' && phase === 'preflop') {
            return `With ${hand}, folding preflop would be a mistake. This is a premium hand that should be raised from any position.`;
        } else if (gameState.handStrength === 'weak' && phase === 'preflop') {
            return `With ${hand} in ${position}, folding is often the correct play, especially against early position raises.`;
        } else {
            return `Folding depends on your hand strength, board texture, and pot odds. With ${hand} on ${board}, consider if you have the right odds to continue.`;
        }
    }
    
    if (lowerQuestion.includes("call") || lowerQuestion.includes("should i call")) {
        const potOdds = (parseFloat(callAmount) / (parseFloat(pot) + parseFloat(callAmount))).toFixed(2);
        return `To call ${callAmount} BB into a ${pot} BB pot, you need approximately ${potOdds} equity to break even. With ${hand} in ${position} against the current board ${board}, calling is ${gameState.handEquity > parseFloat(potOdds) ? 'profitable' : 'unprofitable'} based on simplified equity estimates.`;
    }
    
    if (lowerQuestion.includes("raise") || lowerQuestion.includes("should i raise")) {
        if (phase === 'preflop') {
            if (gameState.handStrength === 'premium' || gameState.handStrength === 'strong') {
                return `With ${hand} in ${position}, raising is recommended. A standard raise would be to 2.5-3BB.`;
            } else {
                return `With ${hand} in ${position}, raising is speculative. It could work as a bluff or semi-bluff if you believe your opponents will fold often.`;
            }
        } else {
            return `Raising on the ${phase} with ${hand} against board ${board} depends on your perceived hand strength and your opponent's tendencies. If you believe you have the best hand, raising for value makes sense.`;
        }
    }
    
    if (lowerQuestion.includes("position") || lowerQuestion.includes("my position")) {
        return positionAdvice[position];
    }
    
    if (lowerQuestion.includes("odds") || lowerQuestion.includes("pot odds")) {
        const potOdds = (parseFloat(callAmount) / (parseFloat(pot) + parseFloat(callAmount))).toFixed(2);
        return `The pot is ${pot} BB and you need to call ${callAmount} BB, giving you pot odds of ${potOdds * 100}%. This means your hand needs at least ${potOdds * 100}% equity against your opponent's range to make a profitable call.`;
    }
    
    if (lowerQuestion.includes("board") || lowerQuestion.includes("community cards")) {
        if (gameState.communityCards.length === 0) {
            return "The community cards haven't been dealt yet. We're still in the preflop betting round.";
        }
        
        return `The current board is ${board}. Look for potential draws, pairs, and how this board interacts with your hand ${hand} and your opponent's likely range.`;
    }
    
    if (lowerQuestion.includes("hand strength") || lowerQuestion.includes("how strong")) {
        return `Your hand ${hand} is categorized as ${gameState.handStrength}. In ${position} against the current board ${board}, your estimated equity is roughly ${(gameState.handEquity * 100).toFixed(0)}% (simplified calculation).`;
    }
    
    // Default response for unrecognized questions
    return `As a poker coach, I can help analyze your current situation. You have ${hand} in ${position} position. The current phase is ${phase} with board ${board}. The pot is ${pot} BB. Ask me about specific concepts like position, hand strength, pot odds, or whether you should fold, call, or raise.`;
}

// Update coach response
function updateCoachResponse(message) {
    if (coachResponseEl) {
        coachResponseEl.textContent = message;
    }
} 