import pytest
from datetime import datetime, timedelta
from read_models.user_access_projection import UserAccessProjection
from domain.access.events import CourseAccessGranted, AccessRevoked, AccessExpired, ProgressUpdated, CourseCompleted
from domain.shared.value_objects import AccessId, UserId, CourseId, Progress

@pytest.fixture
def now():
    return datetime.now()

@pytest.fixture
def projection():
    return UserAccessProjection()

@pytest.fixture
def access_granted_event(now):
    return CourseAccessGranted(
        event_id="e1",
        occurred_on=now,
        aggregate_type="AccessRecord",
        aggregate_id="a1",
        access_id=AccessId("a1"),
        user_id=UserId("u1"),
        course_id=CourseId("c1")
    )

@pytest.fixture
def progress_updated_event(now):
    return ProgressUpdated(
        event_id="e2",
        occurred_on=now,
        aggregate_type="AccessRecord",
        aggregate_id="a1",
        access_id=AccessId("a1"),
        user_id=UserId("u1"),
        course_id=CourseId("c1"),
        progress=Progress(30.0)
    )

@pytest.fixture
def course_completed_event(now):
    return CourseCompleted(
        event_id="e3",
        occurred_on=now,
        aggregate_type="AccessRecord",
        aggregate_id="a1",
        access_id=AccessId("a1"),
        user_id=UserId("u1"),
        course_id=CourseId("c1")
    )

@pytest.fixture
def access_revoked_event(now):
    return AccessRevoked(
        event_id="e4",
        occurred_on=now,
        aggregate_type="AccessRecord",
        aggregate_id="a1",
        access_id=AccessId("a1"),
        user_id=UserId("u1"),
        course_id=CourseId("c1"),
        reason="user requested"
    )

@pytest.fixture
def access_expired_event(now):
    return AccessExpired(
        event_id="e5",
        occurred_on=now,
        aggregate_type="AccessRecord",
        aggregate_id="a1",
        access_id=AccessId("a1"),
        user_id=UserId("u1"),
        course_id=CourseId("c1"),
        expired_at=now + timedelta(days=90)
    )

def test_access_granted(projection, access_granted_event):
    projection.handle(access_granted_event)
    out = projection.get_user_access("u1")
    assert out['courses'][0]['course_id'] == "c1"
    assert out['courses'][0]['status'] == 'active'
    assert out['courses'][0]['progress'] == 0.0
    assert out['last_activity']

def test_duplicate_access_granted(projection, access_granted_event):
    projection.handle(access_granted_event)
    projection.handle(access_granted_event)
    out = projection.get_user_access("u1")
    assert len(out['courses']) == 1  # No duplicate

def test_progress_updated(projection, access_granted_event, progress_updated_event):
    projection.handle(access_granted_event)
    projection.handle(progress_updated_event)
    out = projection.get_user_access("u1")
    assert out['courses'][0]['progress'] == 30.0
    assert out['last_activity']
    
def test_progress_update_nonexistent_access(projection, progress_updated_event):
    projection.handle(progress_updated_event)  # No error, silently ignored
    out = projection.get_user_access("u1")
    assert out['courses'] == []

def test_course_completed(projection, access_granted_event, course_completed_event):
    projection.handle(access_granted_event)
    projection.handle(course_completed_event)
    out = projection.get_user_access("u1")
    assert out['courses'][0]['progress'] == 100.0
    assert out['courses'][0]['status'] == 'completed'

def test_access_revoked(projection, access_granted_event, access_revoked_event):
    projection.handle(access_granted_event)
    projection.handle(access_revoked_event)
    out = projection.get_user_access("u1")
    assert out['courses'][0]['status'] == 'revoked'

def test_access_expired(projection, access_granted_event, access_expired_event):
    projection.handle(access_granted_event)
    projection.handle(access_expired_event)
    out = projection.get_user_access("u1")
    assert out['courses'][0]['status'] == 'expired'
    assert out['courses'][0]['expires_at']

def test_multiple_events_sequential(projection, access_granted_event, progress_updated_event, course_completed_event, access_expired_event, access_revoked_event):
    projection.handle(access_granted_event)
    projection.handle(progress_updated_event)
    projection.handle(course_completed_event)
    projection.handle(access_expired_event)
    projection.handle(access_revoked_event)
    out = projection.get_user_access("u1")
    c = out['courses'][0]
    # Status most recently updated by revoke event
    assert c['status'] == 'revoked'
    # Progress remains 100 if completed before revoke
    assert c['progress'] == 100.0

def test_get_user_access_unknown_user(projection):
    out = projection.get_user_access("unknown")
    assert out['courses'] == []
    assert out['last_activity'] is None

def test_get_all_returns_copy(projection, access_granted_event):
    projection.handle(access_granted_event)
    allproj = projection.get_all()
    assert allproj["u1"]['courses'][0]['course_id'] == "c1"
    assert isinstance(allproj, dict)
