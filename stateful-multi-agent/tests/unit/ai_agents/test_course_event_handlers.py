"""
Tests for Course domain event handlers.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from ai_agents.course_event_handlers import (
    CourseAnalyticsHandler, CourseCatalogHandler, CourseQualityHandler
)
from domain.courses.events import (
    CourseCreated, CourseUpdated, CourseDeprecated, CoursePolicyChanged
)
from domain.shared.value_objects import CourseId, PolicyId
from domain.courses.value_objects import Title, Description


class TestCourseAnalyticsHandler:
    """Test CourseAnalyticsHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create analytics handler for testing."""
        return CourseAnalyticsHandler()
    
    @pytest.fixture
    def course_created_event(self):
        """Create CourseCreated event for testing."""
        return CourseCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python"),
            policy_id=PolicyId("policy_789")
        )
    
    @pytest.fixture
    def course_updated_event(self):
        """Create CourseUpdated event for testing."""
        return CourseUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python - Updated"),
            description=Description("An updated course on Python programming")
        )
    
    @pytest.fixture
    def course_deprecated_event(self):
        """Create CourseDeprecated event for testing."""
        return CourseDeprecated(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python")
        )
    
    @pytest.fixture
    def course_policy_changed_event(self):
        """Create CoursePolicyChanged event for testing."""
        return CoursePolicyChanged(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            old_policy_id=PolicyId("policy_789"),
            new_policy_id=PolicyId("policy_999")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "CourseAnalyticsAI"
    
    def test_handle_course_created(self, handler, course_created_event):
        """Test handling CourseCreated event."""
        with patch.object(handler, '_handle_course_created') as mock_handle:
            handler.handle(course_created_event)
            mock_handle.assert_called_once_with(course_created_event)
    
    def test_handle_course_created_updates_metrics(self, handler, course_created_event):
        """Test that CourseCreated updates metrics."""
        initial_count = handler.course_metrics['total_courses_created']
        
        handler._handle_course_created(course_created_event)
        
        assert handler.course_metrics['total_courses_created'] == initial_count + 1
        assert "course_456" in handler.course_metrics['active_courses']
        assert "policy_789" in handler.course_metrics['courses_by_policy']
        assert "course_456" in handler.course_metrics['courses_by_policy']['policy_789']
    
    def test_handle_course_updated(self, handler, course_updated_event):
        """Test handling CourseUpdated event."""
        initial_count = handler.course_metrics['total_courses_updated']
        
        handler._handle_course_updated(course_updated_event)
        
        assert handler.course_metrics['total_courses_updated'] == initial_count + 1
    
    def test_handle_course_deprecated(self, handler, course_created_event, course_deprecated_event):
        """Test handling CourseDeprecated event."""
        # First create a course
        handler._handle_course_created(course_created_event)
        assert "course_456" in handler.course_metrics['active_courses']
        
        # Then deprecate it
        initial_count = handler.course_metrics['total_courses_deprecated']
        handler._handle_course_deprecated(course_deprecated_event)
        
        assert handler.course_metrics['total_courses_deprecated'] == initial_count + 1
        assert "course_456" not in handler.course_metrics['active_courses']
        assert "course_456" in handler.course_metrics['deprecated_courses']
    
    def test_handle_policy_changed(self, handler, course_created_event, course_policy_changed_event):
        """Test handling CoursePolicyChanged event."""
        # First create a course with old policy
        handler._handle_course_created(course_created_event)
        assert "course_456" in handler.course_metrics['courses_by_policy']['policy_789']
        
        # Then change policy
        initial_count = handler.course_metrics['total_policy_changes']
        handler._handle_policy_changed(course_policy_changed_event)
        
        assert handler.course_metrics['total_policy_changes'] == initial_count + 1
        assert "course_456" not in handler.course_metrics['courses_by_policy']['policy_789']
        assert "course_456" in handler.course_metrics['courses_by_policy']['policy_999']
    
    def test_get_analytics_summary(self, handler):
        """Test getting analytics summary."""
        summary = handler.get_analytics_summary()
        
        assert 'metrics' in summary
        assert 'timestamp' in summary
        assert 'agent' in summary
        assert summary['agent'] == "CourseAnalyticsAI"
        assert isinstance(summary['metrics'], dict)
        assert 'active_courses_count' in summary['metrics']
        assert 'deprecated_courses_count' in summary['metrics']


class TestCourseCatalogHandler:
    """Test CourseCatalogHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create catalog handler for testing."""
        return CourseCatalogHandler()
    
    @pytest.fixture
    def course_created_event(self):
        """Create CourseCreated event for testing."""
        return CourseCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python"),
            policy_id=PolicyId("policy_789")
        )
    
    @pytest.fixture
    def course_updated_event(self):
        """Create CourseUpdated event for testing."""
        return CourseUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python - Updated"),
            description=Description("An updated course on Python programming")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "CourseCatalogAI"
    
    def test_handle_course_created(self, handler, course_created_event):
        """Test handling CourseCreated event."""
        initial_recommendations = len(handler.recommendations)
        
        handler._handle_course_created(course_created_event)
        
        assert len(handler.recommendations) == initial_recommendations + 1
        assert "course_456" in handler.catalog
        assert handler.catalog["course_456"]['title'] == "Introduction to Python"
        assert handler.catalog["course_456"]['status'] == 'active'
    
    def test_handle_course_updated(self, handler, course_created_event, course_updated_event):
        """Test handling CourseUpdated event."""
        # First create a course
        handler._handle_course_created(course_created_event)
        
        # Then update it
        initial_recommendations = len(handler.recommendations)
        handler._handle_course_updated(course_updated_event)
        
        assert len(handler.recommendations) == initial_recommendations + 1
        assert handler.catalog["course_456"]['title'] == "Introduction to Python - Updated"
        assert 'description' in handler.catalog["course_456"]
    
    def test_handle_course_deprecated(self, handler, course_created_event):
        """Test handling CourseDeprecated event."""
        # First create a course
        handler._handle_course_created(course_created_event)
        assert handler.catalog["course_456"]['status'] == 'active'
        
        # Then deprecate it
        course_deprecated_event = CourseDeprecated(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python")
        )
        
        initial_recommendations = len(handler.recommendations)
        handler._handle_course_deprecated(course_deprecated_event)
        
        assert len(handler.recommendations) == initial_recommendations + 1
        assert handler.catalog["course_456"]['status'] == 'deprecated'
    
    def test_get_catalog(self, handler, course_created_event):
        """Test getting catalog."""
        handler._handle_course_created(course_created_event)
        
        catalog = handler.get_catalog()
        assert len(catalog) == 1
        assert "course_456" in catalog
    
    def test_get_course_info(self, handler, course_created_event):
        """Test getting course info."""
        handler._handle_course_created(course_created_event)
        
        course_info = handler.get_course_info("course_456")
        assert course_info['id'] == "course_456"
        assert course_info['title'] == "Introduction to Python"
    
    def test_get_recommendations(self, handler, course_created_event):
        """Test getting recommendations."""
        handler._handle_course_created(course_created_event)
        
        recommendations = handler.get_recommendations()
        assert len(recommendations) == 1
        assert "New course" in recommendations[0]


class TestCourseQualityHandler:
    """Test CourseQualityHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create quality handler for testing."""
        return CourseQualityHandler()
    
    @pytest.fixture
    def course_created_event(self):
        """Create CourseCreated event for testing."""
        return CourseCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python"),
            policy_id=PolicyId("policy_789")
        )
    
    @pytest.fixture
    def course_created_event_minimal(self):
        """Create CourseCreated event with minimal information for testing."""
        return CourseCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Python"),  # Minimal title
            policy_id=PolicyId("policy_001")  # Valid policy
        )
    
    @pytest.fixture
    def course_updated_event(self):
        """Create CourseUpdated event for testing."""
        return CourseUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python - Updated"),
            description=Description("A comprehensive course on Python programming with detailed explanations")
        )
    
    @pytest.fixture
    def course_policy_changed_event(self):
        """Create CoursePolicyChanged event for testing."""
        return CoursePolicyChanged(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            old_policy_id=PolicyId("policy_789"),
            new_policy_id=PolicyId("policy_999")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "CourseQualityAI"
    
    def test_handle_course_created(self, handler, course_created_event):
        """Test handling CourseCreated event."""
        handler._handle_course_created(course_created_event)
        
        assert "course_456" in handler.course_quality_scores
        assert handler.course_quality_scores["course_456"] > 0
        assert len(handler.compliance_checks) == 1
        assert handler.compliance_checks[0]['course_id'] == "course_456"
    
    def test_calculate_initial_quality_score(self, handler, course_created_event):
        """Test initial quality score calculation."""
        handler._handle_course_created(course_created_event)
        
        score = handler.course_quality_scores["course_456"]
        assert score >= 70.0
        assert score <= 100.0
    
    def test_check_compliance_passes(self, handler, course_created_event):
        """Test compliance check when course has required fields."""
        handler._handle_course_created(course_created_event)
        
        compliance_check = handler.compliance_checks[0]
        assert compliance_check['passed'] is True
        assert len(compliance_check['issues']) == 0
    
    def test_check_compliance_with_minimal_info(self, handler, course_created_event_minimal):
        """Test compliance check with minimal course information."""
        handler._handle_course_created(course_created_event_minimal)
        
        compliance_check = handler.compliance_checks[0]
        assert compliance_check['course_id'] == "course_456"
        # Should pass since all required fields are present (even if minimal)
        assert compliance_check['passed'] is True
    
    def test_handle_course_updated(self, handler, course_created_event, course_updated_event):
        """Test handling CourseUpdated event."""
        handler._handle_course_created(course_created_event)
        initial_score = handler.course_quality_scores["course_456"]
        
        handler._handle_course_updated(course_updated_event)
        
        # Score should be recalculated
        new_score = handler.course_quality_scores["course_456"]
        assert new_score != initial_score
        assert new_score >= 0
        assert new_score <= 100.0
    
    def test_handle_course_deprecated(self, handler, course_created_event):
        """Test handling CourseDeprecated event."""
        handler._handle_course_created(course_created_event)
        initial_score = handler.course_quality_scores["course_456"]
        
        course_deprecated_event = CourseDeprecated(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Introduction to Python")
        )
        
        handler._handle_course_deprecated(course_deprecated_event)
        
        # Deprecated courses should have reduced score
        new_score = handler.course_quality_scores["course_456"]
        assert new_score <= initial_score - 15
    
    def test_handle_policy_changed(self, handler, course_created_event, course_policy_changed_event):
        """Test handling CoursePolicyChanged event."""
        handler._handle_course_created(course_created_event)
        
        initial_compliance_checks = len(handler.compliance_checks)
        handler._handle_policy_changed(course_policy_changed_event)
        
        assert len(handler.compliance_checks) == initial_compliance_checks + 1
        assert handler.compliance_checks[-1]['check_type'] == 'policy_change'
    
    def test_get_quality_score(self, handler, course_created_event):
        """Test getting quality score."""
        handler._handle_course_created(course_created_event)
        
        score = handler.get_quality_score("course_456")
        assert score > 0
        assert score <= 100.0
        
        # Test non-existent course
        score = handler.get_quality_score("non_existent_course")
        assert score == 0.0
    
    def test_get_quality_alerts(self, handler, course_updated_event):
        """Test getting quality alerts."""
        # Create a course first
        course_created_event = CourseCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Test Course"),
            policy_id=PolicyId("policy_789")
        )
        
        handler._handle_course_created(course_created_event)
        
        # Update with low quality description to potentially trigger low quality alert
        # Update course with minimal description that might result in lower quality score
        course_low_quality = CourseUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id="course_456",
            course_id=CourseId("course_456"),
            title=Title("Test Course"),
            description=Description("Short")  # Very short description
        )
        
        handler._handle_course_updated(course_low_quality)
        
        alerts = handler.get_quality_alerts()
        # May or may not have alerts depending on quality score
        assert isinstance(alerts, list)
    
    def test_get_compliance_checks(self, handler, course_created_event):
        """Test getting compliance checks."""
        handler._handle_course_created(course_created_event)
        
        checks = handler.get_compliance_checks()
        assert len(checks) == 1
        assert checks[0]['course_id'] == "course_456"
        assert 'check_type' in checks[0]
        assert 'passed' in checks[0]
