"""
Tests for Access domain event handlers.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from ai_agents.access_event_handlers import (
    AccessAnalyticsHandler, AccessLearningAssistantHandler, AccessEngagementHandler
)
from domain.access.events import (
    CourseAccessGranted, AccessRevoked, AccessExpired, 
    ProgressUpdated, CourseCompleted
)
from domain.shared.value_objects import AccessId, UserId, CourseId, Progress


class TestAccessAnalyticsHandler:
    """Test AccessAnalyticsHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create analytics handler for testing."""
        return AccessAnalyticsHandler()
    
    @pytest.fixture
    def access_granted_event(self):
        """Create CourseAccessGranted event for testing."""
        return CourseAccessGranted(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123")
        )
    
    @pytest.fixture
    def access_revoked_event(self):
        """Create AccessRevoked event for testing."""
        return AccessRevoked(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123"),
            reason="user_request"
        )
    
    @pytest.fixture
    def access_expired_event(self):
        """Create AccessExpired event for testing."""
        return AccessExpired(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123"),
            expired_at=datetime.now()
        )
    
    @pytest.fixture
    def progress_updated_event(self):
        """Create ProgressUpdated event for testing."""
        return ProgressUpdated(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123"),
            progress=Progress(50.0)
        )
    
    @pytest.fixture
    def course_completed_event(self):
        """Create CourseCompleted event for testing."""
        return CourseCompleted(
            event_id="event_127",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "AccessAnalyticsAI"
    
    def test_handle_access_granted(self, handler, access_granted_event):
        """Test handling CourseAccessGranted event."""
        with patch.object(handler, '_handle_access_granted') as mock_handle:
            handler.handle(access_granted_event)
            mock_handle.assert_called_once_with(access_granted_event)
    
    def test_handle_access_granted_updates_metrics(self, handler, access_granted_event):
        """Test that CourseAccessGranted updates metrics."""
        initial_count = handler.access_metrics['total_accesses_granted']
        
        handler._handle_access_granted(access_granted_event)
        
        assert handler.access_metrics['total_accesses_granted'] == initial_count + 1
        assert "user_789" in handler.access_metrics['active_users']
        assert "course_123" in handler.access_metrics['active_courses']
    
    def test_handle_access_revoked(self, handler, access_revoked_event):
        """Test handling AccessRevoked event."""
        initial_count = handler.access_metrics['total_accesses_revoked']
        
        handler._handle_access_revoked(access_revoked_event)
        
        assert handler.access_metrics['total_accesses_revoked'] == initial_count + 1
    
    def test_handle_access_expired(self, handler, access_expired_event):
        """Test handling AccessExpired event."""
        initial_count = handler.access_metrics['total_accesses_expired']
        
        handler._handle_access_expired(access_expired_event)
        
        assert handler.access_metrics['total_accesses_expired'] == initial_count + 1
    
    def test_handle_progress_updated(self, handler, progress_updated_event):
        """Test handling ProgressUpdated event."""
        with patch.object(handler, '_handle_progress_updated') as mock_handle:
            handler.handle(progress_updated_event)
            mock_handle.assert_called_once_with(progress_updated_event)
    
    def test_handle_course_completed(self, handler, course_completed_event):
        """Test handling CourseCompleted event."""
        initial_count = handler.access_metrics['total_courses_completed']
        
        handler._handle_course_completed(course_completed_event)
        
        assert handler.access_metrics['total_courses_completed'] == initial_count + 1
    
    def test_get_analytics_summary(self, handler):
        """Test getting analytics summary."""
        summary = handler.get_analytics_summary()
        
        assert 'metrics' in summary
        assert 'timestamp' in summary
        assert 'agent' in summary
        assert summary['agent'] == "AccessAnalyticsAI"
        assert isinstance(summary['metrics'], dict)
        assert 'active_users_count' in summary['metrics']
        assert 'active_courses_count' in summary['metrics']


class TestAccessLearningAssistantHandler:
    """Test AccessLearningAssistantHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create learning assistant handler for testing."""
        return AccessLearningAssistantHandler()
    
    @pytest.fixture
    def access_granted_event(self):
        """Create CourseAccessGranted event for testing."""
        return CourseAccessGranted(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123")
        )
    
    @pytest.fixture
    def progress_updated_event_50(self):
        """Create ProgressUpdated event at 50%."""
        return ProgressUpdated(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123"),
            progress=Progress(50.0)
        )
    
    @pytest.fixture
    def progress_updated_event_80(self):
        """Create ProgressUpdated event at 80%."""
        return ProgressUpdated(
            event_id="event_128",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123"),
            progress=Progress(80.0)
        )
    
    @pytest.fixture
    def course_completed_event(self):
        """Create CourseCompleted event for testing."""
        return CourseCompleted(
            event_id="event_127",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "AccessLearningAssistantAI"
    
    def test_handle_access_granted(self, handler, access_granted_event):
        """Test handling CourseAccessGranted event."""
        initial_recommendations = len(handler.recommendations)
        
        handler._handle_access_granted(access_granted_event)
        
        assert len(handler.recommendations) == initial_recommendations + 1
        assert "Welcome" in handler.recommendations[-1]
        assert "user_789" in handler.user_learning_profiles
        assert "course_123" in handler.user_learning_profiles["user_789"]['active_courses']
    
    def test_handle_progress_updated_50_percent(self, handler, progress_updated_event_50):
        """Test handling ProgressUpdated at 50%."""
        initial_recommendations = len(handler.recommendations)
        
        handler._handle_progress_updated(progress_updated_event_50)
        
        assert len(handler.recommendations) == initial_recommendations + 1
        assert "halfway" in handler.recommendations[-1].lower()
    
    def test_handle_progress_updated_80_percent(self, handler, progress_updated_event_80):
        """Test handling ProgressUpdated at 80%."""
        initial_recommendations = len(handler.recommendations)
        
        handler._handle_progress_updated(progress_updated_event_80)
        
        assert len(handler.recommendations) == initial_recommendations + 1
        assert "almost" in handler.recommendations[-1].lower() or "finish" in handler.recommendations[-1].lower()
    
    def test_handle_course_completed(self, handler, course_completed_event):
        """Test handling CourseCompleted event."""
        # First grant access
        access_granted_event = CourseAccessGranted(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123")
        )
        handler._handle_access_granted(access_granted_event)
        assert "course_123" in handler.user_learning_profiles["user_789"]['active_courses']
        
        # Then complete course
        initial_recommendations = len(handler.recommendations)
        handler._handle_course_completed(course_completed_event)
        
        assert len(handler.recommendations) == initial_recommendations + 1
        assert "course_123" not in handler.user_learning_profiles["user_789"]['active_courses']
        assert "course_123" in handler.user_learning_profiles["user_789"]['completed_courses']
    
    def test_get_recommendations(self, handler, access_granted_event):
        """Test getting recommendations."""
        handler._handle_access_granted(access_granted_event)
        
        recommendations = handler.get_recommendations()
        assert len(recommendations) == 1
        assert "Welcome" in recommendations[0]
    
    def test_get_user_learning_profile(self, handler, access_granted_event):
        """Test getting user learning profile."""
        handler._handle_access_granted(access_granted_event)
        
        profile = handler.get_user_learning_profile("user_789")
        assert 'active_courses' in profile
        assert 'completed_courses' in profile
        assert "course_123" in profile['active_courses']


class TestAccessEngagementHandler:
    """Test AccessEngagementHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create engagement handler for testing."""
        return AccessEngagementHandler()
    
    @pytest.fixture
    def access_granted_event(self):
        """Create CourseAccessGranted event for testing."""
        return CourseAccessGranted(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123")
        )
    
    @pytest.fixture
    def progress_updated_event(self):
        """Create ProgressUpdated event for testing."""
        return ProgressUpdated(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123"),
            progress=Progress(50.0)
        )
    
    @pytest.fixture
    def course_completed_event(self):
        """Create CourseCompleted event for testing."""
        return CourseCompleted(
            event_id="event_127",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123")
        )
    
    @pytest.fixture
    def access_revoked_event(self):
        """Create AccessRevoked event for testing."""
        return AccessRevoked(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123"),
            reason="user_request"
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "AccessEngagementAI"
    
    def test_handle_access_granted(self, handler, access_granted_event):
        """Test handling CourseAccessGranted event."""
        handler._handle_access_granted(access_granted_event)
        
        assert "user_789" in handler.user_engagement
        assert handler.user_engagement["user_789"]['engagement_score'] == 100.0
        assert len(handler.user_engagement["user_789"]['accesses']) == 1
    
    def test_handle_progress_updated(self, handler, access_granted_event, progress_updated_event):
        """Test handling ProgressUpdated event."""
        handler._handle_access_granted(access_granted_event)
        initial_score = handler.user_engagement["user_789"]['engagement_score']
        
        handler._handle_progress_updated(progress_updated_event)
        
        assert len(handler.user_engagement["user_789"]['progress_events']) == 1
        # Engagement score should be updated (may increase slightly)
        assert handler.user_engagement["user_789"]['engagement_score'] >= initial_score
    
    def test_handle_course_completed(self, handler, access_granted_event, course_completed_event):
        """Test handling CourseCompleted event."""
        handler._handle_access_granted(access_granted_event)
        initial_score = handler.user_engagement["user_789"]['engagement_score']
        
        handler._handle_course_completed(course_completed_event)
        
        # Completion should not decrease engagement score (may be capped at 100)
        assert handler.user_engagement["user_789"]['engagement_score'] >= initial_score
        assert handler.user_engagement["user_789"]['engagement_score'] <= 100.0
    
    def test_handle_access_revoked_decreases_engagement(self, handler, access_granted_event, access_revoked_event):
        """Test that AccessRevoked decreases engagement score."""
        handler._handle_access_granted(access_granted_event)
        initial_score = handler.user_engagement["user_789"]['engagement_score']
        
        handler._handle_access_revoked(access_revoked_event)
        
        # Revocation should significantly decrease engagement
        assert handler.user_engagement["user_789"]['engagement_score'] < initial_score
        assert handler.user_engagement["user_789"]['engagement_score'] <= initial_score - 14.0
    
    def test_handle_access_revoked_creates_alert(self, handler, access_granted_event, access_revoked_event):
        """Test that AccessRevoked creates alert when engagement is low."""
        handler._handle_access_granted(access_granted_event)
        
        # Revoke access multiple times to lower engagement
        for _ in range(6):  # Multiple revocations to lower score below 20
            handler._handle_access_revoked(access_revoked_event)
        
        # Should have engagement alerts for low engagement
        alerts = handler.get_engagement_alerts()
        assert len(alerts) > 0
        assert "User user_789" in alerts[0]
    
    def test_get_engagement_alerts(self, handler, access_revoked_event):
        """Test getting engagement alerts."""
        # Create user and revoke access
        access_granted_event = CourseAccessGranted(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id="access_456",
            access_id=AccessId("access_456"),
            user_id=UserId("user_789"),
            course_id=CourseId("course_123")
        )
        handler._handle_access_granted(access_granted_event)
        
        # Revoke multiple times to trigger alert
        for _ in range(6):
            handler._handle_access_revoked(access_revoked_event)
        
        alerts = handler.get_engagement_alerts()
        assert len(alerts) >= 1
    
    def test_get_user_engagement_score(self, handler, access_granted_event):
        """Test getting user engagement score."""
        handler._handle_access_granted(access_granted_event)
        
        score = handler.get_user_engagement_score("user_789")
        assert score == 100.0
        
        # Test non-existent user
        score = handler.get_user_engagement_score("non_existent_user")
        assert score == 0.0
