from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

@dataclass
class CreatePolicyCommand:
    name: str
    policy_type: str
    refund_period_days: Optional[int] = None
    conditions: Optional[str] = None

@dataclass
class CreatePolicyResult:
    policy_id: str
    status: str
    message: Optional[str] = None

@dataclass
class UpdatePolicyCommand:
    policy_id: str
    name: Optional[str] = None
    policy_type: Optional[str] = None
    refund_period_days: Optional[int] = None
    conditions: Optional[str] = None

@dataclass
class UpdatePolicyResult:
    policy_id: str
    status: str
    message: Optional[str] = None

@dataclass
class DeprecatePolicyCommand:
    policy_id: str

@dataclass
class DeprecatePolicyResult:
    policy_id: str
    status: str
    message: Optional[str] = None

@dataclass
class ReactivatePolicyCommand:
    policy_id: str

@dataclass
class ReactivatePolicyResult:
    policy_id: str
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

class PolicyApplicationService:
    def __init__(self, policy_repo, event_bus):
        self.policy_repo = policy_repo
        self.event_bus = event_bus

    def create_policy(self, cmd: CreatePolicyCommand) -> CreatePolicyResult:
        if self.policy_repo.find_by_name(cmd.name):
            raise ValueError("Policy with this name already exists")
        agg_fn = getattr(self, '_create_policy_aggregate', None)
        if agg_fn:
            policy = agg_fn(cmd)
        else:
            raise NotImplementedError("Stub: create policy aggregate")
        self.policy_repo.save(policy)
        ev = _E('PolicyCreated', policy_id=_V(policy.id), policy_type=_V(cmd.policy_type), name=_V(cmd.name))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return CreatePolicyResult(policy_id=policy.id, status=policy.status)

    def update_policy(self, cmd: UpdatePolicyCommand) -> UpdatePolicyResult:
        policy = self.policy_repo.get_by_id(cmd.policy_id)
        if not policy:
            raise ValueError("Policy not found")
        agg_fn = getattr(self, '_update_policy_aggregate', None)
        if agg_fn:
            status, msg = agg_fn(policy, cmd)
        else:
            status, msg = ("UPDATED", "Stub")
        self.policy_repo.save(policy)
        ev = _E('PolicyUpdated', policy_id=_V(cmd.policy_id), policy_type=_V(cmd.policy_type or getattr(policy,'type','standard')), refund_period_days=getattr(cmd,'refund_period_days', None), name=_V(getattr(cmd,'name', getattr(policy,'name',''))))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return UpdatePolicyResult(policy_id=policy.id, status=status, message=msg)

    def deprecate_policy(self, cmd: DeprecatePolicyCommand) -> DeprecatePolicyResult:
        policy = self.policy_repo.get_by_id(cmd.policy_id)
        if not policy:
            raise ValueError("Policy not found")
        if getattr(policy, 'status', None) == "DEPRECATED":
            raise ValueError("Policy already deprecated")
        agg_fn = getattr(self, '_deprecate_policy_aggregate', None)
        if agg_fn:
            status, msg = agg_fn(policy, cmd)
        else:
            status, msg = ("DEPRECATED", "Stub")
        self.policy_repo.save(policy)
        ev = _E('PolicyUpdated', policy_id=_V(cmd.policy_id), status='deprecated')
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return DeprecatePolicyResult(policy_id=policy.id, status=status, message=msg)

    def reactivate_policy(self, cmd: ReactivatePolicyCommand) -> ReactivatePolicyResult:
        policy = self.policy_repo.get_by_id(cmd.policy_id)
        if not policy:
            raise ValueError("Policy not found")
        if getattr(policy, 'status', None) == "ACTIVE":
            raise ValueError("Policy already active")
        agg_fn = getattr(self, '_reactivate_policy_aggregate', None)
        if agg_fn:
            status, msg = agg_fn(policy, cmd)
        else:
            status, msg = ("ACTIVE", "Stub")
        self.policy_repo.save(policy)
        ev = _E('PolicyUpdated', policy_id=_V(cmd.policy_id), status='active')
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return ReactivatePolicyResult(policy_id=policy.id, status=status, message=msg)
