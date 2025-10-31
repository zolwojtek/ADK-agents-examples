"""
Access repository implementation.
"""

from typing import List, Optional

from domain.access.repositories import AccessRepository as IAccessRepository
from domain.access.aggregates import AccessRecord
from domain.shared.value_objects import AccessId, UserId, CourseId, AccessStatus
from .base import InMemoryRepository


class AccessRepository(InMemoryRepository[AccessRecord, AccessId], IAccessRepository):
    """In-memory implementation of AccessRepository."""
    
    def __init__(self):
        super().__init__()
        self._user_index: dict[UserId, List[AccessId]] = {}  # user_id -> [access_ids]
        self._course_index: dict[CourseId, List[AccessId]] = {}  # course_id -> [access_ids]
        self._status_index: dict[AccessStatus, List[AccessId]] = {}  # status -> [access_ids]
        self._user_course_index: dict[tuple[UserId, CourseId], AccessId] = {}  # (user_id, course_id) -> access_id
    
    def find_by_id(self, access_id: AccessId) -> Optional[AccessRecord]:
        """Find access record by ID."""
        return super().get_by_id(access_id)
    
    def find_by_user_and_course(self, user_id: UserId, course_id: CourseId) -> Optional[AccessRecord]:
        """Find access record by user and course."""
        return self.get_user_course_access(user_id, course_id)
    
    def list_by_user(self, user_id: UserId) -> List[AccessRecord]:
        """List access records by user."""
        return self.get_by_user(user_id)
    
    def revoke(self, access_id: AccessId, reason: str) -> None:
        """Revoke access record."""
        access_record = self.find_by_id(access_id)
        if access_record:
            access_record.revoke_access(reason)
            self.save(access_record)
    
    def get_by_user(self, user_id: UserId) -> List[AccessRecord]:
        """Get access records by user ID."""
        access_ids = self._user_index.get(user_id, [])
        return [self.find_by_id(access_id) for access_id in access_ids if self.find_by_id(access_id)]
    
    def get_by_course(self, course_id: CourseId) -> List[AccessRecord]:
        """Get access records by course ID."""
        access_ids = self._course_index.get(course_id, [])
        return [self.find_by_id(access_id) for access_id in access_ids if self.find_by_id(access_id)]
    
    def get_by_status(self, status: AccessStatus) -> List[AccessRecord]:
        """Get access records by status."""
        access_ids = self._status_index.get(status, [])
        return [self.find_by_id(access_id) for access_id in access_ids if self.find_by_id(access_id)]
    
    def get_user_course_access(self, user_id: UserId, course_id: CourseId) -> Optional[AccessRecord]:
        """Get access record for specific user and course."""
        access_id = self._user_course_index.get((user_id, course_id))
        if access_id:
            return self.find_by_id(access_id)
        return None
    
    def get_active_access(self) -> List[AccessRecord]:
        """Get all active access records."""
        return self.get_by_status(AccessStatus.ACTIVE)
    
    def get_expired_access(self) -> List[AccessRecord]:
        """Get all expired access records."""
        return self.get_by_status(AccessStatus.EXPIRED)
    
    def get_revoked_access(self) -> List[AccessRecord]:
        """Get all revoked access records."""
        return self.get_by_status(AccessStatus.REVOKED)
    
    def get_pending_access(self) -> List[AccessRecord]:
        """Get all pending access records."""
        return self.get_by_status(AccessStatus.PENDING)
    
    def get_user_active_courses(self, user_id: UserId) -> List[AccessRecord]:
        """Get user's active course access records."""
        user_access = self.get_by_user(user_id)
        return [access for access in user_access if access.status == AccessStatus.ACTIVE]
    
    def get_course_active_users(self, course_id: CourseId) -> List[AccessRecord]:
        """Get active users for a specific course."""
        course_access = self.get_by_course(course_id)
        return [access for access in course_access if access.status == AccessStatus.ACTIVE]
    
    def save(self, access_record: AccessRecord) -> AccessRecord:
        """Save access record with indexing."""
        # Save access record
        saved_access = super().save(access_record)
        
        # Update indexes
        # User index
        if access_record.user_id not in self._user_index:
            self._user_index[access_record.user_id] = []
        if access_record.id not in self._user_index[access_record.user_id]:
            self._user_index[access_record.user_id].append(access_record.id)
        
        # Course index
        if access_record.course_id not in self._course_index:
            self._course_index[access_record.course_id] = []
        if access_record.id not in self._course_index[access_record.course_id]:
            self._course_index[access_record.course_id].append(access_record.id)
        
        # Status index - remove from old status and add to new status
        if access_record.id:
            # Remove from any existing status index
            statuses_to_remove = []
            for status, access_ids in self._status_index.items():
                if access_record.id in access_ids:
                    access_ids.remove(access_record.id)
                    if not access_ids:  # Mark empty status entries for removal
                        statuses_to_remove.append(status)
            # Remove empty status entries after iteration
            for status in statuses_to_remove:
                del self._status_index[status]
        
        # Add to new status index
        if access_record.status not in self._status_index:
            self._status_index[access_record.status] = []
        if access_record.id not in self._status_index[access_record.status]:
            self._status_index[access_record.status].append(access_record.id)
        
        # User-course index
        self._user_course_index[(access_record.user_id, access_record.course_id)] = access_record.id
        
        return saved_access
    
    def delete(self, access_id: AccessId) -> bool:
        """Delete access record by ID."""
        access_record = self.find_by_id(access_id)
        if access_record:
            # Remove from indexes
            # User index
            if access_record.user_id in self._user_index:
                if access_record.id in self._user_index[access_record.user_id]:
                    self._user_index[access_record.user_id].remove(access_record.id)
                if not self._user_index[access_record.user_id]:
                    del self._user_index[access_record.user_id]
            
            # Course index
            if access_record.course_id in self._course_index:
                if access_record.id in self._course_index[access_record.course_id]:
                    self._course_index[access_record.course_id].remove(access_record.id)
                if not self._course_index[access_record.course_id]:
                    del self._course_index[access_record.course_id]
            
            # Status index
            if access_record.status in self._status_index:
                if access_record.id in self._status_index[access_record.status]:
                    self._status_index[access_record.status].remove(access_record.id)
                if not self._status_index[access_record.status]:
                    del self._status_index[access_record.status]
            
            # User-course index
            key = (access_record.user_id, access_record.course_id)
            if key in self._user_course_index:
                del self._user_course_index[key]
            
            return super().delete(access_id)
        return False
    
    def clear(self) -> None:
        """Clear all access records and indexes."""
        super().clear()
        self._user_index.clear()
        self._course_index.clear()
        self._status_index.clear()
        self._user_course_index.clear()
