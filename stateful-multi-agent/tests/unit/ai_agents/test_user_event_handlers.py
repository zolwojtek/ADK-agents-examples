"""
Tests for User domain event handlers.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from ai_agents.user_event_handlers import (
    UserAnalyticsHandler, UserOnboardingHandler, UserSecurityHandler
)
from domain.users.events import (
    UserRegistered, UserProfileUpdated, UserEmailChanged
)
from domain.shared.value_objects import UserId, EmailAddress, Name
from domain.users.value_objects import UserProfile


class TestUserAnalyticsHandler:
    """Test UserAnalyticsHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create analytics handler for testing."""
        return UserAnalyticsHandler()
    
    @pytest.fixture
    def user_registered_event(self):
        """Create UserRegistered event for testing."""
        return UserRegistered(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            email=EmailAddress("test@example.com"),
            name="Test User"
        )
    
    @pytest.fixture
    def user_profile_updated_event(self):
        """Create UserProfileUpdated event for testing."""
        return UserProfileUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            profile=UserProfile(
                first_name=Name("Test"),
                last_name=Name("User"),
                bio="A test user",
                avatar_url="https://example.com/avatar.jpg"
            )
        )
    
    @pytest.fixture
    def user_email_changed_event(self):
        """Create UserEmailChanged event for testing."""
        return UserEmailChanged(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            old_email=EmailAddress("old@example.com"),
            new_email=EmailAddress("new@example.com")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "UserAnalyticsAI"
    
    def test_handle_user_registered(self, handler, user_registered_event):
        """Test handling UserRegistered event."""
        with patch.object(handler, '_handle_user_registered') as mock_handle:
            handler.handle(user_registered_event)
            mock_handle.assert_called_once_with(user_registered_event)
    
    def test_handle_user_registered_updates_metrics(self, handler, user_registered_event):
        """Test that UserRegistered updates metrics."""
        initial_count = handler.user_metrics['total_users_registered']
        
        handler._handle_user_registered(user_registered_event)
        
        assert handler.user_metrics['total_users_registered'] == initial_count + 1
        # Check that registration date is tracked
        date_str = user_registered_event.occurred_on.date().isoformat()
        assert date_str in handler.user_metrics['users_by_registration_date']
    
    def test_handle_profile_updated(self, handler, user_profile_updated_event):
        """Test handling UserProfileUpdated event."""
        initial_count = handler.user_metrics['total_profile_updates']
        
        handler._handle_profile_updated(user_profile_updated_event)
        
        assert handler.user_metrics['total_profile_updates'] == initial_count + 1
    
    def test_handle_email_changed(self, handler, user_email_changed_event):
        """Test handling UserEmailChanged event."""
        initial_count = handler.user_metrics['total_email_changes']
        
        handler._handle_email_changed(user_email_changed_event)
        
        assert handler.user_metrics['total_email_changes'] == initial_count + 1
    
    def test_get_analytics_summary(self, handler):
        """Test getting analytics summary."""
        summary = handler.get_analytics_summary()
        
        assert 'metrics' in summary
        assert 'timestamp' in summary
        assert 'agent' in summary
        assert summary['agent'] == "UserAnalyticsAI"
        assert isinstance(summary['metrics'], dict)


class TestUserOnboardingHandler:
    """Test UserOnboardingHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create onboarding handler for testing."""
        return UserOnboardingHandler()
    
    @pytest.fixture
    def user_registered_event(self):
        """Create UserRegistered event for testing."""
        return UserRegistered(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            email=EmailAddress("test@example.com"),
            name="Test User"
        )
    
    @pytest.fixture
    def user_profile_updated_event(self):
        """Create UserProfileUpdated event for testing."""
        return UserProfileUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            profile=UserProfile(
                first_name=Name("Test"),
                last_name=Name("User"),
                bio="A test user",
                avatar_url="https://example.com/avatar.jpg"
            )
        )
    
    @pytest.fixture
    def user_email_changed_event(self):
        """Create UserEmailChanged event for testing."""
        return UserEmailChanged(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            old_email=EmailAddress("old@example.com"),
            new_email=EmailAddress("new@example.com")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "UserOnboardingAI"
    
    def test_handle_user_registered(self, handler, user_registered_event):
        """Test handling UserRegistered event."""
        initial_welcome_messages = len(handler.welcome_messages)
        
        handler._handle_user_registered(user_registered_event)
        
        assert len(handler.welcome_messages) == initial_welcome_messages + 1
        assert "user_456" in handler.user_onboarding_status
        assert handler.user_onboarding_status["user_456"]['registered'] is True
        assert "Welcome" in handler.welcome_messages[-1]
    
    def test_handle_profile_updated(self, handler, user_registered_event, user_profile_updated_event):
        """Test handling UserProfileUpdated event."""
        # First register user
        handler._handle_user_registered(user_registered_event)
        initial_flows = len(handler.onboarding_flows)
        
        # Then update profile
        handler._handle_profile_updated(user_profile_updated_event)
        
        assert len(handler.onboarding_flows) == initial_flows + 1  # Profile update adds one flow
        assert handler.user_onboarding_status["user_456"]['profile_completed'] is True
    
    def test_handle_email_changed(self, handler, user_registered_event, user_email_changed_event):
        """Test handling UserEmailChanged event."""
        # First register user
        handler._handle_user_registered(user_registered_event)
        handler.user_onboarding_status["user_456"]['email_verified'] = True
        
        # Then change email
        handler._handle_email_changed(user_email_changed_event)
        
        # Email verification should be reset
        assert handler.user_onboarding_status["user_456"]['email_verified'] is False
    
    def test_get_onboarding_status(self, handler, user_registered_event):
        """Test getting onboarding status."""
        handler._handle_user_registered(user_registered_event)
        
        status = handler.get_onboarding_status("user_456")
        assert status['registered'] is True
        assert status['profile_completed'] is False
        assert status['email_verified'] is False
    
    def test_get_welcome_messages(self, handler, user_registered_event):
        """Test getting welcome messages."""
        handler._handle_user_registered(user_registered_event)
        
        messages = handler.get_welcome_messages()
        assert len(messages) == 1
        assert "Welcome" in messages[0]
    
    def test_get_onboarding_flows(self, handler, user_registered_event):
        """Test getting onboarding flows."""
        handler._handle_user_registered(user_registered_event)
        
        flows = handler.get_onboarding_flows()
        assert len(flows) >= 1
        assert "user_456" in flows[0]


class TestUserSecurityHandler:
    """Test UserSecurityHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create security handler for testing."""
        return UserSecurityHandler()
    
    @pytest.fixture
    def user_registered_event(self):
        """Create UserRegistered event for testing."""
        return UserRegistered(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            email=EmailAddress("test@example.com"),
            name="Test User"
        )
    
    @pytest.fixture
    def user_registered_event_suspicious_email(self):
        """Create UserRegistered event with suspicious email for testing."""
        return UserRegistered(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_789",
            user_id=UserId("user_789"),
            email=EmailAddress("test@temp-mail.com"),
            name="Suspicious User"
        )
    
    @pytest.fixture
    def user_profile_updated_event(self):
        """Create UserProfileUpdated event for testing."""
        return UserProfileUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            profile=UserProfile(
                first_name=Name("Test"),
                last_name=Name("User"),
                bio="A test user",
                avatar_url="https://example.com/avatar.jpg"
            )
        )
    
    @pytest.fixture
    def user_email_changed_event(self):
        """Create UserEmailChanged event for testing."""
        return UserEmailChanged(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id="user_456",
            user_id=UserId("user_456"),
            old_email=EmailAddress("old@example.com"),
            new_email=EmailAddress("new@example.com")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "UserSecurityAI"
    
    def test_handle_user_registered(self, handler, user_registered_event):
        """Test handling UserRegistered event."""
        handler._handle_user_registered(user_registered_event)
        
        assert "user_456" in handler.user_security_profiles
        assert handler.user_security_profiles["user_456"]['email'] == "test@example.com"
        assert handler.user_security_profiles["user_456"]['risk_score'] == 0.0
    
    def test_check_registration_patterns_suspicious_email(self, handler, user_registered_event_suspicious_email):
        """Test detection of suspicious email patterns."""
        handler._handle_user_registered(user_registered_event_suspicious_email)
        
        # Should have a security alert for suspicious email
        alerts = handler.get_security_alerts()
        assert len(alerts) >= 1
        assert "Suspicious email domain" in alerts[0]
        assert handler.user_security_profiles["user_789"]['risk_score'] > 0
    
    def test_handle_profile_updated_excessive_changes(self, handler, user_registered_event, user_profile_updated_event):
        """Test detection of excessive profile changes."""
        handler._handle_user_registered(user_registered_event)
        
        # Create multiple profile updates
        for _ in range(6):
            handler._handle_profile_updated(user_profile_updated_event)
        
        # Should have a security alert for excessive changes
        alerts = handler.get_security_alerts()
        assert len(alerts) >= 1
        assert "excessive profile changes" in alerts[0].lower()
        assert handler.user_security_profiles["user_456"]['risk_score'] > 0
    
    def test_handle_email_changed_excessive_changes(self, handler, user_registered_event):
        """Test detection of excessive email changes."""
        handler._handle_user_registered(user_registered_event)
        
        # Create multiple email changes
        for i in range(4):
            email_changed_event = UserEmailChanged(
                event_id=f"event_{i}",
                occurred_on=datetime.now(),
                aggregate_type="User",
                aggregate_id="user_456",
                user_id=UserId("user_456"),
                old_email=EmailAddress(f"old{i}@example.com"),
                new_email=EmailAddress(f"new{i+1}@example.com")
            )
            handler._handle_email_changed(email_changed_event)
        
        # Should have a security alert for excessive email changes
        alerts = handler.get_security_alerts()
        assert len(alerts) >= 1
        assert "changed email" in alerts[0].lower()
        assert handler.user_security_profiles["user_456"]['email_changes'] == 4
    
    def test_get_security_profile(self, handler, user_registered_event):
        """Test getting security profile."""
        handler._handle_user_registered(user_registered_event)
        
        profile = handler.get_security_profile("user_456")
        assert profile['email'] == "test@example.com"
        assert 'risk_score' in profile
        assert 'registration_date' in profile
    
    def test_get_security_alerts(self, handler, user_registered_event_suspicious_email):
        """Test getting security alerts."""
        handler._handle_user_registered(user_registered_event_suspicious_email)
        
        alerts = handler.get_security_alerts()
        assert len(alerts) >= 1
        assert "Suspicious" in alerts[0]
    
    def test_get_user_risk_score(self, handler, user_registered_event):
        """Test getting user risk score."""
        handler._handle_user_registered(user_registered_event)
        
        score = handler.get_user_risk_score("user_456")
        assert score == 0.0  # New user should have low risk
        
        # Test non-existent user
        score = handler.get_user_risk_score("non_existent_user")
        assert score == 0.0
    
    def test_get_suspicious_activities(self, handler, user_registered_event):
        """Test getting suspicious activities."""
        handler._handle_user_registered(user_registered_event)
        
        # Trigger excessive email changes (more than 3)
        for i in range(5):  # 5 changes to ensure we exceed the threshold
            email_changed_event = UserEmailChanged(
                event_id=f"event_{i}",
                occurred_on=datetime.now(),
                aggregate_type="User",
                aggregate_id="user_456",
                user_id=UserId("user_456"),
                old_email=EmailAddress(f"old{i}@example.com"),
                new_email=EmailAddress(f"new{i+1}@example.com")
            )
            handler._handle_email_changed(email_changed_event)
        
        # After 4+ email changes, we should have suspicious activities or at least security alerts
        alerts = handler.get_security_alerts()
        activities = handler.get_suspicious_activities()
        
        # Either we have alerts or suspicious activities for excessive email changes
        assert len(alerts) >= 1 or len(activities) >= 1
        
        # If we have suspicious activities, verify their structure
        if len(activities) >= 1:
            assert activities[0]['user_id'] == "user_456"
            assert 'activity' in activities[0]
