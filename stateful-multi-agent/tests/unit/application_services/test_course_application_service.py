import pytest
from unittest.mock import Mock
from application_services.course_application_service import (
    CourseApplicationService,
    CreateCourseCommand, CreateCourseResult,
    UpdateCourseCommand, UpdateCourseResult,
    DeprecateCourseCommand, DeprecateCourseResult,
    ChangeCoursePolicyCommand, ChangeCoursePolicyResult
)

@pytest.fixture
def course_repo():
    return Mock()

@pytest.fixture
def policy_repo():
    return Mock()

@pytest.fixture
def event_bus():
    return Mock()

@pytest.fixture
def service(course_repo, policy_repo, event_bus):
    return CourseApplicationService(course_repo, policy_repo, event_bus)

# --- Create ---
def test_create_course_happy(service, course_repo, policy_repo, event_bus):
    policy_repo.get_by_id.return_value = Mock(id="p1")
    course_repo.find_by_title.return_value = None
    course = Mock(id="c1", status="ACTIVE")
    service._create_course_aggregate = lambda p, cmd: course
    cmd = CreateCourseCommand(title="Math", description="desc", policy_id="p1")
    result = service.create_course(cmd)
    assert isinstance(result, CreateCourseResult)
    assert result.course_id == "c1"
    assert result.status == "ACTIVE"
    course_repo.save.assert_called_once_with(course)
    event_bus.publish.assert_called()

def test_create_course_already_exists(service, course_repo):
    course_repo.find_by_title.return_value = Mock(id="cX")
    cmd = CreateCourseCommand(title="Math", description="desc", policy_id="p2")
    with pytest.raises(ValueError):
        service.create_course(cmd)

def test_create_course_policy_not_found(service, course_repo, policy_repo):
    policy_repo.get_by_id.return_value = None
    course_repo.find_by_title.return_value = None
    cmd = CreateCourseCommand(title="Physics", description="sc", policy_id="bad")
    with pytest.raises(ValueError):
        service.create_course(cmd)

# --- Update ---
def test_update_course_happy(service, course_repo, event_bus):
    course = Mock(id="c3", status="ACTIVE")
    course_repo.get_by_id.return_value = course
    service._update_course_aggregate = lambda c, cmd: ("UPDATED", "done")
    cmd = UpdateCourseCommand(course_id="c3", title="New", description="d")
    result = service.update_course(cmd)
    assert isinstance(result, UpdateCourseResult)
    assert result.course_id == "c3"
    course_repo.save.assert_called_with(course)
    event_bus.publish.assert_called()

def test_update_course_not_found(service, course_repo):
    course_repo.get_by_id.return_value = None
    cmd = UpdateCourseCommand(course_id="bad", title="x")
    with pytest.raises(ValueError):
        service.update_course(cmd)

# --- Deprecate ---
def test_deprecate_course_happy(service, course_repo, event_bus):
    course = Mock(id="c5", status="ACTIVE")
    course_repo.get_by_id.return_value = course
    service._deprecate_course_aggregate = lambda c, cmd: ("DEPRECATED", "gone")
    cmd = DeprecateCourseCommand(course_id="c5")
    result = service.deprecate_course(cmd)
    assert isinstance(result, DeprecateCourseResult)
    assert result.status == "DEPRECATED"
    course_repo.save.assert_called_with(course)
    event_bus.publish.assert_called()

def test_deprecate_course_not_found(service, course_repo):
    course_repo.get_by_id.return_value = None
    cmd = DeprecateCourseCommand(course_id="bad")
    with pytest.raises(ValueError):
        service.deprecate_course(cmd)

def test_deprecate_course_already_deprecated(service, course_repo):
    course = Mock(id="c6", status="DEPRECATED")
    course_repo.get_by_id.return_value = course
    service._deprecate_course_aggregate = lambda c, cmd: ("DEPRECATED", "already")
    cmd = DeprecateCourseCommand(course_id="c6")
    with pytest.raises(ValueError):
        service.deprecate_course(cmd)

# --- Change Policy ---
def test_change_policy_happy(service, course_repo, policy_repo, event_bus):
    course = Mock(id="c7", status="ACTIVE")
    course_repo.get_by_id.return_value = course
    policy_repo.get_by_id.return_value = Mock(id="p7")
    service._change_policy_aggregate = lambda c, p, cmd: ("POLICY_CHANGED", "ok")
    cmd = ChangeCoursePolicyCommand(course_id="c7", new_policy_id="p7")
    result = service.change_policy(cmd)
    assert isinstance(result, ChangeCoursePolicyResult)
    assert result.status == "POLICY_CHANGED"
    course_repo.save.assert_called_with(course)
    event_bus.publish.assert_called()

def test_change_policy_course_not_found(service, course_repo, policy_repo):
    course_repo.get_by_id.return_value = None
    policy_repo.get_by_id.return_value = Mock(id="p8")
    cmd = ChangeCoursePolicyCommand(course_id="bad", new_policy_id="p8")
    with pytest.raises(ValueError):
        service.change_policy(cmd)

def test_change_policy_policy_not_found(service, course_repo, policy_repo):
    course = Mock(id="c9", status="ACTIVE")
    course_repo.get_by_id.return_value = course
    policy_repo.get_by_id.return_value = None
    cmd = ChangeCoursePolicyCommand(course_id="c9", new_policy_id="bad")
    with pytest.raises(ValueError):
        service.change_policy(cmd)
