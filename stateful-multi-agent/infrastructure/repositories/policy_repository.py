"""
Policy repository implementation.
"""

from typing import List, Optional
from uuid import uuid4

from domain.policies.repositories import PolicyRepository as IPolicyRepository
from domain.policies.aggregates import RefundPolicy
from domain.policies.value_objects import PolicyStatus
from domain.shared.value_objects import PolicyId, PolicyType, RefundPeriod
from .base import InMemoryRepository


class PolicyRepository(InMemoryRepository[RefundPolicy, PolicyId], IPolicyRepository):
    """In-memory implementation of PolicyRepository."""
    
    def __init__(self):
        super().__init__()
        self._name_index: dict[str, PolicyId] = {}  # name -> policy_id
        self._type_index: dict[PolicyType, List[PolicyId]] = {}  # type -> [policy_ids]
        self._status_index: dict[str, List[PolicyId]] = {}  # status -> [policy_ids]
    
    def find_by_id(self, policy_id: PolicyId) -> Optional[RefundPolicy]:
        """Find policy by ID."""
        return super().get_by_id(policy_id)
    
    def list_active(self) -> List[RefundPolicy]:
        """List all active policies."""
        return self.get_active_policies()
    
    def get_by_name(self, name: str) -> Optional[RefundPolicy]:
        """Get policy by name."""
        policy_id = self._name_index.get(name)
        if policy_id:
            return self.find_by_id(policy_id)
        return None
    
    def get_by_type(self, policy_type: PolicyType) -> List[RefundPolicy]:
        """Get policies by type."""
        policy_ids = self._type_index.get(policy_type, [])
        policies = []
        for policy_id in policy_ids:
            policy = self.find_by_id(policy_id)
            if policy:
                policies.append(policy)
        return policies
    
    def get_by_status(self, status: PolicyStatus) -> List[RefundPolicy]:
        """Get policies by status."""
        policy_ids = self._status_index.get(status, [])
        policies = []
        for policy_id in policy_ids:
            policy = self.find_by_id(policy_id)
            if policy:
                policies.append(policy)
        return policies
    
    def get_active_policies(self) -> List[RefundPolicy]:
        """Get all active policies."""
        return self.get_by_status(PolicyStatus.ACTIVE)
    
    def get_deprecated_policies(self) -> List[RefundPolicy]:
        """Get all deprecated policies."""
        return self.get_by_status(PolicyStatus.DEPRECATED)
    
    def get_refund_policies(self) -> List[RefundPolicy]:
        """Get all refund policies."""
        return self.get_by_type(PolicyType.STANDARD)
    
    def get_policy_by_refund_period(self, refund_period: RefundPeriod) -> Optional[RefundPolicy]:
        """Get policy by refund period."""
        for policy in self.get_all():
            if policy.refund_period.days == refund_period.days:
                return policy
        return None
    
    def save(self, policy: RefundPolicy) -> RefundPolicy:
        """Save policy with indexing."""
        # Remove any existing name for this policy ID from the index
        if policy.id:
            # Find and remove any existing name for this policy ID
            names_to_remove = []
            for name, policy_id in self._name_index.items():
                if policy_id == policy.id:
                    names_to_remove.append(name)
            for name in names_to_remove:
                del self._name_index[name]
        
        # Check for name uniqueness
        if policy.name.value in self._name_index:
            existing_policy_id = self._name_index[policy.name.value]
            if existing_policy_id != policy.id:
                raise ValueError(f"Policy with name '{policy.name.value}' already exists")
        
        # Save policy
        saved_policy = super().save(policy)
        
        # Update name index
        self._name_index[policy.name.value] = policy.id
        
        # Update type index
        if policy.policy_type not in self._type_index:
            self._type_index[policy.policy_type] = []
        if policy.id not in self._type_index[policy.policy_type]:
            self._type_index[policy.policy_type].append(policy.id)
        
        # Update status index - remove from old status and add to new status
        if policy.id:
            # Remove from any existing status index
            statuses_to_remove = []
            for status, policy_ids in self._status_index.items():
                if policy.id in policy_ids:
                    policy_ids.remove(policy.id)
                    if not policy_ids:  # Mark empty status entries for removal
                        statuses_to_remove.append(status)
            # Remove empty status entries after iteration
            for status in statuses_to_remove:
                del self._status_index[status]
        
        # Add to new status index
        if policy.status not in self._status_index:
            self._status_index[policy.status] = []
        if policy.id not in self._status_index[policy.status]:
            self._status_index[policy.status].append(policy.id)
        
        return saved_policy
    
    def delete(self, policy_id: PolicyId) -> bool:
        """Delete policy by ID."""
        policy = self.find_by_id(policy_id)
        if policy:
            # Remove from indexes
            if policy.name.value in self._name_index:
                del self._name_index[policy.name.value]
            
            if policy.policy_type in self._type_index:
                if policy.id in self._type_index[policy.policy_type]:
                    self._type_index[policy.policy_type].remove(policy.id)
                if not self._type_index[policy.policy_type]:
                    del self._type_index[policy.policy_type]
            
            if policy.status in self._status_index:
                if policy.id in self._status_index[policy.status]:
                    self._status_index[policy.status].remove(policy.id)
                if not self._status_index[policy.status]:
                    del self._status_index[policy.status]
            
            return super().delete(policy_id)
        return False
    
    def clear(self) -> None:
        """Clear all policies and indexes."""
        super().clear()
        self._name_index.clear()
        self._type_index.clear()
        self._status_index.clear()
