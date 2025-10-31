"""
User domain value objects.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime

from ..shared.value_objects import AccessRef, Name


class UserStatus(Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    DELETED = "deleted"


@dataclass(frozen=True)
class UserProfile:
    """User profile information."""
    first_name: Name
    last_name: Name
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    def __post_init__(self):
        if not self.first_name or not self.first_name.value.strip():
            raise ValueError("First name cannot be empty")
        if not self.last_name or not self.last_name.value.strip():
            raise ValueError("Last name cannot be empty")
        
        # Trim whitespace
        object.__setattr__(self, 'first_name', self.first_name.value.strip())
        object.__setattr__(self, 'last_name', self.last_name.value.strip())
        
        if self.bio and len(self.bio) > 1000:
            raise ValueError("Bio too long")
        if self.avatar_url and len(self.avatar_url) > 500:
            raise ValueError("Avatar URL too long")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
