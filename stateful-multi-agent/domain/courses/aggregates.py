"""
Course aggregate root.
"""

from dataclasses import dataclass
from datetime import datetime
import uuid

from ..shared.value_objects import CourseId, Money, AccessType, PolicyRef, Entity
from .value_objects import Title, Description
from .events import CourseCreated, CourseUpdated, CoursePolicyChanged, CourseDeprecated


@dataclass
class Course(Entity):
    """
    Course aggregate root.
    
    Responsibility: course metadata, price, access type (limited/unlimited), 
    reference to refund policy.
    """
    id: CourseId
    title: Title
    description: Description
    price: Money
    access_type: AccessType
    policy_ref: PolicyRef
    
    @classmethod
    def create_course(
        cls,
        title: Title,
        description: Description,
        price: Money,
        access_type: AccessType,
        policy_ref: PolicyRef
    ) -> 'Course':
        """Create a new course."""
        course_id = CourseId(str(uuid.uuid4()))
        course = cls(
            id=course_id,
            title=title,
            description=description,
            price=price,
            access_type=access_type,
            policy_ref=policy_ref
        )
        
        # Raise domain event
        event = CourseCreated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id=course_id.value,
            course_id=course_id,
            title=title,
            policy_id=policy_ref.policy_id
        )
        course.add_domain_event(event)
        
        return course
    
    def update_details(self, title: Title, description: Description) -> None:
        """Update course title and description."""
        self.title = title
        self.description = description
        
        # Raise domain event
        event = CourseUpdated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id=self.id.value,
            course_id=self.id,
            title=title,
            description=description
        )
        self.add_domain_event(event)
    
    def assign_refund_policy(self, policy_ref: PolicyRef) -> None:
        """Assign a refund policy to the course."""
        if self.policy_ref == policy_ref:
            return  # No change needed
        
        old_policy_id = self.policy_ref.policy_id
        self.policy_ref = policy_ref
        
        # Raise domain event
        event = CoursePolicyChanged(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id=self.id.value,
            course_id=self.id,
            old_policy_id=old_policy_id,
            new_policy_id=policy_ref.policy_id
        )
        self.add_domain_event(event)
    
    def set_access_type(self, access_type: AccessType) -> None:
        """Set course access type."""
        self.access_type = access_type
        self.touch()
    
    def change_price(self, new_price: Money) -> None:
        """Change course price."""
        if new_price.currency != self.price.currency:
            raise ValueError("Cannot change currency of existing course")
        
        self.price = new_price
        self.touch()
    
    def has_refund_policy(self) -> bool:
        """Check if course has a refund policy assigned."""
        return self.policy_ref is not None
    
    def deprecate(self) -> None:
        """Deprecate the course."""
        self.touch()
        
        # Raise domain event
        event = CourseDeprecated(
            event_id=str(uuid.uuid4()),
            occurred_on=datetime.now(),
            aggregate_type="Course",
            aggregate_id=self.id.value,
            course_id=self.id,
            title=self.title
        )
        self.add_domain_event(event)