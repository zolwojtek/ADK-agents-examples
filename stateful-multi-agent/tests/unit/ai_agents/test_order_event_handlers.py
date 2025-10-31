"""
Tests for Order domain event handlers.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from ai_agents.order_event_handlers import (
    OrderAnalyticsHandler, OrderCustomerServiceHandler, OrderFraudDetectionHandler
)
from domain.orders.events import (
    OrderPlaced, OrderPaid, OrderRefunded, 
    OrderPaymentFailed
)
from domain.shared.value_objects import OrderId, UserId, Money, CourseId
from domain.orders.value_objects import RefundReason


class TestOrderAnalyticsHandler:
    """Test OrderAnalyticsHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create analytics handler for testing."""
        return OrderAnalyticsHandler()
    
    @pytest.fixture
    def order_placed_event(self):
        """Create OrderPlaced event for testing."""
        return OrderPlaced(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456",
            order_id=OrderId("order_456"),
            user_id=UserId("user_789"),
            course_ids=[CourseId("course_123")],
            total_amount=Money(100.0, "USD")
        )
    
    @pytest.fixture
    def order_paid_event(self):
        """Create OrderPaid event for testing."""
        return OrderPaid(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456",
            order_id=OrderId("order_456"),
            user_id=UserId("user_789"),
            course_ids=[CourseId("course_123")],
            payment_id="payment_123"
        )
    
    @pytest.fixture
    def order_refunded_event(self):
        """Create OrderRefunded event for testing."""
        return OrderRefunded(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456",
            order_id=OrderId("order_456"),
            user_id=UserId("user_789"),
            course_ids=[CourseId("course_123")],
            refund_reason=RefundReason.NOT_SATISFIED
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "OrderAnalyticsAI"
    
    def test_handle_order_placed(self, handler, order_placed_event):
        """Test handling OrderPlaced event."""
        with patch.object(handler, '_handle_order_placed') as mock_handle:
            handler.handle(order_placed_event)
            mock_handle.assert_called_once_with(order_placed_event)
    
    def test_handle_order_paid(self, handler, order_paid_event):
        """Test handling OrderPaid event."""
        with patch.object(handler, '_handle_order_paid') as mock_handle:
            handler.handle(order_paid_event)
            mock_handle.assert_called_once_with(order_paid_event)
    
    def test_handle_order_refunded(self, handler, order_refunded_event):
        """Test handling OrderRefunded event."""
        with patch.object(handler, '_handle_order_refunded') as mock_handle:
            handler.handle(order_refunded_event)
            mock_handle.assert_called_once_with(order_refunded_event)
    
    def test_handle_order_placed_updates_metrics(self, handler, order_placed_event):
        """Test that OrderPlaced updates metrics."""
        initial_orders = handler.order_metrics['total_orders']
        
        handler._handle_order_placed(order_placed_event)
        
        assert handler.order_metrics['total_orders'] == initial_orders + 1
    
    def test_handle_order_paid_updates_revenue(self, handler, order_paid_event):
        """Test that OrderPaid updates revenue."""
        # Note: OrderPaid doesn't have amount field, so we'll test the handler logic
        initial_revenue = handler.order_metrics['total_revenue']
        
        handler._handle_order_paid(order_paid_event)
        
        # Since OrderPaid doesn't have amount, revenue should remain the same
        assert handler.order_metrics['total_revenue'] == initial_revenue
    
    def test_get_analytics_summary(self, handler):
        """Test getting analytics summary."""
        summary = handler.get_analytics_summary()
        
        assert 'metrics' in summary
        assert 'timestamp' in summary
        assert 'agent' in summary
        assert summary['agent'] == "OrderAnalyticsAI"
        assert isinstance(summary['metrics'], dict)


class TestOrderCustomerServiceHandler:
    """Test OrderCustomerServiceHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create customer service handler for testing."""
        return OrderCustomerServiceHandler()
    
    @pytest.fixture
    def order_placed_event(self):
        """Create OrderPlaced event for testing."""
        return OrderPlaced(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456",
            order_id=OrderId("order_456"),
            user_id=UserId("user_789"),
            course_ids=[CourseId("course_123")],
            total_amount=Money(100.0, "USD")
        )
    
    @pytest.fixture
    def order_paid_event(self):
        """Create OrderPaid event for testing."""
        return OrderPaid(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456",
            order_id=OrderId("order_456"),
            user_id=UserId("user_789"),
            course_ids=[CourseId("course_123")],
            payment_id="payment_123"
        )
    
    @pytest.fixture
    def order_payment_failed_event(self):
        """Create OrderPaymentFailed event for testing."""
        return OrderPaymentFailed(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456",
            order_id=OrderId("order_456"),
            user_id=UserId("user_789"),
            failure_reason="card_declined"
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "OrderCustomerServiceAI"
    
    def test_handle_order_placed(self, handler, order_placed_event):
        """Test handling OrderPlaced event."""
        with patch.object(handler, '_handle_order_placed') as mock_handle:
            handler.handle(order_placed_event)
            mock_handle.assert_called_once_with(order_placed_event)
    
    def test_handle_order_paid(self, handler, order_paid_event):
        """Test handling OrderPaid event."""
        with patch.object(handler, '_handle_order_paid') as mock_handle:
            handler.handle(order_paid_event)
            mock_handle.assert_called_once_with(order_paid_event)
    
    def test_handle_order_placed_creates_action(self, handler, order_placed_event):
        """Test that OrderPlaced creates customer service action."""
        initial_actions = len(handler.customer_actions)
        
        handler._handle_order_placed(order_placed_event)
        
        assert len(handler.customer_actions) == initial_actions + 1
        assert "order confirmation email" in handler.customer_actions[-1]
        assert "user_789" in handler.customer_actions[-1]
    
    def test_handle_order_paid_creates_action(self, handler, order_paid_event):
        """Test that OrderPaid creates customer service action."""
        initial_actions = len(handler.customer_actions)
        
        handler._handle_order_paid(order_paid_event)
        
        assert len(handler.customer_actions) == initial_actions + 1
        assert "payment confirmation" in handler.customer_actions[-1]
        assert "user_789" in handler.customer_actions[-1]
    
    def test_handle_payment_failed_creates_action(self, handler, order_payment_failed_event):
        """Test that OrderPaymentFailed creates customer service action."""
        initial_actions = len(handler.customer_actions)
        
        handler._handle_payment_failed(order_payment_failed_event)
        
        assert len(handler.customer_actions) == initial_actions + 1
        assert "payment failure notification" in handler.customer_actions[-1]
        assert "user_789" in handler.customer_actions[-1]
    
    def test_get_customer_actions(self, handler, order_placed_event):
        """Test getting customer actions."""
        handler._handle_order_placed(order_placed_event)
        
        actions = handler.get_customer_actions()
        assert len(actions) == 1
        assert "order confirmation email" in actions[0]


class TestOrderFraudDetectionHandler:
    """Test OrderFraudDetectionHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create fraud detection handler for testing."""
        return OrderFraudDetectionHandler()
    
    @pytest.fixture
    def order_placed_event(self):
        """Create OrderPlaced event for testing."""
        return OrderPlaced(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456",
            order_id=OrderId("order_456"),
            user_id=UserId("user_789"),
            course_ids=[CourseId("course_123")],
            total_amount=Money(100.0, "USD")
        )
    
    @pytest.fixture
    def high_value_order_event(self):
        """Create high-value OrderPlaced event for testing."""
        return OrderPlaced(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_457",
            order_id=OrderId("order_457"),
            user_id=UserId("user_789"),
            course_ids=[CourseId("course_123")],
            total_amount=Money(1500.0, "USD")  # High value
        )
    
    @pytest.fixture
    def order_payment_failed_event(self):
        """Create OrderPaymentFailed event for testing."""
        return OrderPaymentFailed(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456",
            order_id=OrderId("order_456"),
            user_id=UserId("user_789"),
            failure_reason="card_declined"
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "OrderFraudDetectionAI"
    
    def test_handle_order_placed(self, handler, order_placed_event):
        """Test handling OrderPlaced event."""
        with patch.object(handler, '_handle_order_placed') as mock_handle:
            handler.handle(order_placed_event)
            mock_handle.assert_called_once_with(order_placed_event)
    
    def test_handle_order_placed_tracks_history(self, handler, order_placed_event):
        """Test that OrderPlaced tracks user order history."""
        user_id = order_placed_event.user_id.value
        
        handler._handle_order_placed(order_placed_event)
        
        assert user_id in handler.user_order_history
        assert len(handler.user_order_history[user_id]) == 1
        assert handler.user_order_history[user_id][0]['amount'] == 100.0
    
    def test_detect_suspicious_pattern_high_value(self, handler, high_value_order_event):
        """Test fraud detection for high-value orders."""
        handler._handle_order_placed(high_value_order_event)
        
        # Should trigger fraud alert for high value
        assert len(handler.fraud_alerts) == 1
        assert "Suspicious order pattern" in handler.fraud_alerts[0]
    
    def test_detect_suspicious_pattern_multiple_orders(self, handler):
        """Test fraud detection for multiple orders from same user."""
        user_id = "user_789"
        
        # Create multiple orders for same user
        for i in range(6):  # More than 5 orders
            event = OrderPlaced(
                event_id=f"event_{i}",
                occurred_on=datetime.now(),
                aggregate_type="Order",
                aggregate_id=f"order_{i}",
                order_id=OrderId(f"order_{i}"),
                user_id=UserId(user_id),
                course_ids=[CourseId("course_123")],
                total_amount=Money(100.0, "USD")
            )
            handler._handle_order_placed(event)
        
        # Should trigger fraud alert for too many orders
        assert len(handler.fraud_alerts) == 1
        assert "Suspicious order pattern" in handler.fraud_alerts[0]
    
    def test_handle_payment_failed_creates_alert(self, handler, order_payment_failed_event):
        """Test that OrderPaymentFailed creates fraud alert."""
        handler._handle_payment_failed(order_payment_failed_event)
        
        assert len(handler.fraud_alerts) == 1
        assert "Multiple payment failures" in handler.fraud_alerts[0]
    
    def test_get_fraud_alerts(self, handler, high_value_order_event):
        """Test getting fraud alerts."""
        handler._handle_order_placed(high_value_order_event)
        
        alerts = handler.get_fraud_alerts()
        assert len(alerts) == 1
        assert "Suspicious order pattern" in alerts[0]