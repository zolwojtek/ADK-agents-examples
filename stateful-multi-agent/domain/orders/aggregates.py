"""
Order aggregate root.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid

from ..shared.value_objects import OrderId, UserId, Money, OrderStatus, PaymentInfo, Entity
from .value_objects import OrderItem, RefundReason
from .events import OrderPlaced, OrderPaid, OrderRefunded, OrderCancelled, OrderPaymentFailed, OrderRefundRequested


@dataclass(eq=False)
class Order(Entity):
    """
    Order aggregate root.
    
    Responsibility: represent the purchase transaction lifecycle and its items; 
    manage statuses (placed, paid, refunded, cancelled).
    """
    id: OrderId
    user_id: UserId
    items: List[OrderItem]
    status: OrderStatus
    total_amount: Money
    payment_info: Optional[PaymentInfo] = None
    refund_reason: Optional[RefundReason] = None
    cancellation_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    refund_amount: Optional[Money] = None

    @classmethod
    def create_order(
        cls,
        user_id: UserId,
        items: List[OrderItem],
        id: Optional[OrderId] = None,
        total_amount: Optional[Money] = None,
        status: OrderStatus = OrderStatus.PENDING,
        **_: object,
    ) -> 'Order':
        """Create a new order.

        Accepts optional id/total_amount/status to be compatible with callers
        that provide these as keyword args. If not provided, sensible defaults
        are computed.
        """
        if not items:
            raise ValueError("Order must contain at least one item")
        
        order_id = id or OrderId(str(uuid.uuid4()))
        
        # Calculate total amount if not provided
        if total_amount is None:
            total_amount = Money(Decimal('0'), items[0].price_snapshot.currency)
            for item in items:
                if item.price_snapshot.currency != total_amount.currency:
                    raise ValueError("All items must have the same currency")
                total_amount = total_amount.add(item.get_total_price())
        
        order = cls(
            id=order_id,
            user_id=user_id,
            items=items,
            status=status,
            total_amount=total_amount
        )
        
        # Raise domain event
        course_ids = [item.course_id for item in items]
        event = OrderPlaced(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id=order_id.value,
            order_id=order_id,
            user_id=user_id,
            course_ids=course_ids,
            total_amount=total_amount
        )
        order.add_domain_event(event)
        
        return order
    
    def add_item(self, course_id, price: Money, policy_id) -> None:
        """Add item to order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Cannot add items to non-pending order")
        
        # Check for duplicate course
        for item in self.items:
            if item.course_id == course_id:
                raise ValueError("Course already in order")
        
        # Check currency consistency
        if self.items and price.currency != self.items[0].price_snapshot.currency:
            raise ValueError("Item currency must match order currency")
        
        from ..shared.value_objects import CourseId, PolicyId
        new_item = OrderItem(
            course_id=CourseId(course_id) if isinstance(course_id, str) else course_id,
            price_snapshot=price,
            policy_id=PolicyId(policy_id) if isinstance(policy_id, str) else policy_id
        )
        
        self.items.append(new_item)
        self.total_amount = self.total_amount.add(new_item.get_total_price())
        self.updated_at = datetime.now()
    
    def remove_item(self, course_id) -> None:
        """Remove item from order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Cannot remove items from non-pending order")
        
        from ..shared.value_objects import CourseId
        course_id_obj = CourseId(course_id) if isinstance(course_id, str) else course_id
        
        for i, item in enumerate(self.items):
            if item.course_id == course_id_obj:
                self.items.pop(i)
                self.total_amount = self.total_amount.subtract(item.get_total_price())
                self.updated_at = datetime.now()
                return
        
        raise ValueError("Course not found in order")
    
    def confirm_payment(self, payment_info: PaymentInfo) -> None:
        """Confirm payment for the order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be paid")
        
        self.status = OrderStatus.PAID
        self.payment_info = payment_info
        self.touch()
        
        # Raise domain event
        course_ids = [item.course_id for item in self.items]
        event = OrderPaid(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id=self.id.value,
            order_id=self.id,
            user_id=self.user_id,
            course_ids=course_ids,
            payment_id=payment_info.payment_id
        )
        self.add_domain_event(event)
    
    def complete_order(self) -> None:
        """Mark order as completed."""
        if self.status != OrderStatus.PAID:
            raise ValueError("Only paid orders can be completed")
        
        # For now, we don't have a COMPLETED status, so this is a no-op
        # In a real system, you might want to add a COMPLETED status
        self.updated_at = datetime.now()
    
    def cancel(self, reason: str) -> None:
        """Cancel the order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Cannot cancel order in current status")
        
        self.status = OrderStatus.CANCELLED
        self.cancellation_reason = reason
        self.touch()
        
        # Raise domain event
        event = OrderCancelled(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id=self.id.value,
            order_id=self.id,
            user_id=self.user_id
        )
        self.add_domain_event(event)
    
    def expire_order(self) -> None:
        """Expire the order (e.g., after timeout)."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can expire")
        
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def can_be_refunded(self) -> bool:
        """Check if order can be refunded."""
        return self.status == OrderStatus.PAID
    
    def is_payment_pending(self) -> bool:
        """Check if order payment is pending."""
        return self.status == OrderStatus.PENDING
    
    def request_refund(self, reason: RefundReason) -> None:
        """Request refund for the order."""
        if not self.can_be_refunded():
            raise ValueError("Order cannot be refunded")
        self.status = OrderStatus.REFUND_REQUESTED
        self.refund_reason = reason
        self.touch()
        
        # Raise domain event
        course_ids = [item.course_id for item in self.items]
        event = OrderRefundRequested(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id=self.id.value,
            order_id=self.id,
            user_id=self.user_id,
            course_ids=course_ids,
            refund_reason=reason
        )
        self.add_domain_event(event)

    def mark_payment_failed(self, failure_reason: str) -> None:
        """Mark the payment as failed."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can fail payment")
        self.status = OrderStatus.FAILED
        self.failure_reason = failure_reason
        self.touch()
        
        # Raise domain event
        course_ids = [item.course_id for item in self.items]
        event = OrderPaymentFailed(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id=self.id.value,
            order_id=self.id,
            user_id=self.user_id,
            failure_reason=failure_reason
        )
        self.add_domain_event(event)
    
    def approve_refund(self, refund_amount: Money) -> None:
        """Approve refund request."""
        if self.status != OrderStatus.REFUND_REQUESTED:
            raise ValueError("Only orders with refund requests can be approved")
        if not self.refund_reason:
            raise ValueError("No refund request found")
        
        self.status = OrderStatus.REFUNDED
        self.refund_amount = refund_amount
        self.touch()
        
        # Raise domain event
        course_ids = [item.course_id for item in self.items]
        event = OrderRefunded(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id=self.id.value,
            order_id=self.id,
            user_id=self.user_id,
            course_ids=course_ids,
            refund_reason=self.refund_reason
        )
        self.add_domain_event(event)
    
    def reject_refund(self, reason: str) -> None:
        """Reject refund request."""
        if self.status != OrderStatus.REFUND_REQUESTED:
            raise ValueError("No active refund request to reject")
        if not self.refund_reason:
            raise ValueError("No refund request found")
        
        self.refund_reason = None
        self.updated_at = datetime.now()
    
    def get_domain_events(self) -> List:
        """Get and clear domain events."""
        events = self._domain_events.copy()
        return events
    
    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()
