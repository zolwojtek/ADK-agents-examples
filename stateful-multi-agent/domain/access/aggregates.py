"""
AccessRecord aggregate root.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

from ..shared.value_objects import AccessId, UserId, CourseId, Progress, AccessStatus, Entity
from .value_objects import ActivityType, ActivityRecord
from .events import CourseAccessGranted, AccessRevoked, AccessExpired, ProgressUpdated, CourseCompleted


@dataclass
class AccessRecord(Entity):
    """
    AccessRecord aggregate root.
    
    Responsibility: represent granted access to a specific course for a specific user; 
    control progress and expiration; be the canonical source for whether access is active.
    """
    id: AccessId
    user_id: UserId
    course_id: CourseId
    purchase_date: datetime
    access_expires_at: Optional[datetime]
    progress: Progress
    status: AccessStatus
    activities: List[ActivityRecord] = field(default_factory=list)
    
    @classmethod
    def grant_access(
        cls,
        user_id: UserId,
        course_id: CourseId,
        purchase_date: datetime,
        access_expires_at: Optional[datetime] = None
    ) -> 'AccessRecord':
        """Grant access to a course for a user."""
        access_id = AccessId(str(uuid.uuid4()))
        
        # Validate expiration date
        if access_expires_at and access_expires_at <= purchase_date:
            raise ValueError("Access expiration must be after purchase date")
        
        access_record = cls(
            id=access_id,
            user_id=user_id,
            course_id=course_id,
            purchase_date=purchase_date,
            access_expires_at=access_expires_at,
            progress=Progress(0.0),
            status=AccessStatus.ACTIVE
        )
        
        # Raise domain event
        event = CourseAccessGranted(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id=access_id.value,
            access_id=access_id,
            user_id=user_id,
            course_id=course_id
        )
        access_record._domain_events.append(event)
        
        return access_record
    
    def revoke_access(self, reason: str) -> None:
        """Revoke access to the course."""
        if self.status == AccessStatus.REVOKED:
            raise ValueError("Access is already revoked")
        
        self.status = AccessStatus.REVOKED
        self.updated_at = datetime.now()
        
        # Raise domain event
        event = AccessRevoked(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id=self.id.value,
            access_id=self.id,
            user_id=self.user_id,
            course_id=self.course_id,
            reason=reason
        )
        self._domain_events.append(event)
    
    def expire_access(self, current_time: datetime) -> None:
        """Expire access if it has passed the expiration date."""
        if self.status != AccessStatus.ACTIVE:
            return
        
        if self.access_expires_at and current_time >= self.access_expires_at:
            self.status = AccessStatus.EXPIRED
            self.updated_at = datetime.now()
            
            # Raise domain event
            event = AccessExpired(
                event_id=str(uuid.uuid4()),
                occurred_on=datetime.now(),
                aggregate_type="AccessRecord",
                aggregate_id=self.id.value,
                access_id=self.id,
                user_id=self.user_id,
                course_id=self.course_id,
                expired_at=self.access_expires_at
            )
            self._domain_events.append(event)
    
    def reactivate_access(self, new_expiration: Optional[datetime]) -> None:
        """Reactivate access with new expiration date."""
        if self.status not in [AccessStatus.EXPIRED, AccessStatus.REVOKED]:
            raise ValueError("Can only reactivate expired or revoked access")
        
        self.status = AccessStatus.ACTIVE
        self.access_expires_at = new_expiration
        self.updated_at = datetime.now()
    
    def update_progress(self, new_progress: Progress) -> None:
        """Update course progress."""
        if self.status not in [AccessStatus.ACTIVE]:
            raise ValueError("Cannot update progress for inactive access")
        
        if new_progress.value < self.progress.value:
            raise ValueError("Progress cannot decrease")
        
        old_progress = self.progress
        self.progress = new_progress
        self.updated_at = datetime.now()
        
        # Raise domain event
        event = ProgressUpdated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id=self.id.value,
            access_id=self.id,
            user_id=self.user_id,
            course_id=self.course_id,
            progress=new_progress
        )
        self._domain_events.append(event)
        
        # Check if course is completed
        if new_progress.value >= 100.0 and old_progress.value < 100.0:
            self.mark_completed()
    
    def mark_completed(self) -> None:
        """Mark course as completed."""
        if self.status != AccessStatus.ACTIVE:
            raise ValueError("Cannot complete inactive access")
        
        self.progress = Progress(100.0)
        self.updated_at = datetime.now()
        
        # Raise domain event
        event = CourseCompleted(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="AccessRecord",
            aggregate_id=self.id.value,
            access_id=self.id,
            user_id=self.user_id,
            course_id=self.course_id
        )
        self._domain_events.append(event)
    
    def record_activity(self, activity_type: ActivityType, timestamp: datetime, metadata: dict = None) -> None:
        """Record user activity in the course."""
        if self.status != AccessStatus.ACTIVE:
            raise ValueError("Cannot record activity for inactive access")
        
        activity = ActivityRecord(
            activity_type=activity_type,
            timestamp=timestamp,
            metadata=metadata or {}
        )
        self.activities.append(activity)
        self.updated_at = datetime.now()
    
    def can_be_refunded(self, current_time: datetime, refund_policy) -> bool:
        """Check if access can be refunded based on policy."""
        if self.status != AccessStatus.ACTIVE:
            return False
        
        return refund_policy.is_refund_allowed(
            purchase_date=self.purchase_date,
            current_date=current_time,
            progress=self.progress.value
        )
    
    def is_active(self) -> bool:
        """Check if access is currently active."""
        if self.status != AccessStatus.ACTIVE:
            return False
        
        # Check if expired
        if self.access_expires_at and datetime.now() >= self.access_expires_at:
            return False
        
        return True
    
    def has_expired(self) -> bool:
        """Check if access has expired."""
        return self.status == AccessStatus.EXPIRED or (
            self.access_expires_at and datetime.now() >= self.access_expires_at
        )
    
    def is_revoked(self) -> bool:
        """Check if access is revoked."""
        return self.status == AccessStatus.REVOKED
    
    def get_domain_events(self) -> List:
        """Get and clear domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()
