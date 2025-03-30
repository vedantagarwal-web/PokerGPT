import pytest
from flask import Flask
from src.web.app import app
import json
from datetime import datetime
from src.core.poker import Card, Hand, Board, Suit, Rank

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test the home page route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'PokerGPT' in response.data

def test_analyze_page(client):
    """Test the analyze page route."""
    response = client.get('/analyze')
    assert response.status_code == 302  # Should redirect to login
    
    # Test with logged in user
    with client.session_transaction() as session:
        session['user_id'] = 'test_user'
    
    response = client.get('/analyze')
    assert response.status_code == 200
    assert b'Hand Analysis' in response.data

def test_learn_page(client):
    """Test the learn page route."""
    response = client.get('/learn')
    assert response.status_code == 302  # Should redirect to login
    
    # Test with logged in user
    with client.session_transaction() as session:
        session['user_id'] = 'test_user'
    
    response = client.get('/learn')
    assert response.status_code == 200
    assert b'Learning Paths' in response.data

def test_profile_page(client):
    """Test the profile page route."""
    response = client.get('/profile')
    assert response.status_code == 302  # Should redirect to login
    
    # Test with logged in user
    with client.session_transaction() as session:
        session['user_id'] = 'test_user'
    
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'User Profile' in response.data

def test_user_registration(client):
    """Test user registration API."""
    data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    
    response = client.post('/api/register', json=data)
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['username'] == 'test_user'
    
    # Test duplicate registration
    response = client.post('/api/register', json=data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_user_login(client):
    """Test user login API."""
    # First register a user
    data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }
    client.post('/api/register', json=data)
    
    # Test login with correct credentials
    login_data = {
        'username': 'test_user',
        'password': 'test_password'
    }
    response = client.post('/api/login', json=login_data)
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['username'] == 'test_user'
    
    # Test login with incorrect password
    login_data['password'] = 'wrong_password'
    response = client.post('/api/login', json=login_data)
    assert response.status_code == 401
    assert 'error' in response.json

def test_user_logout(client):
    """Test user logout API."""
    # First login
    with client.session_transaction() as session:
        session['user_id'] = 'test_user'
    
    response = client.get('/api/logout')
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Verify session is cleared
    with client.session_transaction() as session:
        assert 'user_id' not in session

def test_update_learning_progress(client):
    """Test updating learning progress API."""
    # First login
    with client.session_transaction() as session:
        session['user_id'] = 'test_user'
    
    data = {
        'concept_id': 'test_concept',
        'completed': True,
        'score': 5
    }
    
    response = client.post('/api/learn/progress', json=data)
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Test with missing concept_id
    data = {'completed': True, 'score': 5}
    response = client.post('/api/learn/progress', json=data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_record_review(client):
    """Test recording review API."""
    # First login
    with client.session_transaction() as session:
        session['user_id'] = 'test_user'
    
    data = {
        'concept_id': 'test_concept',
        'difficulty': 5,
        'next_review': datetime.now().isoformat()
    }
    
    response = client.post('/api/review', json=data)
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Test with missing fields
    data = {'concept_id': 'test_concept'}
    response = client.post('/api/review', json=data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_record_activity(client):
    """Test recording activity API."""
    # First login
    with client.session_transaction() as session:
        session['user_id'] = 'test_user'
    
    data = {
        'activity_type': 'study',
        'concept_id': 'test_concept',
        'duration': 30
    }
    
    response = client.post('/api/activity', json=data)
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Test with missing fields
    data = {'activity_type': 'study'}
    response = client.post('/api/activity', json=data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_hand_analysis_api(client):
    """Test hand analysis API."""
    # First login
    with client.session_transaction() as session:
        session['user_id'] = 'test_user'
    
    data = {
        'hand': 'Ah Kd',
        'board': '2h 3h 4h',
        'position': 'BTN',
        'opponents': 1,
        'stack_size': 100
    }
    
    response = client.post('/analyze', json=data)
    assert response.status_code == 200
    assert 'action' in response.json
    assert 'equity' in response.json
    assert 'explanation' in response.json
    
    # Test with missing fields
    data = {'hand': 'Ah Kd'}
    response = client.post('/analyze', json=data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_learning_progress_api(client):
    """Test the learning progress API endpoint."""
    data = {
        'concept_id': 'preflop_position',
        'completed': True,
        'score': 0.8
    }
    response = client.post('/api/learn/progress', json=data)
    assert response.status_code == 200
    result = response.get_json()
    assert 'success' in result
    assert result['success'] is True

def test_review_api(client):
    """Test the review API endpoint."""
    data = {
        'concept_id': 'preflop_position',
        'difficulty': 3,
        'next_review': '2024-03-20'
    }
    response = client.post('/api/review', json=data)
    assert response.status_code == 200
    result = response.get_json()
    assert 'success' in result
    assert result['success'] is True

def test_activity_api(client):
    """Test the activity API endpoint."""
    data = {
        'activity_type': 'study',
        'concept_id': 'preflop_position',
        'duration': 30
    }
    response = client.post('/api/activity', json=data)
    assert response.status_code == 200
    result = response.get_json()
    assert 'success' in result
    assert result['success'] is True

def test_error_handling(client):
    """Test error handling in the application."""
    # Test invalid hand analysis request
    data = {
        'hand': 'invalid',
        'board': 'invalid',
        'position': 'invalid'
    }
    response = client.post('/api/analyze', json=data)
    assert response.status_code == 400
    result = response.get_json()
    assert 'error' in result

    # Test invalid concept ID
    data = {
        'concept_id': 'invalid_concept',
        'completed': True
    }
    response = client.post('/api/learn/progress', json=data)
    assert response.status_code == 404
    result = response.get_json()
    assert 'error' in result 