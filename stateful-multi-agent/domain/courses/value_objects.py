"""
Course domain value objects.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Title:
    """Course title."""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Title cannot be empty")
        # Trim whitespace
        object.__setattr__(self, 'value', self.value.strip())
        if len(self.value) > 200:
            raise ValueError("Title too long")


@dataclass(frozen=True)
class Description:
    """Course description."""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Description cannot be empty")
        # Trim whitespace
        object.__setattr__(self, 'value', self.value.strip())
        if len(self.value) > 2000:
            raise ValueError("Description too long")