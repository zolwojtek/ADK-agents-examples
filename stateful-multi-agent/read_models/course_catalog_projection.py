from typing import Dict, Any
from domain.courses.events import CourseCreated, CourseUpdated, CoursePolicyChanged
from domain.policies.events import PolicyUpdated

class CourseCatalogProjection:
    """
    Read model projection providing a catalog of all available courses
    with pricing, policies, and metadata. Maintains eventual consistency with domain state.
    """
    def __init__(self):
        # { course_id: { title, description, price, policy, instructor_id, status } }
        self.catalog: Dict[str, Dict[str, Any]] = {}

    def handle(self, event: Any) -> None:
        cls_name = event.__class__.__name__
        event_type = getattr(event, "__event_type__", None)
        if (
            isinstance(event, CourseCreated) or cls_name == "CourseCreated" or event_type == "CourseCreated"
        ):
            self._on_course_created(event)
        elif (
            isinstance(event, CourseUpdated) or cls_name == "CourseUpdated" or event_type == "CourseUpdated"
        ):
            self._on_course_updated(event)
        elif (
            isinstance(event, CoursePolicyChanged) or cls_name == "CoursePolicyChanged" or event_type == "CoursePolicyChanged"
        ):
            self._on_policy_changed(event)
        elif (
            isinstance(event, PolicyUpdated) or cls_name == "PolicyUpdated" or event_type == "PolicyUpdated"
        ):
            self._on_policy_updated(event)

    def _on_course_created(self, event):
        course_id = event.course_id.value
        self.catalog[course_id] = {
            'course_id': course_id,
            'title': event.title.value,
            'description': getattr(event, 'description', None) and getattr(event, 'description').value or None,
            'price': getattr(event, 'price', None),
            'policy': {
                'policy_id': event.policy_id.value,
                'type': None,
                'refund_period_days': None
            },
            'instructor_id': getattr(event, 'instructor_id', None),
            'status': 'active',
        }

    def _on_course_updated(self, event):
        course_id = event.course_id.value
        if course_id in self.catalog:
            self.catalog[course_id]['title'] = event.title.value
            self.catalog[course_id]['description'] = event.description.value

    def _on_policy_changed(self, event):
        course_id = event.course_id.value
        if course_id in self.catalog:
            self.catalog[course_id]['policy']['policy_id'] = event.new_policy_id.value
            self.catalog[course_id]['policy']['type'] = None
            self.catalog[course_id]['policy']['refund_period_days'] = None

    def _on_policy_updated(self, event):
        policy_id = event.policy_id.value
        for course in self.catalog.values():
            if course['policy']['policy_id'] == policy_id:
                course['policy']['type'] = getattr(event, 'policy_type', None) and event.policy_type.value or None
                course['policy']['refund_period_days'] = getattr(event, 'refund_period_days', None)
                if hasattr(event, 'status') and getattr(event, 'status', None) == 'deprecated':
                    course['status'] = 'deprecated'

    def get_course(self, course_id: str) -> Dict[str, Any]:
        return self.catalog.get(course_id)

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        return self.catalog.copy()
