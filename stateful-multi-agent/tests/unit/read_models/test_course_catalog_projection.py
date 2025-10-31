import pytest
from datetime import datetime
from read_models.course_catalog_projection import CourseCatalogProjection

class DummyEvent:
    def __init__(self, __event_type__, **kwargs):
        self.__event_type__ = __event_type__
        self.__dict__.update(kwargs)
    def __repr__(self):
        return f"DummyEvent({self.__event_type__}, {self.__dict__})"

@pytest.fixture
def now():
    return datetime.now()

@pytest.fixture
def projection():
    return CourseCatalogProjection()

@pytest.fixture
def course_created_event(now):
    return DummyEvent(
        "CourseCreated",
        event_id="e1",
        occurred_on=now,
        aggregate_type="Course",
        aggregate_id="c1",
        course_id=type('CID', (), {'value': 'c1'})(),
        title=type('T', (), {'value': 'Course 1'})(),
        description=type('D', (), {'value': 'A great course.'})(),
        policy_id=type('PID', (), {'value': 'p1'})(),
        price=100,
        instructor_id="instructor_1"
    )

@pytest.fixture
def course_updated_event(now):
    return DummyEvent(
        "CourseUpdated",
        event_id="e2",
        occurred_on=now,
        aggregate_type="Course",
        aggregate_id="c1",
        course_id=type('CID', (), {'value': 'c1'})(),
        title=type('T', (), {'value': 'Course 1 - Updated'})(),
        description=type('D', (), {'value': 'New description!'})()
    )

@pytest.fixture
def policy_changed_event(now):
    return DummyEvent(
        "CoursePolicyChanged",
        event_id="e3",
        occurred_on=now,
        aggregate_type="Course",
        aggregate_id="c1",
        course_id=type('CID', (), {'value': 'c1'})(),
        old_policy_id=type('PID', (), {'value': 'p1'})(),
        new_policy_id=type('PID', (), {'value': 'p2'})()
    )

@pytest.fixture
def policy_updated_event(now):
    return DummyEvent(
        "PolicyUpdated",
        event_id="e4",
        occurred_on=now,
        aggregate_type="RefundPolicy",
        aggregate_id="p2",
        policy_id=type('PID', (), {'value': 'p2'})(),
        policy_type=type('PT', (), {'value': 'extended'})(),
        refund_period_days=60
    )

@pytest.fixture
def policy_deprecated_event(now):
    return DummyEvent(
        "PolicyUpdated",
        event_id="e5",
        occurred_on=now,
        aggregate_type="RefundPolicy",
        aggregate_id="p2",
        policy_id=type('PID', (), {'value': 'p2'})(),
        status='deprecated'
    )

def test_initial_empty(projection):
    assert projection.get_all() == {}
    assert projection.get_course("nonexistent") is None

def test_course_created(projection, course_created_event):
    projection.handle(course_created_event)
    out = projection.get_course("c1")
    assert out['title'] == "Course 1"
    assert out['description'] == "A great course."
    assert out['price'] == 100
    assert out['policy']['policy_id'] == "p1"
    assert out['status'] == 'active'

def test_course_updated(projection, course_created_event, course_updated_event):
    projection.handle(course_created_event)
    projection.handle(course_updated_event)
    out = projection.get_course("c1")
    assert out['title'] == "Course 1 - Updated"
    assert out['description'] == "New description!"

def test_policy_changed(projection, course_created_event, policy_changed_event):
    projection.handle(course_created_event)
    projection.handle(policy_changed_event)
    out = projection.get_course("c1")
    assert out['policy']['policy_id'] == "p2"
    assert out['policy']['type'] is None
    assert out['policy']['refund_period_days'] is None

def test_policy_updated(projection, course_created_event, policy_changed_event, policy_updated_event):
    projection.handle(course_created_event)
    projection.handle(policy_changed_event)
    projection.handle(policy_updated_event)
    out = projection.get_course("c1")
    assert out['policy']['policy_id'] == "p2"
    assert out['policy']['type'] == "extended"
    assert out['policy']['refund_period_days'] == 60

def test_policy_deprecated(projection, course_created_event, policy_changed_event, policy_updated_event, policy_deprecated_event):
    projection.handle(course_created_event)
    projection.handle(policy_changed_event)
    projection.handle(policy_updated_event)
    projection.handle(policy_deprecated_event)
    out = projection.get_course("c1")
    assert out['status'] == 'deprecated'

def test_all_and_get(projection, course_created_event):
    projection.handle(course_created_event)
    allproj = projection.get_all()
    assert "c1" in allproj
    assert allproj["c1"]['title'] == "Course 1"
