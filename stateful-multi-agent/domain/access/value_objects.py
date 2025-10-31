"""
Access domain value objects.
"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ActivityType(Enum):
    """Types of user activities in a course."""
    LOGIN = "login"
    VIDEO_WATCHED = "video_watched"
    QUIZ_COMPLETED = "quiz_completed"
    LESSON_COMPLETED = "lesson_completed"
    ASSIGNMENT_SUBMITTED = "assignment_submitted"
    FORUM_POST = "forum_post"
    DOWNLOAD = "download"


@dataclass(frozen=True)
class ActivityRecord:
    """Record of user activity in a course."""
    activity_type: ActivityType
    timestamp: datetime
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
