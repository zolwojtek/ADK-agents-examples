"""
Unit tests for UserRepository implementation.
"""

import pytest
from uuid import uuid4

from infrastructure.repositories.user_repository import UserRepository
from domain.users.aggregates import User
from domain.users.value_objects import UserProfile, UserStatus
from domain.shared.value_objects import UserId, EmailAddress, Name


class TestUserRepository:
    """Test UserRepository implementation."""
    
    @pytest.fixture
    def user_repository(self):
        """Create a test user repository."""
        return UserRepository()
    
    @pytest.fixture
    def user_profile(self):
        """Create a test user profile."""
        return UserProfile(
            first_name=Name("John"),
            last_name=Name("Doe"),
        )
    
    @pytest.fixture
    def user(self, user_profile):
        """Create a test user."""
        return User(
            id=UserId(str(uuid4())),
            profile=user_profile,
            status=UserStatus.ACTIVE,
            email=EmailAddress("john.doe@example.com")
        )
    
    def test_save_user(self, user_repository, user):
        """Test saving a user."""
        saved_user = user_repository.save(user)
        
        assert saved_user == user
        assert user_repository.get_by_id(user.id) == user
        assert user_repository.count() == 1
    
    def test_get_by_id(self, user_repository, user):
        """Test getting user by ID."""
        user_repository.save(user)
        
        retrieved_user = user_repository.get_by_id(user.id)
        assert retrieved_user == user
        
        non_existent_id = UserId(str(uuid4()))
        assert user_repository.get_by_id(non_existent_id) is None
    
    def test_get_by_email(self, user_repository, user):
        """Test getting user by email."""
        user_repository.save(user)
        
        retrieved_user = user_repository.get_by_email(user.email)
        assert retrieved_user == user
        
        non_existent_email = EmailAddress("nonexistent@example.com")
        assert user_repository.get_by_email(non_existent_email) is None
    
    def test_get_by_name(self, user_repository, user):
        """Test getting users by name."""
        user_repository.save(user)
        
        users = user_repository.get_by_name("John", "Doe")
        assert len(users) == 1
        assert users[0] == user
        
        users = user_repository.get_by_name("Jane", "Smith")
        assert len(users) == 0
    
    def test_search_by_name(self, user_repository, user):
        """Test searching users by name."""
        user_repository.save(user)
        
        # Search by first name
        users = user_repository.search_by_name("John")
        assert len(users) == 1
        assert users[0] == user
        
        # Search by last name
        users = user_repository.search_by_name("Doe")
        assert len(users) == 1
        assert users[0] == user
        
        # Case insensitive search
        users = user_repository.search_by_name("john")
        assert len(users) == 1
        assert users[0] == user
        
        # Partial match
        users = user_repository.search_by_name("Jo")
        assert len(users) == 1
        assert users[0] == user
        
        # No match
        users = user_repository.search_by_name("Jane")
        assert len(users) == 0
    
    def test_email_uniqueness(self, user_repository, user):
        """Test email uniqueness constraint."""
        user_repository.save(user)
        
        # Try to save another user with same email
        duplicate_user = User(
            id=UserId(str(uuid4())),
            email=user.email, # Same email
            profile=UserProfile(
                first_name=Name("Jane"),
                last_name=Name("Smith"),
            ),
            status=UserStatus.ACTIVE
        )
        
        with pytest.raises(ValueError, match="Email .* already exists"):
            user_repository.save(duplicate_user)
    
    def test_update_user_email(self, user_repository, user):
        """Test updating user email."""
        user_repository.save(user)
        
        new_email = EmailAddress("new.email@example.com")
        user.email = new_email
        
        updated_user = user_repository.save(user)
        assert updated_user.email == new_email
        assert user_repository.get_by_email(new_email) == user
        assert user_repository.get_by_email(EmailAddress("john.doe@example.com")) is None
    
    def test_delete_user(self, user_repository, user):
        """Test deleting user."""
        user_repository.save(user)
        assert user_repository.count() == 1
        
        result = user_repository.delete(user.id)
        assert result is True
        assert user_repository.count() == 0
        assert user_repository.get_by_id(user.id) is None
        assert user_repository.get_by_email(user.email) is None
        
        # Try to delete non-existent user
        result = user_repository.delete(UserId(str(uuid4())))
        assert result is False
    
    def test_get_all_users(self, user_repository, user):
        """Test getting all users."""
        user_repository.save(user)
        
        users = user_repository.get_all()
        assert len(users) == 1
        assert users[0] == user
    
    def test_exists(self, user_repository, user):
        """Test checking if user exists."""
        assert not user_repository.exists(user.id)
        
        user_repository.save(user)
        assert user_repository.exists(user.id)
    
    def test_clear_repository(self, user_repository, user):
        """Test clearing repository."""
        user_repository.save(user)
        assert user_repository.count() == 1
        
        user_repository.clear()
        assert user_repository.count() == 0
        assert user_repository.get_by_id(user.id) is None
    
    def test_multiple_users(self, user_repository):
        """Test repository with multiple users."""
        user1 = User(
            id=UserId(str(uuid4())),
            profile=UserProfile(
                first_name=Name("John"),
                last_name=Name("Doe"),
            ),
            status=UserStatus.ACTIVE,
            email=EmailAddress("john.doe@example.com")
        )
        
        user2 = User(
            id=UserId(str(uuid4())),
            profile=UserProfile(
                first_name=Name("Jane"),
                last_name=Name("Smith"),
            ),
            status=UserStatus.ACTIVE,
            email=EmailAddress("jane.smith@example.com")
        )
        
        user_repository.save(user1)
        user_repository.save(user2)
        
        assert user_repository.count() == 2
        assert user_repository.get_by_email(user1.email) == user1
        assert user_repository.get_by_email(user2.email) == user2
        
        # Search by name
        johns = user_repository.search_by_name("John")
        assert len(johns) == 1
        assert johns[0] == user1
        
        # Get all users
        all_users = user_repository.get_all()
        assert len(all_users) == 2
        assert user1 in all_users
        assert user2 in all_users
