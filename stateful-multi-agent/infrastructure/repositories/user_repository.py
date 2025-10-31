"""
User repository implementation.
"""

from typing import List, Optional

from domain.users.repositories import UserRepository as IUserRepository
from domain.users.aggregates import User
from domain.shared.value_objects import Name, UserId, EmailAddress
from .base import InMemoryRepository


class UserRepository(InMemoryRepository[User, UserId], IUserRepository):
    """In-memory implementation of UserRepository."""
    
    def __init__(self):
        super().__init__()
        self._email_index: dict[str, UserId] = {}  # email -> id
    
    def find_by_id(self, id: UserId) -> Optional[User]:
        """Find user by ID."""
        return super().get_by_id(id)
    
    def get_by_email(self, email: EmailAddress) -> Optional[User]:
        """Get user by email address."""
        id = self._email_index.get(email.value)
        if id:
            return self.find_by_id(id)
        return None
    
    def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if user exists by email."""
        return email.value in self._email_index
    
    def get_by_name(self, first_name: Name, last_name: Name) -> List[User]:
        """Get users by first and last name."""
        return [
            user for user in self.get_all()
            if user.profile.first_name == first_name and 
               user.profile.last_name == last_name
        ]
    
    def search_by_name(self, query: str) -> List[User]:
        """Search users by name (partial match)."""
        query_lower = query.lower()
        return [
            user for user in self.get_all()
            if (query_lower in user.profile.first_name.lower() or 
                query_lower in user.profile.last_name.lower())
        ]
    
    def save(self, user: User) -> User:
        """Save user with email uniqueness check."""
        # Determine if this user already exists in the repository
        existing_user = super().get_by_id(user.id) if user.id else None

        # Check if the new email is already used by a different user
        mapped_id = self._email_index.get(user.email.value)
        if mapped_id is not None and mapped_id != user.id:
            raise ValueError(f"Email {user.email.value} already exists")

        # If updating, remove old email mapping if the email changed
        if existing_user is not None:
            # Find the previous email for this user via the index (robust to in-place mutations)
            previous_email_value = None
            for email_value, uid in self._email_index.items():
                if uid == user.id:
                    previous_email_value = email_value
                    break

            if previous_email_value is not None and previous_email_value != user.email.value:
                # Remove old mapping
                if previous_email_value in self._email_index:
                    del self._email_index[previous_email_value]

        # Save user using base repository
        saved_user = super().save(user)

        # Update email index with the new email mapping
        self._email_index[user.email.value] = user.id

        return saved_user
    
    def delete(self, id: UserId) -> bool:
        """Delete user by ID."""
        user = self.find_by_id(id)
        if user:
            # Remove from email index
            if user.email.value in self._email_index:
                del self._email_index[user.email.value]
            return super().delete(id)
        return False
    
    def clear(self) -> None:
        """Clear all users and email index."""
        super().clear()
        self._email_index.clear()
