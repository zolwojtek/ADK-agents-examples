from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class RegisterUserCommand:
    email: str
    password: str
    profile: Any

@dataclass
class RegisterUserResult:
    user_id: str
    status: str
    message: Optional[str] = None

@dataclass
class UpdateProfileCommand:
    user_id: str
    profile: Any

@dataclass
class UpdateProfileResult:
    user_id: str
    status: str
    message: Optional[str] = None

@dataclass
class ChangeEmailCommand:
    user_id: str
    new_email: str

@dataclass
class ChangeEmailResult:
    user_id: str
    status: str
    message: Optional[str] = None

class UserApplicationService:
    def __init__(self, user_repo, event_bus):
        self.user_repo = user_repo
        self.event_bus = event_bus

    def register_user(self, cmd: RegisterUserCommand) -> RegisterUserResult:
        if not cmd.email or not cmd.password:
            raise ValueError("Email and password required")
        if self.user_repo.find_by_email(cmd.email):
            raise ValueError("Email already registered")
        aggregate_fn = getattr(self, '_create_user_aggregate', None)
        if aggregate_fn:
            user = aggregate_fn(cmd)
        else:
            raise NotImplementedError("Stub: need domain user factory")
        self.user_repo.save(user)
        self.event_bus.publish("user_registered_event")
        return RegisterUserResult(user_id=user.id, status=user.status)

    def update_profile(self, cmd: UpdateProfileCommand) -> UpdateProfileResult:
        user = self.user_repo.get_by_id(cmd.user_id)
        if not user:
            raise ValueError("User not found")
        agg_fn = getattr(self, '_update_user_profile_aggregate', None)
        if agg_fn:
            status, msg = agg_fn(user, cmd)
        else:
            status, msg = ("UPDATED", "Stub")
        self.user_repo.save(user)
        self.event_bus.publish("user_profile_updated_event")
        return UpdateProfileResult(user_id=user.id, status=status, message=msg)

    def change_email(self, cmd: ChangeEmailCommand) -> ChangeEmailResult:
        user = self.user_repo.get_by_id(cmd.user_id)
        if not user:
            raise ValueError("User not found")
        if self.user_repo.find_by_email(cmd.new_email):
            raise ValueError("Email already in use")
        agg_fn = getattr(self, '_change_email_aggregate', None)
        if agg_fn:
            status, msg = agg_fn(user, cmd)
        else:
            status, msg = ("PENDING", "Stub")
        self.user_repo.save(user)
        self.event_bus.publish("user_email_change_event")
        return ChangeEmailResult(user_id=user.id, status=status, message=msg)
