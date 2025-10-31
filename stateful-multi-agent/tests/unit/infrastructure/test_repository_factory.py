"""
Unit tests for RepositoryFactory.
"""

import pytest

from infrastructure.repositories.factory import RepositoryFactory
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.course_repository import CourseRepository
from infrastructure.repositories.policy_repository import PolicyRepository
from infrastructure.repositories.order_repository import OrderRepository
from infrastructure.repositories.access_repository import AccessRepository


class TestRepositoryFactory:
    """Test RepositoryFactory."""
    
    def test_create_user_repository(self):
        """Test creating user repository."""
        # Reset factory to ensure clean state
        RepositoryFactory.reset_factory()
        
        user_repo = RepositoryFactory.create_user_repository()
        assert isinstance(user_repo, UserRepository)
        
        # Test singleton behavior
        user_repo2 = RepositoryFactory.create_user_repository()
        assert user_repo is user_repo2
    
    def test_create_course_repository(self):
        """Test creating course repository."""
        RepositoryFactory.reset_factory()
        
        course_repo = RepositoryFactory.create_course_repository()
        assert isinstance(course_repo, CourseRepository)
        
        # Test singleton behavior
        course_repo2 = RepositoryFactory.create_course_repository()
        assert course_repo is course_repo2
    
    def test_create_policy_repository(self):
        """Test creating policy repository."""
        RepositoryFactory.reset_factory()
        
        policy_repo = RepositoryFactory.create_policy_repository()
        assert isinstance(policy_repo, PolicyRepository)
        
        # Test singleton behavior
        policy_repo2 = RepositoryFactory.create_policy_repository()
        assert policy_repo is policy_repo2
    
    def test_create_order_repository(self):
        """Test creating order repository."""
        RepositoryFactory.reset_factory()
        
        order_repo = RepositoryFactory.create_order_repository()
        assert isinstance(order_repo, OrderRepository)
        
        # Test singleton behavior
        order_repo2 = RepositoryFactory.create_order_repository()
        assert order_repo is order_repo2
    
    def test_create_access_repository(self):
        """Test creating access repository."""
        RepositoryFactory.reset_factory()
        
        access_repo = RepositoryFactory.create_access_repository()
        assert isinstance(access_repo, AccessRepository)
        
        # Test singleton behavior
        access_repo2 = RepositoryFactory.create_access_repository()
        assert access_repo is access_repo2
    
    def test_get_all_repositories(self):
        """Test getting all repository instances."""
        RepositoryFactory.reset_factory()
        
        # Create all repositories
        user_repo = RepositoryFactory.create_user_repository()
        course_repo = RepositoryFactory.create_course_repository()
        policy_repo = RepositoryFactory.create_policy_repository()
        order_repo = RepositoryFactory.create_order_repository()
        access_repo = RepositoryFactory.create_access_repository()
        
        all_repos = RepositoryFactory.get_all_repositories()
        
        assert len(all_repos) == 5
        assert 'user_repository' in all_repos
        assert 'course_repository' in all_repos
        assert 'policy_repository' in all_repos
        assert 'order_repository' in all_repos
        assert 'access_repository' in all_repos
        
        assert all_repos['user_repository'] is user_repo
        assert all_repos['course_repository'] is course_repo
        assert all_repos['policy_repository'] is policy_repo
        assert all_repos['order_repository'] is order_repo
        assert all_repos['access_repository'] is access_repo
    
    def test_clear_all_repositories(self):
        """Test clearing all repository instances."""
        RepositoryFactory.reset_factory()
        
        # Create repositories and add some data
        user_repo = RepositoryFactory.create_user_repository()
        course_repo = RepositoryFactory.create_course_repository()
        
        # Add some test data
        from domain.users.aggregates import User
        from domain.users.value_objects import UserProfile, UserStatus
        from domain.shared.value_objects import UserId, EmailAddress, Name
        
        test_user = User(
            id=UserId("test_user"),
            email=EmailAddress("test@example.com"),
            profile=UserProfile(
                first_name=Name("Test"),
                last_name=Name("User")
            ),
            status=UserStatus.ACTIVE
        )
        user_repo.save(test_user)
        
        assert user_repo.count() == 1
        assert course_repo.count() == 0
        
        # Clear all repositories
        RepositoryFactory.clear_all_repositories()
        
        # Check that data is cleared
        assert user_repo.count() == 0
        assert course_repo.count() == 0
        
        # Check that instances still exist (singleton behavior)
        user_repo2 = RepositoryFactory.create_user_repository()
        assert user_repo is user_repo2
    
    def test_reset_factory(self):
        """Test resetting factory to initial state."""
        RepositoryFactory.reset_factory()
        
        # Create repositories
        user_repo = RepositoryFactory.create_user_repository()
        course_repo = RepositoryFactory.create_course_repository()
        
        # Add some data
        from domain.users.aggregates import User
        from domain.users.value_objects import UserProfile, UserStatus
        from domain.shared.value_objects import UserId, EmailAddress, Name
        
        test_user = User(
            id=UserId("test_user"),
            email=EmailAddress("test@example.com"),
            profile=UserProfile(
                first_name=Name("Test"),
                last_name=Name("User")
            ),
            status=UserStatus.ACTIVE
        )
        user_repo.save(test_user)
        
        assert user_repo.count() == 1
        
        # Reset factory
        RepositoryFactory.reset_factory()
        
        # Check that instances are cleared
        all_repos = RepositoryFactory.get_all_repositories()
        assert len(all_repos) == 0
        
        # Create new repositories
        new_user_repo = RepositoryFactory.create_user_repository()
        new_course_repo = RepositoryFactory.create_course_repository()
        
        # These should be new instances
        assert new_user_repo is not user_repo
        assert new_course_repo is not course_repo
        assert new_user_repo.count() == 0
        assert new_course_repo.count() == 0
    
    def test_repository_independence(self):
        """Test that different repository types are independent."""
        RepositoryFactory.reset_factory()
        
        user_repo = RepositoryFactory.create_user_repository()
        course_repo = RepositoryFactory.create_course_repository()
        policy_repo = RepositoryFactory.create_policy_repository()
        order_repo = RepositoryFactory.create_order_repository()
        access_repo = RepositoryFactory.create_access_repository()
        
        # All should be different instances
        assert user_repo is not course_repo
        assert user_repo is not policy_repo
        assert user_repo is not order_repo
        assert user_repo is not access_repo
        assert course_repo is not policy_repo
        assert course_repo is not order_repo
        assert course_repo is not access_repo
        assert policy_repo is not order_repo
        assert policy_repo is not access_repo
        assert order_repo is not access_repo
    
    def test_factory_persistence_across_calls(self):
        """Test that factory maintains state across multiple calls."""
        RepositoryFactory.reset_factory()
        
        # Create repositories
        user_repo1 = RepositoryFactory.create_user_repository()
        course_repo1 = RepositoryFactory.create_course_repository()
        
        # Create them again
        user_repo2 = RepositoryFactory.create_user_repository()
        course_repo2 = RepositoryFactory.create_course_repository()
        
        # Should be the same instances
        assert user_repo1 is user_repo2
        assert course_repo1 is course_repo2
        
        # Add data to one
        from domain.users.aggregates import User
        from domain.users.value_objects import UserProfile, UserStatus
        from domain.shared.value_objects import UserId, EmailAddress, Name
        
        test_user = User(
            id=UserId("test_user"),
            email=EmailAddress("test@example.com"),
            profile=UserProfile(
                first_name=Name("Test"),
                last_name=Name("User")
            ),
            status=UserStatus.ACTIVE
        )
        user_repo1.save(test_user)
        
        # Data should be available in the other reference
        assert user_repo2.count() == 1
        assert user_repo2.get_by_id(test_user.id) == test_user
