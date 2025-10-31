"""
Order Processing Service for orchestrating order payment and access granting.
"""

from datetime import datetime
from typing import List

from ..orders.repositories import OrderRepository
from ..access.aggregates import AccessRecord
from ..access.repositories import AccessRepository
from ..shared.value_objects import OrderId, UserId, CourseId
from ..shared.value_objects import Money


class OrderProcessingService:
    """Service for orchestrating order processing and access management."""
    
    def __init__(
        self,
        order_repository: OrderRepository,
        access_repository: AccessRepository
    ):
        self.order_repository = order_repository
        self.access_repository = access_repository
    
    def process_payment(
        self, 
        order_id: OrderId, 
        payment_info: dict,
        access_expires_at: datetime = None
    ) -> List[AccessRecord]:
        """
        Process order payment and grant access to courses.
        
        Args:
            order_id: Order identifier
            payment_info: Payment information
            access_expires_at: Optional access expiration date
            
        Returns:
            List of created access records
            
        Raises:
            ValueError: If order not found or not in pending status
        """
        # Get the order
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if order.status.value != "pending":
            raise ValueError(f"Order {order_id} is not in pending status")
        
        # Confirm payment
        from ..shared.value_objects import PaymentInfo
        payment = PaymentInfo(
            payment_id=payment_info["payment_id"],
            method=payment_info["method"],
            transaction_id=payment_info.get("transaction_id")
        )
        
        order.confirm_payment(payment)
        self.order_repository.save(order)
        
        # Grant access to courses
        access_records = []
        for item in order.items:
            access_record = self._grant_course_access(
                user_id=order.user_id,
                course_id=item.course_id,
                purchase_date=order.created_at,
                access_expires_at=access_expires_at
            )
            access_records.append(access_record)
        
        return access_records
    
    def process_refund(
        self, 
        order_id: OrderId, 
        refund_amount: Money,
        refund_reason: str
    ) -> List[AccessRecord]:
        """
        Process order refund and revoke access to courses.
        
        Args:
            order_id: Order identifier
            refund_amount: Amount to refund
            refund_reason: Reason for refund
            
        Returns:
            List of revoked access records
            
        Raises:
            ValueError: If order not found or not eligible for refund
        """
        # Get the order
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if order.status.value != "paid":
            raise ValueError(f"Order {order_id} is not in paid status")
        
        # Approve refund
        order.approve_refund(refund_amount)
        self.order_repository.save(order)
        
        # Revoke access to courses
        revoked_records = []
        for item in order.items:
            access_record = self._revoke_course_access(
                user_id=order.user_id,
                course_id=item.course_id,
                reason=refund_reason
            )
            if access_record:
                revoked_records.append(access_record)
        
        return revoked_records
    
    def _grant_course_access(
        self,
        user_id: UserId,
        course_id: CourseId,
        purchase_date: datetime,
        access_expires_at: datetime = None
    ) -> AccessRecord:
        """Grant access to a course for a user."""
        # Check if access already exists
        existing_access = self.access_repository.get_user_course_access(user_id, course_id)
        if existing_access:
            # If access exists and is active, no need to create new one
            if existing_access.is_active():
                return existing_access
            # If access exists but is expired/revoked, reactivate it
            existing_access.reactivate_access(access_expires_at)
            self.access_repository.save(existing_access)
            return existing_access
        
        # Create new access record
        access_record = AccessRecord.grant_access(
            user_id=user_id,
            course_id=course_id,
            purchase_date=purchase_date,
            access_expires_at=access_expires_at
        )
        
        self.access_repository.save(access_record)
        return access_record
    
    def _revoke_course_access(
        self,
        user_id: UserId,
        course_id: CourseId,
        reason: str
    ) -> AccessRecord:
        """Revoke access to a course for a user."""
        access_record = self.access_repository.get_user_course_access(user_id, course_id)
        if not access_record:
            return None
        
        access_record.revoke_access(reason)
        self.access_repository.save(access_record)
        return access_record
