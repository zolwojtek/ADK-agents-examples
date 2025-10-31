"""
Order domain events.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from ..shared.value_objects import OrderId, UserId, CourseId, Money
from ..shared.events import DomainEvent
from .value_objects import RefundReason


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    """Event raised when an order is placed."""
    order_id: OrderId
    user_id: UserId
    course_ids: List[CourseId]
    total_amount: Money
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Order",
            aggregate_id=self.order_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'order_id': self.order_id.value,
            'user_id': self.user_id.value,
            'course_ids': [course_id.value for course_id in self.course_ids],
            'total_amount': {
                'amount': str(self.total_amount.amount),
                'currency': self.total_amount.currency
            }
        })
        return base_dict


@dataclass(frozen=True)
class OrderPaid(DomainEvent):
    """Event raised when an order is paid."""
    order_id: OrderId
    user_id: UserId
    course_ids: List[CourseId]
    payment_id: str
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Order",
            aggregate_id=self.order_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'order_id': self.order_id.value,
            'user_id': self.user_id.value,
            'course_ids': [course_id.value for course_id in self.course_ids],
            'payment_id': self.payment_id
        })
        return base_dict


@dataclass(frozen=True)
class OrderRefundRequested(DomainEvent):
    """Event raised when an order refund is requested."""
    order_id: OrderId
    user_id: UserId
    course_ids: List[CourseId]
    refund_reason: RefundReason
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Order",
            aggregate_id=self.order_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'order_id': self.order_id.value,
            'user_id': self.user_id.value,
            'course_ids': [course_id.value for course_id in self.course_ids],
            'refund_reason': self.refund_reason.value
        })
        return base_dict


@dataclass(frozen=True)
class OrderRefunded(DomainEvent):
    """Event raised when an order is refunded."""
    order_id: OrderId
    user_id: UserId
    course_ids: List[CourseId]
    refund_reason: RefundReason
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Order",
            aggregate_id=self.order_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'order_id': self.order_id.value,
            'user_id': self.user_id.value,
            'course_ids': [course_id.value for course_id in self.course_ids],
            'refund_reason': self.refund_reason.value
        })
        return base_dict


@dataclass(frozen=True)
class OrderPaymentFailed(DomainEvent):
    """Event raised when an order payment fails."""
    order_id: OrderId
    user_id: UserId
    failure_reason: str
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Order",
            aggregate_id=self.order_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'order_id': self.order_id.value,
            'user_id': self.user_id.value,
            'failure_reason': self.failure_reason
        })
        return base_dict


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    """Event raised when an order is cancelled."""
    order_id: OrderId
    user_id: UserId
    
    def __post_init__(self):
        super().__init__(
            event_id=self.event_id,
            occurred_on=self.occurred_on,
            aggregate_type="Order",
            aggregate_id=self.order_id.value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'order_id': self.order_id.value,
            'user_id': self.user_id.value
        })
        return base_dict
