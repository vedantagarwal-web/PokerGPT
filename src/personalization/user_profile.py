from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: Optional[datetime]

@dataclass
class LearningPath:
    id: str
    name: str
    description: str
    progress: float
    completed_concepts: List[str]
    current_concept: Optional[str]

@dataclass
class Activity:
    id: str
    title: str
    description: str
    timestamp: datetime
    type: str  # 'concept_completed', 'practice_completed', 'hand_analyzed'

class UserProfile(UserMixin):
    _profiles = {}
    _profiles_file = None

    def __init__(self, username, email, password_hash, level='beginner'):
        self.id = username
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.level = level
        self.learning_paths = []  # List of learning path progress
        self.achievements = []
        self.last_study_date = None
        self.study_streak = 0
        self.total_study_time = 0
        self.created_at = datetime.now()
        self.recent_activities = []

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'level': self.level,
            'learning_paths': self.learning_paths,
            'achievements': self.achievements,
            'last_study_date': self.last_study_date.isoformat() if self.last_study_date else None,
            'study_streak': self.study_streak,
            'total_study_time': self.total_study_time,
            'created_at': self.created_at.isoformat(),
            'recent_activities': self.recent_activities
        }

    @classmethod
    def from_dict(cls, data):
        profile = cls(
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            level=data.get('level', 'beginner')
        )
        profile.learning_paths = data.get('learning_paths', [])
        profile.achievements = data.get('achievements', [])
        last_study = data.get('last_study_date')
        profile.last_study_date = datetime.fromisoformat(last_study) if last_study else None
        profile.study_streak = data.get('study_streak', 0)
        profile.total_study_time = data.get('total_study_time', 0)
        profile.created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        profile.recent_activities = data.get('recent_activities', [])
        return profile

    @classmethod
    def set_profiles_file(cls, file_path):
        cls._profiles_file = file_path
        cls._load_profiles()

    @classmethod
    def _load_profiles(cls):
        if not cls._profiles_file:
            return

        if not os.path.exists(cls._profiles_file):
            cls._save_profiles()
            return

        try:
            with open(cls._profiles_file, 'r') as f:
                data = json.load(f)
                profiles = data.get('users', {})
                cls._profiles = {
                    username: cls.from_dict(profile_data)
                    for username, profile_data in profiles.items()
                }
        except (json.JSONDecodeError, FileNotFoundError):
            cls._profiles = {}

    @classmethod
    def _save_profiles(cls):
        if not cls._profiles_file:
            return

        data = {
            'users': {
                username: profile.to_dict()
                for username, profile in cls._profiles.items()
            }
        }
        
        os.makedirs(os.path.dirname(cls._profiles_file), exist_ok=True)
        with open(cls._profiles_file, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def create_profile(cls, username, email, password):
        if username in cls._profiles:
            return False

        profile = cls(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        cls._profiles[username] = profile
        cls._save_profiles()
        return True

    @classmethod
    def get_profile(cls, username):
        return cls._profiles.get(username)

    def update_profile(self, updates: Dict) -> bool:
        """Update user profile with new data."""
        try:
            for key, value in updates.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self._save_profiles()
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False

    def add_achievement(self, achievement):
        if achievement not in self.achievements:
            self.achievements.append(achievement)
            self._save_profiles()

    def get_learning_stats(self):
        """Get learning statistics for all paths."""
        stats = {}
        for i, path in enumerate(self.learning_paths):
            stats[i] = {
                'score': path.get('score', 0),
                'completed': path.get('completed', False),
                'concepts_completed': len(path.get('concepts', {})),
                'last_study': path.get('timestamp')
            }
        return stats

    def get_id(self):
        """Get the user's ID for Flask-Login."""
        return self.username

    def add_activity(self, activity_type: str, description: str):
        """Add a new activity to the recent activities list."""
        activity = {
            'type': activity_type,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        self.recent_activities.insert(0, activity)
        # Keep only the last 10 activities
        self.recent_activities = self.recent_activities[:10]
        self.update_profile({'recent_activities': self.recent_activities})

class UserProfileManager:
    """Manages user profiles in the system."""
    def __init__(self, profiles_file: str):
        self.profiles_file = profiles_file
        self.profiles: Dict[str, UserProfile] = {}
        self._load_profiles()

    def _load_profiles(self):
        """Load profiles from the file."""
        try:
            with open(self.profiles_file, 'r') as f:
                data = json.load(f)
                self.profiles = {
                    username: UserProfile.from_dict(profile_data)
                    for username, profile_data in data.get('users', {}).items()
                }
        except FileNotFoundError:
            # Create empty profiles file
            self._save_profiles()

    def _save_profiles(self):
        """Save profiles to the file."""
        with open(self.profiles_file, 'w') as f:
            json.dump({
                'users': {
                    username: profile.to_dict()
                    for username, profile in self.profiles.items()
                }
            }, f, indent=4)

    def create_profile(self, user_data: Dict) -> UserProfile:
        """Create a new user profile."""
        username = user_data['username']
        if username in self.profiles:
            raise ValueError(f"Username {username} already exists")

        profile = UserProfile(username, user_data['email'], user_data['password_hash'])
        self.profiles[username] = profile
        self._save_profiles()
        return profile

    def get_profile(self, username: str) -> Optional[UserProfile]:
        """Get a user's profile."""
        return self.profiles.get(username)

    def update_profile(self, username: str, updates: Dict) -> Optional[UserProfile]:
        """Update a user's profile."""
        profile = self.get_profile(username)
        if not profile:
            return None

        if 'email' in updates:
            profile.email = updates['email']
        if 'password_hash' in updates:
            profile.password_hash = updates['password_hash']
        if 'level' in updates:
            profile.level = updates['level']

        self._save_profiles()
        return profile

    def add_achievement(self, username: str, achievement: Dict) -> Optional[UserProfile]:
        """Add an achievement to a user's profile."""
        profile = self.get_profile(username)
        if not profile:
            return None

        profile.achievements.append(achievement)
        self._save_profiles()
        return profile

    def update_learning_progress(self, username: str, progress: Dict) -> Optional[UserProfile]:
        """Update a user's learning progress."""
        profile = self.get_profile(username)
        if not profile:
            return None

        path_id = progress['path_id']
        concept_id = progress['concept_id']
        score = progress['score']

        if path_id not in profile.learning_paths:
            profile.learning_paths.append({
                'concepts': {},
                'score': 0,
                'completed': False
            })

        # Update concept score
        profile.learning_paths[-1]['concepts'][concept_id] = score

        # Update overall path score
        concepts = profile.learning_paths[-1]['concepts']
        total_score = sum(concepts.values()) / len(concepts)
        profile.learning_paths[-1]['score'] = total_score
        profile.learning_paths[-1]['completed'] = total_score >= 0.8

        # Update study streak
        now = datetime.now()
        if profile.last_study_date:
            days_diff = (now - profile.last_study_date).days
            if days_diff == 1:
                profile.study_streak += 1
            elif days_diff > 1:
                profile.study_streak = 1
        else:
            profile.study_streak = 1

        profile.last_study_date = now
        profile.total_study_time += 10  # Assume 10 minutes per concept
        self._save_profiles()
        return profile

    def get_learning_stats(self, username: str) -> Dict:
        """Get learning statistics for a user."""
        profile = self.get_profile(username)
        if not profile:
            return {}

        return {
            path_id: {
                'score': path_data['score'],
                'completed': path_data['completed'],
                'concepts_completed': len(path_data['concepts']),
                'last_study': path_data['last_study']
            }
            for path_id, path_data in enumerate(profile.learning_paths)
        }

    def _calculate_level(self, xp: int) -> int:
        """Calculate user level based on XP."""
        # Simple level calculation: level = 1 + floor(xp/1000)
        return 1 + (xp // 1000) 