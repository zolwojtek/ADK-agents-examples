from typing import Dict, Any, List
from datetime import datetime
from domain.access.events import (
    CourseAccessGranted, AccessRevoked, AccessExpired, ProgressUpdated, CourseCompleted
)

class UserAccessProjection:
    """
    Read model to show all courses a user can access, including status, progress, and expiration.
    Event-driven, denormalized, and query-optimized.
    """
    def __init__(self):
        # { user_id: { 'courses': [ ... ], 'last_activity': datetime } }
        self.data: Dict[str, Dict[str, Any]] = {}

    def handle(self, event: Any) -> None:
        if isinstance(event, CourseAccessGranted):
            self._on_access_granted(event)
        elif isinstance(event, AccessRevoked):
            self._on_access_revoked(event)
        elif isinstance(event, AccessExpired):
            self._on_access_expired(event)
        elif isinstance(event, ProgressUpdated):
            self._on_progress_updated(event)
        elif isinstance(event, CourseCompleted):
            self._on_course_completed(event)

    def _ensure_user(self, user_id: str):
        if user_id not in self.data:
            self.data[user_id] = { 'courses': [], 'last_activity': None }

    def _find_course(self, user_id: str, access_id: str) -> Any:
        courses = self.data[user_id]['courses']
        for course in courses:
            if course['access_id'] == access_id:
                return course
        return None

    def _on_access_granted(self, event: CourseAccessGranted):
        user_id = event.user_id.value
        self._ensure_user(user_id)
        courses = self.data[user_id]['courses']
        # Avoid duplicates
        if not any(c['access_id'] == event.access_id.value for c in courses):
            courses.append({
                'course_id': event.course_id.value,
                'access_id': event.access_id.value,
                'status': 'active',
                'progress': 0.0,
                'expires_at': None,
            })
        self.data[user_id]['last_activity'] = event.occurred_on

    def _on_access_revoked(self, event: AccessRevoked):
        user_id = event.user_id.value
        self._ensure_user(user_id)
        course = self._find_course(user_id, event.access_id.value)
        if course:
            course['status'] = 'revoked'
        self.data[user_id]['last_activity'] = event.occurred_on

    def _on_access_expired(self, event: AccessExpired):
        user_id = event.user_id.value
        self._ensure_user(user_id)
        course = self._find_course(user_id, event.access_id.value)
        if course:
            course['status'] = 'expired'
            course['expires_at'] = event.expired_at
        self.data[user_id]['last_activity'] = event.occurred_on

    def _on_progress_updated(self, event: ProgressUpdated):
        user_id = event.user_id.value
        self._ensure_user(user_id)
        course = self._find_course(user_id, event.access_id.value)
        if course:
            course['progress'] = event.progress.value
        self.data[user_id]['last_activity'] = event.occurred_on

    def _on_course_completed(self, event: CourseCompleted):
        user_id = event.user_id.value
        self._ensure_user(user_id)
        course = self._find_course(user_id, event.access_id.value)
        if course:
            course['progress'] = 100.0
            course['status'] = 'completed'
        self.data[user_id]['last_activity'] = event.occurred_on

    def get_user_access(self, user_id: str) -> Dict[str, Any]:
        return self.data.get(user_id, { 'courses': [], 'last_activity': None })

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        return self.data.copy()
