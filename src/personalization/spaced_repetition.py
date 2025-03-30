from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import os
import math
from src.config import (
    INITIAL_INTERVAL,
    INITIAL_EASE_FACTOR,
    MIN_EASE_FACTOR,
    MAX_EASE_FACTOR
)

@dataclass
class Review:
    """Represents a review of a concept."""
    concept_id: str
    difficulty: int  # 0-5, where 0 is "again" and 5 is "easy"
    next_review: str  # ISO format datetime
    interval: int  # Days until next review
    ease_factor: float
    repetitions: int

class SpacedRepetition:
    """Manages spaced repetition learning for poker concepts."""
    
    def __init__(self, reviews_file: str):
        """Initialize the spaced repetition system.
        
        Args:
            reviews_file: Path to the JSON file storing review data.
        """
        self.reviews_file = reviews_file
        self.reviews = self._load_reviews()
    
    def _load_reviews(self) -> Dict:
        """Load reviews from file."""
        if os.path.exists(self.reviews_file):
            with open(self.reviews_file, 'r') as f:
                return json.load(f)
        return {'reviews': {}}
    
    def _save_reviews(self):
        """Save reviews to file."""
        os.makedirs(os.path.dirname(self.reviews_file), exist_ok=True)
        with open(self.reviews_file, 'w') as f:
            json.dump(self.reviews, f, indent=2)
    
    def add_review(self, username: str, review_data: Dict) -> bool:
        """Add a new review for a user."""
        if username not in self.reviews['reviews']:
            self.reviews['reviews'][username] = []
        
        review_data['timestamp'] = datetime.now().isoformat()
        self.reviews['reviews'][username].append(review_data)
        self._save_reviews()
        return True
    
    def get_review_stats(self, username: str) -> Dict:
        """Get review statistics for a user."""
        if username not in self.reviews['reviews']:
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'next_review': None
            }

        user_reviews = self.reviews['reviews'][username]
        
        # Calculate total reviews
        total_reviews = len(user_reviews)
        
        # Calculate average rating (1-5 scale)
        ratings = [review.get('difficulty', 3) for review in user_reviews]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Find next review date
        next_review = None
        for review in user_reviews:
            review_date = datetime.fromisoformat(review['next_review'])
            if review_date > datetime.now():
                if next_review is None or review_date < next_review:
                    next_review = review_date
        
        return {
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 1),
            'next_review': next_review.strftime('%Y-%m-%d') if next_review else None
        }
    
    def get_due_reviews(self, username: str) -> List[Dict]:
        """Get all reviews due for a user."""
        if username not in self.reviews['reviews']:
            return []

        now = datetime.now()
        due_reviews = []
        
        for review in self.reviews['reviews'][username]:
            next_review = datetime.fromisoformat(review['next_review'])
            if next_review <= now:
                due_reviews.append(review)
        
        return due_reviews
    
    def update_review(self, username: str, concept_id: str, difficulty: int) -> bool:
        """Update a review based on user performance."""
        if username not in self.reviews['reviews']:
            return False

        # Find the review
        review = None
        for r in self.reviews['reviews'][username]:
            if r['concept_id'] == concept_id:
                review = r
                break

        if not review:
            return False

        # Update review parameters
        review['repetitions'] += 1
        review['difficulty'] = difficulty
        
        # Calculate new interval using SuperMemo 2 algorithm
        if difficulty >= 3:  # Good response
            review['ease_factor'] = max(1.3, review['ease_factor'] + (0.1 - (5 - difficulty) * (0.08 + (5 - difficulty) * 0.02)))
            review['interval'] = review['interval'] * review['ease_factor']
        else:  # Poor response
            review['ease_factor'] = max(1.3, review['ease_factor'] + (0.1 - (5 - difficulty) * (0.08 + (5 - difficulty) * 0.02)))
            review['interval'] = 1  # Reset interval

        # Set next review date
        review['next_review'] = (datetime.now() + timedelta(days=review['interval'])).isoformat()
        
        self._save_reviews()
        return True
    
    def get_review_history(self, username: str, concept_id: str) -> List[Dict]:
        """Get the review history for a specific concept.
        
        Args:
            username: The username to get history for.
            concept_id: The ID of the concept.
            
        Returns:
            List of dictionaries containing review history.
        """
        if username not in self.reviews['reviews'] or concept_id not in self.reviews['reviews'][username]:
            return []
        
        review = self.reviews['reviews'][username][concept_id]
        return [{
            'difficulty': review['difficulty'],
            'repetitions': review['repetitions'],
            'interval': review['interval'],
            'ease_factor': review['ease_factor']
        }]
    
    def reset_review(self, username: str, concept_id: str) -> Optional[Review]:
        """Reset a review to its initial state.
        
        Args:
            username: The username of the reviewer.
            concept_id: The ID of the concept to reset.
            
        Returns:
            The reset Review object, or None if reset failed.
        """
        if username not in self.reviews['reviews'] or concept_id not in self.reviews['reviews'][username]:
            return None
        
        # Create new review with initial values
        review = Review(
            concept_id=concept_id,
            difficulty=3,
            next_review=datetime.now().isoformat(),
            interval=1,
            ease_factor=2.5,
            repetitions=0
        )
        
        self.reviews['reviews'][username][concept_id] = review
        self._save_reviews()
        return review

    def get_all_stats(self, user_id: str) -> Dict[str, Dict]:
        """Get statistics for all concepts."""
        return {
            concept_id: self.get_concept_stats(user_id, concept_id)
            for concept_id in self.reviews['reviews'][user_id]
        }
    
    def get_due_count(self, user_id: str) -> int:
        """Get number of concepts due for review."""
        return len(self.get_due_reviews(user_id))
    
    def get_mastery_level(self, user_id: str, concept_id: str) -> Optional[float]:
        """Get mastery level (0-100) for a concept."""
        if user_id not in self.reviews or concept_id not in self.reviews[user_id]:
            return None
        review = self.reviews[user_id][concept_id]
        return self._calculate_mastery(review)
    
    def get_review_schedule(self, user_id: str) -> List[Dict]:
        """Get upcoming review schedule for all concepts."""
        if user_id not in self.reviews:
            return []
        
        now = datetime.now()
        schedule = []
        
        for concept_id, review in self.reviews[user_id].items():
            days_until_review = (datetime.fromisoformat(review.next_review) - now).days
            if days_until_review > 0:
                schedule.append({
                    'concept_id': concept_id,
                    'days_until_review': days_until_review,
                    'mastery_level': self._calculate_mastery(review)
                })
        
        return sorted(schedule, key=lambda x: x['days_until_review'])
    
    def get_concept_history(self, user_id: str, concept_id: str) -> List[Dict]:
        """Get review history for a concept."""
        if user_id not in self.reviews or concept_id not in self.reviews[user_id]:
            return []
        
        review = self.reviews[user_id][concept_id]
        history = []
        
        history.append({
            'difficulty': review.difficulty,
            'repetitions': review.repetitions,
            'interval': review.interval,
            'ease_factor': review.ease_factor
        })
        
        return history
    
    def get_concept_stats(self, user_id: str, concept_id: str) -> Optional[Dict]:
        """Get statistics for a concept."""
        if user_id not in self.reviews or concept_id not in self.reviews[user_id]:
            return None
        
        review = self.reviews[user_id][concept_id]
        return {
            'next_review': review.next_review,
            'interval': review.interval,
            'ease_factor': review.ease_factor,
            'repetitions': review.repetitions,
            'difficulty': review.difficulty,
            'mastery_level': self._calculate_mastery(review)
        }
    
    def _calculate_mastery(self, review: Review) -> float:
        """Calculate mastery level (0-100) for a concept."""
        # Base mastery on ease factor and repetitions
        base_mastery = min(100, (review.ease_factor / MAX_EASE_FACTOR) * 100)
        
        # Adjust based on difficulty
        difficulty_factor = (5 - review.difficulty) / 5
        
        # Adjust based on number of successful repetitions
        repetition_factor = min(1, review.repetitions / 10)
        
        return base_mastery * difficulty_factor * repetition_factor 