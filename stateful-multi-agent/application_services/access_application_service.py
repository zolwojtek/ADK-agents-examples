from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

@dataclass
class GrantAccessCommand:
    user_id: str
    course_id: str
    access_type: str
    validity_days: Optional[int] = None

@dataclass
class GrantAccessResult:
    access_id: str
    status: str
    message: Optional[str] = None

@dataclass
class RevokeAccessCommand:
    access_id: str
    reason: Optional[str] = None

@dataclass
class RevokeAccessResult:
    access_id: str
    status: str
    message: Optional[str] = None

@dataclass
class RefreshAccessCommand:
    access_id: str

@dataclass
class RefreshAccessResult:
    access_id: str
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

class AccessApplicationService:
    def __init__(self, access_repo, user_repo, course_repo, event_bus):
        self.access_repo = access_repo
        self.user_repo = user_repo
        self.course_repo = course_repo
        self.event_bus = event_bus

    def grant_access(self, cmd: GrantAccessCommand) -> GrantAccessResult:
        user = self.user_repo.get_by_id(cmd.user_id)
        if not user:
            raise ValueError("User not found")
        course = self.course_repo.get_by_id(cmd.course_id)
        if not course:
            raise ValueError("Course not found")
        existing = self.access_repo.find_by_user_course(cmd.user_id, cmd.course_id)
        if existing:
            raise ValueError("Access already exists")
        aggregate_fn = getattr(self, '_create_access_aggregate', None)
        if aggregate_fn:
            access = aggregate_fn(user, course, cmd)
        else:
            raise NotImplementedError("Stub: aggregate factory needed")
        self.access_repo.save(access)
        ev = _E('CourseAccessGranted', access_id=_V(access.id), user_id=_V(cmd.user_id), course_id=_V(cmd.course_id))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return GrantAccessResult(access_id=access.id, status=access.status)

    def revoke_access(self, cmd: RevokeAccessCommand) -> RevokeAccessResult:
        access = self.access_repo.get_by_id(cmd.access_id)
        if not access:
            raise ValueError("Access record not found")
        if getattr(access, 'status', None) == "REVOKED":
            raise ValueError("Access already revoked")
        revoke_fn = getattr(self, '_revoke_access_aggregate', None)
        if revoke_fn:
            status, msg = revoke_fn(access, cmd)
        else:
            status, msg = ("REVOKED", "Stub")
        self.access_repo.save(access)
        ev = _E('AccessRevoked', access_id=_V(cmd.access_id), user_id=_V(getattr(access, 'user_id', 'u?')), course_id=_V(getattr(access,'course_id','c?')))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return RevokeAccessResult(access_id=access.id, status=status, message=msg)

    def refresh_access(self, cmd: RefreshAccessCommand) -> RefreshAccessResult:
        access = self.access_repo.get_by_id(cmd.access_id)
        if not access:
            raise ValueError("Access record not found")
        refresh_fn = getattr(self, '_refresh_access_aggregate', None)
        if refresh_fn:
            status, msg = refresh_fn(access, cmd)
        else:
            if getattr(access, 'status', None) != "EXPIRED":
                raise ValueError("Cannot refresh access unless expired")
            status, msg = ("ACTIVE", "Stub")
        if status != "ACTIVE":
            raise ValueError("Cannot refresh access in current state")
        self.access_repo.save(access)
        # On refresh, emit CourseAccessGranted again for projection simplicity
        ev = _E('CourseAccessGranted', access_id=_V(cmd.access_id), user_id=_V(getattr(access,'user_id','u?')), course_id=_V(getattr(access,'course_id','c?')))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return RefreshAccessResult(access_id=access.id, status=status, message=msg)
