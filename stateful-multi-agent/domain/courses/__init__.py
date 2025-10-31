"""
Course domain components.
"""

from .aggregates import Course
from .value_objects import Title, Description
from .events import CourseCreated, CourseUpdated, CourseDeprecated, CoursePolicyChanged

__all__ = [
    'Course',
    'Title',
    'Description',
    'CourseCreated',
    'CourseUpdated',
    'CourseDeprecated',
    'CoursePolicyChanged'
]
