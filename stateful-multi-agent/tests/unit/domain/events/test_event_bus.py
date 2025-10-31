"""
Tests for EventBus.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import threading
import time

from domain.events.event_bus import EventBus, EventHandler
from domain.events.domain_event import DomainEvent


class TestDomainEvent(DomainEvent):
    """Test domain event for testing."""
    
    def __init__(self, event_id: str, occurred_on: datetime, aggregate_type: str, aggregate_id: str):
        super().__init__(event_id, occurred_on, aggregate_type, aggregate_id)


class TestEventHandler(EventHandler):
    """Test event handler for testing."""
    
    def __init__(self, name: str = "TestHandler"):
        self.name = name
        self.handled_events = []
        self.should_raise_error = False
    
    def handle(self, event: DomainEvent) -> None:
        """Handle an event."""
        if self.should_raise_error:
            raise ValueError(f"Handler {self.name} error")
        
        self.handled_events.append(event)
    
    @property
    def handler_name(self) -> str:
        return self.name


class TestEventBus:
    """Test EventBus."""
    
    @pytest.fixture
    def event_bus(self):
        """Create event bus for testing."""
        return EventBus()
    
    @pytest.fixture
    def test_event(self):
        """Create test event."""
        return TestDomainEvent(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="Order",
            aggregate_id="order_456"
        )
    
    @pytest.fixture
    def test_handler(self):
        """Create test handler."""
        return TestEventHandler("TestHandler")
    
    def test_subscribe_handler(self, event_bus, test_handler):
        """Test subscribing a handler to an event type."""
        event_type = "TestDomainEvent"
        
        event_bus.subscribe(event_type, test_handler)
        
        handlers = event_bus.get_subscribed_handlers(event_type)
        assert len(handlers) == 1
        assert handlers[0] == test_handler
    
    def test_subscribe_multiple_handlers(self, event_bus):
        """Test subscribing multiple handlers to the same event type."""
        event_type = "TestDomainEvent"
        handler1 = TestEventHandler("Handler1")
        handler2 = TestEventHandler("Handler2")
        
        event_bus.subscribe(event_type, handler1)
        event_bus.subscribe(event_type, handler2)
        
        handlers = event_bus.get_subscribed_handlers(event_type)
        assert len(handlers) == 2
        assert handler1 in handlers
        assert handler2 in handlers
    
    def test_subscribe_different_event_types(self, event_bus):
        """Test subscribing handlers to different event types."""
        handler1 = TestEventHandler("Handler1")
        handler2 = TestEventHandler("Handler2")
        
        event_bus.subscribe("EventType1", handler1)
        event_bus.subscribe("EventType2", handler2)
        
        handlers1 = event_bus.get_subscribed_handlers("EventType1")
        handlers2 = event_bus.get_subscribed_handlers("EventType2")
        
        assert len(handlers1) == 1
        assert len(handlers2) == 1
        assert handlers1[0] == handler1
        assert handlers2[0] == handler2
    
    def test_unsubscribe_handler(self, event_bus, test_handler):
        """Test unsubscribing a handler."""
        event_type = "TestDomainEvent"
        
        event_bus.subscribe(event_type, test_handler)
        assert len(event_bus.get_subscribed_handlers(event_type)) == 1
        
        event_bus.unsubscribe(event_type, test_handler)
        assert len(event_bus.get_subscribed_handlers(event_type)) == 0
    
    def test_unsubscribe_nonexistent_handler(self, event_bus, test_handler):
        """Test unsubscribing a handler that was never subscribed."""
        event_type = "TestDomainEvent"
        
        # Should not raise an error
        event_bus.unsubscribe(event_type, test_handler)
        assert len(event_bus.get_subscribed_handlers(event_type)) == 0
    
    def test_publish_sync(self, event_bus, test_event, test_handler):
        """Test synchronous event publishing."""
        event_type = "TestDomainEvent"
        
        event_bus.subscribe(event_type, test_handler)
        event_bus.publish_sync(test_event)
        
        assert len(test_handler.handled_events) == 1
        assert test_handler.handled_events[0] == test_event
    
    def test_publish_sync_multiple_handlers(self, event_bus, test_event):
        """Test synchronous publishing to multiple handlers."""
        event_type = "TestDomainEvent"
        handler1 = TestEventHandler("Handler1")
        handler2 = TestEventHandler("Handler2")
        
        event_bus.subscribe(event_type, handler1)
        event_bus.subscribe(event_type, handler2)
        event_bus.publish_sync(test_event)
        
        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 1
        assert handler1.handled_events[0] == test_event
        assert handler2.handled_events[0] == test_event
    
    def test_publish_sync_no_handlers(self, event_bus, test_event):
        """Test publishing to event type with no handlers."""
        # Should not raise an error
        event_bus.publish_sync(test_event)
    
    def test_publish_sync_handler_error(self, event_bus, test_event):
        """Test that handler errors don't stop other handlers."""
        event_type = "TestDomainEvent"
        handler1 = TestEventHandler("Handler1")
        handler2 = TestEventHandler("Handler2")
        handler2.should_raise_error = True
        
        event_bus.subscribe(event_type, handler1)
        event_bus.subscribe(event_type, handler2)
        
        # Should not raise an error even though handler2 fails
        event_bus.publish_sync(test_event)
        
        # Handler1 should still have received the event
        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 0  # Failed before handling
    
    def test_get_all_subscriptions(self, event_bus):
        """Test getting all subscriptions."""
        handler1 = TestEventHandler("Handler1")
        handler2 = TestEventHandler("Handler2")
        
        event_bus.subscribe("EventType1", handler1)
        event_bus.subscribe("EventType1", handler2)
        event_bus.subscribe("EventType2", handler1)
        
        subscriptions = event_bus.get_all_subscriptions()
        
        expected = {
            "EventType1": ["Handler1", "Handler2"],
            "EventType2": ["Handler1"]
        }
        
        assert subscriptions == expected
    
    def test_clear_subscriptions(self, event_bus, test_handler):
        """Test clearing all subscriptions."""
        event_bus.subscribe("EventType1", test_handler)
        event_bus.subscribe("EventType2", test_handler)
        
        assert len(event_bus.get_all_subscriptions()) == 2
        
        event_bus.clear_subscriptions()
        
        assert len(event_bus.get_all_subscriptions()) == 0
    
    def test_publish_async(self, event_bus, test_event, test_handler):
        """Test asynchronous event publishing."""
        event_type = "TestDomainEvent"
        
        event_bus.subscribe(event_type, test_handler)
        event_bus.publish(test_event)
        
        # Wait a bit for async processing
        time.sleep(0.1)
        
        assert len(test_handler.handled_events) == 1
        assert test_handler.handled_events[0] == test_event
    
    def test_publish_async_multiple_events(self, event_bus, test_handler):
        """Test publishing multiple events asynchronously."""
        event_type = "TestDomainEvent"
        event1 = TestDomainEvent("event_1", datetime.now(), "Order", "order_1")
        event2 = TestDomainEvent("event_2", datetime.now(), "Order", "order_2")
        
        event_bus.subscribe(event_type, test_handler)
        event_bus.publish(event1)
        event_bus.publish(event2)
        
        # Wait for async processing
        time.sleep(0.1)
        
        assert len(test_handler.handled_events) == 2
        assert event1 in test_handler.handled_events
        assert event2 in test_handler.handled_events
