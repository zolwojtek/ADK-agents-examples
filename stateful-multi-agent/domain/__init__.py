"""
Domain layer for the IT Developers Platform.

This module contains all domain components organized by bounded contexts:
- Users: User management and identity
- Courses: Course catalog and metadata
- Policies: Refund policies and rules
- Orders: Purchase transactions and lifecycle
- Access: Course access and progress tracking
- Shared: Common value objects and utilities
"""

# Import shared components
from .shared import *

# Import bounded contexts
from . import users
from . import courses
from . import policies
from . import orders
from . import access

__all__ = [
    # Shared components are already exported by shared module
    'users',
    'courses', 
    'policies',
    'orders',
    'access'
]
