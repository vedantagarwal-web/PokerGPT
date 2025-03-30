// Global variables for learning state
let currentLevel = 'beginner';
let currentPath = null;
let currentLesson = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up skill level tabs
    document.querySelectorAll('.skill-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.skill-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update current level
            currentLevel = tab.dataset.level;
            
            // Show paths for selected level
            showPathsForLevel(currentLevel);
        });
    });
    
    // Set up start learning buttons
    document.querySelectorAll('.start-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const pathId = e.target.getAttribute('data-path');
            if (pathId) {
                startLearningPath(pathId);
            }
        });
    });
    
    // Initial load - show beginner paths
    showPathsForLevel('beginner');
});

/**
 * Show learning paths for the selected level
 */
function showPathsForLevel(level) {
    // Show paths for selected level
    document.querySelectorAll('.path-card').forEach(card => {
        if (card.getAttribute('data-level') === level) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Start a learning path
 */
function startLearningPath(pathId) {
    // Basic client-side navigation
    window.location.href = `/learn/${pathId}`;
}

// Handle coach advice form if it exists
const coachQuestion = document.getElementById('coach-question');
const coachResponse = document.getElementById('coach-response');

if (coachQuestion && coachResponse) {
    document.querySelector('button[onclick="getCoachAdvice()"]').addEventListener('click', () => {
        getCoachAdvice();
    });
}

/**
 * Get coaching advice
 */
function getCoachAdvice() {
    const question = coachQuestion.value;
    
    if (!question) {
        alert('Please enter a question for the coach');
        return;
    }
    
    // Use fallback advice if API is not working
    let fallbackAdvice = "As a poker coach, I'd recommend focusing on position, pot odds, and hand selection. These are fundamental concepts that will improve your game the most.";
    
    fetch('/api/coach/advice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            skill_level: currentLevel,
            context: 'general'
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        coachResponse.innerHTML = data.advice || fallbackAdvice;
    })
    .catch(error => {
        console.error('Error getting coach advice:', error);
        coachResponse.innerHTML = fallbackAdvice;
    });
} 