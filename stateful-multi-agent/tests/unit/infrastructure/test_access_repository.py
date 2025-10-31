"""
Unit tests for AccessRepository implementation.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from infrastructure.repositories.access_repository import AccessRepository
from domain.access.aggregates import AccessRecord
from domain.shared.value_objects import AccessId, UserId, CourseId, Progress, AccessStatus


class TestAccessRepository:
    """Test AccessRepository implementation."""
    
    @pytest.fixture
    def access_repository(self):
        """Create a test access repository."""
        return AccessRepository()
    
    @pytest.fixture
    def access_data(self):
        """Create test access data."""
        return {
            "id": AccessId(str(uuid4())),
            "user_id": UserId("user_123"),
            "course_id": CourseId("course_456"),
            "purchase_date": datetime.now(),
            "access_expires_at": None,
            "progress": Progress(0.0),
            "status": AccessStatus.ACTIVE
        }
    
    @pytest.fixture
    def access_record(self, access_data):
        """Create a test access record."""
        return AccessRecord(**access_data)
    
    def test_save_access_record(self, access_repository, access_record):
        """Test saving an access record."""
        saved_access = access_repository.save(access_record)
        
        assert saved_access == access_record
        assert access_repository.get_by_id(access_record.id) == access_record
        assert access_repository.count() == 1
    
    def test_get_by_id(self, access_repository, access_record):
        """Test getting access record by ID."""
        access_repository.save(access_record)
        
        retrieved_access = access_repository.get_by_id(access_record.id)
        assert retrieved_access == access_record
        
        non_existent_id = AccessId(str(uuid4()))
        assert access_repository.get_by_id(non_existent_id) is None
    
    def test_get_by_user(self, access_repository, access_record):
        """Test getting access records by user."""
        access_repository.save(access_record)
        
        access_records = access_repository.get_by_user(access_record.user_id)
        assert len(access_records) == 1
        assert access_records[0] == access_record
        
        non_existent_user = UserId("non_existent_user")
        access_records = access_repository.get_by_user(non_existent_user)
        assert len(access_records) == 0
    
    def test_get_by_course(self, access_repository, access_record):
        """Test getting access records by course."""
        access_repository.save(access_record)
        
        access_records = access_repository.get_by_course(access_record.course_id)
        assert len(access_records) == 1
        assert access_records[0] == access_record
        
        non_existent_course = CourseId("non_existent_course")
        access_records = access_repository.get_by_course(non_existent_course)
        assert len(access_records) == 0
    
    def test_get_by_status(self, access_repository, access_record):
        """Test getting access records by status."""
        access_repository.save(access_record)
        
        access_records = access_repository.get_by_status(access_record.status)
        assert len(access_records) == 1
        assert access_records[0] == access_record
        
        access_records = access_repository.get_by_status(AccessStatus.EXPIRED)
        assert len(access_records) == 0
    
    def test_get_user_course_access(self, access_repository, access_record):
        """Test getting access record for specific user and course."""
        access_repository.save(access_record)
        
        retrieved_access = access_repository.get_user_course_access(
            access_record.user_id, 
            access_record.course_id
        )
        assert retrieved_access == access_record
        
        # Test with non-existent user
        non_existent_user = UserId("non_existent_user")
        assert access_repository.get_user_course_access(
            non_existent_user, 
            access_record.course_id
        ) is None
        
        # Test with non-existent course
        non_existent_course = CourseId("non_existent_course")
        assert access_repository.get_user_course_access(
            access_record.user_id, 
            non_existent_course
        ) is None
    
    def test_get_active_access(self, access_repository, access_record):
        """Test getting active access records."""
        access_repository.save(access_record)
        
        active_access = access_repository.get_active_access()
        assert len(active_access) == 1
        assert active_access[0] == access_record
        
        # Change status to expired
        access_record.status = AccessStatus.EXPIRED
        access_repository.save(access_record)
        
        active_access = access_repository.get_active_access()
        assert len(active_access) == 0
    
    def test_get_expired_access(self, access_repository, access_record):
        """Test getting expired access records."""
        access_repository.save(access_record)
        
        expired_access = access_repository.get_expired_access()
        assert len(expired_access) == 0
        
        # Change status to expired
        access_record.status = AccessStatus.EXPIRED
        access_repository.save(access_record)
        
        expired_access = access_repository.get_expired_access()
        assert len(expired_access) == 1
        assert expired_access[0] == access_record
    
    def test_get_revoked_access(self, access_repository, access_record):
        """Test getting revoked access records."""
        access_repository.save(access_record)
        
        revoked_access = access_repository.get_revoked_access()
        assert len(revoked_access) == 0
        
        # Change status to revoked
        access_record.status = AccessStatus.REVOKED
        access_repository.save(access_record)
        
        revoked_access = access_repository.get_revoked_access()
        assert len(revoked_access) == 1
        assert revoked_access[0] == access_record
    
    def test_get_pending_access(self, access_repository, access_record):
        """Test getting pending access records."""
        access_repository.save(access_record)
        
        pending_access = access_repository.get_pending_access()
        assert len(pending_access) == 0
        
        # Change status to pending
        access_record.status = AccessStatus.PENDING
        access_repository.save(access_record)
        
        pending_access = access_repository.get_pending_access()
        assert len(pending_access) == 1
        assert pending_access[0] == access_record
    
    def test_get_user_active_courses(self, access_repository, access_record):
        """Test getting user's active course access records."""
        access_repository.save(access_record)
        
        active_courses = access_repository.get_user_active_courses(access_record.user_id)
        assert len(active_courses) == 1
        assert active_courses[0] == access_record
        
        # Change status to expired
        access_record.status = AccessStatus.EXPIRED
        access_repository.save(access_record)
        
        active_courses = access_repository.get_user_active_courses(access_record.user_id)
        assert len(active_courses) == 0
    
    def test_get_course_active_users(self, access_repository, access_record):
        """Test getting active users for a specific course."""
        access_repository.save(access_record)
        
        active_users = access_repository.get_course_active_users(access_record.course_id)
        assert len(active_users) == 1
        assert active_users[0] == access_record
        
        # Change status to expired
        access_record.status = AccessStatus.EXPIRED
        access_repository.save(access_record)
        
        active_users = access_repository.get_course_active_users(access_record.course_id)
        assert len(active_users) == 0
    
    def test_delete_access_record(self, access_repository, access_record):
        """Test deleting access record."""
        access_repository.save(access_record)
        assert access_repository.count() == 1
        
        result = access_repository.delete(access_record.id)
        assert result is True
        assert access_repository.count() == 0
        assert access_repository.get_by_id(access_record.id) is None
        
        # Try to delete non-existent access record
        result = access_repository.delete(AccessId(str(uuid4())))
        assert result is False
    
    def test_get_all_access_records(self, access_repository, access_record):
        """Test getting all access records."""
        access_repository.save(access_record)
        
        access_records = access_repository.get_all()
        assert len(access_records) == 1
        assert access_records[0] == access_record
    
    def test_exists(self, access_repository, access_record):
        """Test checking if access record exists."""
        assert not access_repository.exists(access_record.id)
        
        access_repository.save(access_record)
        assert access_repository.exists(access_record.id)
    
    def test_clear_repository(self, access_repository, access_record):
        """Test clearing repository."""
        access_repository.save(access_record)
        assert access_repository.count() == 1
        
        access_repository.clear()
        assert access_repository.count() == 0
        assert access_repository.get_by_id(access_record.id) is None
    
    def test_multiple_access_records(self, access_repository):
        """Test repository with multiple access records."""
        access1 = AccessRecord(
            id=AccessId(str(uuid4())),
            user_id=UserId("user_123"),
            course_id=CourseId("course_456"),
            purchase_date=datetime.now(),
            access_expires_at=None,
            progress=Progress(0.0),
            status=AccessStatus.ACTIVE
        )
        
        access2 = AccessRecord(
            id=AccessId(str(uuid4())),
            user_id=UserId("user_789"),
            course_id=CourseId("course_101"),
            purchase_date=datetime.now(),
            access_expires_at=datetime.now() + timedelta(days=30),
            progress=Progress(50.0),
            status=AccessStatus.ACTIVE
        )
        
        access_repository.save(access1)
        access_repository.save(access2)
        
        assert access_repository.count() == 2
        
        # Test user queries
        user1_access = access_repository.get_by_user(access1.user_id)
        assert len(user1_access) == 1
        assert user1_access[0] == access1
        
        user2_access = access_repository.get_by_user(access2.user_id)
        assert len(user2_access) == 1
        assert user2_access[0] == access2
        
        # Test status queries
        active_access = access_repository.get_active_access()
        assert len(active_access) == 2
        assert access1 in active_access
        assert access2 in active_access
