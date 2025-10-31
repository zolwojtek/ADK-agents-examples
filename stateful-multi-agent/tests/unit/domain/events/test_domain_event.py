"""
Tests for DomainEvent base class.
"""

import pytest
from datetime import datetime
from domain.events.domain_event import DomainEvent


class TestDomainEvent(DomainEvent):
    """Test implementation of DomainEvent."""
    
    def __init__(self, event_id: str, occurred_on: datetime, aggregate_type: str, aggregate_id: str):
        super().__init__(event_id, occurred_on, aggregate_type, aggregate_id)


class TestDomainEventWithData(DomainEvent):
    """Test implementation with additional data."""
    
    def __init__(self, event_id: str, occurred_on: datetime, aggregate_type: str, aggregate_id: str, data: str):
        super().__init__(event_id, occurred_on, aggregate_type, aggregate_id)
        self.data = data


class TestDomainEventClass:
    """Test DomainEvent base class."""
    
    def test_create_domain_event(self):
        """Test creating a domain event."""
        event_id = "event_123"
        occurred_on = datetime.now()
        aggregate_type = "Order"
        aggregate_id = "order_456"
        
        event = TestDomainEvent(event_id, occurred_on, aggregate_type, aggregate_id)
        
        assert event.event_id == event_id
        assert event.occurred_on == occurred_on
        assert event.aggregate_type == aggregate_type
        assert event.aggregate_id == aggregate_id
    
    def test_domain_event_immutable(self):
        """Test that domain events are immutable."""
        event = TestDomainEvent("event_123", datetime.now(), "Order", "order_456")
        
        # Should not be able to modify fields
        with pytest.raises(AttributeError):
            event.event_id = "new_id"
        
        with pytest.raises(AttributeError):
            event.aggregate_type = "User"
    
    def test_to_dict(self):
        """Test converting event to dictionary."""
        event_id = "event_123"
        occurred_on = datetime(2023, 1, 1, 12, 0, 0)
        aggregate_type = "Order"
        aggregate_id = "order_456"
        
        event = TestDomainEvent(event_id, occurred_on, aggregate_type, aggregate_id)
        result = event.to_dict()
        
        expected = {
            'event_id': event_id,
            'occurred_on': occurred_on.isoformat(),
            'aggregate_type': aggregate_type,
            'aggregate_id': aggregate_id,
            'event_type': 'TestDomainEvent'
        }
        
        assert result == expected
    
    def test_to_dict_with_additional_data(self):
        """Test converting event with additional data to dictionary."""
        event_id = "event_123"
        occurred_on = datetime(2023, 1, 1, 12, 0, 0)
        aggregate_type = "Order"
        aggregate_id = "order_456"
        data = "test_data"
        
        event = TestDomainEventWithData(event_id, occurred_on, aggregate_type, aggregate_id, data)
        result = event.to_dict()
        
        expected = {
            'event_id': event_id,
            'occurred_on': occurred_on.isoformat(),
            'aggregate_type': aggregate_type,
            'aggregate_id': aggregate_id,
            'event_type': 'TestDomainEventWithData'
        }
        
        assert result == expected
        assert event.data == data  # Additional data is preserved but not in base dict
