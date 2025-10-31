"""
Tests for AccessLifecycleService.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from domain.services.access_lifecycle_service import AccessLifecycleService
from domain.shared.value_objects import UserId, CourseId


class TestAccessLifecycleService:
    """Test AccessLifecycleService."""
    
    @pytest.fixture
    def mock_access_repository(self):
        """Create mock access repository."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_access_repository):
        """Create service with mock repository."""
        return AccessLifecycleService(mock_access_repository)
    
    def test_expire_access_records(self, service, mock_access_repository):
        """Test expiring access records."""
        # Setup
        current_time = datetime.now()
        expired_time = current_time - timedelta(days=1)
        
        # Create mock access records
        access_record1 = Mock()
        access_record1.has_expired.return_value = True
        access_record1.expire_access = Mock()
        
        access_record2 = Mock()
        access_record2.has_expired.return_value = False
        
        mock_access_repository.get_active_access.return_value = [access_record1, access_record2]
        
        # Execute
        expired_records = service.expire_access_records(current_time)
        
        # Assert
        assert len(expired_records) == 1
        assert access_record1 in expired_records
        access_record1.expire_access.assert_called_once_with(current_time)
        mock_access_repository.save.assert_called_once_with(access_record1)
    
    def test_reactivate_user_access(self, service, mock_access_repository):
        """Test reactivating user access."""
        # Setup
        user_id = UserId("user_123")
        course_id = CourseId("course_456")
        new_expiration = datetime.now() + timedelta(days=30)
        
        access_record = Mock()
        access_record.reactivate_access = Mock()
        mock_access_repository.get_user_course_access.return_value = access_record
        
        # Execute
        result = service.reactivate_user_access(user_id, course_id, new_expiration)
        
        # Assert
        assert result == access_record
        access_record.reactivate_access.assert_called_once_with(new_expiration)
        mock_access_repository.save.assert_called_once_with(access_record)
    
    def test_reactivate_user_access_not_found(self, service, mock_access_repository):
        """Test reactivating access when record not found."""
        # Setup
        user_id = UserId("user_123")
        course_id = CourseId("course_456")
        new_expiration = datetime.now() + timedelta(days=30)
        
        mock_access_repository.get_user_course_access.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="No access record found"):
            service.reactivate_user_access(user_id, course_id, new_expiration)
    
    def test_get_expired_access_for_user(self, service, mock_access_repository):
        """Test getting expired access for a user."""
        # Setup
        user_id = UserId("user_123")
        current_time = datetime.now()
        
        access_record1 = Mock()
        access_record1.has_expired.return_value = True
        
        access_record2 = Mock()
        access_record2.has_expired.return_value = False
        
        mock_access_repository.get_by_user.return_value = [access_record1, access_record2]
        
        # Execute
        expired_records = service.get_expired_access_for_user(user_id)
        
        # Assert
        assert len(expired_records) == 1
        assert access_record1 in expired_records
        mock_access_repository.get_by_user.assert_called_once_with(user_id)
