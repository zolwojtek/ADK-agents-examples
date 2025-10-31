"""
Course repository interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..shared.value_objects import CourseId, PolicyId
from .aggregates import Course


class CourseRepository(ABC):
    """Repository interface for Course aggregate."""
    
    @abstractmethod
    def save(self, course: Course) -> None:
        """Save course aggregate."""
        pass
    
    @abstractmethod
    def find_by_id(self, course_id: CourseId) -> Optional[Course]:
        """Find course by ID."""
        pass
    
    @abstractmethod
    def list_by_policy(self, policy_id: PolicyId) -> List[Course]:
        """List courses by refund policy."""
        pass
    
    @abstractmethod
    def search_by_criteria(self, criteria: dict) -> List[Course]:
        """Search courses by criteria."""
        pass
