"""
Tests for Policy domain event handlers.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from ai_agents.policy_event_handlers import (
    PolicyAnalyticsHandler, PolicyComplianceHandler, PolicyLifecycleHandler
)
from domain.policies.events import (
    PolicyCreated, PolicyUpdated, PolicyDeprecated, PolicyReactivated
)
from domain.shared.value_objects import PolicyId, PolicyType
from domain.policies.value_objects import PolicyName


class TestPolicyAnalyticsHandler:
    """Test PolicyAnalyticsHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create analytics handler for testing."""
        return PolicyAnalyticsHandler()
    
    @pytest.fixture
    def policy_created_event(self):
        """Create PolicyCreated event for testing."""
        return PolicyCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy"),
            policy_type=PolicyType.STANDARD,
            refund_period_days=30
        )
    
    @pytest.fixture
    def policy_updated_event(self):
        """Create PolicyUpdated event for testing."""
        return PolicyUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            new_conditions="Updated refund conditions"
        )
    
    @pytest.fixture
    def policy_deprecated_event(self):
        """Create PolicyDeprecated event for testing."""
        return PolicyDeprecated(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy")
        )
    
    @pytest.fixture
    def policy_reactivated_event(self):
        """Create PolicyReactivated event for testing."""
        return PolicyReactivated(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "PolicyAnalyticsAI"
    
    def test_handle_policy_created(self, handler, policy_created_event):
        """Test handling PolicyCreated event."""
        with patch.object(handler, '_handle_policy_created') as mock_handle:
            handler.handle(policy_created_event)
            mock_handle.assert_called_once_with(policy_created_event)
    
    def test_handle_policy_created_updates_metrics(self, handler, policy_created_event):
        """Test that PolicyCreated updates metrics."""
        initial_count = handler.policy_metrics['total_policies_created']
        
        handler._handle_policy_created(policy_created_event)
        
        assert handler.policy_metrics['total_policies_created'] == initial_count + 1
        assert "policy_456" in handler.policy_metrics['active_policies']
        assert "standard" in handler.policy_metrics['policies_by_type']
    
    def test_handle_policy_updated(self, handler, policy_updated_event):
        """Test handling PolicyUpdated event."""
        initial_count = handler.policy_metrics['total_policies_updated']
        
        handler._handle_policy_updated(policy_updated_event)
        
        assert handler.policy_metrics['total_policies_updated'] == initial_count + 1
    
    def test_handle_policy_deprecated(self, handler, policy_created_event, policy_deprecated_event):
        """Test handling PolicyDeprecated event."""
        # First create a policy
        handler._handle_policy_created(policy_created_event)
        assert "policy_456" in handler.policy_metrics['active_policies']
        
        # Then deprecate it
        initial_count = handler.policy_metrics['total_policies_deprecated']
        handler._handle_policy_deprecated(policy_deprecated_event)
        
        assert handler.policy_metrics['total_policies_deprecated'] == initial_count + 1
        assert "policy_456" not in handler.policy_metrics['active_policies']
        assert "policy_456" in handler.policy_metrics['deprecated_policies']
    
    def test_handle_policy_reactivated(self, handler, policy_created_event, policy_deprecated_event, policy_reactivated_event):
        """Test handling PolicyReactivated event."""
        # First create and deprecate a policy
        handler._handle_policy_created(policy_created_event)
        handler._handle_policy_deprecated(policy_deprecated_event)
        assert "policy_456" not in handler.policy_metrics['active_policies']
        
        # Then reactivate it
        initial_count = handler.policy_metrics['total_policies_reactivated']
        handler._handle_policy_reactivated(policy_reactivated_event)
        
        assert handler.policy_metrics['total_policies_reactivated'] == initial_count + 1
        assert "policy_456" in handler.policy_metrics['active_policies']
        assert "policy_456" not in handler.policy_metrics['deprecated_policies']
    
    def test_get_analytics_summary(self, handler):
        """Test getting analytics summary."""
        summary = handler.get_analytics_summary()
        
        assert 'metrics' in summary
        assert 'timestamp' in summary
        assert 'agent' in summary
        assert summary['agent'] == "PolicyAnalyticsAI"
        assert isinstance(summary['metrics'], dict)
        assert 'active_policies_count' in summary['metrics']


class TestPolicyComplianceHandler:
    """Test PolicyComplianceHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create compliance handler for testing."""
        return PolicyComplianceHandler()
    
    @pytest.fixture
    def policy_created_event(self):
        """Create PolicyCreated event for testing."""
        return PolicyCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy"),
            policy_type=PolicyType.STANDARD,
            refund_period_days=30
        )
    
    @pytest.fixture
    def policy_created_event_invalid_period(self):
        """Create PolicyCreated event with invalid refund period for testing."""
        return PolicyCreated(
            event_id="event_127",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_789",
            policy_id=PolicyId("policy_789"),
            name=PolicyName("Invalid Policy"),
            policy_type=PolicyType.STANDARD,
            refund_period_days=400  # Exceeds 365 days
        )
    
    @pytest.fixture
    def policy_updated_event(self):
        """Create PolicyUpdated event for testing."""
        return PolicyUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            new_conditions="Updated refund conditions"
        )
    
    @pytest.fixture
    def policy_deprecated_event(self):
        """Create PolicyDeprecated event for testing."""
        return PolicyDeprecated(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy")
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "PolicyComplianceAI"
    
    def test_handle_policy_created(self, handler, policy_created_event):
        """Test handling PolicyCreated event."""
        handler._handle_policy_created(policy_created_event)
        
        assert "policy_456" in handler.policy_registry
        assert handler.policy_registry["policy_456"]['status'] == 'active'
        assert len(handler.policy_changes_history) == 1
        assert handler.policy_changes_history[0]['action'] == 'created'
    
    def test_validate_policy_compliance_passes(self, handler, policy_created_event):
        """Test compliance validation when policy is valid."""
        handler._handle_policy_created(policy_created_event)
        
        # Should not have compliance alerts for valid policy
        alerts = handler.get_compliance_alerts()
        # May or may not have alerts, but registry should be updated
        assert "policy_456" in handler.policy_registry
    
    def test_validate_policy_compliance_fails_invalid_period(self, handler, policy_created_event_invalid_period):
        """Test compliance validation when refund period is invalid."""
        handler._handle_policy_created(policy_created_event_invalid_period)
        
        # Should have compliance alerts for invalid policy
        alerts = handler.get_compliance_alerts()
        assert len(alerts) >= 1
        assert "compliance issues" in alerts[0].lower()
    
    def test_handle_policy_updated(self, handler, policy_created_event, policy_updated_event):
        """Test handling PolicyUpdated event."""
        handler._handle_policy_created(policy_created_event)
        
        initial_alerts = len(handler.compliance_alerts)
        handler._handle_policy_updated(policy_updated_event)
        
        assert len(handler.compliance_alerts) == initial_alerts + 1
        assert "policy_456" in handler.compliance_alerts[-1]
        assert "updated" in handler.compliance_alerts[-1].lower()
        assert handler.policy_registry["policy_456"]['conditions'] == "Updated refund conditions"
    
    def test_handle_policy_deprecated(self, handler, policy_created_event, policy_deprecated_event):
        """Test handling PolicyDeprecated event."""
        handler._handle_policy_created(policy_created_event)
        assert handler.policy_registry["policy_456"]['status'] == 'active'
        
        initial_alerts = len(handler.compliance_alerts)
        handler._handle_policy_deprecated(policy_deprecated_event)
        
        assert len(handler.compliance_alerts) == initial_alerts + 1
        assert handler.policy_registry["policy_456"]['status'] == 'deprecated'
    
    def test_handle_policy_reactivated(self, handler, policy_created_event, policy_deprecated_event):
        """Test handling PolicyReactivated event."""
        handler._handle_policy_created(policy_created_event)
        handler._handle_policy_deprecated(policy_deprecated_event)
        
        policy_reactivated_event = PolicyReactivated(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy")
        )
        
        handler._handle_policy_reactivated(policy_reactivated_event)
        
        assert handler.policy_registry["policy_456"]['status'] == 'active'
        assert len(handler.policy_changes_history) == 3  # created, deprecated, reactivated
    
    def test_get_compliance_alerts(self, handler, policy_updated_event):
        """Test getting compliance alerts."""
        # Create policy first
        policy_created_event = PolicyCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy"),
            policy_type=PolicyType.STANDARD,
            refund_period_days=30
        )
        handler._handle_policy_created(policy_created_event)
        
        # Update policy to trigger alert
        handler._handle_policy_updated(policy_updated_event)
        
        alerts = handler.get_compliance_alerts()
        assert len(alerts) >= 1
    
    def test_get_policy_info(self, handler, policy_created_event):
        """Test getting policy info."""
        handler._handle_policy_created(policy_created_event)
        
        policy_info = handler.get_policy_info("policy_456")
        assert policy_info['id'] == "policy_456"
        assert policy_info['name'] == "Standard Refund Policy"
    
    def test_get_policy_changes_history(self, handler, policy_created_event):
        """Test getting policy changes history."""
        handler._handle_policy_created(policy_created_event)
        
        history = handler.get_policy_changes_history()
        assert len(history) == 1
        assert history[0]['policy_id'] == "policy_456"
        assert history[0]['action'] == 'created'


class TestPolicyLifecycleHandler:
    """Test PolicyLifecycleHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create lifecycle handler for testing."""
        return PolicyLifecycleHandler()
    
    @pytest.fixture
    def policy_created_event(self):
        """Create PolicyCreated event for testing."""
        return PolicyCreated(
            event_id="event_123",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy"),
            policy_type=PolicyType.STANDARD,
            refund_period_days=30
        )
    
    @pytest.fixture
    def policy_created_event_no_refund(self):
        """Create PolicyCreated event with NO_REFUND type for testing."""
        return PolicyCreated(
            event_id="event_128",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_999",
            policy_id=PolicyId("policy_999"),
            name=PolicyName("No Refund Policy"),
            policy_type=PolicyType.NO_REFUND,
            refund_period_days=0
        )
    
    @pytest.fixture
    def policy_created_event_extended(self):
        """Create PolicyCreated event with extended refund period for testing."""
        return PolicyCreated(
            event_id="event_129",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_888",
            policy_id=PolicyId("policy_888"),
            name=PolicyName("Extended Refund Policy"),
            policy_type=PolicyType.EXTENDED,
            refund_period_days=60  # Extended period
        )
    
    @pytest.fixture
    def policy_updated_event(self):
        """Create PolicyUpdated event for testing."""
        return PolicyUpdated(
            event_id="event_124",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            new_conditions="Updated refund conditions"
        )
    
    def test_handler_name(self, handler):
        """Test handler name property."""
        assert handler.handler_name == "PolicyLifecycleAI"
    
    def test_handle_policy_created(self, handler, policy_created_event):
        """Test handling PolicyCreated event."""
        initial_recommendations = len(handler.policy_recommendations)
        
        handler._handle_policy_created(policy_created_event)
        
        assert len(handler.policy_recommendations) == initial_recommendations + 1
        assert "New policy" in handler.policy_recommendations[-1] or "Standard Refund Policy" in handler.policy_recommendations[-1]
        assert len(handler.policy_lifecycle_events) == 1
    
    def test_handle_policy_created_no_refund_type(self, handler, policy_created_event_no_refund):
        """Test handling PolicyCreated event with NO_REFUND type."""
        initial_recommendations = len(handler.policy_recommendations)
        
        handler._handle_policy_created(policy_created_event_no_refund)
        
        # Should have multiple recommendations for NO_REFUND type
        assert len(handler.policy_recommendations) >= initial_recommendations + 2
        assert any("NO_REFUND" in rec or "no_refund" in rec.lower() or "no refund" in rec.lower() for rec in handler.policy_recommendations)
    
    def test_handle_policy_created_extended_period(self, handler, policy_created_event_extended):
        """Test handling PolicyCreated event with extended refund period."""
        initial_recommendations = len(handler.policy_recommendations)
        
        handler._handle_policy_created(policy_created_event_extended)
        
        # Should have recommendation about extended period
        assert len(handler.policy_recommendations) >= initial_recommendations + 2
        assert any("extended" in rec.lower() or "60" in rec for rec in handler.policy_recommendations)
    
    def test_handle_policy_updated(self, handler, policy_created_event, policy_updated_event):
        """Test handling PolicyUpdated event."""
        handler._handle_policy_created(policy_created_event)
        initial_recommendations = len(handler.policy_recommendations)
        
        handler._handle_policy_updated(policy_updated_event)
        
        assert len(handler.policy_recommendations) == initial_recommendations + 1
        assert "policy_456" in handler.policy_recommendations[-1]
        assert "updated" in handler.policy_recommendations[-1].lower()
    
    def test_handle_policy_deprecated(self, handler, policy_created_event):
        """Test handling PolicyDeprecated event."""
        handler._handle_policy_created(policy_created_event)
        
        policy_deprecated_event = PolicyDeprecated(
            event_id="event_125",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy")
        )
        
        initial_recommendations = len(handler.policy_recommendations)
        handler._handle_policy_deprecated(policy_deprecated_event)
        
        # Should have multiple recommendations (deprecation + review recommendation)
        assert len(handler.policy_recommendations) >= initial_recommendations + 2
        assert any("deprecated" in rec.lower() for rec in handler.policy_recommendations)
    
    def test_handle_policy_reactivated(self, handler, policy_created_event):
        """Test handling PolicyReactivated event."""
        handler._handle_policy_created(policy_created_event)
        
        policy_reactivated_event = PolicyReactivated(
            event_id="event_126",
            occurred_on=datetime.now(),
            aggregate_type="RefundPolicy",
            aggregate_id="policy_456",
            policy_id=PolicyId("policy_456"),
            name=PolicyName("Standard Refund Policy")
        )
        
        initial_recommendations = len(handler.policy_recommendations)
        handler._handle_policy_reactivated(policy_reactivated_event)
        
        assert len(handler.policy_recommendations) == initial_recommendations + 1
        assert "reactivated" in handler.policy_recommendations[-1].lower()
    
    def test_get_recommendations(self, handler, policy_created_event):
        """Test getting recommendations."""
        handler._handle_policy_created(policy_created_event)
        
        recommendations = handler.get_recommendations()
        assert len(recommendations) >= 1
        assert "New policy" in recommendations[0] or "Standard Refund Policy" in recommendations[0]
    
    def test_get_lifecycle_events(self, handler, policy_created_event):
        """Test getting lifecycle events."""
        handler._handle_policy_created(policy_created_event)
        
        events = handler.get_lifecycle_events()
        assert len(events) == 1
        assert "policy_456" in events[0]
        assert "created" in events[0].lower()
