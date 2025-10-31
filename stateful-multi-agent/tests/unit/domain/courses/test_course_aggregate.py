"""
Unit tests for Course aggregate.
"""

import pytest
from uuid import uuid4

from domain.courses.aggregates import Course
from domain.courses.value_objects import Title, Description
from domain.shared.value_objects import CourseId, PolicyId, Money, AccessType, PolicyRef


class TestCourseAggregate:
    """Test Course aggregate."""
    
    @pytest.fixture
    def course_data(self):
        """Create test course data."""
        return {
            "course_id": CourseId(str(uuid4())),
            "title": Title("Python Programming"),
            "description": Description("Learn Python from scratch"),
            "price": Money(99.99, "USD"),
            "access_type": AccessType.UNLIMITED,
            "policy_ref": PolicyRef(PolicyId(str(uuid4())))
        }
    
    @pytest.fixture
    def course(self, course_data):
        """Create a test course."""
        return Course.create_course(
            title=course_data["title"],
            description=course_data["description"],
            price=course_data["price"],
            access_type=course_data["access_type"],
            policy_ref=course_data["policy_ref"]
        )
    
    def test_create_course(self, course_data):
        """Test creating a course."""
        course = Course.create_course(
            title=course_data["title"],
            description=course_data["description"],
            price=course_data["price"],
            access_type=course_data["access_type"],
            policy_ref=course_data["policy_ref"]
        )
        
        assert course.id is not None
        assert course.title == course_data["title"]
        assert course.description == course_data["description"]
        assert course.price == course_data["price"]
        assert course.access_type == course_data["access_type"]
        assert course.policy_ref == course_data["policy_ref"]
        assert course.created_at is not None
        assert course.updated_at is not None
        events = course.get_domain_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "CourseCreated"
    
    def test_update_course_details(self, course):
        """Test updating course details."""
        new_title = Title("Advanced Python Programming")
        new_description = Description("Advanced Python concepts and techniques")
        
        course.update_details(new_title, new_description)
        
        assert course.title == new_title
        assert course.description == new_description
        assert course.updated_at > course.created_at
        events = course.get_domain_events()
        assert len(events) == 2
        assert events[1].__class__.__name__ == "CourseUpdated"
    
    def test_assign_refund_policy(self, course):
        """Test assigning refund policy."""
        new_policy_id = PolicyId(str(uuid4()))
        old_policy_id = course.policy_ref.policy_id
        
        course.assign_refund_policy(PolicyRef(new_policy_id))
        
        assert course.policy_ref.policy_id == new_policy_id
        assert course.updated_at > course.created_at
        events = course.get_domain_events()
        assert len(events) == 2
        event = events[1]
        assert event.__class__.__name__ == "CoursePolicyChanged"
        assert event.old_policy_id == old_policy_id
        assert event.new_policy_id == new_policy_id
    
    def test_deprecate_course(self, course):
        """Test deprecating course."""
        course.deprecate()
        
        assert course.updated_at > course.created_at
        events = course.get_domain_events()
        assert len(events) == 2
        assert events[1].__class__.__name__ == "CourseDeprecated"
    
    def test_change_price(self, course):
        """Test changing course price."""
        new_price = Money(149.99, "USD")
        
        course.change_price(new_price)
        
        assert course.price == new_price
        assert course.updated_at > course.created_at
    
    def test_clear_domain_events(self, course):
        """Test clearing domain events."""
        course.update_details(course.title, course.description)  # Generate an event
        
        events = course.get_domain_events()
        assert len(events) == 2
        course.clear_domain_events()
        events = course.get_domain_events()
        assert len(events) == 0
    
    def test_course_equality(self, course_data):
        """Test course equality."""
        course1 = Course.create_course(
            title=course_data["title"],
            description=course_data["description"],
            price=course_data["price"],
            access_type=course_data["access_type"],
            policy_ref=course_data["policy_ref"]
        )
        course2 = Course.create_course(
            title=course_data["title"],
            description=course_data["description"],
            price=course_data["price"],
            access_type=course_data["access_type"],
            policy_ref=course_data["policy_ref"]
        )
        
        assert course1 != course2  # Different instances with different IDs
    
    def test_course_inequality(self, course_data):
        """Test course inequality."""
        course1 = Course.create_course(
            title=course_data["title"],
            description=course_data["description"],
            price=course_data["price"],
            access_type=course_data["access_type"],
            policy_ref=course_data["policy_ref"]
        )
        course2 = Course.create_course(
            title=course_data["title"],
            description=course_data["description"],
            price=course_data["price"],
            access_type=course_data["access_type"],
            policy_ref=course_data["policy_ref"]
        )
        
        assert course1 != course2
