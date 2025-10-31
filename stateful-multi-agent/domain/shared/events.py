"""
Shared domain event base class.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""
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
            'aggregate_id': self.aggregate_id
        }
