from flask import Blueprint, jsonify, request, render_template, session
from .curriculum import Curriculum
from .ai_coach import PokerCoach
from typing import Dict
import json
import os

bp = Blueprint("routes", __name__)
curriculum = Curriculum()
coach = PokerCoach()

@bp.route("/practice")
def practice():
    """Render the practice page."""
    return render_template("practice.html")

@bp.route('/api/learn/paths')
def get_learning_paths():
    """Get available learning paths for a skill level."""
    level = request.args.get('level', 'beginner')
    paths = curriculum.get_paths_by_level(level)
    return jsonify(paths)

@bp.route('/api/coach/advice', methods=['POST'])
def get_coach_advice():
    """Get personalized coaching advice."""
    data = request.get_json()
    game_state = data.get('game_state', {})
    question = data.get('question', '')
    context = data.get('context', 'general')
    skill_level = data.get('skill_level', 'intermediate')
    
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
