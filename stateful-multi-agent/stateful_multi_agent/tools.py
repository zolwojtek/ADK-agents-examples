from typing import Any, Dict, List

# Order tools
class GetUserOrdersTool:
    name = "get_user_orders"
    description = "List orders for a user"
    def __init__(self, order_service):
        self.svc = order_service
    def __call__(self, user_id: str) -> List[Dict[str, Any]]:
        return self.svc.get_user_orders(user_id)

class RequestRefundTool:
    name = "request_refund"
    description = "Request a refund for an order"
    def __init__(self, order_service):
        self.svc = order_service
    def __call__(self, order_id: str, reason: str = "not satisfied") -> Dict[str, Any]:
        return self.svc.request_refund(order_id, reason)

class ProcessRefundTool:
    name = "process_refund"
    description = "Process a refund for an order"
    def __init__(self, order_service):
        self.svc = order_service
    def __call__(self, order_id: str) -> Dict[str, Any]:
        return self.svc.process_refund(order_id)

class CreateOrderTool:
    name = "create_order"
    description = "Create a new order for a user"
    def __init__(self, order_service):
        self.svc = order_service
    def __call__(self, user_id: str, course_ids: List[str]) -> Dict[str, Any]:
        return self.svc.create_order(user_id, course_ids)

class CompleteOrderTool:
    name = "complete_order"
    description = "Mark order as completed/paid"
    def __init__(self, order_service):
        self.svc = order_service
    def __call__(self, order_id: str) -> Dict[str, Any]:
        return self.svc.complete_order(order_id)

# Course tools
class GetCoursesTool:
    name = "get_courses"
    description = "List available courses"
    def __init__(self, course_service):
        self.svc = course_service
    def __call__(self) -> Dict[str, Dict[str, Any]]:
        return self.svc.list_courses()

class GetCourseContentTool:
    name = "get_course_content"
    description = "Get details/content for a course"
    def __init__(self, course_service):
        self.svc = course_service
    def __call__(self, course_id: str) -> Dict[str, Any]:
        return self.svc.get_course_content(course_id)

class GetUserCoursesTool:
    name = "get_user_courses"
    description = "List courses a user has access to"
    def __init__(self, course_service):
        self.svc = course_service
    def __call__(self, user_id: str) -> List[Dict[str, Any]]:
        return self.svc.get_user_courses(user_id)

class UpdateCourseProgressTool:
    name = "update_course_progress"
    description = "Update a user's course progress"
    def __init__(self, course_service):
        self.svc = course_service
    def __call__(self, user_id: str, course_id: str, progress: float) -> Dict[str, Any]:
        return self.svc.update_progress(user_id, course_id, progress)

# Policy tools
class GetPolicyTool:
    name = "get_policy"
    description = "Get a policy by id"
    def __init__(self, policy_service):
        self.svc = policy_service
    def __call__(self, policy_id: str) -> Dict[str, Any]:
        return self.svc.get_policy(policy_id)

class GetRefundPolicyTool:
    name = "get_refund_policy"
    description = "Get active refund policy"
    def __init__(self, policy_service):
        self.svc = policy_service
    def __call__(self) -> Dict[str, Any]:
        return self.svc.get_refund_policy()

class CreatePolicyTool:
    name = "create_policy"
    description = "Create a new policy"
    def __init__(self, policy_service):
        self.svc = policy_service
    def __call__(self, name: str, policy_type: str, refund_period_days: int = 30) -> Dict[str, Any]:
        return self.svc.create_policy(name, policy_type, refund_period_days)

class AddPolicyVersionTool:
    name = "add_policy_version"
    description = "Add version/conditions to a policy"
    def __init__(self, policy_service):
        self.svc = policy_service
    def __call__(self, policy_id: str, conditions: str) -> Dict[str, Any]:
        return self.svc.add_version(policy_id, conditions)

class ActivatePolicyTool:
    name = "activate_policy"
    description = "Activate (reactivate) a policy"
    def __init__(self, policy_service):
        self.svc = policy_service
    def __call__(self, policy_id: str) -> Dict[str, Any]:
        return self.svc.activate(policy_id)
