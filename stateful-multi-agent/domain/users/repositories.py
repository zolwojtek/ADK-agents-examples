"""
User repository interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..shared.value_objects import UserId, EmailAddress
from .aggregates import User


class UserRepository(ABC):
    """Repository interface for User aggregate."""
    
    @abstractmethod
    def save(self, user: User) -> None:
        """Save user aggregate."""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    def get_by_email(self, email: EmailAddress) -> Optional[User]:
        """Get user by email address."""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if user exists by email."""
        pass
