"""
AI Agent event handlers for Order domain events.
"""

from typing import List, Dict, Any
from datetime import datetime
import logging

from domain.events.event_bus import EventHandler
from domain.events.domain_event import DomainEvent
from domain.orders.events import (
    OrderPlaced, OrderPaid, OrderRefunded, OrderCancelled, 
    OrderPaymentFailed, OrderRefundRequested
)
from domain.shared.value_objects import OrderId, UserId, Money


class OrderAnalyticsHandler(EventHandler):
    """AI Agent that analyzes order patterns and provides insights."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.order_metrics = {
            'total_orders': 0,
            'total_revenue': 0.0,
            'refund_rate': 0.0,
            'payment_failure_rate': 0.0
        }
    
    @property
    def handler_name(self) -> str:
        return "OrderAnalyticsAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle order domain events for analytics."""
        if isinstance(event, OrderPlaced):
            self._handle_order_placed(event)
        elif isinstance(event, OrderPaid):
            self._handle_order_paid(event)
        elif isinstance(event, OrderRefunded):
            self._handle_order_refunded(event)
        elif isinstance(event, OrderCancelled):
            self._handle_order_cancelled(event)
        elif isinstance(event, OrderPaymentFailed):
            self._handle_payment_failed(event)
        elif isinstance(event, OrderRefundRequested):
            self._handle_refund_requested(event)
    
    def _handle_order_placed(self, event: OrderPlaced) -> None:
        """Handle order placement for analytics."""
        self.order_metrics['total_orders'] += 1
        self.logger.info(f"📊 Analytics: Order {event.order_id.value} placed by user {event.user_id.value}")
        self.logger.info(f"📊 Analytics: Total orders tracked: {self.order_metrics['total_orders']}")
    
    def _handle_order_paid(self, event: OrderPaid) -> None:
        """Handle successful payment for analytics."""
        # Note: OrderPaid doesn't have amount field, so we'll just log the payment
        self.logger.info(f"📊 Analytics: Order {event.order_id.value} paid - Payment ID: {event.payment_id}")
        self.logger.info(f"📊 Analytics: Total revenue: ${self.order_metrics['total_revenue']}")
    
    def _handle_order_refunded(self, event: OrderRefunded) -> None:
        """Handle refund for analytics."""
        self.logger.info(f"📊 Analytics: Order {event.order_id.value} refunded - Reason: {event.refund_reason.value}")
        self._update_refund_rate()
    
    def _handle_order_cancelled(self, event: OrderCancelled) -> None:
        """Handle order cancellation for analytics."""
        self.logger.info(f"📊 Analytics: Order {event.order_id.value} cancelled")
    
    def _handle_payment_failed(self, event: OrderPaymentFailed) -> None:
        """Handle payment failure for analytics."""
        self.logger.info(f"📊 Analytics: Payment failed for order {event.order_id.value} - Reason: {event.failure_reason}")
        self._update_payment_failure_rate()
    
    def _handle_refund_requested(self, event: OrderRefundRequested) -> None:
        """Handle refund request for analytics."""
        self.logger.info(f"📊 Analytics: Refund requested for order {event.order_id.value} - Reason: {event.reason.value}")
    
    def _update_refund_rate(self) -> None:
        """Update refund rate calculation."""
        if self.order_metrics['total_orders'] > 0:
            # Simplified calculation - in real scenario would track refunds separately
            self.order_metrics['refund_rate'] = 0.1  # Placeholder
    
    def _update_payment_failure_rate(self) -> None:
        """Update payment failure rate calculation."""
        if self.order_metrics['total_orders'] > 0:
            # Simplified calculation - in real scenario would track failures separately
            self.order_metrics['payment_failure_rate'] = 0.05  # Placeholder
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get current analytics summary."""
        return {
            'metrics': self.order_metrics.copy(),
            'timestamp': datetime.now().isoformat(),
            'agent': self.handler_name
        }


class OrderCustomerServiceHandler(EventHandler):
    """AI Agent that provides customer service based on order events."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.customer_actions = []
    
    @property
    def handler_name(self) -> str:
        return "OrderCustomerServiceAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle order domain events for customer service."""
        if isinstance(event, OrderPlaced):
            self._handle_order_placed(event)
        elif isinstance(event, OrderPaid):
            self._handle_order_paid(event)
        elif isinstance(event, OrderRefunded):
            self._handle_order_refunded(event)
        elif isinstance(event, OrderCancelled):
            self._handle_order_cancelled(event)
        elif isinstance(event, OrderPaymentFailed):
            self._handle_payment_failed(event)
        elif isinstance(event, OrderRefundRequested):
            self._handle_refund_requested(event)
    
    def _handle_order_placed(self, event: OrderPlaced) -> None:
        """Handle order placement for customer service."""
        action = f"Send order confirmation email to user {event.user_id.value}"
        self.customer_actions.append(action)
        self.logger.info(f"🤖 CustomerService: {action}")
    
    def _handle_order_paid(self, event: OrderPaid) -> None:
        """Handle successful payment for customer service."""
        action = f"Send payment confirmation and welcome email to user {event.user_id.value}"
        self.customer_actions.append(action)
        self.logger.info(f"🤖 CustomerService: {action}")
    
    def _handle_order_refunded(self, event: OrderRefunded) -> None:
        """Handle refund for customer service."""
        action = f"Send refund confirmation email to user {event.user_id.value}"
        self.customer_actions.append(action)
        self.logger.info(f"🤖 CustomerService: {action}")
    
    def _handle_order_cancelled(self, event: OrderCancelled) -> None:
        """Handle order cancellation for customer service."""
        action = f"Send cancellation confirmation email to user {event.user_id.value}"
        self.customer_actions.append(action)
        self.logger.info(f"🤖 CustomerService: {action}")
    
    def _handle_payment_failed(self, event: OrderPaymentFailed) -> None:
        """Handle payment failure for customer service."""
        action = f"Send payment failure notification and retry instructions to user {event.user_id.value}"
        self.customer_actions.append(action)
        self.logger.info(f"🤖 CustomerService: {action}")
    
    def _handle_refund_requested(self, event: OrderRefundRequested) -> None:
        """Handle refund request for customer service."""
        action = f"Send refund request acknowledgment to user {event.user_id.value}"
        self.customer_actions.append(action)
        self.logger.info(f"🤖 CustomerService: {action}")
    
    def get_customer_actions(self) -> List[str]:
        """Get list of customer service actions taken."""
        return self.customer_actions.copy()


