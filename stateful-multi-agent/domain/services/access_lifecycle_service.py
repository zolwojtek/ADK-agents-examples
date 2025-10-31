"""
Access Lifecycle Service for managing access expiration and reactivation.
"""

from datetime import datetime
from typing import List

from ..access.aggregates import AccessRecord
from ..access.repositories import AccessRepository
from ..shared.value_objects import UserId, CourseId


class AccessLifecycleService:
    """Service for managing access lifecycle operations."""
    
    def __init__(self, access_repository: AccessRepository):
        self.access_repository = access_repository
    
    def expire_access_records(self, current_time: datetime) -> List[AccessRecord]:
        """
        Expire all access records that have passed their expiration date.
        
        Args:
            current_time: Current timestamp to check against
            
        Returns:
            List of expired access records
        """
        expired_records = []
        
        # Get all active access records
        active_records = self.access_repository.get_active_access()
        
        for record in active_records:
            if record.has_expired(current_time):
                record.expire_access(current_time)
                self.access_repository.save(record)
                expired_records.append(record)
        
        return expired_records
    
    def reactivate_user_access(
        self, 
        user_id: UserId, 
        course_id: CourseId, 
        new_expiration: datetime
    ) -> AccessRecord:
        """
        Reactivate access for a specific user and course.
        
        Args:
            user_id: User identifier
            course_id: Course identifier  
            new_expiration: New expiration date
            
        Returns:
            Reactivated access record
            
        Raises:
            ValueError: If no expired/revoked access found
        """
        # Find existing access record
        access_record = self.access_repository.get_user_course_access(user_id, course_id)
        
        if not access_record:
            raise ValueError(f"No access record found for user {user_id} and course {course_id}")
        
        # Reactivate the access
        access_record.reactivate_access(new_expiration)
        self.access_repository.save(access_record)
        
        return access_record
    
    def get_expired_access_for_user(self, user_id: UserId) -> List[AccessRecord]:
        """
        Get all expired access records for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of expired access records for the user
        """
        user_access = self.access_repository.get_by_user(user_id)
        current_time = datetime.now()
        
        return [
            record for record in user_access 
            if record.has_expired(current_time)
        ]
