from typing import Dict, Any, Set

class PolicyUsageProjection:
    """
    Read model projection to show policy details and their usage/adoption across courses.
    Handles events for policy create/update and mapping of policies to courses via CoursePolicyChanged.
    """
    def __init__(self):
        # policy_id -> metadata and usage
        self.policies: Dict[str, Dict[str, Any]] = {}
        # course_id -> policy_id
        self.course_to_policy: Dict[str, str] = {}

    def handle(self, event: Any) -> None:
        event_type = getattr(event, "__event_type__", event.__class__.__name__)
        if event_type == "PolicyCreated":
            self._on_policy_created(event)
        elif event_type == "PolicyUpdated":
            self._on_policy_updated(event)
        elif event_type == "CoursePolicyChanged":
            self._on_course_policy_changed(event)

    def _on_policy_created(self, event):
        policy_id = event.policy_id.value
        self.policies[policy_id] = {
            'policy_id': policy_id,
            'type': getattr(event, 'policy_type', None) and event.policy_type.value or None,
            'refund_period_days': getattr(event, 'refund_period_days', None),
            'name': getattr(event, 'name', None) and event.name.value or None,
            'status': 'active',
            'adoption_count': 0,
            'courses_using': set(),
        }

    def _on_policy_updated(self, event):
        policy_id = event.policy_id.value
        if policy_id in self.policies:
            # Update metadata
            if hasattr(event, 'policy_type') and event.policy_type:
                self.policies[policy_id]['type'] = event.policy_type.value
            if hasattr(event, 'refund_period_days'):
                self.policies[policy_id]['refund_period_days'] = event.refund_period_days
            if hasattr(event, 'name') and event.name:
                self.policies[policy_id]['name'] = event.name.value
            # Update status (e.g., deprecated/reactivated)
            if hasattr(event, 'status') and getattr(event, 'status', None) == 'deprecated':
                self.policies[policy_id]['status'] = 'deprecated'
            if hasattr(event, 'status') and getattr(event, 'status', None) == 'active':
                self.policies[policy_id]['status'] = 'active'

    def _on_course_policy_changed(self, event):
        course_id = event.course_id.value
        old_policy_id = event.old_policy_id.value if hasattr(event, 'old_policy_id') else None
        new_policy_id = event.new_policy_id.value
        # Remove from old policy (if present)
        if old_policy_id and old_policy_id in self.policies:
            if course_id in self.policies[old_policy_id]['courses_using']:
                self.policies[old_policy_id]['courses_using'].remove(course_id)
                self.policies[old_policy_id]['adoption_count'] = len(self.policies[old_policy_id]['courses_using'])
        # Add to new policy
        if new_policy_id in self.policies:
            self.policies[new_policy_id]['courses_using'].add(course_id)
            self.policies[new_policy_id]['adoption_count'] = len(self.policies[new_policy_id]['courses_using'])
        # Update course-to-policy map
        self.course_to_policy[course_id] = new_policy_id

    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        # Return with courses_using as sorted list (not a set)
        policy = self.policies.get(policy_id)
        if policy:
            res = policy.copy()
            res['courses_using'] = sorted(list(res['courses_using']))
            return res
        return None

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        # Return a copy with lists for all courses_using
        out = {}
        for pid, p in self.policies.items():
            cp = p.copy()
            cp['courses_using'] = sorted(list(cp['courses_using']))
            out[pid] = cp
        return out
