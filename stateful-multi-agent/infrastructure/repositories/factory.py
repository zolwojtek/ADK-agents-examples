"""
Repository factory for dependency injection.
"""

from typing import Dict, Any
from .base import BaseRepository
from .user_repository import UserRepository
from .course_repository import CourseRepository
from .policy_repository import PolicyRepository
from .order_repository import OrderRepository
from .access_repository import AccessRepository


class RepositoryFactory:
    """Factory for creating repository instances."""
    
    _instances: Dict[str, BaseRepository] = {}
    
    @classmethod
    def create_user_repository(cls) -> UserRepository:
        """Create or get UserRepository instance."""
        if 'user_repository' not in cls._instances:
            cls._instances['user_repository'] = UserRepository()
        return cls._instances['user_repository']
    
    @classmethod
    def create_course_repository(cls) -> CourseRepository:
        """Create or get CourseRepository instance."""
        if 'course_repository' not in cls._instances:
            cls._instances['course_repository'] = CourseRepository()
        return cls._instances['course_repository']
    
    @classmethod
    def create_policy_repository(cls) -> PolicyRepository:
        """Create or get PolicyRepository instance."""
        if 'policy_repository' not in cls._instances:
            cls._instances['policy_repository'] = PolicyRepository()
        return cls._instances['policy_repository']
    
    @classmethod
    def create_order_repository(cls) -> OrderRepository:
        """Create or get OrderRepository instance."""
        if 'order_repository' not in cls._instances:
            cls._instances['order_repository'] = OrderRepository()
        return cls._instances['order_repository']
    
    @classmethod
    def create_access_repository(cls) -> AccessRepository:
        """Create or get AccessRepository instance."""
        if 'access_repository' not in cls._instances:
            cls._instances['access_repository'] = AccessRepository()
        return cls._instances['access_repository']
    
    @classmethod
    def get_all_repositories(cls) -> Dict[str, BaseRepository]:
        """Get all repository instances."""
        return cls._instances.copy()
    
    @classmethod
    def clear_all_repositories(cls) -> None:
        """Clear all repository data but keep instances."""
        for repository in cls._instances.values():
            if hasattr(repository, 'clear'):
                repository.clear()
    
    @classmethod
    def reset_factory(cls) -> None:
        """Reset factory to initial state."""
        cls.clear_all_repositories()
        cls._instances.clear()
