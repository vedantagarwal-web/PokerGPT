from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json
import os
from enum import Enum

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class Concept:
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    prerequisites: List[str]
    explanations: Dict[DifficultyLevel, str]
    examples: List[Dict[str, str]]
    related_concepts: List[str]

class PokerKnowledge:
    def __init__(self, knowledge_path: str):
        """Initialize poker knowledge base with a path to the knowledge database."""
        self.knowledge_path = knowledge_path
        self.concepts = self._load_concepts()
    
    def _load_concepts(self) -> Dict:
        """Load poker concepts from database."""
        if not os.path.exists(self.knowledge_path):
            return {}
        
        with open(self.knowledge_path, 'r') as f:
            return json.load(f)
    
    def _save_concepts(self) -> None:
        """Save poker concepts to database."""
        with open(self.knowledge_path, 'w') as f:
            json.dump(self.concepts, f)
    
    def get_concept(self, concept_id: str) -> Optional[Dict]:
        """Get a concept by ID."""
        return self.concepts.get(concept_id)
    
    def get_explanation(self, concept_id: str, 
                       difficulty: DifficultyLevel) -> str:
        """Get explanation for a concept at a specific difficulty level."""
        concept = self.get_concept(concept_id)
        if not concept:
            return ""
        
        return concept.get('explanations', {}).get(difficulty.value, "")
    
    def get_examples(self, concept_id: str) -> List[Dict]:
        """Get examples for a concept."""
        concept = self.get_concept(concept_id)
        if not concept:
            return []
        
        return concept.get('examples', [])
    
    def get_prerequisites(self, concept_id: str) -> List[str]:
        """Get prerequisites for a concept."""
        concept = self.get_concept(concept_id)
        if not concept:
            return []
        
        return concept.get('prerequisites', [])
    
    def get_learning_path(self, start_concept: str, 
                         end_concept: str) -> List[str]:
        """Get a learning path from start concept to end concept."""
        path = []
        current = end_concept
        
        while current and current != start_concept:
            path.append(current)
            prereqs = self.get_prerequisites(current)
            if not prereqs:
                break
            current = prereqs[0]  # Take first prerequisite
        
        if current == start_concept:
            path.append(start_concept)
            return list(reversed(path))
        
        return []
    
    def get_related_concepts(self, concept_id: str) -> List[str]:
        """Get related concepts for a concept."""
        concept = self.get_concept(concept_id)
        if not concept:
            return []
        
        return concept.get('related_concepts', [])
    
    def get_practice_questions(self, concept_id: str) -> List[Dict]:
        """Get practice questions for a concept."""
        concept = self.get_concept(concept_id)
        if not concept:
            return []
        
        return concept.get('practice_questions', [])
    
    def add_concept(self, concept_id: str, concept_data: Dict) -> None:
        """Add a new concept to the knowledge base."""
        self.concepts[concept_id] = concept_data
        self._save_concepts()
    
    def update_concept(self, concept_id: str, 
                      concept_data: Dict) -> None:
        """Update an existing concept."""
        if concept_id in self.concepts:
            self.concepts[concept_id].update(concept_data)
            self._save_concepts()
    
    def delete_concept(self, concept_id: str) -> None:
        """Delete a concept from the knowledge base."""
        if concept_id in self.concepts:
            del self.concepts[concept_id]
            self._save_concepts()
    
    def get_all_concepts(self) -> List[Dict]:
        """Get all concepts in the knowledge base."""
        return list(self.concepts.values())
    
    def get_concepts_by_difficulty(self, 
                                 difficulty: DifficultyLevel) -> List[Dict]:
        """Get all concepts at a specific difficulty level."""
        return [
            concept
            for concept in self.concepts.values()
            if concept.get('difficulty') == difficulty.value
        ]
    
    def get_concepts_by_category(self, category: str) -> List[Dict]:
        """Get all concepts in a specific category."""
        return [
            concept
            for concept in self.concepts.values()
            if concept.get('category') == category
        ]
    
    def search_concepts(self, query: str) -> List[Dict]:
        """Search concepts by title or description."""
        query = query.lower()
        return [
            concept
            for concept in self.concepts.values()
            if query in concept.get('title', '').lower() or
               query in concept.get('description', '').lower()
        ]

    def _build_concept_graph(self) -> Dict[str, Set[str]]:
        """Build a graph representation of concept relationships."""
        graph = {}
        for concept_id, concept in self.concepts.items():
            graph[concept_id] = set(concept.prerequisites + concept.related_concepts)
        return graph
    
    def get_learning_path(self, start_concept: str, target_concept: str) -> List[str]:
        """
        Returns ordered list of concepts to learn.
        
        Args:
            start_concept: Starting concept ID
            target_concept: Target concept ID
            
        Returns:
            List of concept IDs in learning order
        """
        if start_concept not in self.concepts or target_concept not in self.concepts:
            raise ValueError("Invalid concept ID")
        
        # Use breadth-first search to find the shortest path
        visited = {start_concept}
        queue = [(start_concept, [start_concept])]
        
        while queue:
            current, path = queue.pop(0)
            if current == target_concept:
                return path
            
            for next_concept in self.concept_graph[current]:
                if next_concept not in visited:
                    visited.add(next_concept)
                    queue.append((next_concept, path + [next_concept]))
        
        raise ValueError("No path found between concepts")
    
    def get_related_concepts(self, concept_id: str) -> List[str]:
        """Get list of related concepts for a given concept."""
        if concept_id not in self.concepts:
            raise ValueError(f"Concept {concept_id} not found")
        return self.concepts[concept_id].related_concepts
    
    def get_examples(self, concept_id: str) -> List[Dict[str, str]]:
        """Get example hands for a given concept."""
        if concept_id not in self.concepts:
            raise ValueError(f"Concept {concept_id} not found")
        return self.concepts[concept_id].examples
    
    def get_concepts_by_difficulty(self, difficulty: DifficultyLevel) -> List[str]:
        """Get all concepts at a given difficulty level."""
        return [
            concept_id
            for concept_id, concept in self.concepts.items()
            if concept.difficulty == difficulty
        ] 