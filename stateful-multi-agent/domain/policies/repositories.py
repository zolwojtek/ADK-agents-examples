"""
Policy repository interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..shared.value_objects import PolicyId
from .aggregates import RefundPolicy


class PolicyRepository(ABC):
    """Repository interface for RefundPolicy aggregate."""
    
    @abstractmethod
    def save(self, policy: RefundPolicy) -> None:
        """Save policy aggregate."""
        pass
    
    @abstractmethod
    def find_by_id(self, policy_id: PolicyId) -> Optional[RefundPolicy]:
        """Find policy by ID."""
        pass
    
    @abstractmethod
    def list_active(self) -> List[RefundPolicy]:
        """List all active policies."""
        pass
