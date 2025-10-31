"""
Access domain events.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from ..shared.value_objects import AccessId, UserId, CourseId, Progress
from ..shared.events import DomainEvent


@dataclass(frozen=True)
class CourseAccessGranted(DomainEvent):
    """Event raised when course access is granted."""
    access_id: AccessId
    user_id: UserId
    course_id: CourseId
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="AccessRecord",
            aggregate_id=self.access_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'access_id': self.access_id.value,
            'user_id': self.user_id.value,
            'course_id': self.course_id.value
        })
        return base_dict


@dataclass(frozen=True)
class AccessRevoked(DomainEvent):
    """Event raised when access is revoked."""
    access_id: AccessId
    user_id: UserId
    course_id: CourseId
    reason: str
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="AccessRecord",
            aggregate_id=self.access_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'access_id': self.access_id.value,
            'user_id': self.user_id.value,
            'course_id': self.course_id.value,
            'reason': self.reason
        })
        return base_dict


@dataclass(frozen=True)
class AccessExpired(DomainEvent):
    """Event raised when access expires."""
    access_id: AccessId
    user_id: UserId
    course_id: CourseId
    expired_at: datetime
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="AccessRecord",
            aggregate_id=self.access_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'access_id': self.access_id.value,
            'user_id': self.user_id.value,
            'course_id': self.course_id.value,
            'expired_at': self.expired_at.isoformat()
        })
        return base_dict


@dataclass(frozen=True)
class ProgressUpdated(DomainEvent):
    """Event raised when course progress is updated."""
    access_id: AccessId
    user_id: UserId
    course_id: CourseId
    progress: Progress
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="AccessRecord",
            aggregate_id=self.access_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'access_id': self.access_id.value,
            'user_id': self.user_id.value,
            'course_id': self.course_id.value,
            'progress': self.progress.value
        })
        return base_dict


@dataclass(frozen=True)
class CourseCompleted(DomainEvent):
    """Event raised when a course is completed."""
    access_id: AccessId
    user_id: UserId
    course_id: CourseId
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="AccessRecord",
            aggregate_id=self.access_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'access_id': self.access_id.value,
            'user_id': self.user_id.value,
            'course_id': self.course_id.value
        })
        return base_dict
