import pytest
import os
import json
from datetime import datetime, timedelta
from src.personalization.spaced_repetition import SpacedRepetition, Review

@pytest.fixture
def setup_test_data(tmp_path):
    """Create a temporary directory for test data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def spaced_repetition(setup_test_data):
    """Create a SpacedRepetition instance with test data."""
    reviews_path = setup_test_data / "reviews.json"
    return SpacedRepetition(str(reviews_path))

def test_add_review(spaced_repetition):
    """Test adding a new review."""
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 3,
        'next_review': datetime.now().isoformat(),
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    
    review = spaced_repetition.add_review('test_user', review_data)
    assert review is not None
    assert review.concept_id == 'test_concept'
    assert review.difficulty == 3
    assert review.interval == 1
    assert review.ease_factor == 2.5
    assert review.repetitions == 0

def test_get_due_reviews(spaced_repetition):
    """Test getting due reviews."""
    # Add a review due now
    now = datetime.now()
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 3,
        'next_review': now.isoformat(),
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    spaced_repetition.add_review('test_user', review_data)
    
    # Add a review due in the future
    future = now + timedelta(days=1)
    review_data['next_review'] = future.isoformat()
    spaced_repetition.add_review('test_user', review_data)
    
    # Get due reviews
    due_reviews = spaced_repetition.get_due_reviews('test_user')
    assert len(due_reviews) == 1
    assert due_reviews[0].concept_id == 'test_concept'

def test_process_review(spaced_repetition):
    """Test processing a review result."""
    # Add initial review
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 3,
        'next_review': datetime.now().isoformat(),
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    spaced_repetition.add_review('test_user', review_data)
    
    # Process review with different difficulties
    review = spaced_repetition.process_review('test_user', 'test_concept', 5)
    assert review is not None
    assert review.difficulty == 5
    assert review.repetitions == 1
    assert review.ease_factor > 2.5  # Should increase for good performance
    
    review = spaced_repetition.process_review('test_user', 'test_concept', 1)
    assert review is not None
    assert review.difficulty == 1
    assert review.repetitions == 2
    assert review.ease_factor < 2.5  # Should decrease for poor performance

def test_get_review_stats(spaced_repetition):
    """Test getting review statistics."""
    # Add some reviews
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 3,
        'next_review': datetime.now().isoformat(),
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    spaced_repetition.add_review('test_user', review_data)
    
    # Process some reviews
    spaced_repetition.process_review('test_user', 'test_concept', 5)
    spaced_repetition.process_review('test_user', 'test_concept', 4)
    
    # Get stats
    stats = spaced_repetition.get_review_stats('test_user')
    assert stats['total_reviews'] == 1
    assert stats['due_reviews'] == 1
    assert stats['average_difficulty'] > 0
    assert stats['concepts_mastered'] >= 0

def test_get_review_history(spaced_repetition):
    """Test getting review history."""
    # Add and process a review
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 3,
        'next_review': datetime.now().isoformat(),
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    spaced_repetition.add_review('test_user', review_data)
    spaced_repetition.process_review('test_user', 'test_concept', 5)
    
    # Get history
    history = spaced_repetition.get_review_history('test_user', 'test_concept')
    assert len(history) == 1
    assert history[0]['difficulty'] == 5
    assert history[0]['repetitions'] == 1

def test_reset_review(spaced_repetition):
    """Test resetting a review."""
    # Add and process a review
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 3,
        'next_review': datetime.now().isoformat(),
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    spaced_repetition.add_review('test_user', review_data)
    spaced_repetition.process_review('test_user', 'test_concept', 5)
    
    # Reset review
    review = spaced_repetition.reset_review('test_user', 'test_concept')
    assert review is not None
    assert review.difficulty == 3
    assert review.repetitions == 0
    assert review.interval == 1
    assert review.ease_factor == 2.5

def test_persistence(spaced_repetition, setup_test_data):
    """Test that reviews are persisted correctly."""
    # Add a review
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 3,
        'next_review': datetime.now().isoformat(),
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    spaced_repetition.add_review('test_user', review_data)
    
    # Create new instance
    new_reviews_path = setup_test_data / "reviews.json"
    new_spaced_repetition = SpacedRepetition(str(new_reviews_path))
    
    # Check that review is still there
    due_reviews = new_spaced_repetition.get_due_reviews('test_user')
    assert len(due_reviews) == 1
    assert due_reviews[0].concept_id == 'test_concept'

def test_invalid_review_data(spaced_repetition):
    """Test handling of invalid review data."""
    # Missing required fields
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 3
    }
    review = spaced_repetition.add_review('test_user', review_data)
    assert review is None
    
    # Invalid difficulty
    review_data = {
        'concept_id': 'test_concept',
        'difficulty': 6,  # Invalid difficulty
        'next_review': datetime.now().isoformat(),
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0
    }
    review = spaced_repetition.add_review('test_user', review_data)
    assert review is None

def test_nonexistent_user(spaced_repetition):
    """Test handling of nonexistent user."""
    # Try to get reviews for nonexistent user
    due_reviews = spaced_repetition.get_due_reviews('nonexistent_user')
    assert len(due_reviews) == 0
    
    # Try to get stats for nonexistent user
    stats = spaced_repetition.get_review_stats('nonexistent_user')
    assert stats['total_reviews'] == 0
    assert stats['due_reviews'] == 0
    assert stats['average_difficulty'] == 0
    assert stats['concepts_mastered'] == 0 