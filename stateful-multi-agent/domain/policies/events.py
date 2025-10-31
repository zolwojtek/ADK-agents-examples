"""
Policy domain events.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from ..shared.value_objects import PolicyId, PolicyType, RefundPeriod
from ..shared.events import DomainEvent
from .value_objects import PolicyName


@dataclass(frozen=True)
class PolicyCreated(DomainEvent):
    """Event raised when a refund policy is created."""
    policy_id: PolicyId
    name: PolicyName
    policy_type: PolicyType
    refund_period_days: int
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="RefundPolicy",
            aggregate_id=self.policy_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'policy_id': self.policy_id.value,
            'name': self.name.value,
            'policy_type': self.policy_type.value,
            'refund_period_days': self.refund_period_days
        })
        return base_dict


@dataclass(frozen=True)
class PolicyUpdated(DomainEvent):
    """Event raised when a refund policy is updated."""
    policy_id: PolicyId
    new_conditions: str
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="RefundPolicy",
            aggregate_id=self.policy_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'policy_id': self.policy_id.value,
            'new_conditions': self.new_conditions
        })
        return base_dict


@dataclass(frozen=True)
class PolicyDeprecated(DomainEvent):
    """Event raised when a refund policy is deprecated."""
    policy_id: PolicyId
    name: PolicyName
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="RefundPolicy",
            aggregate_id=self.policy_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'policy_id': self.policy_id.value,
            'name': self.name.value
        })
        return base_dict


@dataclass(frozen=True)
class PolicyReactivated(DomainEvent):
    """Event raised when a refund policy is reactivated."""
    policy_id: PolicyId
    name: PolicyName
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="RefundPolicy",
            aggregate_id=self.policy_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'policy_id': self.policy_id.value,
            'name': self.name.value
        })
        return base_dict
