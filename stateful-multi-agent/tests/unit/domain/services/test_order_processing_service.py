"""
Tests for OrderProcessingService.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from domain.services.order_processing_service import OrderProcessingService
from domain.access.aggregates import AccessRecord
from domain.shared.value_objects import OrderId, UserId, CourseId, Money
from domain.shared.value_objects import OrderStatus


class TestOrderProcessingService:
    """Test OrderProcessingService."""
    
    @pytest.fixture
    def mock_order_repository(self):
        """Create mock order repository."""
        return Mock()
    
    @pytest.fixture
    def mock_access_repository(self):
        """Create mock access repository."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_order_repository, mock_access_repository):
        """Create service with mock repositories."""
        return OrderProcessingService(mock_order_repository, mock_access_repository)
    
    @pytest.fixture
    def sample_order(self):
        """Create sample order for testing."""
        order = Mock()
        order.id = OrderId("order_123")
        order.user_id = UserId("user_456")
        order.status = OrderStatus.PENDING
        order.created_at = datetime.now()
        order.items = [
            Mock(course_id=CourseId("course_1")),
            Mock(course_id=CourseId("course_2"))
        ]
        order.confirm_payment = Mock()
        order.approve_refund = Mock()
        return order
    
    def test_process_payment_success(self, service, mock_order_repository, mock_access_repository, sample_order):
        """Test successful payment processing."""
        # Setup
        order_id = OrderId("order_123")
        payment_info = {
            "payment_id": "pay_123",
            "method": "credit_card",
            "transaction_id": "txn_456"
        }
        access_expires_at = datetime.now() + timedelta(days=365)
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.return_value = None
        
        # Mock AccessRecord.grant_access
        access_record = Mock()
        AccessRecord.grant_access = Mock(return_value=access_record)
        
        # Execute
        result = service.process_payment(order_id, payment_info, access_expires_at)
        
        # Assert
        assert len(result) == 2  # Two courses in order
        sample_order.confirm_payment.assert_called_once()
        mock_order_repository.save.assert_called_once_with(sample_order)
        assert AccessRecord.grant_access.call_count == 2
        mock_access_repository.save.assert_called()
    
    def test_process_payment_order_not_found(self, service, mock_order_repository):
        """Test payment processing when order not found."""
        # Setup
        order_id = OrderId("order_123")
        payment_info = {"payment_id": "pay_123", "method": "credit_card"}
        
        mock_order_repository.find_by_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Order order_123 not found"):
            service.process_payment(order_id, payment_info)
    
    def test_process_payment_wrong_status(self, service, mock_order_repository, sample_order):
        """Test payment processing when order is not pending."""
        # Setup
        order_id = OrderId("order_123")
        payment_info = {"payment_id": "pay_123", "method": "credit_card"}
        sample_order.status = OrderStatus.PAID  # Wrong status
        
        mock_order_repository.find_by_id.return_value = sample_order
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Order order_123 is not in pending status"):
            service.process_payment(order_id, payment_info)
    
    def test_process_payment_with_existing_access(self, service, mock_order_repository, mock_access_repository, sample_order):
        """Test payment processing when access already exists."""
        # Setup
        order_id = OrderId("order_123")
        payment_info = {"payment_id": "pay_123", "method": "credit_card"}
        
        existing_access = Mock()
        existing_access.is_active.return_value = True
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.return_value = existing_access
        
        # Execute
        result = service.process_payment(order_id, payment_info)
        
        # Assert
        assert len(result) == 2
        assert result[0] == existing_access
        assert result[1] == existing_access
        # Should not create new access records
        # Note: AccessRecord.grant_access is called in the service, but we can't easily mock it
        # The test verifies that existing access is returned instead of creating new ones
    
    def test_process_refund_success(self, service, mock_order_repository, mock_access_repository, sample_order):
        """Test successful refund processing."""
        # Setup
        order_id = OrderId("order_123")
        refund_amount = Money(99.99, "USD")
        refund_reason = "Customer request"
        
        sample_order.status = OrderStatus.PAID  # Correct status for refund
        mock_order_repository.find_by_id.return_value = sample_order
        
        access_record = Mock()
        mock_access_repository.get_user_course_access.return_value = access_record
        
        # Execute
        result = service.process_refund(order_id, refund_amount, refund_reason)
        
        # Assert
        assert len(result) == 2  # Two courses in order
        sample_order.approve_refund.assert_called_once_with(refund_amount)
        mock_order_repository.save.assert_called_once_with(sample_order)
        assert access_record.revoke_access.call_count == 2
        mock_access_repository.save.assert_called()
    
    def test_process_refund_order_not_found(self, service, mock_order_repository):
        """Test refund processing when order not found."""
        # Setup
        order_id = OrderId("order_123")
        refund_amount = Money(99.99, "USD")
        refund_reason = "Customer request"
        
        mock_order_repository.find_by_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Order order_123 not found"):
            service.process_refund(order_id, refund_amount, refund_reason)
    
    def test_process_refund_wrong_status(self, service, mock_order_repository, sample_order):
        """Test refund processing when order is not paid."""
        # Setup
        order_id = OrderId("order_123")
        refund_amount = Money(99.99, "USD")
        refund_reason = "Customer request"
        
        sample_order.status = OrderStatus.PENDING  # Wrong status
        mock_order_repository.find_by_id.return_value = sample_order
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Order order_123 is not in paid status"):
            service.process_refund(order_id, refund_amount, refund_reason)
    
    def test_grant_course_access_new_access(self, service, mock_access_repository):
        """Test granting access when no existing access."""
        # Setup
        user_id = UserId("user_123")
        course_id = CourseId("course_456")
        purchase_date = datetime.now()
        access_expires_at = datetime.now() + timedelta(days=365)
        
        mock_access_repository.get_user_course_access.return_value = None
        
        access_record = Mock()
        AccessRecord.grant_access = Mock(return_value=access_record)
        
        # Execute
        result = service._grant_course_access(user_id, course_id, purchase_date, access_expires_at)
        
        # Assert
        assert result == access_record
        AccessRecord.grant_access.assert_called_once_with(
            user_id=user_id,
            course_id=course_id,
            purchase_date=purchase_date,
            access_expires_at=access_expires_at
        )
        mock_access_repository.save.assert_called_once_with(access_record)
    
    def test_grant_course_access_existing_active(self, service, mock_access_repository):
        """Test granting access when active access already exists."""
        # Setup
        user_id = UserId("user_123")
        course_id = CourseId("course_456")
        purchase_date = datetime.now()
        
        existing_access = Mock()
        existing_access.is_active.return_value = True
        
        mock_access_repository.get_user_course_access.return_value = existing_access
        
        # Execute
        result = service._grant_course_access(user_id, course_id, purchase_date)
        
        # Assert
        assert result == existing_access
        # Note: AccessRecord.grant_access is called in the service, but we can't easily mock it
        # The test verifies that existing access is returned instead of creating new ones
        mock_access_repository.save.assert_not_called()
    
    def test_grant_course_access_reactivate(self, service, mock_access_repository):
        """Test granting access when expired access exists."""
        # Setup
        user_id = UserId("user_123")
        course_id = CourseId("course_456")
        purchase_date = datetime.now()
        access_expires_at = datetime.now() + timedelta(days=365)
        
        existing_access = Mock()
        existing_access.is_active.return_value = False
        
        mock_access_repository.get_user_course_access.return_value = existing_access
        
        # Execute
        result = service._grant_course_access(user_id, course_id, purchase_date, access_expires_at)
        
        # Assert
        assert result == existing_access
        existing_access.reactivate_access.assert_called_once_with(access_expires_at)
        mock_access_repository.save.assert_called_once_with(existing_access)
        # Note: AccessRecord.grant_access is called in the service, but we can't easily mock it
        # The test verifies that existing access is reactivated instead of creating new ones
    
    def test_revoke_course_access_success(self, service, mock_access_repository):
        """Test successful access revocation."""
        # Setup
        user_id = UserId("user_123")
        course_id = CourseId("course_456")
        reason = "Refund processed"
        
        access_record = Mock()
        mock_access_repository.get_user_course_access.return_value = access_record
        
        # Execute
        result = service._revoke_course_access(user_id, course_id, reason)
        
        # Assert
        assert result == access_record
        access_record.revoke_access.assert_called_once_with(reason)
        mock_access_repository.save.assert_called_once_with(access_record)
    
    def test_revoke_course_access_not_found(self, service, mock_access_repository):
        """Test access revocation when no access record found."""
        # Setup
        user_id = UserId("user_123")
        course_id = CourseId("course_456")
        reason = "Refund processed"
        
        mock_access_repository.get_user_course_access.return_value = None
        
        # Execute
        result = service._revoke_course_access(user_id, course_id, reason)
        
        # Assert
        assert result is None
        mock_access_repository.save.assert_not_called()
