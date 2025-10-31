"""
Unit tests for Order aggregate.
"""

import pytest
from uuid import uuid4

from domain.orders.aggregates import Order
from domain.orders.value_objects import OrderItem, RefundReason
from domain.shared.value_objects import OrderId, PaymentInfo, UserId, CourseId, Money, OrderStatus, PolicyId


class TestOrderAggregate:
    """Test Order aggregate."""
    
    @pytest.fixture
    def order_data(self):
        """Create test order data."""
        return {
            "id": OrderId(str(uuid4())),
            "user_id": UserId("user_123"),
            "items": [OrderItem(course_id=CourseId("course_456"), price_snapshot=Money(99.99, "USD"), policy_id=PolicyId(str(uuid4())))],
            "total_amount": Money(99.99, "USD"),
            "status": OrderStatus.PENDING
        }
    
    @pytest.fixture
    def order(self, order_data):
        """Create a test order."""
        return Order.create_order(**order_data)
    
    def test_create_order(self, order_data):
        """Test creating an order."""
        order = Order.create_order(**order_data)
        
        assert order.id == order_data["id"]
        assert order.user_id == order_data["user_id"]
        assert order.items == order_data["items"]
        assert order.total_amount == order_data["total_amount"]
        assert order.status == order_data["status"]
        assert order.created_at is not None
        assert order.updated_at is not None
        assert len(order.get_domain_events()) == 1
        assert order.get_domain_events()[0].__class__.__name__ == "OrderPlaced"
    
    def test_confirm_payment(self, order):
        """Test confirming payment."""
        payment_info = PaymentInfo("pay_123", "credit_card")
        
        order.confirm_payment(payment_info)
        
        assert order.status == OrderStatus.PAID
        assert order.payment_info == payment_info
        assert order.updated_at > order.created_at
        assert len(order.get_domain_events()) == 2
        assert order.get_domain_events()[1].__class__.__name__ == "OrderPaid"
    
    def test_mark_payment_failed(self, order):
        """Test marking payment as failed."""
        failure_reason = "Insufficient funds"
        
        order.mark_payment_failed(failure_reason)
        
        assert order.status == OrderStatus.FAILED
        assert order.failure_reason == failure_reason
        assert order.updated_at > order.created_at
        assert len(order.get_domain_events()) == 2
        assert order.get_domain_events()[1].__class__.__name__ == "OrderPaymentFailed"
    
    def test_request_refund(self, order):
        """Test requesting refund."""
        order.status = OrderStatus.PAID  # Must be paid to request refund
        refund_reason = RefundReason.NOT_SATISFIED
        
        order.request_refund(refund_reason)
        
        assert order.status == OrderStatus.REFUND_REQUESTED
        assert order.refund_reason == refund_reason
        assert order.updated_at > order.created_at
        assert len(order.get_domain_events()) == 2
        assert order.get_domain_events()[1].__class__.__name__ == "OrderRefundRequested"
    
    def test_request_refund_non_paid_order_raises_error(self, order):
        """Test requesting refund on non-paid order raises error."""
        refund_reason = RefundReason.NOT_SATISFIED
        
        with pytest.raises(ValueError):
            order.request_refund(refund_reason)
    
    def test_approve_refund(self, order):
        """Test approving refund."""
        order.status = OrderStatus.REFUND_REQUESTED
        order.refund_reason = RefundReason.NOT_SATISFIED
        refund_amount = Money(99.99, "USD")
        
        order.approve_refund(refund_amount)
        
        assert order.status == OrderStatus.REFUNDED
        assert order.refund_amount == refund_amount
        assert order.updated_at > order.created_at
        assert len(order.get_domain_events()) == 2
        assert order.get_domain_events()[1].__class__.__name__ == "OrderRefunded"
    
    def test_approve_refund_non_requested_order_raises_error(self, order):
        """Test approving refund on non-requested order raises error."""
        order.status = OrderStatus.PAID  # Not REFUND_REQUESTED
        refund_amount = Money(99.99, "USD")
        
        with pytest.raises(ValueError):
            order.approve_refund(refund_amount)
    
    def test_complete_refund_workflow(self, order):
        """Test complete refund workflow: request -> approve."""
        # Start with paid order
        order.status = OrderStatus.PAID
        refund_reason = RefundReason.NOT_SATISFIED
        refund_amount = Money(99.99, "USD")
        
        # Step 1: Request refund
        order.request_refund(refund_reason)
        assert order.status == OrderStatus.REFUND_REQUESTED
        assert order.refund_reason == refund_reason
        assert len(order.get_domain_events()) == 2
        assert order.get_domain_events()[1].__class__.__name__ == "OrderRefundRequested"
        
        # Step 2: Approve refund
        order.approve_refund(refund_amount)
        assert order.status == OrderStatus.REFUNDED
        assert order.refund_amount == refund_amount
        assert len(order.get_domain_events()) == 3
        assert order.get_domain_events()[2].__class__.__name__ == "OrderRefunded"
    
    def test_reject_refund(self, order):
        """Test rejecting refund request."""
        # Start with refund requested order
        order.status = OrderStatus.REFUND_REQUESTED
        order.refund_reason = RefundReason.NOT_SATISFIED
        
        order.reject_refund("Policy violation")
        
        assert order.status == OrderStatus.REFUND_REQUESTED  # Status doesn't change
        assert order.refund_reason is None  # Reason is cleared
        assert order.updated_at > order.created_at
    
    def test_reject_refund_non_requested_order_raises_error(self, order):
        """Test rejecting refund on non-requested order raises error."""
        order.status = OrderStatus.PAID  # Not REFUND_REQUESTED
        
        with pytest.raises(ValueError, match="No active refund request to reject"):
            order.reject_refund("Policy violation")
    
    def test_cancel_order(self, order):
        """Test cancelling order."""
        cancellation_reason = RefundReason.CHANGED_MIND
        
        order.cancel(cancellation_reason)
        
        assert order.status == OrderStatus.CANCELLED
        assert order.cancellation_reason == cancellation_reason
        assert order.updated_at > order.created_at
        assert len(order.get_domain_events()) == 2
        assert order.get_domain_events()[1].__class__.__name__ == "OrderCancelled"
    
    def test_cancel_paid_order_raises_error(self, order):
        """Test cancelling paid order raises error."""
        order.status = OrderStatus.PAID
        
        with pytest.raises(ValueError):
            order.cancel("Changed mind")
    
    def test_clear_domain_events(self, order):
        """Test clearing domain events."""
        order.confirm_payment(PaymentInfo("payment_id", "pay_123"))  # Generate an event
        
        assert len(order.get_domain_events()) == 2
        order.clear_domain_events()
        assert len(order.get_domain_events()) == 0
    
    def test_order_equality(self, order_data):
        """Test order equality."""
        order1 = Order(**order_data)
        order2 = Order(**order_data)
        
        assert order1 == order2
    
    def test_order_inequality(self, order_data):
        """Test order inequality."""
        order1 = Order(**order_data)
        order_data["id"] = OrderId(str(uuid4()))
        order2 = Order(**order_data)
        
        assert order1 != order2
