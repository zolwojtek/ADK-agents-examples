"""
Access repository interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..shared.value_objects import AccessId, UserId, CourseId
from .aggregates import AccessRecord


class AccessRepository(ABC):
    """Repository interface for AccessRecord aggregate."""
    
    @abstractmethod
    def save(self, access: AccessRecord) -> None:
        """Save access record aggregate."""
        pass
    
    @abstractmethod
    def find_by_id(self, access_id: AccessId) -> Optional[AccessRecord]:
        """Find access record by ID."""
        pass
    
    @abstractmethod
    def find_by_user_and_course(self, user_id: UserId, course_id: CourseId) -> Optional[AccessRecord]:
        """Find access record by user and course."""
        pass
    
    @abstractmethod
    def list_by_user(self, user_id: UserId) -> List[AccessRecord]:
        """List access records by user."""
        pass
    
    @abstractmethod
    def revoke(self, access_id: AccessId, reason: str) -> None:
        """Revoke access record."""
        pass
