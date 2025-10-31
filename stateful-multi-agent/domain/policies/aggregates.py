"""
RefundPolicy aggregate root.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

from ..shared.value_objects import PolicyId, RefundPeriod, PolicyType, Entity
from .value_objects import PolicyName, PolicyConditions, PolicyStatus
from .events import PolicyCreated, PolicyUpdated, PolicyDeprecated, PolicyReactivated


@dataclass
class RefundPolicy(Entity):
    """
    RefundPolicy aggregate root.
    
    Responsibility: express refund eligibility rules (time-window, conditions, exceptions).
    """
    id: PolicyId
    name: PolicyName
    policy_type: PolicyType
    refund_period: RefundPeriod
    conditions: PolicyConditions
    status: PolicyStatus = PolicyStatus.ACTIVE
    
    @classmethod
    def create_policy(
        cls,
        name: PolicyName,
        policy_type: PolicyType,
        refund_period: RefundPeriod,
        conditions: PolicyConditions
    ) -> 'RefundPolicy':
        """Create a new refund policy."""
        policy_id = PolicyId(str(uuid.uuid4()))
        policy = cls(
            id=policy_id,
            name=name,
            policy_type=policy_type,
            refund_period=refund_period,
            conditions=conditions,
            status=PolicyStatus.ACTIVE
        )
        
        # Raise domain event
        event = PolicyCreated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id=policy_id.value,
            policy_id=policy_id,
            name=name,
            policy_type=policy_type,
            refund_period_days=refund_period.days
        )
        policy.add_domain_event(event)
        
        return policy
    
    def update_terms(self, new_refund_period: RefundPeriod, new_conditions: PolicyConditions) -> None:
        """Update policy terms."""
        if self.status != PolicyStatus.ACTIVE:
            raise ValueError("Cannot update deprecated or archived policy")
        
        self.refund_period = new_refund_period
        self.conditions = new_conditions
        self.updated_at = datetime.now()
        
        # Raise domain event
        event = PolicyUpdated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id=self.id.value,
            policy_id=self.id,
            new_conditions=new_conditions.value
        )
        self._domain_events.append(event)
    
    def rename(self, new_name: PolicyName) -> None:
        """Rename the policy."""
        if self.status != PolicyStatus.ACTIVE:
            raise ValueError("Cannot rename deprecated or archived policy")
        
        self.name = new_name
        self.updated_at = datetime.now()
    
    def deprecate(self, reason: str) -> None:
        """Deprecate the policy."""
        if self.status == PolicyStatus.DEPRECATED:
            raise ValueError("Policy is already deprecated")
        if self.status == PolicyStatus.ARCHIVED:
            raise ValueError("Cannot deprecate archived policy")
        
        self.status = PolicyStatus.DEPRECATED
        self.updated_at = datetime.now()
        
        # Raise domain event
        event = PolicyDeprecated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id=self.id.value,
            policy_id=self.id,
            name=self.name
        )
        self._domain_events.append(event)
    
    def reactivate(self) -> None:
        """Reactivate a deprecated policy."""
        if self.status != PolicyStatus.DEPRECATED:
            raise ValueError("Can only reactivate deprecated policies")
        
        self.status = PolicyStatus.ACTIVE
        self.updated_at = datetime.now()
        
        # Raise domain event
        event = PolicyReactivated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id=self.id.value,
            policy_id=self.id,
            name=self.name
        )
        self._domain_events.append(event)
    
    def archive(self) -> None:
        """Archive the policy."""
        if self.status == PolicyStatus.ARCHIVED:
            raise ValueError("Policy is already archived")
        
        self.status = PolicyStatus.ARCHIVED
        self.updated_at = datetime.now()
    
    def is_refund_allowed(self, purchase_date: datetime, current_date: datetime, progress: float) -> bool:
        """Check if refund is allowed based on policy rules."""
        if self.status != PolicyStatus.ACTIVE:
            return False
        
        # Check time window
        days_since_purchase = (current_date - purchase_date).days
        if days_since_purchase > self.refund_period.days:
            return False
        
        # Check progress conditions (basic implementation)
        if self.policy_type == PolicyType.NO_REFUND:
            return False
        
        # For now, allow refund if within time window and not completed
        return progress < 100.0
    
    def can_be_assigned(self) -> bool:
        """Check if policy can be assigned to new courses."""
        return self.status == PolicyStatus.ACTIVE
    
    def get_domain_events(self) -> List:
        """Get and clear domain events."""
        events = self._domain_events.copy()
        return events
    
    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()
