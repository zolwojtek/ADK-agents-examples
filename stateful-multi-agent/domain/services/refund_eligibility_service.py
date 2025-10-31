"""
Refund Eligibility Service for evaluating refund eligibility across aggregates.
"""

from datetime import datetime
from typing import List, Tuple

from ..access.aggregates import AccessRecord
from ..access.repositories import AccessRepository
from ..policies.aggregates import RefundPolicy
from ..policies.repositories import PolicyRepository
from ..orders.aggregates import Order
from ..orders.repositories import OrderRepository
from ..shared.value_objects import OrderId


class RefundEligibilityService:
    """Service for evaluating refund eligibility across aggregates."""
    
    def __init__(
        self,
        access_repository: AccessRepository,
        policy_repository: PolicyRepository,
        order_repository: OrderRepository
    ):
        self.access_repository = access_repository
        self.policy_repository = policy_repository
        self.order_repository = order_repository
    
    def evaluate_refund_eligibility(
        self, 
        order_id: OrderId, 
        current_time: datetime
    ) -> Tuple[bool, str]:
        """
        Evaluate if an order is eligible for refund based on policy rules.
        
        Args:
            order_id: Order identifier
            current_time: Current timestamp
            
        Returns:
            Tuple of (is_eligible, reason)
        """
        # Get the order
        order = self.order_repository.find_by_id(order_id)
        if not order:
            return False, "Order not found"
        
        if order.status.value != "paid":
            return False, "Order is not in paid status"
        
        # Get access records for this order
        access_records = self._get_access_records_for_order(order)
        
        if not access_records:
            return False, "No access records found for this order"
        
        # Check refund eligibility for each access record
        eligible_records = []
        ineligible_records = []
        
        for access_record in access_records:
            # Get the policy for this course
            policy = self._get_policy_for_access_record(access_record)
            if not policy:
                ineligible_records.append(f"Course {access_record.course_id} has no refund policy")
                continue
            
            # Check if access record is eligible for refund
            if access_record.can_be_refunded(current_time, policy):
                eligible_records.append(access_record)
            else:
                ineligible_records.append(f"Course {access_record.course_id} not eligible per policy")
        
        if not eligible_records:
            return False, f"No eligible courses: {', '.join(ineligible_records)}"
        
        if len(eligible_records) == len(access_records):
            return True, "All courses eligible for refund"
        else:
            partial_reason = f"Partial refund: {len(eligible_records)}/{len(access_records)} courses eligible"
            return True, partial_reason
    
    def get_eligible_courses_for_refund(
        self, 
        order_id: OrderId, 
        current_time: datetime
    ) -> List[AccessRecord]:
        """
        Get list of courses that are eligible for refund for a specific order.
        
        Args:
            order_id: Order identifier
            current_time: Current timestamp
            
        Returns:
            List of access records eligible for refund
        """
        order = self.order_repository.find_by_id(order_id)
        if not order or order.status.value != "paid":
            return []
        
        access_records = self._get_access_records_for_order(order)
        eligible_records = []
        
        for access_record in access_records:
            policy = self._get_policy_for_access_record(access_record)
            if policy and access_record.can_be_refunded(current_time, policy):
                eligible_records.append(access_record)
        
        return eligible_records
    
    def _get_access_records_for_order(self, order: Order) -> List[AccessRecord]:
        """Get access records for all courses in an order."""
        access_records = []
        
        for item in order.items:
            # Find access record for this user and course
            access_record = self.access_repository.get_user_course_access(
                order.user_id, 
                item.course_id
            )
            if access_record:
                access_records.append(access_record)
        
        return access_records
    
    def _get_policy_for_access_record(self, access_record: AccessRecord) -> RefundPolicy:
        """Get the refund policy for an access record."""
        # This would need to be implemented based on how policies are linked to courses
        # For now, return None - this would need to be connected to course-policy relationships
        return None
