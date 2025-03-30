import pytest
import os
from src.knowledge.poker_knowledge import PokerKnowledge

@pytest.fixture
def knowledge_base():
    """Create a test knowledge base instance."""
    test_data_path = os.path.join(os.path.dirname(__file__), 'data')
    knowledge = PokerKnowledge(os.path.join(test_data_path, 'knowledge.json'))
    return knowledge

def test_load_concepts(knowledge_base):
    """Test loading concepts from the knowledge base."""
    concepts = knowledge_base.get_all_concepts()
    assert len(concepts) > 0
    assert 'preflop_position' in concepts
    assert 'range_construction' in concepts
    assert 'game_theory' in concepts

def test_get_concept(knowledge_base):
    """Test retrieving a specific concept."""
    concept = knowledge_base.get_concept('preflop_position')
    assert concept is not None
    assert concept['title'] == 'Preflop Position'
    assert concept['difficulty'] == 'beginner'

def test_get_explanation(knowledge_base):
    """Test retrieving explanations at different difficulty levels."""
    # Test beginner explanation
    beginner_explanation = knowledge_base.get_explanation('preflop_position', 'beginner')
    assert 'Position in poker refers to where you are seated' in beginner_explanation

    # Test intermediate explanation
    intermediate_explanation = knowledge_base.get_explanation('preflop_position', 'intermediate')
    assert 'Position is crucial in poker because it determines' in intermediate_explanation

    # Test advanced explanation
    advanced_explanation = knowledge_base.get_explanation('preflop_position', 'advanced')
    assert 'Positional advantage in poker is a fundamental concept' in advanced_explanation

def test_get_prerequisites(knowledge_base):
    """Test retrieving prerequisites for concepts."""
    # Test concept with no prerequisites
    preflop_prereqs = knowledge_base.get_prerequisites('preflop_position')
    assert len(preflop_prereqs) == 0

    # Test concept with prerequisites
    range_prereqs = knowledge_base.get_prerequisites('range_construction')
    assert len(range_prereqs) == 1
    assert 'preflop_position' in range_prereqs

def test_get_related_concepts(knowledge_base):
    """Test retrieving related concepts."""
    related = knowledge_base.get_related_concepts('preflop_position')
    assert len(related) == 2
    assert 'range_construction' in related
    assert 'betting_strategy' in related

def test_get_examples(knowledge_base):
    """Test retrieving examples for a concept."""
    examples = knowledge_base.get_examples('preflop_position')
    assert len(examples) == 1
    assert examples[0]['hand'] == 'As Kh'
    assert examples[0]['position'] == 'BTN'
    assert examples[0]['action'] == 'raise'

def test_filter_by_difficulty(knowledge_base):
    """Test filtering concepts by difficulty level."""
    beginner_concepts = knowledge_base.filter_by_difficulty('beginner')
    assert len(beginner_concepts) == 1
    assert 'preflop_position' in beginner_concepts

    intermediate_concepts = knowledge_base.filter_by_difficulty('intermediate')
    assert len(intermediate_concepts) == 1
    assert 'range_construction' in intermediate_concepts

    advanced_concepts = knowledge_base.filter_by_difficulty('advanced')
    assert len(advanced_concepts) == 1
    assert 'game_theory' in advanced_concepts

def test_search_concepts(knowledge_base):
    """Test searching concepts by title or description."""
    # Search by title
    title_results = knowledge_base.search('Position')
    assert len(title_results) > 0
    assert any('preflop_position' in result['id'] for result in title_results)

    # Search by description
    desc_results = knowledge_base.search('balanced ranges')
    assert len(desc_results) > 0
    assert any('range_construction' in result['id'] for result in desc_results)

def test_get_learning_path(knowledge_base):
    """Test retrieving a learning path for a concept."""
    path = knowledge_base.get_learning_path('game_theory')
    assert len(path) == 3
    assert path[0]['id'] == 'preflop_position'
    assert path[1]['id'] == 'range_construction'
    assert path[2]['id'] == 'game_theory' 