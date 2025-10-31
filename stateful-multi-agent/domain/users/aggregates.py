"""
User aggregate root.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

from ..shared.value_objects import UserId, EmailAddress, AccessRef, Entity
from .value_objects import UserProfile, UserStatus
from .events import UserRegistered, UserProfileUpdated, UserEmailChanged


@dataclass
class User(Entity):
    """
    User aggregate root.
    
    Responsibility: identity, credentials/profile, references to access records (IDs), 
    user-level preferences.
    """
    id: UserId
    email: EmailAddress
    profile: UserProfile
    status: UserStatus = UserStatus.INACTIVE
    email_verified: bool = False
    access_refs: List[AccessRef] = field(default_factory=list)
    
    @classmethod
    def create_user(cls, email: EmailAddress, profile: UserProfile) -> 'User':
        """Create a new user through registration."""
        user_id = UserId(str(uuid.uuid4()))
        user = cls(
            id=user_id,
            email=email,
            profile=profile,
            status=UserStatus.INACTIVE,
            email_verified=False
        )
        
        # Raise domain event
        event = UserRegistered(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id=user_id.value,
            user_id=user_id,
            email=email,
            name=profile.full_name
        )
        user.add_domain_event(event)
        
        return user
    
    def verify_identity(self) -> None:
        """Mark user's email as verified."""
        if self.email_verified:
            raise ValueError("Email is already verified")
        
        self.email_verified = True
        self.status = UserStatus.ACTIVE
        self.touch()
    
    def update_profile(self, new_profile: UserProfile) -> None:
        """Update user profile information."""
        if self.status in [UserStatus.BANNED, UserStatus.DELETED]:
            raise ValueError("Cannot update profile for banned or deleted user")
        
        self.profile = new_profile
        
        # Raise domain event
        event = UserProfileUpdated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id=self.id.value,
            user_id=self.id,
            profile=new_profile
        )
        self.add_domain_event(event)
    
    def change_email(self, new_email: EmailAddress) -> None:
        """Change user's email address."""
        if self.status in [UserStatus.BANNED, UserStatus.DELETED]:
            raise ValueError("Cannot change email for banned or deleted user")
        
        if self.email == new_email:
            return  # No change needed
        
        old_email = self.email
        self.email = new_email
        self.email_verified = False  # New email needs verification
        
        # Raise domain event
        event = UserEmailChanged(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="User",
            aggregate_id=self.id.value,
            user_id=self.id,
            old_email=old_email,
            new_email=new_email
        )
        self.add_domain_event(event)
    
    def activate(self) -> None:
        """Activate user account."""
        if self.status == UserStatus.ACTIVE:
            raise ValueError("User is already active")
        
        if self.status == UserStatus.DELETED:
            raise ValueError("Cannot activate deleted user")
        
        self.status = UserStatus.ACTIVE
        self.touch()
    
    def deactivate(self, reason: str) -> None:
        """Deactivate user account."""
        if self.status == UserStatus.DELETED:
            raise ValueError("Cannot deactivate deleted user")
        
        self.status = UserStatus.INACTIVE
        self.touch()
    
    def ban(self, reason: str) -> None:
        """Ban user account."""
        if self.status == UserStatus.DELETED:
            raise ValueError("Cannot ban deleted user")
        
        self.status = UserStatus.BANNED
        self.touch()
    
    def mark_as_deleted(self) -> None:
        """Mark user as deleted (soft delete)."""
        self.status = UserStatus.DELETED
        self.touch()
    
    def can_place_order(self) -> bool:
        """Check if user can place orders."""
        return (
            self.status == UserStatus.ACTIVE and 
            self.email_verified
        )
    
    def has_verified_email(self) -> bool:
        """Check if user has verified email."""
        return self.email_verified
    
    def add_access_ref(self, access_ref: AccessRef) -> None:
        """Add reference to access record."""
        # Check for duplicates
        for existing_ref in self.access_refs:
            if existing_ref.access_id == access_ref.access_id:
                return  # Already exists
        
        self.access_refs.append(access_ref)
        self.touch()
    
    def remove_access_ref(self, access_id: str) -> None:
        """Remove reference to access record."""
        self.access_refs = [
            ref for ref in self.access_refs 
            if ref.access_id.value != access_id
        ]
        self.touch()


#possible events to be implemented later if needed e.g. UserBanned, USerDeleted, UserActivated and so on...