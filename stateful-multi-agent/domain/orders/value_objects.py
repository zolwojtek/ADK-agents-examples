"""
Order domain value objects.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ..shared.value_objects import CourseId, Money, PolicyId


class RefundReason(Enum):
    """Refund request reasons."""
    NOT_SATISFIED = "not_satisfied"
    TECHNICAL_ISSUES = "technical_issues"
    CHANGED_MIND = "changed_mind"
    DUPLICATE_PURCHASE = "duplicate_purchase"
    OTHER = "other"


@dataclass(frozen=True)
class OrderItem:
    """Order item representing a course purchase."""
    course_id: CourseId
    price_snapshot: Money
    policy_id: PolicyId
    quantity: int = 1
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.quantity > 1:
            raise ValueError("Course quantity cannot be more than 1")
    
    def get_total_price(self) -> Money:
        """Get total price for this item."""
        return self.price_snapshot.multiply(self.quantity)
