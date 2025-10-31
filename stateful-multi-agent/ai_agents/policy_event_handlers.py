"""
AI Agent event handlers for Policy domain events.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from domain.events.event_bus import EventHandler
from domain.events.domain_event import DomainEvent
from domain.policies.events import (
    PolicyCreated, PolicyUpdated, PolicyDeprecated, PolicyReactivated
)
from domain.shared.value_objects import PolicyId, PolicyType
from domain.policies.value_objects import PolicyName


class PolicyAnalyticsHandler(EventHandler):
    """AI Agent that analyzes policy patterns and provides insights."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.policy_metrics = {
            'total_policies_created': 0,
            'total_policies_updated': 0,
            'total_policies_deprecated': 0,
            'total_policies_reactivated': 0,
            'active_policies': set(),
            'deprecated_policies': set(),
            'policies_by_type': {}  # policy_type -> count
        }
    
    @property
    def handler_name(self) -> str:
        return "PolicyAnalyticsAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle policy domain events for analytics."""
        if isinstance(event, PolicyCreated):
            self._handle_policy_created(event)
        elif isinstance(event, PolicyUpdated):
            self._handle_policy_updated(event)
        elif isinstance(event, PolicyDeprecated):
            self._handle_policy_deprecated(event)
        elif isinstance(event, PolicyReactivated):
            self._handle_policy_reactivated(event)
    
    def _handle_policy_created(self, event: PolicyCreated) -> None:
        """Handle policy creation for analytics."""
        self.policy_metrics['total_policies_created'] += 1
        self.policy_metrics['active_policies'].add(event.policy_id.value)
        
        # Track policies by type
        policy_type = event.policy_type.value
        if policy_type not in self.policy_metrics['policies_by_type']:
            self.policy_metrics['policies_by_type'][policy_type] = 0
        self.policy_metrics['policies_by_type'][policy_type] += 1
        
        self.logger.info(f"📊 Analytics: Policy created - ID: {event.policy_id.value}, Name: {event.name.value}, Type: {policy_type}")
        self.logger.info(f"📊 Analytics: Total policies created: {self.policy_metrics['total_policies_created']}")
        self.logger.info(f"📊 Analytics: Active policies: {len(self.policy_metrics['active_policies'])}")
        self.logger.info(f"📊 Analytics: Refund period: {event.refund_period_days} days")
    
    def _handle_policy_updated(self, event: PolicyUpdated) -> None:
        """Handle policy update for analytics."""
        self.policy_metrics['total_policies_updated'] += 1
        
        self.logger.info(f"📊 Analytics: Policy updated - ID: {event.policy_id.value}")
        self.logger.info(f"📊 Analytics: Total policies updated: {self.policy_metrics['total_policies_updated']}")
    
    def _handle_policy_deprecated(self, event: PolicyDeprecated) -> None:
        """Handle policy deprecation for analytics."""
        self.policy_metrics['total_policies_deprecated'] += 1
        
        policy_id = event.policy_id.value
        if policy_id in self.policy_metrics['active_policies']:
            self.policy_metrics['active_policies'].remove(policy_id)
        self.policy_metrics['deprecated_policies'].add(policy_id)
        
        self.logger.info(f"📊 Analytics: Policy deprecated - ID: {policy_id}, Name: {event.name.value}")
        self.logger.info(f"📊 Analytics: Total policies deprecated: {self.policy_metrics['total_policies_deprecated']}")
        self.logger.info(f"📊 Analytics: Active policies: {len(self.policy_metrics['active_policies'])}")
    
    def _handle_policy_reactivated(self, event: PolicyReactivated) -> None:
        """Handle policy reactivation for analytics."""
        self.policy_metrics['total_policies_reactivated'] += 1
        
        policy_id = event.policy_id.value
        if policy_id in self.policy_metrics['deprecated_policies']:
            self.policy_metrics['deprecated_policies'].remove(policy_id)
        self.policy_metrics['active_policies'].add(policy_id)
        
        self.logger.info(f"📊 Analytics: Policy reactivated - ID: {policy_id}, Name: {event.name.value}")
        self.logger.info(f"📊 Analytics: Total policies reactivated: {self.policy_metrics['total_policies_reactivated']}")
        self.logger.info(f"📊 Analytics: Active policies: {len(self.policy_metrics['active_policies'])}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get current analytics summary."""
        return {
            'metrics': {
                **self.policy_metrics,
                'active_policies_count': len(self.policy_metrics['active_policies']),
                'deprecated_policies_count': len(self.policy_metrics['deprecated_policies'])
            },
            'timestamp': datetime.now().isoformat(),
            'agent': self.handler_name
        }


class PolicyComplianceHandler(EventHandler):
    """AI Agent that monitors policy compliance and changes."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.policy_registry = {}  # policy_id -> policy_info
        self.compliance_alerts = []
        self.policy_changes_history = []
    
    @property
    def handler_name(self) -> str:
        return "PolicyComplianceAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle policy domain events for compliance monitoring."""
        if isinstance(event, PolicyCreated):
            self._handle_policy_created(event)
        elif isinstance(event, PolicyUpdated):
            self._handle_policy_updated(event)
        elif isinstance(event, PolicyDeprecated):
            self._handle_policy_deprecated(event)
        elif isinstance(event, PolicyReactivated):
            self._handle_policy_reactivated(event)
    
    def _handle_policy_created(self, event: PolicyCreated) -> None:
        """Handle policy creation for compliance."""
        policy_id = event.policy_id.value
        
        self.policy_registry[policy_id] = {
            'id': policy_id,
            'name': event.name.value,
            'type': event.policy_type.value,
            'refund_period_days': event.refund_period_days,
            'status': 'active',
            'created_at': event.occurred_on
        }
        
        # Validate policy compliance
        compliance = self._validate_policy_compliance(event)
        if not compliance['passed']:
            alert = f"⚠️ Compliance Alert: Policy {policy_id} has compliance issues: {', '.join(compliance['issues'])}"
            if not any(policy_id in existing_alert for existing_alert in self.compliance_alerts[-3:]):
                self.compliance_alerts.append(alert)
                self.logger.warning(alert)
        
        self.policy_changes_history.append({
            'policy_id': policy_id,
            'action': 'created',
            'timestamp': event.occurred_on
        })
        
        self.logger.info(f"🔍 Compliance: Policy {policy_id} created - Compliance: {'PASS' if compliance['passed'] else 'FAIL'}")
    
    def _handle_policy_updated(self, event: PolicyUpdated) -> None:
        """Handle policy update for compliance."""
        policy_id = event.policy_id.value
        
        if policy_id in self.policy_registry:
            self.policy_registry[policy_id]['conditions'] = event.new_conditions
            
            # Check if update affects compliance
            alert = f"⚠️ Compliance Alert: Policy {policy_id} updated - Review required for existing course assignments"
            if not any(policy_id in existing_alert for existing_alert in self.compliance_alerts[-3:]):
                self.compliance_alerts.append(alert)
                self.logger.warning(alert)
        
        self.policy_changes_history.append({
            'policy_id': policy_id,
            'action': 'updated',
            'timestamp': event.occurred_on
        })
        
        self.logger.info(f"🔍 Compliance: Policy {policy_id} updated - Review required")
    
    def _handle_policy_deprecated(self, event: PolicyDeprecated) -> None:
        """Handle policy deprecation for compliance."""
        policy_id = event.policy_id.value
        
        if policy_id in self.policy_registry:
            self.policy_registry[policy_id]['status'] = 'deprecated'
            
            alert = f"⚠️ Compliance Alert: Policy {policy_id} deprecated - Existing courses may be affected"
            if not any(policy_id in existing_alert for existing_alert in self.compliance_alerts[-3:]):
                self.compliance_alerts.append(alert)
                self.logger.warning(alert)
        
        self.policy_changes_history.append({
            'policy_id': policy_id,
            'action': 'deprecated',
            'timestamp': event.occurred_on
        })
        
        self.logger.info(f"🔍 Compliance: Policy {policy_id} deprecated - Compliance review required")
    
    def _handle_policy_reactivated(self, event: PolicyReactivated) -> None:
        """Handle policy reactivation for compliance."""
        policy_id = event.policy_id.value
        
        if policy_id in self.policy_registry:
            self.policy_registry[policy_id]['status'] = 'active'
        
        self.policy_changes_history.append({
            'policy_id': policy_id,
            'action': 'reactivated',
            'timestamp': event.occurred_on
        })
        
        self.logger.info(f"🔍 Compliance: Policy {policy_id} reactivated - Available for new course assignments")
    
    def _validate_policy_compliance(self, event: PolicyCreated) -> Dict[str, Any]:
        """Validate policy compliance on creation."""
        issues = []
        
        # Check refund period is reasonable
        if event.refund_period_days < 0:
            issues.append("Negative refund period")
        elif event.refund_period_days > 365:
            issues.append("Refund period exceeds 1 year")
        
        # Check policy type is valid
        valid_types = ['standard', 'extended', 'no_refund']
        if event.policy_type.value not in valid_types:
            issues.append(f"Invalid policy type: {event.policy_type.value}")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def get_compliance_alerts(self) -> List[str]:
        """Get list of compliance alerts."""
        return self.compliance_alerts.copy()
    
    def get_policy_info(self, policy_id: str) -> Dict[str, Any]:
        """Get information about a specific policy."""
        return self.policy_registry.get(policy_id, {}).copy()
    
    def get_policy_changes_history(self) -> List[Dict[str, Any]]:
        """Get history of policy changes."""
        return self.policy_changes_history.copy()


class PolicyLifecycleHandler(EventHandler):
    """AI Agent that manages policy lifecycle and provides recommendations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.policy_recommendations = []
        self.policy_lifecycle_events = []
    
    @property
    def handler_name(self) -> str:
        return "PolicyLifecycleAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle policy domain events for lifecycle management."""
        if isinstance(event, PolicyCreated):
            self._handle_policy_created(event)
        elif isinstance(event, PolicyUpdated):
            self._handle_policy_updated(event)
        elif isinstance(event, PolicyDeprecated):
            self._handle_policy_deprecated(event)
        elif isinstance(event, PolicyReactivated):
            self._handle_policy_reactivated(event)
    
    def _handle_policy_created(self, event: PolicyCreated) -> None:
        """Handle policy creation for lifecycle management."""
        policy_id = event.policy_id.value
        policy_type = event.policy_type.value
        
        recommendation = f"📋 Lifecycle: New policy '{event.name.value}' created. Type: {policy_type}, Refund period: {event.refund_period_days} days"
        self.policy_recommendations.append(recommendation)
        self.policy_lifecycle_events.append(f"Policy {policy_id} created and activated")
        
        # Provide recommendations based on policy type
        if policy_type == 'no_refund':
            recommendation = f"⚠️ Lifecycle: Policy {policy_id} is NO_REFUND type - Ensure clear customer communication"
            self.policy_recommendations.append(recommendation)
        elif event.refund_period_days > 30:
            recommendation = f"💡 Lifecycle: Policy {policy_id} has extended refund period ({event.refund_period_days} days) - Monitor refund rates"
            self.policy_recommendations.append(recommendation)
        
        self.logger.info(f"📋 Lifecycle: {recommendation}")
    
    def _handle_policy_updated(self, event: PolicyUpdated) -> None:
        """Handle policy update for lifecycle management."""
        policy_id = event.policy_id.value
        
        recommendation = f"📋 Lifecycle: Policy {policy_id} terms updated - Existing courses using this policy may need review"
        self.policy_recommendations.append(recommendation)
        self.policy_lifecycle_events.append(f"Policy {policy_id} terms updated")
        
        self.logger.info(f"📋 Lifecycle: {recommendation}")
    
    def _handle_policy_deprecated(self, event: PolicyDeprecated) -> None:
        """Handle policy deprecation for lifecycle management."""
        policy_id = event.policy_id.value
        
        recommendation = f"📋 Lifecycle: Policy '{event.name.value}' deprecated - No new course assignments allowed"
        self.policy_recommendations.append(recommendation)
        self.policy_lifecycle_events.append(f"Policy {policy_id} deprecated")
        
        # Recommend reviewing affected courses
        recommendation = f"💡 Lifecycle: Review courses currently using deprecated policy {policy_id} for migration options"
        self.policy_recommendations.append(recommendation)
        
        self.logger.info(f"📋 Lifecycle: {recommendation}")
    
    def _handle_policy_reactivated(self, event: PolicyReactivated) -> None:
        """Handle policy reactivation for lifecycle management."""
        policy_id = event.policy_id.value
        
        recommendation = f"📋 Lifecycle: Policy '{event.name.value}' reactivated - Available for new course assignments"
        self.policy_recommendations.append(recommendation)
        self.policy_lifecycle_events.append(f"Policy {policy_id} reactivated")
        
        self.logger.info(f"📋 Lifecycle: {recommendation}")
    
    def get_recommendations(self) -> List[str]:
        """Get list of policy recommendations."""
        return self.policy_recommendations.copy()
    
    def get_lifecycle_events(self) -> List[str]:
        """Get list of lifecycle events."""
        return self.policy_lifecycle_events.copy()