class OrderFraudDetectionHandler(EventHandler):
    """AI Agent that detects potential fraud based on order patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fraud_alerts = []
        self.user_order_history = {}  # Track user order patterns
    
    @property
    def handler_name(self) -> str:
        return "OrderFraudDetectionAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle order domain events for fraud detection."""
        if isinstance(event, OrderPlaced):
            self._handle_order_placed(event)
        elif isinstance(event, OrderPaid):
            self._handle_order_paid(event)
        elif isinstance(event, OrderPaymentFailed):
            self._handle_payment_failed(event)
    
    def _handle_order_placed(self, event: OrderPlaced) -> None:
        """Analyze order placement for fraud patterns."""
        user_id = event.user_id.value
        amount = event.total_amount.amount
        
        # Track user order history
        if user_id not in self.user_order_history:
            self.user_order_history[user_id] = []
        
        self.user_order_history[user_id].append({
            'amount': amount,
            'timestamp': event.occurred_on,
            'order_id': event.order_id.value
        })
        
        # Simple fraud detection logic
        if self._detect_suspicious_pattern(user_id, amount):
            alert = f"🚨 Fraud Alert: Suspicious order pattern detected for user {user_id}"
            # Only add alert if we haven't already alerted for this user recently
            if not any(f"user {user_id}" in existing_alert for existing_alert in self.fraud_alerts[-3:]):
                self.fraud_alerts.append(alert)
                self.logger.warning(alert)
    
    def _handle_order_paid(self, event: OrderPaid) -> None:
        """Analyze successful payment for fraud patterns."""
        self.logger.info(f"🔍 FraudDetection: Order {event.order_id.value} paid successfully")
    
    def _handle_payment_failed(self, event: OrderPaymentFailed) -> None:
        """Analyze payment failure for fraud patterns."""
        if event.failure_reason.lower() in ['insufficient_funds', 'card_declined']:
            alert = f"🚨 Fraud Alert: Multiple payment failures for order {event.order_id.value}"
            self.fraud_alerts.append(alert)
            self.logger.warning(alert)
    
    def _detect_suspicious_pattern(self, user_id: str, amount: float) -> bool:
        """Detect suspicious ordering patterns."""
        user_orders = self.user_order_history.get(user_id, [])
        
        # Simple heuristics for fraud detection
        if len(user_orders) > 5:  # Too many orders
            return True
        
        if amount > 1000:  # High value order
            return True
        
        # Check for rapid successive orders
        if len(user_orders) >= 2:
            recent_orders = [order for order in user_orders[-3:] 
                           if (datetime.now() - order['timestamp']).seconds < 300]
            if len(recent_orders) >= 2:
                return True
        
        return False
    
    def get_fraud_alerts(self) -> List[str]:
        """Get list of fraud alerts."""
        return self.fraud_alerts.copy()
