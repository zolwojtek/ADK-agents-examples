"""
Unit tests for OrderRepository implementation.
"""

import pytest
from uuid import uuid4

from infrastructure.repositories.order_repository import OrderRepository
from domain.orders.aggregates import Order
from domain.orders.value_objects import OrderItem
from domain.shared.value_objects import OrderId, UserId, CourseId, Money, OrderStatus, PolicyId


class TestOrderRepository:
    """Test OrderRepository implementation."""
    
    @pytest.fixture
    def order_repository(self):
        """Create a test order repository."""
        return OrderRepository()
    
    @pytest.fixture
    def order_data(self):
        """Create test order data."""
        return {
            "id": OrderId(str(uuid4())),
            "user_id": UserId("user_123"),
            "items": [OrderItem(course_id=CourseId("course_456"), price_snapshot=Money(99.99, "USD"), policy_id=PolicyId("policy_123"))],
            "total_amount": Money(99.99, "USD"),
            "status": OrderStatus.PENDING
        }
    
    @pytest.fixture
    def order(self, order_data):
        """Create a test order."""
        return Order(**order_data)
    
    def test_save_order(self, order_repository, order):
        """Test saving an order."""
        saved_order = order_repository.save(order)
        
        assert saved_order == order
        assert order_repository.get_by_id(order.id) == order
        assert order_repository.count() == 1
    
    def test_get_by_id(self, order_repository, order):
        """Test getting order by ID."""
        order_repository.save(order)
        
        retrieved_order = order_repository.get_by_id(order.id)
        assert retrieved_order == order
        
        non_existent_id = OrderId(str(uuid4()))
        assert order_repository.get_by_id(non_existent_id) is None
    
    def test_get_by_user(self, order_repository, order):
        """Test getting orders by user."""
        order_repository.save(order)
        
        orders = order_repository.get_by_user(order.user_id)
        assert len(orders) == 1
        assert orders[0] == order
        
        non_existent_user = UserId("non_existent_user")
        orders = order_repository.get_by_user(non_existent_user)
        assert len(orders) == 0
    
    def test_get_by_course(self, order_repository, order):
        """Test getting orders by course."""
        order_repository.save(order)
        
        orders = order_repository.get_by_course(order.items[0].course_id)
        assert len(orders) == 1
        assert orders[0] == order
        
        non_existent_course = CourseId("non_existent_course")
        orders = order_repository.get_by_course(non_existent_course)
        assert len(orders) == 0
    
    def test_get_by_status(self, order_repository, order):
        """Test getting orders by status."""
        order_repository.save(order)
        
        orders = order_repository.get_by_status(order.status)
        assert len(orders) == 1
        assert orders[0] == order
        
        orders = order_repository.get_by_status(OrderStatus.PAID)
        assert len(orders) == 0
    
    def test_get_pending_orders(self, order_repository, order):
        """Test getting pending orders."""
        order_repository.save(order)
        
        pending_orders = order_repository.get_pending_orders()
        assert len(pending_orders) == 1
        assert pending_orders[0] == order
        
        # Change status to paid
        order.status = OrderStatus.PAID
        order_repository.save(order)
        
        pending_orders = order_repository.get_pending_orders()
        assert len(pending_orders) == 0
    
    def test_get_paid_orders(self, order_repository, order):
        """Test getting paid orders."""
        order_repository.save(order)
        
        paid_orders = order_repository.get_paid_orders()
        assert len(paid_orders) == 0
        
        # Change status to paid
        order.status = OrderStatus.PAID
        order_repository.save(order)
        
        paid_orders = order_repository.get_paid_orders()
        assert len(paid_orders) == 1
        assert paid_orders[0] == order
    
    def test_get_failed_orders(self, order_repository, order):
        """Test getting failed orders."""
        order_repository.save(order)
        
        failed_orders = order_repository.get_failed_orders()
        assert len(failed_orders) == 0
        
        # Change status to failed
        order.status = OrderStatus.FAILED
        order_repository.save(order)
        
        failed_orders = order_repository.get_failed_orders()
        assert len(failed_orders) == 1
        assert failed_orders[0] == order
    
    def test_get_refunded_orders(self, order_repository, order):
        """Test getting refunded orders."""
        order_repository.save(order)
        
        refunded_orders = order_repository.get_refunded_orders()
        assert len(refunded_orders) == 0
        
        # Change status to refunded
        order.status = OrderStatus.REFUNDED
        order_repository.save(order)
        
        refunded_orders = order_repository.get_refunded_orders()
        assert len(refunded_orders) == 1
        assert refunded_orders[0] == order
    
    def test_get_cancelled_orders(self, order_repository, order):
        """Test getting cancelled orders."""
        order_repository.save(order)
        
        cancelled_orders = order_repository.get_cancelled_orders()
        assert len(cancelled_orders) == 0
        
        # Change status to cancelled
        order.status = OrderStatus.CANCELLED
        order_repository.save(order)
        
        cancelled_orders = order_repository.get_cancelled_orders()
        assert len(cancelled_orders) == 1
        assert cancelled_orders[0] == order
    
    def test_get_user_course_order(self, order_repository, order):
        """Test getting order for specific user and course."""
        order_repository.save(order)
        
        retrieved_order = order_repository.get_user_course_order(order.user_id, order.items[0].course_id)
        assert retrieved_order == order
        
        # Test with non-existent user
        non_existent_user = UserId("non_existent_user")
        assert order_repository.get_user_course_order(non_existent_user, order.items[0].course_id) is None
        
        # Test with non-existent course
        non_existent_course = CourseId("non_existent_course")
        assert order_repository.get_user_course_order(order.user_id, non_existent_course) is None
    
    def test_delete_order(self, order_repository, order):
        """Test deleting order."""
        order_repository.save(order)
        assert order_repository.count() == 1
        
        result = order_repository.delete(order.id)
        assert result is True
        assert order_repository.count() == 0
        assert order_repository.get_by_id(order.id) is None
        
        # Try to delete non-existent order
        result = order_repository.delete(OrderId(str(uuid4())))
        assert result is False
    
    def test_get_all_orders(self, order_repository, order):
        """Test getting all orders."""
        order_repository.save(order)
        
        orders = order_repository.get_all()
        assert len(orders) == 1
        assert orders[0] == order
    
    def test_exists(self, order_repository, order):
        """Test checking if order exists."""
        assert not order_repository.exists(order.id)
        
        order_repository.save(order)
        assert order_repository.exists(order.id)
    
    def test_clear_repository(self, order_repository, order):
        """Test clearing repository."""
        order_repository.save(order)
        assert order_repository.count() == 1
        
        order_repository.clear()
        assert order_repository.count() == 0
        assert order_repository.get_by_id(order.id) is None
    
    def test_multiple_orders(self, order_repository):
        """Test repository with multiple orders."""
        order1 = Order(
            id=OrderId(str(uuid4())),
            user_id=UserId("user_123"),
            items=[OrderItem(course_id=CourseId("course_456"), price_snapshot=Money(99.99, "USD"), policy_id=PolicyId("policy_123"))],
            total_amount=Money(99.99, "USD"),
            status=OrderStatus.PENDING
        )
        
        order2 = Order(
            id=OrderId(str(uuid4())),
            user_id=UserId("user_789"),
            items=[OrderItem(course_id=CourseId("course_101"), price_snapshot=Money(149.99, "USD"), policy_id=PolicyId("policy_456"))],
            total_amount=Money(149.99, "USD"),
            status=OrderStatus.PAID
        )
        
        order_repository.save(order1)
        order_repository.save(order2)
        
        assert order_repository.count() == 2
        
        # Test user queries
        user1_orders = order_repository.get_by_user(order1.user_id)
        assert len(user1_orders) == 1
        assert user1_orders[0] == order1
        
        user2_orders = order_repository.get_by_user(order2.user_id)
        assert len(user2_orders) == 1
        assert user2_orders[0] == order2
        
        # Test status queries
        pending_orders = order_repository.get_pending_orders()
        assert len(pending_orders) == 1
        assert pending_orders[0] == order1
        
        paid_orders = order_repository.get_paid_orders()
        assert len(paid_orders) == 1
        assert paid_orders[0] == order2
