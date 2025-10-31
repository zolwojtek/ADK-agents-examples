"""
Shared Value Objects for the IT Developers Platform.

Value Objects are immutable domain concepts that represent meaningful business data.
They enforce invariants and provide type safety.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime, date
import re
import uuid


# ============================================================================
# IDENTIFIER VALUE OBJECTS
# ============================================================================

@dataclass(frozen=True)
class Identifier:
    """Base class for all identifier value objects."""
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError(f"{self.__class__.__name__} must be a non-empty string")
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.value}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class UserId(Identifier):
    """Unique user identifier."""
    
    def __post_init__(self):
        super().__post_init__()
        # Validate UUID format if it looks like one
        if len(self.value) == 36 and self.value.count('-') == 4:
            try:
                uuid.UUID(self.value)
            except ValueError:
                raise ValueError("UserId must be a valid UUID format")


@dataclass(frozen=True)
class CourseId(Identifier):
    """Unique course identifier."""


@dataclass(frozen=True)
class OrderId(Identifier):
    """Unique order identifier."""


@dataclass(frozen=True)
class PolicyId(Identifier):
    """Unique refund policy identifier."""


@dataclass(frozen=True)
class AccessId(Identifier):
    """Unique access record identifier."""


# ============================================================================
# BASE ENTITY CLASS
# ============================================================================

from dataclasses import field
from typing import List, Any
from abc import ABC

@dataclass
class Entity(ABC):
    """Base class for all domain entities."""
    id: Identifier
    created_at: datetime = field(default_factory=datetime.now, init=False)
    updated_at: datetime = field(default_factory=datetime.now, init=False)
    _domain_events: List[Any] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Initialize entity after creation."""
        if not hasattr(self, 'id') or not self.id:
            raise ValueError("Entity must have a valid ID")
    
    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()
    
    def add_domain_event(self, event: Any) -> None:
        """Add a domain event to the entity."""
        self._domain_events.append(event)
        self.touch()
    
    def get_domain_events(self) -> List[Any]:
        """Get and return domain events."""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID and type."""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)


# ============================================================================
# MONEY AND PRICING VALUE OBJECTS
# ============================================================================

@dataclass(frozen=True)
class Money:
    """Represents monetary value with currency."""
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code (e.g., USD)")
        # Convert to Decimal if it's not already
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money amounts (same currency only)."""
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract money amounts (same currency only)."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Result cannot be negative")
        return Money(result, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """Multiply money by a factor."""
        if factor < 0:
            raise ValueError("Factor cannot be negative")
        return Money(self.amount * factor, self.currency)


@dataclass(frozen=True)
class PriceSnapshot:
    """Immutable price at time of purchase."""
    amount: Decimal
    currency: str
    captured_at: datetime
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Price amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))


# ============================================================================
# CONTACT AND IDENTIFICATION VALUE OBJECTS
# ============================================================================

@dataclass(frozen=True)
class EmailAddress:
    """Validated email address."""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Email address cannot be empty")
        
        # Basic email validation (RFC 5322 simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.value):
            raise ValueError("Invalid email address format")
        
        if len(self.value) > 254:  # RFC 5321 limit
            raise ValueError("Email address too long")


@dataclass(frozen=True)
class Name:
    """Display name for users or courses."""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Name cannot be empty")
        # Trim whitespace
        object.__setattr__(self, 'value', self.value.strip())
        if len(self.value) > 255:
            raise ValueError("Name too long")


# ============================================================================
# PROGRESS AND TIME VALUE OBJECTS
# ============================================================================

@dataclass(frozen=True)
class Progress:
    """Course completion progress as percentage."""
    value: float
    
    def __post_init__(self):
        if not isinstance(self.value, (int, float)):
            raise ValueError("Progress must be a number")
        if self.value < 0 or self.value > 100:
            raise ValueError("Progress must be between 0 and 100")
        # Round to 2 decimal places
        object.__setattr__(self, 'value', round(float(self.value), 2))


@dataclass(frozen=True)
class RefundPeriod:
    """Refund time window in days."""
    days: int
    
    def __post_init__(self):
        if self.days < 0:
            raise ValueError("Refund period cannot be negative")


@dataclass(frozen=True)
class DateRange:
    """Valid date span."""
    start: date
    end: date
    
    def __post_init__(self):
        if self.end < self.start:
            raise ValueError("End date must be after start date")


# ============================================================================
# REFERENCE VALUE OBJECTS
# ============================================================================

@dataclass(frozen=True)
class AccessRef:
    """Reference to AccessRecord ID."""
    access_id: AccessId
    
    def __post_init__(self):
        if not isinstance(self.access_id, AccessId):
            raise ValueError("AccessRef must contain a valid AccessId")


@dataclass(frozen=True)
class PolicyRef:
    """Reference to RefundPolicy ID."""
    policy_id: PolicyId
    
    def __post_init__(self):
        if not isinstance(self.policy_id, PolicyId):
            raise ValueError("PolicyRef must contain a valid PolicyId")


# ============================================================================
# PAYMENT VALUE OBJECTS
# ============================================================================

@dataclass(frozen=True)
class PaymentInfo:
    """Payment method and transaction details."""
    payment_id: str
    method: str
    transaction_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.payment_id or not isinstance(self.payment_id, str):
            raise ValueError("Payment ID must be a non-empty string")
        if not self.method or not isinstance(self.method, str):
            raise ValueError("Payment method must be a non-empty string")


# ============================================================================
# ENUMERATION VALUE OBJECTS
# ============================================================================

class AccessStatus(Enum):
    """Access record status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


class OrderStatus(Enum):
    """Order status."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUND_REQUESTED = "refund_requested"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class AccessType(Enum):
    """Course access type."""
    UNLIMITED = "unlimited"
    LIMITED = "limited"


class PolicyType(Enum):
    """Refund policy type."""
    STANDARD = "standard"
    EXTENDED = "extended"
    NO_REFUND = "no_refund"
