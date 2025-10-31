"""
Unit tests for User aggregate.
"""

import pytest
from uuid import uuid4

from domain.users.aggregates import User
from domain.users.value_objects import UserProfile, UserStatus
from domain.shared.value_objects import UserId, EmailAddress, Name


class TestUserAggregate:
    """Test User aggregate."""
    
    @pytest.fixture
    def user_profile(self):
        """Create a test user profile."""
        return UserProfile(
            first_name=Name("John"),
            last_name=Name("Doe")
        )
    
    @pytest.fixture
    def user(self, user_profile):
        """Create a test user."""
        return User(
            id=UserId(str(uuid4())),
            email=EmailAddress("john.doe@example.com"),
            profile=user_profile
        )
    
    def test_create_user(self, user_profile):
        """Test creating a user."""
        user = User.create_user(
            email="john.doe@example.com",
            profile=user_profile
        )
        
        assert user.id is not None
        assert user.profile == user_profile
        assert user.status == UserStatus.INACTIVE
        assert user.created_at is not None
        assert user.updated_at is not None
        domain_events = user.get_domain_events()
        assert len(domain_events) == 1
        assert domain_events[0].__class__.__name__ == "UserRegistered"
    
    def test_verify_identity(self, user):
        """Test verifying user identity."""
        user.verify_identity()
        
        assert user.status == UserStatus.ACTIVE
        assert user.email_verified is True
    
    def test_update_profile(self, user):
        """Test updating user profile."""
        new_profile = UserProfile(
            first_name=Name("Jane"),
            last_name=Name("Smith"),
        )
        
        user.update_profile(new_profile)
        
        assert user.profile == new_profile
        assert user.updated_at > user.created_at
        domain_events = user.get_domain_events()
        assert len(domain_events) == 1
        assert domain_events[0].__class__.__name__ == "UserProfileUpdated"
    
    def test_change_email(self, user):
        """Test changing user email."""
        new_email = EmailAddress("new.email@example.com")
        
        user.change_email(new_email)
        
        assert user.email == new_email
        assert user.updated_at > user.created_at
        domain_events = user.get_domain_events()
        assert len(domain_events) == 1
        assert domain_events[0].__class__.__name__ == "UserEmailChanged"
    
    def test_deactivate_user(self, user):
        """Test deactivating user."""
        user.deactivate("Reason for deactivation")
        
        assert user.status == UserStatus.INACTIVE
    
    def test_reactivate_user(self, user):
        """Test reactivating user."""
        user.status = UserStatus.INACTIVE
        user.activate()
        
        assert user.status == UserStatus.ACTIVE
    
    def test_clear_domain_events(self, user):
        """Test clearing domain events."""
        user.update_profile(user.profile)  # Generate an event
        
        assert len(user.get_domain_events()) == 1
        user.clear_domain_events()
        assert len(user.get_domain_events()) == 0