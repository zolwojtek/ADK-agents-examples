"""
Policy domain value objects.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PolicyStatus(Enum):
    """Refund policy status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class PolicyName:
    """Policy name."""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Policy name cannot be empty")
        # Trim whitespace
        object.__setattr__(self, 'value', self.value.strip())
        if len(self.value) > 100:
            raise ValueError("Policy name too long")


@dataclass(frozen=True)
class PolicyConditions:
    """Policy conditions and rules."""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Policy conditions cannot be empty")
        # Trim whitespace
        object.__setattr__(self, 'value', self.value.strip())
        if len(self.value) > 1000:
            raise ValueError("Policy conditions too long")
