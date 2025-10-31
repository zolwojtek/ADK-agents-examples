from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

@dataclass
class CreateCourseCommand:
    title: str
    description: str
    policy_id: str
    price: Optional[float] = None
    instructor_id: Optional[str] = None

@dataclass
class CreateCourseResult:
    course_id: str
    status: str
    message: Optional[str] = None

@dataclass
class UpdateCourseCommand:
    course_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

@dataclass
class UpdateCourseResult:
    course_id: str
    status: str
    message: Optional[str] = None

@dataclass
class DeprecateCourseCommand:
    course_id: str

@dataclass
class DeprecateCourseResult:
    course_id: str
    status: str
    message: Optional[str] = None

@dataclass
class ChangeCoursePolicyCommand:
    course_id: str
    new_policy_id: str

@dataclass
class ChangeCoursePolicyResult:
    course_id: str
    status: str
    message: Optional[str] = None

class _V:
    def __init__(self, value):
        self.value = value

class _E:
    def __init__(self, event_type: str, **kwargs):
        self.__event_type__ = event_type
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'occurred_on'):
            self.occurred_on = datetime.now()

class CourseApplicationService:
    def __init__(self, course_repo, policy_repo, event_bus):
        self.course_repo = course_repo
        self.policy_repo = policy_repo
        self.event_bus = event_bus

    def create_course(self, cmd: CreateCourseCommand) -> CreateCourseResult:
        if self.course_repo.find_by_title(cmd.title):
            raise ValueError("Course already exists")
        policy = self.policy_repo.get_by_id(cmd.policy_id)
        if not policy:
            raise ValueError("Policy not found")
        agg_fn = getattr(self, '_create_course_aggregate', None)
        if agg_fn:
            course = agg_fn(policy, cmd)
        else:
            raise NotImplementedError("Stub: create course aggregate")
        self.course_repo.save(course)
        ev = _E('CourseCreated', course_id=_V(course.id), title=_V(cmd.title), policy_id=_V(cmd.policy_id))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return CreateCourseResult(course_id=course.id, status=course.status)

    def update_course(self, cmd: UpdateCourseCommand) -> UpdateCourseResult:
        course = self.course_repo.get_by_id(cmd.course_id)
        if not course:
            raise ValueError("Course not found")
        agg_fn = getattr(self, '_update_course_aggregate', None)
        if agg_fn:
            status, msg = agg_fn(course, cmd)
        else:
            status, msg = ("UPDATED", "Stub")
        self.course_repo.save(course)
        ev = _E('CourseUpdated', course_id=_V(cmd.course_id), title=_V(cmd.title or getattr(course,'title','Untitled')), description=_V(cmd.description or ''))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return UpdateCourseResult(course_id=course.id, status=status, message=msg)

    def deprecate_course(self, cmd: DeprecateCourseCommand) -> DeprecateCourseResult:
        course = self.course_repo.get_by_id(cmd.course_id)
        if not course:
            raise ValueError("Course not found")
        if getattr(course, 'status', None) == "DEPRECATED":
            raise ValueError("Course already deprecated")
        agg_fn = getattr(self, '_deprecate_course_aggregate', None)
        if agg_fn:
            status, msg = agg_fn(course, cmd)
        else:
            status, msg = ("DEPRECATED", "Stub")
        self.course_repo.save(course)
        ev = _E('CourseDeprecated', course_id=_V(cmd.course_id), title=_V(getattr(course,'title','Untitled')))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return DeprecateCourseResult(course_id=course.id, status=status, message=msg)

    def change_policy(self, cmd: ChangeCoursePolicyCommand) -> ChangeCoursePolicyResult:
        course = self.course_repo.get_by_id(cmd.course_id)
        if not course:
            raise ValueError("Course not found")
        policy = self.policy_repo.get_by_id(cmd.new_policy_id)
        if not policy:
            raise ValueError("Policy not found")
        agg_fn = getattr(self, '_change_policy_aggregate', None)
        if agg_fn:
            status, msg = agg_fn(course, policy, cmd)
        else:
            status, msg = ("POLICY_CHANGED", "Stub")
        self.course_repo.save(course)
        ev = _E('CoursePolicyChanged', course_id=_V(cmd.course_id), new_policy_id=_V(cmd.new_policy_id), old_policy_id=_V(getattr(course,'policy_id','p?')))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return ChangeCoursePolicyResult(course_id=course.id, status=status, message=msg)
