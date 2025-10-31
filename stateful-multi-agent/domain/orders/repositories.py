"""
Order repository interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..shared.value_objects import OrderId, UserId
from .aggregates import Order


class OrderRepository(ABC):
    """Repository interface for Order aggregate."""
    
    @abstractmethod
    def save(self, order: Order) -> None:
        """Save order aggregate."""
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        """Find order by ID."""
        pass
    
    @abstractmethod
    def list_by_user(self, user_id: UserId) -> List[Order]:
        """List orders by user."""
        pass
    
    @abstractmethod
    def find_by_payment_id(self, payment_id: str) -> Optional[Order]:
        """Find order by payment ID."""
        pass
