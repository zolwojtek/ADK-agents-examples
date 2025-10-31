import pytest
from unittest.mock import Mock
from application_services.user_application_service import (
    UserApplicationService,
    RegisterUserCommand, RegisterUserResult,
    UpdateProfileCommand, UpdateProfileResult,
    ChangeEmailCommand, ChangeEmailResult
)

@pytest.fixture
def user_repo():
    return Mock()

@pytest.fixture
def event_bus():
    return Mock()

@pytest.fixture
def service(user_repo, event_bus):
    return UserApplicationService(user_repo, event_bus)

# --- Register User ---
def test_register_user_happy_path(service, user_repo, event_bus):
    # No existing user with email
    user_repo.find_by_email.return_value = None
    user_agg = Mock(id="uid-1", status="ACTIVE")
    # Patch domain method
    service._create_user_aggregate = lambda cmd: user_agg
    cmd = RegisterUserCommand(email="a@b.com", password="pw", profile={"first":"A"})
    result = service.register_user(cmd)
    assert isinstance(result, RegisterUserResult)
    assert result.status == "ACTIVE"
    assert result.user_id == "uid-1"
    user_repo.save.assert_called_once_with(user_agg)
    event_bus.publish.assert_called()

def test_register_user_email_conflict(service, user_repo):
    user_repo.find_by_email.return_value = Mock()
    cmd = RegisterUserCommand(email="a@b.com", password="pw", profile={})
    with pytest.raises(ValueError):
        service.register_user(cmd)

def test_register_user_invalid_input(service):
    cmd = RegisterUserCommand(email="", password="", profile={})
    with pytest.raises(ValueError):
        service.register_user(cmd)

# --- Update Profile ---
def test_update_profile_happy(service, user_repo, event_bus):
    user = Mock(id="u2")
    user_repo.get_by_id.return_value = user
    service._update_user_profile_aggregate = lambda u, c: ("UPDATED", "ok")
    cmd = UpdateProfileCommand(user_id="u2", profile={"first":"B"})
    result = service.update_profile(cmd)
    assert isinstance(result, UpdateProfileResult)
    assert result.user_id == "u2"
    assert result.status == "UPDATED"
    user_repo.save.assert_called_once_with(user)
    event_bus.publish.assert_called()

def test_update_profile_user_not_found(service, user_repo):
    user_repo.get_by_id.return_value = None
    cmd = UpdateProfileCommand(user_id="bad", profile={})
    with pytest.raises(ValueError):
        service.update_profile(cmd)

# --- Change Email ---
def test_change_email_happy(service, user_repo, event_bus):
    user = Mock(id="u3", status="ACTIVE")
    user_repo.get_by_id.return_value = user
    user_repo.find_by_email.return_value = None
    service._change_email_aggregate = lambda u, c: ("PENDING", "sent")
    cmd = ChangeEmailCommand(user_id="u3", new_email="new@example.com")
    result = service.change_email(cmd)
    assert isinstance(result, ChangeEmailResult)
    assert result.status == "PENDING"
    user_repo.save.assert_called_with(user)
    event_bus.publish.assert_called()

def test_change_email_user_not_found(service, user_repo):
    user_repo.get_by_id.return_value = None
    cmd = ChangeEmailCommand(user_id="bad", new_email="c@example.com")
    with pytest.raises(ValueError):
        service.change_email(cmd)

def test_change_email_in_use(service, user_repo):
    user_repo.get_by_id.return_value = Mock(id="u4")
    user_repo.find_by_email.return_value = Mock()
    cmd = ChangeEmailCommand(user_id="u4", new_email="used@email.com")
    with pytest.raises(ValueError):
        service.change_email(cmd)
