import pytest
import os
from datetime import datetime
from src.personalization.user_profile import UserProfile, UserProfileManager

@pytest.fixture
def setup_test_data(tmp_path):
    """Create a temporary directory for test data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def profile_manager(setup_test_data):
    """Create a UserProfileManager instance with test data."""
    profiles_path = setup_test_data / "profiles.json"
    return UserProfileManager(str(profiles_path))

def test_create_profile(profile_manager):
    """Test creating a new user profile."""
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    
    profile = profile_manager.create_profile(user_data)
    assert profile is not None
    assert profile.username == 'test_user'
    assert profile.email == 'test@example.com'
    assert profile.level == 1
    assert profile.xp == 0
    assert len(profile.learning_paths) == 0
    assert len(profile.achievements) == 0
    assert profile.study_streak == 0
    assert profile.total_study_time == 0

def test_get_profile(profile_manager):
    """Test retrieving a user profile."""
    # First create a profile
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    profile_manager.create_profile(user_data)
    
    # Then retrieve it
    profile = profile_manager.get_profile('test_user')
    assert profile is not None
    assert profile.username == 'test_user'
    assert profile.email == 'test@example.com'

def test_update_profile(profile_manager):
    """Test updating a user profile."""
    # First create a profile
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    profile_manager.create_profile(user_data)
    
    # Update the profile
    update_data = {
        'email': 'new_email@example.com',
        'level': 2,
        'xp': 100
    }
    profile = profile_manager.update_profile('test_user', update_data)
    assert profile is not None
    assert profile.email == 'new_email@example.com'
    assert profile.level == 2
    assert profile.xp == 100

def test_add_achievement(profile_manager):
    """Test adding an achievement to a profile."""
    # First create a profile
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    profile_manager.create_profile(user_data)
    
    # Add an achievement
    achievement = {
        'id': 'first_win',
        'title': 'First Victory',
        'description': 'Won your first hand',
        'date_earned': datetime.now().isoformat()
    }
    profile = profile_manager.add_achievement('test_user', achievement)
    assert profile is not None
    assert len(profile.achievements) == 1
    assert profile.achievements[0]['id'] == 'first_win'

def test_update_learning_progress(profile_manager):
    """Test updating learning progress."""
    # First create a profile
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    profile_manager.create_profile(user_data)
    
    # Update learning progress
    progress_data = {
        'concept_id': 'test_concept',
        'completed': True,
        'score': 5,
        'date_completed': datetime.now().isoformat()
    }
    profile = profile_manager.update_learning_progress('test_user', progress_data)
    assert profile is not None
    assert len(profile.learning_paths) == 1
    assert profile.learning_paths[0]['concept_id'] == 'test_concept'
    assert profile.learning_paths[0]['completed'] == True
    assert profile.learning_paths[0]['score'] == 5

def test_update_study_streak(profile_manager):
    """Test updating study streak."""
    # First create a profile
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    profile_manager.create_profile(user_data)
    
    # Update study streak
    profile = profile_manager.update_study_streak('test_user', datetime.now())
    assert profile is not None
    assert profile.study_streak == 1
    assert profile.last_study_date is not None

def test_get_learning_stats(profile_manager):
    """Test getting learning statistics."""
    # First create a profile
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    profile_manager.create_profile(user_data)
    
    # Add some learning progress
    progress_data = {
        'concept_id': 'test_concept',
        'completed': True,
        'score': 5,
        'date_completed': datetime.now().isoformat()
    }
    profile_manager.update_learning_progress('test_user', progress_data)
    
    # Get learning stats
    stats = profile_manager.get_learning_stats('test_user')
    assert stats['total_concepts'] == 1
    assert stats['completed_concepts'] == 1
    assert stats['average_score'] == 5.0
    assert stats['study_streak'] == 0
    assert stats['total_study_time'] == 0

def test_calculate_level(profile_manager):
    """Test calculating user level based on XP."""
    # Test different XP thresholds
    assert profile_manager._calculate_level(0) == 1
    assert profile_manager._calculate_level(100) == 2
    assert profile_manager._calculate_level(500) == 3
    assert profile_manager._calculate_level(1000) == 4
    assert profile_manager._calculate_level(2000) == 5

def test_persistence(profile_manager, setup_test_data):
    """Test that profiles are persisted correctly."""
    # Create a profile
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    profile_manager.create_profile(user_data)
    
    # Create new instance
    new_profiles_path = setup_test_data / "profiles.json"
    new_profile_manager = UserProfileManager(str(new_profiles_path))
    
    # Check that profile is still there
    profile = new_profile_manager.get_profile('test_user')
    assert profile is not None
    assert profile.username == 'test_user'
    assert profile.email == 'test@example.com'

def test_invalid_profile_data(profile_manager):
    """Test handling of invalid profile data."""
    # Missing required fields
    user_data = {
        'username': 'test_user'
    }
    profile = profile_manager.create_profile(user_data)
    assert profile is None
    
    # Invalid email format
    user_data = {
        'username': 'test_user',
        'email': 'invalid_email',
        'password': 'test_password'
    }
    profile = profile_manager.create_profile(user_data)
    assert profile is None

def test_nonexistent_user(profile_manager):
    """Test handling of nonexistent user."""
    # Try to get profile
    profile = profile_manager.get_profile('nonexistent_user')
    assert profile is None
    
    # Try to update profile
    profile = profile_manager.update_profile('nonexistent_user', {'email': 'new@example.com'})
    assert profile is None
    
    # Try to add achievement
    profile = profile_manager.add_achievement('nonexistent_user', {'id': 'test'})
    assert profile is None
    
    # Try to update learning progress
    profile = profile_manager.update_learning_progress('nonexistent_user', {'concept_id': 'test'})
    assert profile is None 