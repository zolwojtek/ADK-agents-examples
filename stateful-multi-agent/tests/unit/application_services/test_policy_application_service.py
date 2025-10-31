import pytest
from unittest.mock import Mock
from application_services.policy_application_service import (
    PolicyApplicationService,
    CreatePolicyCommand, CreatePolicyResult,
    UpdatePolicyCommand, UpdatePolicyResult,
    DeprecatePolicyCommand, DeprecatePolicyResult,
    ReactivatePolicyCommand, ReactivatePolicyResult
)

@pytest.fixture
def policy_repo():
    return Mock()

@pytest.fixture
def event_bus():
    return Mock()

@pytest.fixture
def service(policy_repo, event_bus):
    return PolicyApplicationService(policy_repo, event_bus)

# --- Create ---
def test_create_policy_happy(service, policy_repo, event_bus):
    policy_repo.find_by_name.return_value = None
    policy = Mock(id="p1", status="ACTIVE")
    service._create_policy_aggregate = lambda cmd: policy
    cmd = CreatePolicyCommand(name="Standard", policy_type="standard", refund_period_days=30)
    result = service.create_policy(cmd)
    assert isinstance(result, CreatePolicyResult)
    assert result.policy_id == "p1"
    assert result.status == "ACTIVE"
    policy_repo.save.assert_called_with(policy)
    event_bus.publish.assert_called()

def test_create_policy_already_exists(service, policy_repo):
    policy_repo.find_by_name.return_value = Mock(id="pX")
    cmd = CreatePolicyCommand(name="Standard", policy_type="standard")
    with pytest.raises(ValueError):
        service.create_policy(cmd)

# --- Update ---
def test_update_policy_happy(service, policy_repo, event_bus):
    policy = Mock(id="p2", status="ACTIVE")
    policy_repo.get_by_id.return_value = policy
    service._update_policy_aggregate = lambda p, cmd: ("UPDATED", "ok")
    cmd = UpdatePolicyCommand(policy_id="p2", refund_period_days=45)
    result = service.update_policy(cmd)
    assert isinstance(result, UpdatePolicyResult)
    assert result.policy_id == "p2"
    policy_repo.save.assert_called_with(policy)
    event_bus.publish.assert_called()

def test_update_policy_not_found(service, policy_repo):
    policy_repo.get_by_id.return_value = None
    cmd = UpdatePolicyCommand(policy_id="bad", refund_period_days=10)
    with pytest.raises(ValueError):
        service.update_policy(cmd)

# --- Deprecate ---
def test_deprecate_policy_happy(service, policy_repo, event_bus):
    policy = Mock(id="p3", status="ACTIVE")
    policy_repo.get_by_id.return_value = policy
    service._deprecate_policy_aggregate = lambda p, cmd: ("DEPRECATED", "done")
    cmd = DeprecatePolicyCommand(policy_id="p3")
    result = service.deprecate_policy(cmd)
    assert isinstance(result, DeprecatePolicyResult)
    assert result.status == "DEPRECATED"
    policy_repo.save.assert_called_with(policy)
    event_bus.publish.assert_called()

def test_deprecate_policy_not_found(service, policy_repo):
    policy_repo.get_by_id.return_value = None
    cmd = DeprecatePolicyCommand(policy_id="bad")
    with pytest.raises(ValueError):
        service.deprecate_policy(cmd)

def test_deprecate_policy_already_deprecated(service, policy_repo):
    policy = Mock(id="p4", status="DEPRECATED")
    policy_repo.get_by_id.return_value = policy
    service._deprecate_policy_aggregate = lambda p, cmd: ("DEPRECATED", "already")
    cmd = DeprecatePolicyCommand(policy_id="p4")
    with pytest.raises(ValueError):
        service.deprecate_policy(cmd)

# --- Reactivate ---
def test_reactivate_policy_happy(service, policy_repo, event_bus):
    policy = Mock(id="p5", status="DEPRECATED")
    policy_repo.get_by_id.return_value = policy
    service._reactivate_policy_aggregate = lambda p, cmd: ("ACTIVE", "ok")
    cmd = ReactivatePolicyCommand(policy_id="p5")
    result = service.reactivate_policy(cmd)
    assert isinstance(result, ReactivatePolicyResult)
    assert result.status == "ACTIVE"
    policy_repo.save.assert_called_with(policy)
    event_bus.publish.assert_called()

def test_reactivate_policy_not_found(service, policy_repo):
    policy_repo.get_by_id.return_value = None
    cmd = ReactivatePolicyCommand(policy_id="bad")
    with pytest.raises(ValueError):
        service.reactivate_policy(cmd)

def test_reactivate_policy_already_active(service, policy_repo):
    policy = Mock(id="p6", status="ACTIVE")
    policy_repo.get_by_id.return_value = policy
    service._reactivate_policy_aggregate = lambda p, cmd: ("ACTIVE", "already")
    cmd = ReactivatePolicyCommand(policy_id="p6")
    with pytest.raises(ValueError):
        service.reactivate_policy(cmd)
