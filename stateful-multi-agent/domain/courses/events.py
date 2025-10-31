"""
Course domain events.
"""

from dataclasses import dataclass
from typing import Any, Dict

from ..shared.value_objects import CourseId, PolicyId
from ..shared.events import DomainEvent
from .value_objects import Title, Description


@dataclass(frozen=True)
class CourseCreated(DomainEvent):
    """Event raised when a course is created."""
    course_id: CourseId
    title: Title
    policy_id: PolicyId
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Course",
            aggregate_id=self.course_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'course_id': self.course_id.value,
            'title': self.title.value,
            'policy_id': self.policy_id.value
        })
        return base_dict


@dataclass(frozen=True)
class CourseUpdated(DomainEvent):
    """Event raised when course details are updated."""
    course_id: CourseId
    title: Title
    description: Description
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Course",
            aggregate_id=self.course_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'course_id': self.course_id.value,
            'title': self.title.value,
            'description': self.description.value
        })
        return base_dict


@dataclass(frozen=True)
class CourseDeprecated(DomainEvent):
    """Event raised when a course is deprecated."""
    course_id: CourseId
    title: Title
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Course",
            aggregate_id=self.course_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'course_id': self.course_id.value,
            'title': self.title.value
        })
        return base_dict


@dataclass(frozen=True)
class CoursePolicyChanged(DomainEvent):
    """Event raised when course refund policy is changed."""
    course_id: CourseId
    old_policy_id: PolicyId
    new_policy_id: PolicyId
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Course",
            aggregate_id=self.course_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'course_id': self.course_id.value,
            'old_policy_id': self.old_policy_id.value,
            'new_policy_id': self.new_policy_id.value
        })
        return base_dict
