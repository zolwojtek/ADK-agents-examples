"""
User domain events.
"""

from dataclasses import dataclass
from typing import Any, Dict

from ..shared.value_objects import UserId, EmailAddress
from ..shared.events import DomainEvent
from .value_objects import UserProfile


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    """Event raised when a user registers."""
    user_id: UserId
    email: EmailAddress
    name: str
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="User",
            aggregate_id=self.user_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': self.user_id.value,
            'email': self.email.value,
            'name': self.name
        })
        return base_dict


@dataclass(frozen=True)
class UserProfileUpdated(DomainEvent):
    """Event raised when user profile is updated."""
    user_id: UserId
    profile: UserProfile
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="User",
            aggregate_id=self.user_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': self.user_id.value,
            'profile': {
                'first_name': self.profile.first_name,
                'last_name': self.profile.last_name,
                'bio': self.profile.bio,
                'avatar_url': self.profile.avatar_url
            }
        })
        return base_dict


@dataclass(frozen=True)
class UserEmailChanged(DomainEvent):
    """Event raised when user email is changed."""
    user_id: UserId
    old_email: EmailAddress
    new_email: EmailAddress
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="User",
            aggregate_id=self.user_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': self.user_id.value,
            'old_email': self.old_email.value,
            'new_email': self.new_email.value
        })
        return base_dict
