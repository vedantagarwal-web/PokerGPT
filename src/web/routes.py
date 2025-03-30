from flask import Blueprint, jsonify, request, render_template
from .curriculum import Curriculum
from .ai_coach import PokerCoach
from typing import Dict
import json
import os

bp = Blueprint('routes', __name__)
curriculum = Curriculum()
coach = PokerCoach()

@bp.route('/learn')
def learn():
    """Render the learning dashboard."""
    return render_template('learn.html')

@bp.route('/learn/<path_id>')
def learn_path(path_id):
    """Render a specific learning path."""
    path = curriculum.get_path(path_id)
    if not path:
        return render_template('learn.html', error=f"Learning path '{path_id}' not found")
    
    return render_template('learn_path.html', path=path, path_id=path_id)

@bp.route('/lesson')
def lesson():
    """Render a specific lesson."""
    path_id = request.args.get('path')
    lesson_name = request.args.get('lesson')
    
    if not path_id or not lesson_name:
        return render_template('learn.html', error="Missing path or lesson parameter")
    
    path = curriculum.get_path(path_id)
    if not path:
        return render_template('learn.html', error="Learning path not found")
    
    # Find the lesson by name
    lesson_index = next((i for i, lesson in enumerate(path['lessons']) 
                     if lesson['title'].lower().replace(' ', '_') == lesson_name), 0)
    
    lesson = curriculum.get_lesson(path_id, lesson_index)
    if not lesson:
        return render_template('learn.html', error="Lesson not found")
    
    return render_template('lesson.html', path=path, lesson=lesson, index=lesson_index, path_id=path_id)

@bp.route('/api/learn/paths')
def get_learning_paths():
    """Get available learning paths for a skill level."""
    level = request.args.get('level', 'beginner')
    paths = curriculum.get_paths_by_level(level)
    return jsonify(paths)

@bp.route('/api/learn/start', methods=['POST'])
def start_learning_path():
    """Start or continue a learning path."""
    data = request.get_json()
    path_id = data.get('path')
    level = data.get('level', 'beginner')
    
    path = curriculum.get_path(path_id)
    if not path:
        return jsonify({'error': 'Path not found'}), 404
    
    # Here you would typically save the user's progress
    return jsonify({
        'path_id': path_id,
        'first_lesson': path['lessons'][0]
    })

@bp.route('/api/learn/lesson/<path_id>/<int:lesson_index>')
def get_lesson(path_id: str, lesson_index: int):
    """Get a specific lesson's content."""
    lesson = curriculum.get_lesson(path_id, lesson_index)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    return jsonify(lesson)

@bp.route('/api/coach/advice', methods=['POST'])
def get_coach_advice():
    """Get personalized coaching advice."""
    data = request.get_json()
    game_state: Dict = data.get('game_state', {})
    question: str = data.get('question', '')
    context: str = data.get('context', 'general')
    skill_level: str = data.get('skill_level', 'intermediate')
    
    try:
        advice = coach.get_coaching_advice(
            game_state=game_state,
            question=question,
            context=context,
            skill_level=skill_level
        )
        return jsonify({'advice': advice})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/coach/analyze', methods=['POST'])
def analyze_hand():
    """Analyze a complete hand history."""
    data = request.get_json()
    hand_history = data.get('hand_history', [])
    focus_area = data.get('focus_area')
    
    try:
        analysis = coach.analyze_hand_history(
            hand_history=hand_history,
            focus_area=focus_area
        )
        return jsonify({'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/coach/session', methods=['POST'])
def start_coach_session():
    """Start a new AI coaching session."""
    data = request.get_json()
    skill_level = data.get('skill_level', 'intermediate')
    
    # Here you would typically create a new coaching session
    session_id = 'new_session'  # Generate a real session ID
    
    return jsonify({
        'session_id': session_id,
        'skill_level': skill_level
    })

@bp.route('/api/poker-coach/advice', methods=['POST'])
def get_poker_advice():
    """Get advice from the poker coach."""
    try:
        data = request.json
        if not data:
            return jsonify({'advice': 'I need more information to provide advice. Please include position, phase, and other game details.'}), 200
        
        # Get advice from AI coach
        advice = coach.get_advice(
            position=data.get('position', 'CO'),
            phase=data.get('phase', 'preflop'),
            pot=data.get('pot', 0),
            current_bet=data.get('current_bet', 0),
            player_cards=data.get('player_cards', []),
            community_cards=data.get('community_cards', []),
            bets=data.get('bets', {})
        )
        
        # Determine related concept based on position and phase
        related_concept = None
        phase = data.get('phase', 'preflop')
        if phase == 'preflop':
            related_concept = 'preflop_ranges'
        elif phase in ['flop', 'turn', 'river']:
            related_concept = 'postflop_play'
        
        return jsonify({
            'advice': advice,
            'related_concept': related_concept
        })
    except Exception as e:
        return jsonify({
            'advice': 'Sorry, I encountered an error generating advice. For preflop play, focus on position and hand strength. In later positions, you can play more hands profitably.',
            'related_concept': 'position'
        }), 200

@bp.route('/api/learning-path/<skill_level>')
def get_learning_path(skill_level):
    """Get learning path for a skill level."""
    try:
        # Get learning path for skill level
        concepts = coach.get_learning_path(skill_level)
        
        # Get concept details
        concept_details = []
        for concept_id in concepts:
            concept = coach.knowledge_base['concepts'].get(concept_id)
            if concept:
                concept_details.append({
                    'id': concept_id,
                    'name': concept['name'],
                    'difficulty': concept['difficulty'],
                    'prerequisites': concept['prerequisites']
                })
        
        return jsonify({
            'concepts': concept_details
        })
    except Exception as e:
        # Return basic concepts for fallback
        return jsonify({
            'concepts': [
                {
                    'id': 'position',
                    'name': 'Position',
                    'difficulty': 'beginner',
                    'prerequisites': []
                },
                {
                    'id': 'pot_odds',
                    'name': 'Pot Odds',
                    'difficulty': 'beginner',
                    'prerequisites': ['position']
                },
                {
                    'id': 'preflop_ranges',
                    'name': 'Preflop Ranges',
                    'difficulty': 'intermediate',
                    'prerequisites': ['position', 'pot_odds']
                }
            ]
        }), 200

@bp.route('/api/concept/<concept_id>')
def get_concept_details(concept_id):
    """Get details of a specific concept."""
    try:
        # Get concept details from knowledge base
        concept = coach.knowledge_base['concepts'].get(concept_id)
        
        if concept:
            return jsonify({
                'id': concept_id,
                'name': concept['name'],
                'difficulty': concept['difficulty'],
                'prerequisites': concept['prerequisites'],
                'explanations': concept['explanations']
            })
        else:
            return jsonify({'error': 'Concept not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/practice')
def practice():
    """Render the practice page."""
    return render_template('practice.html') 