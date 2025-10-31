"""
Course repository implementation.
"""

from typing import List, Optional

from domain.courses.repositories import CourseRepository as ICourseRepository
from domain.courses.aggregates import Course
from domain.shared.value_objects import CourseId, PolicyId
from .base import InMemoryRepository


class CourseRepository(InMemoryRepository[Course, CourseId], ICourseRepository):
    """In-memory implementation of CourseRepository."""
    
    def __init__(self):
        super().__init__()
        self._title_index: dict[str, CourseId] = {}  # title -> course_id
        self._policy_index: dict[PolicyId, List[CourseId]] = {}  # policy_id -> [course_ids]
    
    def find_by_id(self, course_id: CourseId) -> Optional[Course]:
        """Find course by ID."""
        return super().get_by_id(course_id)
    
    def list_by_policy(self, policy_or_ref) -> List[Course]:
        """List courses by refund policy (accepts PolicyId or PolicyRef)."""
        # Normalize key to PolicyId
        key = getattr(policy_or_ref, 'policy_id', policy_or_ref)
        course_ids = self._policy_index.get(key, [])
        return [self.find_by_id(course_id) for course_id in course_ids if self.find_by_id(course_id)]
    
    def search_by_criteria(self, criteria: dict) -> List[Course]:
        """Search courses by criteria."""
        courses = self.get_all()
        
        # Filter by criteria
        if 'instructor_id' in criteria:
            courses = [c for c in courses if c.instructor_id == criteria['instructor_id']]
        if 'is_deprecated' in criteria:
            courses = [c for c in courses if c.is_deprecated == criteria['is_deprecated']]
        if 'title_contains' in criteria:
            title_query = criteria['title_contains'].lower()
            courses = [c for c in courses if title_query in c.title.value.lower()]
        
        return courses
    
    def get_by_title(self, title: str) -> Optional[Course]:
        """Get course by title."""
        course_id = self._title_index.get(title)
        if course_id:
            return self.find_by_id(course_id)
        return None
    
    def get_by_policy(self, policy_or_ref) -> List[Course]:
        """Get courses by refund policy (accepts PolicyId or PolicyRef)."""
        key = getattr(policy_or_ref, 'policy_id', policy_or_ref)
        course_ids = self._policy_index.get(key, [])
        return [self.find_by_id(course_id) for course_id in course_ids if self.find_by_id(course_id)]
    
    def save(self, course: Course) -> Course:
        """Save course with indexing."""
        # Determine if course exists already
        existing_course = super().get_by_id(course.id) if course.id else None

        # Enforce title uniqueness across different courses
        mapped_id = self._title_index.get(course.title.value)
        if mapped_id is not None and mapped_id != course.id:
            raise ValueError(f"Course with title '{course.title.value}' already exists")

        # If updating, remove old title mapping if it changed (robust to in-place mutation)
        if existing_course is not None:
            previous_title_value = None
            for title_value, cid in self._title_index.items():
                if cid == course.id:
                    previous_title_value = title_value
                    break
            if previous_title_value is not None and previous_title_value != course.title.value:
                if previous_title_value in self._title_index:
                    del self._title_index[previous_title_value]

        # Save course
        saved = super().save(course)
        
        # Update indexes
        self._title_index[course.title.value] = course.id
        
        # Update policy index (keyed by PolicyId)
        policy_id = course.policy_ref.policy_id
        if policy_id not in self._policy_index:
            self._policy_index[policy_id] = []
        if course.id not in self._policy_index[policy_id]:
            self._policy_index[policy_id].append(course.id)

        return saved
    
    def delete(self, course_id: CourseId) -> bool:
        """Delete course by ID."""
        course = self.find_by_id(course_id)
        if course:
            # Remove from indexes
            if course.title.value in self._title_index:
                del self._title_index[course.title.value]

            policy_id = course.policy_ref.policy_id
            if policy_id in self._policy_index:
                if course.id in self._policy_index[policy_id]:
                    self._policy_index[policy_id].remove(course.id)
                if not self._policy_index[policy_id]:
                    del self._policy_index[policy_id]

            return super().delete(course_id)
        return False
    
    def clear(self) -> None:
        """Clear all courses and indexes."""
        super().clear()
        self._title_index.clear()
        self._policy_index.clear()
