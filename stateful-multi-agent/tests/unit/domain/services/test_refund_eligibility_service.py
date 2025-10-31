"""
Tests for RefundEligibilityService.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from domain.services.refund_eligibility_service import RefundEligibilityService
from domain.shared.value_objects import OrderId, UserId, CourseId
from domain.shared.value_objects import OrderStatus


class TestRefundEligibilityService:
    """Test RefundEligibilityService."""
    
    @pytest.fixture
    def mock_access_repository(self):
        """Create mock access repository."""
        return Mock()
    
    @pytest.fixture
    def mock_policy_repository(self):
        """Create mock policy repository."""
        return Mock()
    
    @pytest.fixture
    def mock_order_repository(self):
        """Create mock order repository."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_access_repository, mock_policy_repository, mock_order_repository):
        """Create service with mock repositories."""
        return RefundEligibilityService(mock_access_repository, mock_policy_repository, mock_order_repository)
    
    @pytest.fixture
    def sample_order(self):
        """Create sample order for testing."""
        order = Mock()
        order.id = OrderId("order_123")
        order.user_id = UserId("user_456")
        order.status = OrderStatus.PAID
        order.items = [
            Mock(course_id=CourseId("course_1")),
            Mock(course_id=CourseId("course_2"))
        ]
        return order
    
    @pytest.fixture
    def sample_access_record(self):
        """Create sample access record for testing."""
        access_record = Mock()
        access_record.course_id = CourseId("course_1")
        access_record.can_be_refunded = Mock(return_value=True)
        return access_record
    
    @pytest.fixture
    def sample_policy(self):
        """Create sample refund policy for testing."""
        policy = Mock()
        policy.id = "policy_123"
        return policy
    
    def test_evaluate_refund_eligibility_success(self, service, mock_order_repository, mock_access_repository, 
                                                sample_order, sample_access_record, sample_policy):
        """Test successful refund eligibility evaluation."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.return_value = sample_access_record
        service._get_policy_for_access_record = Mock(return_value=sample_policy)
        
        # Execute
        is_eligible, reason = service.evaluate_refund_eligibility(order_id, current_time)
        
        # Assert
        assert is_eligible is True
        assert "All courses eligible" in reason
        # Note: can_be_refunded is called for each course in the order (2 times)
        assert sample_access_record.can_be_refunded.call_count == 2
    
    def test_evaluate_refund_eligibility_order_not_found(self, service, mock_order_repository):
        """Test refund eligibility when order not found."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        mock_order_repository.find_by_id.return_value = None
        
        # Execute
        is_eligible, reason = service.evaluate_refund_eligibility(order_id, current_time)
        
        # Assert
        assert is_eligible is False
        assert reason == "Order not found"
    
    def test_evaluate_refund_eligibility_wrong_status(self, service, mock_order_repository, sample_order):
        """Test refund eligibility when order is not paid."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        sample_order.status = OrderStatus.PENDING  # Wrong status
        mock_order_repository.find_by_id.return_value = sample_order
        
        # Execute
        is_eligible, reason = service.evaluate_refund_eligibility(order_id, current_time)
        
        # Assert
        assert is_eligible is False
        assert reason == "Order is not in paid status"
    
    def test_evaluate_refund_eligibility_no_access_records(self, service, mock_order_repository, mock_access_repository, sample_order):
        """Test refund eligibility when no access records found."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.return_value = None
        
        # Execute
        is_eligible, reason = service.evaluate_refund_eligibility(order_id, current_time)
        
        # Assert
        assert is_eligible is False
        assert reason == "No access records found for this order"
    
    def test_evaluate_refund_eligibility_no_policy(self, service, mock_order_repository, mock_access_repository,
                                                  sample_order, sample_access_record):
        """Test refund eligibility when no policy found."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.return_value = sample_access_record
        service._get_policy_for_access_record = Mock(return_value=None)
        
        # Execute
        is_eligible, reason = service.evaluate_refund_eligibility(order_id, current_time)
        
        # Assert
        assert is_eligible is False
        assert "No eligible courses" in reason
        assert "has no refund policy" in reason
    
    def test_evaluate_refund_eligibility_not_eligible(self, service, mock_order_repository, mock_access_repository,
                                                     sample_order, sample_access_record, sample_policy):
        """Test refund eligibility when access record is not eligible."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        sample_access_record.can_be_refunded.return_value = False
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.return_value = sample_access_record
        service._get_policy_for_access_record = Mock(return_value=sample_policy)
        
        # Execute
        is_eligible, reason = service.evaluate_refund_eligibility(order_id, current_time)
        
        # Assert
        assert is_eligible is False
        assert "No eligible courses" in reason
        assert "not eligible per policy" in reason
    
    def test_evaluate_refund_eligibility_partial_eligibility(self, service, mock_order_repository, mock_access_repository,
                                                            sample_order):
        """Test refund eligibility with partial eligibility."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        # Create two access records - one eligible, one not
        eligible_access = Mock()
        eligible_access.course_id = CourseId("course_1")
        eligible_access.can_be_refunded = Mock(return_value=True)
        
        ineligible_access = Mock()
        ineligible_access.course_id = CourseId("course_2")
        ineligible_access.can_be_refunded = Mock(return_value=False)
        
        sample_policy = Mock()
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.side_effect = [eligible_access, ineligible_access]
        service._get_policy_for_access_record = Mock(return_value=sample_policy)
        
        # Execute
        is_eligible, reason = service.evaluate_refund_eligibility(order_id, current_time)
        
        # Assert
        assert is_eligible is True
        assert "Partial refund" in reason
        assert "1/2 courses eligible" in reason
    
    def test_get_eligible_courses_for_refund_success(self, service, mock_order_repository, mock_access_repository,
                                                    sample_order, sample_access_record, sample_policy):
        """Test getting eligible courses for refund."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.return_value = sample_access_record
        service._get_policy_for_access_record = Mock(return_value=sample_policy)
        
        # Execute
        result = service.get_eligible_courses_for_refund(order_id, current_time)
        
        # Assert
        assert len(result) == 2  # Two courses in order
        assert result[0] == sample_access_record
        assert result[1] == sample_access_record
        sample_access_record.can_be_refunded.assert_called()
    
    def test_get_eligible_courses_for_refund_order_not_found(self, service, mock_order_repository):
        """Test getting eligible courses when order not found."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        mock_order_repository.find_by_id.return_value = None
        
        # Execute
        result = service.get_eligible_courses_for_refund(order_id, current_time)
        
        # Assert
        assert result == []
    
    def test_get_eligible_courses_for_refund_wrong_status(self, service, mock_order_repository, sample_order):
        """Test getting eligible courses when order is not paid."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        sample_order.status = OrderStatus.PENDING  # Wrong status
        mock_order_repository.find_by_id.return_value = sample_order
        
        # Execute
        result = service.get_eligible_courses_for_refund(order_id, current_time)
        
        # Assert
        assert result == []
    
    def test_get_eligible_courses_for_refund_no_policy(self, service, mock_order_repository, mock_access_repository,
                                                      sample_order, sample_access_record):
        """Test getting eligible courses when no policy found."""
        # Setup
        order_id = OrderId("order_123")
        current_time = datetime.now()
        
        mock_order_repository.find_by_id.return_value = sample_order
        mock_access_repository.get_user_course_access.return_value = sample_access_record
        service._get_policy_for_access_record = Mock(return_value=None)
        
        # Execute
        result = service.get_eligible_courses_for_refund(order_id, current_time)
        
        # Assert
        assert result == []
    
    def test_get_access_records_for_order(self, service, mock_access_repository, sample_order):
        """Test getting access records for an order."""
        # Setup
        access_record = Mock()
        mock_access_repository.get_user_course_access.return_value = access_record
        
        # Execute
        result = service._get_access_records_for_order(sample_order)
        
        # Assert
        assert len(result) == 2  # Two courses in order
        assert result[0] == access_record
        assert result[1] == access_record
        assert mock_access_repository.get_user_course_access.call_count == 2
    
    def test_get_access_records_for_order_missing_access(self, service, mock_access_repository, sample_order):
        """Test getting access records when some access records are missing."""
        # Setup
        access_record = Mock()
        mock_access_repository.get_user_course_access.side_effect = [access_record, None]
        
        # Execute
        result = service._get_access_records_for_order(sample_order)
        
        # Assert
        assert len(result) == 1  # Only one access record found
        assert result[0] == access_record
    
    def test_get_policy_for_access_record(self, service, sample_access_record):
        """Test getting policy for access record (placeholder implementation)."""
        # Execute
        result = service._get_policy_for_access_record(sample_access_record)
        
        # Assert
        assert result is None  # Current implementation returns None
