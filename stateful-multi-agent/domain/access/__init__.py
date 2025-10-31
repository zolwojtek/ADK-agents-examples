"""
Access domain components.
"""

from .aggregates import AccessRecord
from .value_objects import ActivityType
from .events import CourseAccessGranted, AccessRevoked, AccessExpired, ProgressUpdated, CourseCompleted

__all__ = [
    'AccessRecord',
    'ActivityType',
    'CourseAccessGranted',
    'AccessRevoked',
    'AccessExpired',
    'ProgressUpdated',
    'CourseCompleted'
]
