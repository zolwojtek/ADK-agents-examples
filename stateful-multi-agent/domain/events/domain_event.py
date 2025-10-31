"""
Base domain event class.
"""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass(frozen=True)
class DomainEvent(ABC):
    """
    Base class for all domain events.
    
    All domain events should inherit from this class and be immutable.
    """
    event_id: str
    occurred_on: datetime
    aggregate_type: str
    aggregate_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_id': self.event_id,
            'occurred_on': self.occurred_on.isoformat(),
            'aggregate_type': self.aggregate_type,
            'aggregate_id': self.aggregate_id,
            'event_type': self.__class__.__name__
        }
