"""
Order repository implementation.
"""

from typing import List, Optional

from domain.orders.repositories import OrderRepository as IOrderRepository
from domain.orders.aggregates import Order
from domain.shared.value_objects import OrderId, UserId, CourseId, OrderStatus
from .base import InMemoryRepository


class OrderRepository(InMemoryRepository[Order, OrderId], IOrderRepository):
    """In-memory implementation of OrderRepository."""
    
    def __init__(self):
        super().__init__()
        self._user_index: dict[UserId, List[OrderId]] = {}  # user_id -> [order_ids]
        self._course_index: dict[CourseId, List[OrderId]] = {}  # course_id -> [order_ids]
        self._status_index: dict[OrderStatus, List[OrderId]] = {}  # status -> [order_ids]
    
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        """Find order by ID."""
        return super().get_by_id(order_id)
    
    def list_by_user(self, user_id: UserId) -> List[Order]:
        """List orders by user."""
        return self.get_by_user(user_id)
    
    def find_by_payment_id(self, payment_id: str) -> Optional[Order]:
        """Find order by payment ID."""
        for order in self.get_all():
            if hasattr(order, 'payment_info') and order.payment_info and order.payment_info.get('payment_id') == payment_id:
                return order
        return None
    
    def get_by_user(self, user_id: UserId) -> List[Order]:
        """Get orders by user ID."""
        order_ids = self._user_index.get(user_id, [])
        return [self.find_by_id(order_id) for order_id in order_ids if self.find_by_id(order_id)]
    
    def get_by_course(self, course_id: CourseId) -> List[Order]:
        """Get orders by course ID."""
        order_ids = self._course_index.get(course_id, [])
        return [self.find_by_id(order_id) for order_id in order_ids if self.find_by_id(order_id)]
    
    def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders by status."""
        order_ids = self._status_index.get(status, [])
        return [self.find_by_id(order_id) for order_id in order_ids if self.find_by_id(order_id)]
    
    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders."""
        return self.get_by_status(OrderStatus.PENDING)
    
    def get_paid_orders(self) -> List[Order]:
        """Get all paid orders."""
        return self.get_by_status(OrderStatus.PAID)
    
    def get_failed_orders(self) -> List[Order]:
        """Get all failed orders."""
        return self.get_by_status(OrderStatus.FAILED)
    
    def get_refunded_orders(self) -> List[Order]:
        """Get all refunded orders."""
        return self.get_by_status(OrderStatus.REFUNDED)
    
    def get_cancelled_orders(self) -> List[Order]:
        """Get all cancelled orders."""
        return self.get_by_status(OrderStatus.CANCELLED)
    
    def get_user_course_order(self, user_id: UserId, course_id: CourseId) -> Optional[Order]:
        """Get order for specific user and course."""
        user_orders = self.get_by_user(user_id)
        for order in user_orders:
            # Check if any item in the order matches the course_id
            for item in order.items:
                if item.course_id == course_id:
                    return order
        return None
    
    def save(self, order: Order) -> Order:
        """Save order with indexing."""
        # Check if order already exists to handle status changes
        existing_order = super().get_by_id(order.id)
        
        # Save order
        saved_order = super().save(order)
        
        # Update indexes
        # User index
        if order.user_id not in self._user_index:
            self._user_index[order.user_id] = []
        if order.id not in self._user_index[order.user_id]:
            self._user_index[order.user_id].append(order.id)
        
        # Status index - remove from old status if it changed
        if existing_order and existing_order.status != order.status:
            old_status = existing_order.status
            if old_status in self._status_index:
                if order.id in self._status_index[old_status]:
                    self._status_index[old_status].remove(order.id)
                if not self._status_index[old_status]:
                    del self._status_index[old_status]
        
        # Always remove from all status indexes first, then add to new one
        for status in list(self._status_index.keys()):
            if order.id in self._status_index[status]:
                self._status_index[status].remove(order.id)
                if not self._status_index[status]:
                    del self._status_index[status]
        
        # Add to new status (only if not already there)
        if order.status not in self._status_index:
            self._status_index[order.status] = []
        if order.id not in self._status_index[order.status]:
            self._status_index[order.status].append(order.id)
        
        # Course index - add to all course indexes
        for item in order.items:
            if item.course_id not in self._course_index:
                self._course_index[item.course_id] = []
            if order.id not in self._course_index[item.course_id]:
                self._course_index[item.course_id].append(order.id)
        
        return saved_order
    
    def delete(self, order_id: OrderId) -> bool:
        """Delete order by ID."""
        order = self.find_by_id(order_id)
        if order:
            # Remove from indexes
            # User index
            if order.user_id in self._user_index:
                if order.id in self._user_index[order.user_id]:
                    self._user_index[order.user_id].remove(order.id)
                if not self._user_index[order.user_id]:
                    del self._user_index[order.user_id]
            
            # Course index - remove from all course indexes
            for item in order.items:
                if item.course_id in self._course_index:
                    if order.id in self._course_index[item.course_id]:
                        self._course_index[item.course_id].remove(order.id)
                    if not self._course_index[item.course_id]:
                        del self._course_index[item.course_id]
            
            # Status index
            if order.status in self._status_index:
                if order.id in self._status_index[order.status]:
                    self._status_index[order.status].remove(order.id)
                if not self._status_index[order.status]:
                    del self._status_index[order.status]
            
            return super().delete(order_id)
        return False
    
    def clear(self) -> None:
        """Clear all orders and indexes."""
        super().clear()
        self._user_index.clear()
        self._course_index.clear()
        self._status_index.clear()
