from typing import List, Dict, Any, Optional
from composition_root import build_container

# Build a singleton container lazily
_container: Optional[Dict[str, Any]] = None

def _get_container() -> Dict[str, Any]:
    global _container
    if _container is None:
        _container = build_container()
    return _container

class OrderService:
    def __init__(self, order_repo, course_repo, policy_repo) -> None:
        self.container = _get_container()

    def get_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        return self.container['projections']['order_history'].get_orders_for_user(user_id)

    def request_refund(self, order_id: str, reason: str) -> Dict[str, Any]:
        from application_services.order_application_service import RequestRefundCommand
        res = self.container['services']['orders'].request_refund(RequestRefundCommand(order_id=order_id, refund_reason=reason))
        return {"order_id": res.order_id, "status": res.status}

    def process_refund(self, order_id: str) -> Dict[str, Any]:
        # For demo, assume process == request
        return self.request_refund(order_id, "not satisfied")

    def create_order(self, user_id: str, course_ids: List[str]) -> Dict[str, Any]:
        from application_services.order_application_service import PlaceOrderCommand
        res = self.container['services']['orders'].place_order(PlaceOrderCommand(user_id=user_id, course_ids=course_ids, total_amount=100.0, payment_info={}))
        return {"order_id": res.order_id, "status": res.status}

    def complete_order(self, order_id: str) -> Dict[str, Any]:
        # Placeholder: mark as paid could be added here
        return {"order_id": order_id, "status": "PAID"}

class CourseService:
    def __init__(self, course_repo) -> None:
        self.container = _get_container()

    def list_courses(self) -> Dict[str, Dict[str, Any]]:
        return self.container['projections']['course_catalog'].get_all()

    def get_course_content(self, course_id: str) -> Dict[str, Any]:
        cat = self.container['projections']['course_catalog'].get_all()
        return cat.get(course_id) or {}

    def get_user_courses(self, user_id: str) -> List[Dict[str, Any]]:
        ua = self.container['projections']['user_access'].get_user_access(user_id)
        return ua.get('courses', [])

    def update_progress(self, user_id: str, course_id: str, progress: float) -> Dict[str, Any]:
        # For demo, directly adjust projection is not appropriate; normally an event would be emitted
        return {"user_id": user_id, "course_id": course_id, "progress": progress}

class PolicyService:
    def __init__(self, policy_repo) -> None:
        self.container = _get_container()

    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        pu = self.container['projections']['policy_usage'].get_all()
        return pu.get(policy_id) or {}

    def get_refund_policy(self) -> Dict[str, Any]:
        # Return any policy marked as type standard for demo
        pu = self.container['projections']['policy_usage'].get_all()
        for p in pu.values():
            if p.get('type') in ("standard","extended"):
                return p
        return {}

    def create_policy(self, name: str, policy_type: str, refund_period_days: int) -> Dict[str, Any]:
        from application_services.policy_application_service import CreatePolicyCommand
        res = self.container['services']['policies'].create_policy(CreatePolicyCommand(name=name, policy_type=policy_type, refund_period_days=refund_period_days))
        return {"policy_id": res.policy_id, "status": res.status}

    def add_version(self, policy_id: str, conditions: str) -> Dict[str, Any]:
        # Placeholder - in a real system would add versioning
        return {"policy_id": policy_id, "conditions": conditions}

    def activate(self, policy_id: str) -> Dict[str, Any]:
        # Placeholder - ensure policy active
        pol = self.get_policy(policy_id)
        pol['status'] = 'active'
        return pol
