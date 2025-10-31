"""
Unit tests for AccessRecord aggregate.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from domain.access.aggregates import AccessRecord
from domain.access.value_objects import ActivityType
from domain.shared.value_objects import AccessId, UserId, CourseId, Progress, AccessStatus


class TestAccessRecordAggregate:
    """Test AccessRecord aggregate."""
    
    @pytest.fixture
    def access_data(self):
        """Create test access data."""
        return {
            "id": AccessId(str(uuid4())),
            "user_id": UserId("user_123"),
            "course_id": CourseId("course_456"),
            "purchase_date": datetime(2025, 10, 16),
            "access_expires_at": datetime(2025, 12, 31),
            "progress": Progress(0.0),
            "status": AccessStatus.ACTIVE
        }
    
    @pytest.fixture
    def access_record(self, access_data):
        """Create a test access record."""
        return AccessRecord.grant_access(
            user_id=access_data["user_id"],
            course_id=access_data["course_id"],
            purchase_date=access_data["purchase_date"],
            access_expires_at=access_data["access_expires_at"]
        )
    
    def test_create_access_record(self, access_data):
        """Test creating an access record."""
        access = AccessRecord.grant_access(
            user_id=access_data["user_id"],
            course_id=access_data["course_id"],
            purchase_date=access_data["purchase_date"],
            access_expires_at=access_data["access_expires_at"]
        )
        
        assert access.id is not None
        assert access.user_id == access_data["user_id"]
        assert access.course_id == access_data["course_id"]
        assert access.purchase_date == access_data["purchase_date"]
        assert access.access_expires_at == access_data["access_expires_at"]
        assert access.progress == access_data["progress"]
        assert access.status == access_data["status"]
        assert access.created_at is not None
        assert access.updated_at is not None
        events = access.get_domain_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "CourseAccessGranted"
    
    def test_update_progress(self, access_record):
        """Test updating progress."""
        new_progress = Progress(75.5)
        
        access_record.update_progress(new_progress)
        
        assert access_record.progress == new_progress
        assert access_record.updated_at > access_record.created_at
        events = access_record.get_domain_events()
        assert len(events) == 2
        assert events[1].__class__.__name__ == "ProgressUpdated"
    
    def test_mark_completed(self, access_record):
        """Test completing course."""
        access_record.mark_completed()
        
        assert access_record.progress.value == 100.0
        assert access_record.updated_at > access_record.created_at
        events = access_record.get_domain_events()
        assert len(events) == 2
        assert events[1].__class__.__name__ == "CourseCompleted"
    
    def test_revoke_access(self, access_record):
        """Test revoking access."""
        reason = "Policy violation"
        
        access_record.revoke_access(reason)
        
        assert access_record.status == AccessStatus.REVOKED
        assert access_record.updated_at > access_record.created_at
        events = access_record.get_domain_events()
        assert len(events) == 2
        assert events[1].__class__.__name__ == "AccessRevoked"
        assert events[1].reason == reason
    
    def test_expire_access(self, access_record):
        """Test expiring access."""
        access_record.expire_access(datetime(2026, 10, 16))
        
        assert access_record.status == AccessStatus.EXPIRED
        assert access_record.updated_at > access_record.created_at
        events = access_record.get_domain_events()
        assert len(events) == 2
        assert events[1].__class__.__name__ == "AccessExpired"
    
    def test_reactivate_access(self, access_record):
        """Test reactivating access."""
        access_record.status = AccessStatus.REVOKED
        access_record.reactivate_access(datetime(2299, 10, 18))
        
        assert access_record.status == AccessStatus.ACTIVE
        assert access_record.updated_at > access_record.created_at
        events = access_record.get_domain_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "CourseAccessGranted"
    
    def test_record_activity(self, access_record):
        """Test adding activity."""
        activity_timestamp = datetime.now()
        activity_metadata = {"lesson_id": "lesson_123", "duration": 30}
        
        access_record.record_activity(
            activity_type=ActivityType.LESSON_COMPLETED,
            timestamp=activity_timestamp,
            metadata=activity_metadata
        )
        
        assert len(access_record.activities) == 1
        assert access_record.activities[0].activity_type == ActivityType.LESSON_COMPLETED
        assert access_record.activities[0].timestamp == activity_timestamp
        assert access_record.activities[0].metadata == activity_metadata
        assert access_record.updated_at > access_record.created_at
    
    def test_is_access_active(self, access_record):
        """Test checking if access is active."""
        assert access_record.is_active()
        
        access_record.status = AccessStatus.EXPIRED
        assert not access_record.is_active()
        
        access_record.status = AccessStatus.REVOKED
        assert not access_record.is_active()
    
    def test_is_access_expired_with_expiration_date(self):
        """Test checking if access is expired with expiration date."""
        access_data = {
            "id": AccessId(str(uuid4())),
            "user_id": UserId("user_123"),
            "course_id": CourseId("course_456"),
            "purchase_date": datetime.now() - timedelta(days=35),
            "access_expires_at": datetime.now() - timedelta(days=5),
            "progress": Progress(0.0),
            "status": AccessStatus.ACTIVE
        }
        access = AccessRecord(**access_data)
        
        assert access.has_expired()

    
    def test_clear_domain_events(self, access_record):
        """Test clearing domain events."""
        access_record.update_progress(Progress(50.0))  # Generate an event
        
        events = access_record.get_domain_events()
        assert len(events) == 2
        access_record.clear_domain_events()
        assert len(access_record.get_domain_events()) == 0
