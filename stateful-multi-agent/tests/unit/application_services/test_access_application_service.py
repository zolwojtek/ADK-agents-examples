import pytest
from unittest.mock import Mock
from application_services.access_application_service import (
    AccessApplicationService,
    GrantAccessCommand, GrantAccessResult,
    RevokeAccessCommand, RevokeAccessResult,
    RefreshAccessCommand, RefreshAccessResult
)

@pytest.fixture
def access_repo():
    return Mock()

@pytest.fixture
def user_repo():
    return Mock()

@pytest.fixture
def course_repo():
    return Mock()

@pytest.fixture
def event_bus():
    return Mock()

@pytest.fixture
def service(access_repo, user_repo, course_repo, event_bus):
    return AccessApplicationService(access_repo, user_repo, course_repo, event_bus)

# --- Grant Access ---
def test_grant_access_happy(service, access_repo, user_repo, course_repo, event_bus):
    user_repo.get_by_id.return_value = Mock(id="u10")
    course_repo.get_by_id.return_value = Mock(id="c10")
    access_repo.find_by_user_course.return_value = None
    access_rec = Mock(id="a1", status="ACTIVE")
    service._create_access_aggregate = lambda user, course, cmd: access_rec
    cmd = GrantAccessCommand(user_id="u10", course_id="c10", access_type="enroll")
    result = service.grant_access(cmd)
    assert isinstance(result, GrantAccessResult)
    assert result.access_id == "a1"
    assert result.status == "ACTIVE"
    access_repo.save.assert_called_once_with(access_rec)
    event_bus.publish.assert_called()

def test_grant_access_user_not_found(service, user_repo):
    user_repo.get_by_id.return_value = None
    cmd = GrantAccessCommand(user_id="bad", course_id="c20", access_type="enroll")
    with pytest.raises(ValueError):
        service.grant_access(cmd)

def test_grant_access_course_not_found(service, user_repo, course_repo):
    user_repo.get_by_id.return_value = Mock(id="u15")
    course_repo.get_by_id.return_value = None
    cmd = GrantAccessCommand(user_id="u15", course_id="bad", access_type="enroll")
    with pytest.raises(ValueError):
        service.grant_access(cmd)

def test_grant_access_already_exists(service, user_repo, course_repo, access_repo):
    user_repo.get_by_id.return_value = Mock(id="u16")
    course_repo.get_by_id.return_value = Mock(id="c16")
    access_repo.find_by_user_course.return_value = Mock(id="a16", status="ACTIVE")
    cmd = GrantAccessCommand(user_id="u16", course_id="c16", access_type="enroll")
    with pytest.raises(ValueError):
        service.grant_access(cmd)

# --- Revoke Access ---
def test_revoke_access_happy(service, access_repo, event_bus):
    access = Mock(id="a2", status="ACTIVE")
    access_repo.get_by_id.return_value = access
    service._revoke_access_aggregate = lambda rec, cmd: ("REVOKED", "revoked")
    cmd = RevokeAccessCommand(access_id="a2", reason="violation")
    result = service.revoke_access(cmd)
    assert isinstance(result, RevokeAccessResult)
    assert result.access_id == "a2"
    assert result.status == "REVOKED"
    access_repo.save.assert_called_with(access)
    event_bus.publish.assert_called()

def test_revoke_access_not_found(service, access_repo):
    access_repo.get_by_id.return_value = None
    cmd = RevokeAccessCommand(access_id="bad")
    with pytest.raises(ValueError):
        service.revoke_access(cmd)

def test_revoke_access_already_revoked(service, access_repo):
    access = Mock(id="a4", status="REVOKED")
    access_repo.get_by_id.return_value = access
    service._revoke_access_aggregate = lambda rec, cmd: ("REVOKED", "already")
    cmd = RevokeAccessCommand(access_id="a4", reason="")
    with pytest.raises(ValueError):
        service.revoke_access(cmd)

# --- Refresh Access ---
def test_refresh_access_happy(service, access_repo, event_bus):
    access = Mock(id="a3", status="EXPIRED")
    access_repo.get_by_id.return_value = access
    service._refresh_access_aggregate = lambda rec, cmd: ("ACTIVE", "renewed")
    cmd = RefreshAccessCommand(access_id="a3")
    result = service.refresh_access(cmd)
    assert isinstance(result, RefreshAccessResult)
    assert result.access_id == "a3"
    assert result.status == "ACTIVE"
    access_repo.save.assert_called_with(access)
    event_bus.publish.assert_called()

def test_refresh_access_not_found(service, access_repo):
    access_repo.get_by_id.return_value = None
    cmd = RefreshAccessCommand(access_id="bad")
    with pytest.raises(ValueError):
        service.refresh_access(cmd)

def test_refresh_access_invalid_state(service, access_repo):
    access = Mock(id="a5", status="REVOKED")  # Can't refresh revoked
    access_repo.get_by_id.return_value = access
    service._refresh_access_aggregate = lambda rec, cmd: ("REVOKED", "can't refresh")
    cmd = RefreshAccessCommand(access_id="a5")
    with pytest.raises(ValueError):
        service.refresh_access(cmd)
