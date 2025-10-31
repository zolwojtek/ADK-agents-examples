"""
Unit tests for CourseRepository implementation.
"""

import pytest
from uuid import uuid4

from infrastructure.repositories.course_repository import CourseRepository
from domain.courses.aggregates import Course
from domain.courses.value_objects import Title, Description
from domain.shared.value_objects import AccessType, CourseId, PolicyId, Money, PolicyRef


class TestCourseRepository:
    """Test CourseRepository implementation."""
    
    @pytest.fixture
    def course_repository(self):
        """Create a test course repository."""
        return CourseRepository()
    
    @pytest.fixture
    def course_data(self):
        """Create test course data."""
        return {
            "id": CourseId(str(uuid4())),
            "title": Title("Python Programming"),
            "description": Description("Learn Python from scratch"),
            "price": Money(99.99, "USD"),
            "access_type": AccessType.UNLIMITED,
            "policy_ref": PolicyRef(PolicyId(str(uuid4())))
        }
    
    @pytest.fixture
    def course(self, course_data):
        """Create a test course."""
        return Course(**course_data)
    
    def test_save_course(self, course_repository, course):
        """Test saving a course."""
        saved_course = course_repository.save(course)
        
        assert saved_course == course
        assert course_repository.get_by_id(course.id) == course
        assert course_repository.count() == 1
    
    def test_get_by_id(self, course_repository, course):
        """Test getting course by ID."""
        course_repository.save(course)
        
        retrieved_course = course_repository.get_by_id(course.id)
        assert retrieved_course == course
        
        non_existent_id = CourseId(str(uuid4()))
        assert course_repository.get_by_id(non_existent_id) is None
    
    def test_get_by_title(self, course_repository, course):
        """Test getting course by title."""
        course_repository.save(course)
        
        retrieved_course = course_repository.get_by_title(course.title.value)
        assert retrieved_course == course
        
        assert course_repository.get_by_title("Non-existent Course") is None
    
    def test_get_by_policy(self, course_repository, course):
        """Test getting courses by policy."""
        course_repository.save(course)
        
        courses = course_repository.get_by_policy(course.policy_ref)
        assert len(courses) == 1
        assert courses[0] == course
        
        non_existent_policy = PolicyId(str(uuid4()))
        courses = course_repository.get_by_policy(non_existent_policy)
        assert len(courses) == 0

    
    def test_title_uniqueness(self, course_repository, course):
        """Test title uniqueness constraint."""
        course_repository.save(course)
        
        # Try to save another course with same title
        duplicate_course = Course(
            id=CourseId(str(uuid4())),
            title=course.title,  # Same title
            description=Description("Different description"),
            price=Money(149.99, "USD"),
            access_type=AccessType.UNLIMITED,
            policy_ref=PolicyRef(PolicyId(str(uuid4())))
        )
        
        with pytest.raises(ValueError, match="Course with title .* already exists"):
            course_repository.save(duplicate_course)
    
    def test_update_course_title(self, course_repository, course):
        """Test updating course title."""
        course_repository.save(course)
        
        new_title = Title("Advanced Python Programming")
        course.title = new_title
        
        updated_course = course_repository.save(course)
        assert updated_course.title == new_title
        assert course_repository.get_by_title(new_title.value) == course
        assert course_repository.get_by_title("Python Programming") is None
    
    def test_delete_course(self, course_repository, course):
        """Test deleting course."""
        course_repository.save(course)
        assert course_repository.count() == 1
        
        result = course_repository.delete(course.id)
        assert result is True
        assert course_repository.count() == 0
        assert course_repository.get_by_id(course.id) is None
        assert course_repository.get_by_title(course.title.value) is None
        
        # Try to delete non-existent course
        result = course_repository.delete(CourseId(str(uuid4())))
        assert result is False
    
    def test_get_all_courses(self, course_repository, course):
        """Test getting all courses."""
        course_repository.save(course)
        
        courses = course_repository.get_all()
        assert len(courses) == 1
        assert courses[0] == course
    
    def test_exists(self, course_repository, course):
        """Test checking if course exists."""
        assert not course_repository.exists(course.id)
        
        course_repository.save(course)
        assert course_repository.exists(course.id)
    
    def test_clear_repository(self, course_repository, course):
        """Test clearing repository."""
        course_repository.save(course)
        assert course_repository.count() == 1
        
        course_repository.clear()
        assert course_repository.count() == 0
        assert course_repository.get_by_id(course.id) is None
    
    def test_multiple_courses(self, course_repository):
        """Test repository with multiple courses."""
        course1 = Course(
            id=CourseId(str(uuid4())),
            title=Title("Python Programming"),
            description=Description("Learn Python from scratch"),
            price=Money(99.99, "USD"),
            access_type=AccessType.UNLIMITED,
            policy_ref=PolicyRef(PolicyId(str(uuid4())))
        )
        
        course2 = Course(
            id=CourseId(str(uuid4())),
            title=Title("JavaScript Programming"),
            description=Description("Learn JavaScript from scratch"),
            price=Money(149.99, "USD"),
            access_type=AccessType.UNLIMITED,
            policy_ref=PolicyRef(PolicyId(str(uuid4())))
        )
        
        course_repository.save(course1)
        course_repository.save(course2)
        
        assert course_repository.count() == 2
