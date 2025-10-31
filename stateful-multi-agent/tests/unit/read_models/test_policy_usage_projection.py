import pytest
from read_models.policy_usage_projection import PolicyUsageProjection

class Dummy:
    def __init__(self, value):
        self.value = value

class DummyEvent:
    def __init__(self, __event_type__, **kwargs):
        self.__event_type__ = __event_type__
        self.__dict__.update(kwargs)

@pytest.fixture
def proj():
    return PolicyUsageProjection()

@pytest.fixture
def policy_created():
    return DummyEvent(
        "PolicyCreated",
        policy_id=Dummy("p1"),
        policy_type=Dummy("standard"),
        refund_period_days=30,
        name=Dummy("Refund Standard Policy")
    )

@pytest.fixture
def policy2_created():
    return DummyEvent(
        "PolicyCreated",
        policy_id=Dummy("p2"),
        policy_type=Dummy("strict"),
        refund_period_days=7,
        name=Dummy("No-Refund Policy")
    )

@pytest.fixture
def policy_updated():
    return DummyEvent(
        "PolicyUpdated",
        policy_id=Dummy("p1"),
        policy_type=Dummy("extended"),
        refund_period_days=60,
        name=Dummy("Returned Extended"),
        status="active"
    )

@pytest.fixture
def policy_deprecated():
    return DummyEvent(
        "PolicyUpdated",
        policy_id=Dummy("p1"),
        status="deprecated"
    )

@pytest.fixture
def policy_reactivated():
    return DummyEvent(
        "PolicyUpdated",
        policy_id=Dummy("p1"),
        status="active"
    )

@pytest.fixture
def course_policy_changed():
    return DummyEvent(
        "CoursePolicyChanged",
        course_id=Dummy("c1"),
        old_policy_id=Dummy("p1"),
        new_policy_id=Dummy("p2")
    )

@pytest.fixture
def course_policy_set2():
    return DummyEvent(
        "CoursePolicyChanged",
        course_id=Dummy("c2"),
        old_policy_id=Dummy("p2"),
        new_policy_id=Dummy("p1")
    )

def test_policy_created_basic(proj, policy_created):
    proj.handle(policy_created)
    out = proj.get_policy("p1")
    assert out['policy_id'] == "p1"
    assert out['type'] == "standard"
    assert out['refund_period_days'] == 30
    assert out['name'] == "Refund Standard Policy"
    assert out['status'] == 'active'
    assert out['adoption_count'] == 0
    assert out['courses_using'] == []

def test_policy_updated(proj, policy_created, policy_updated):
    proj.handle(policy_created)
    proj.handle(policy_updated)
    out = proj.get_policy("p1")
    assert out['type'] == "extended"
    assert out['refund_period_days'] == 60
    assert out['name'] == "Returned Extended"
    assert out['status'] == "active"

def test_policy_deprecate_reactivate(proj, policy_created, policy_updated, policy_deprecated, policy_reactivated):
    proj.handle(policy_created)
    proj.handle(policy_updated)
    proj.handle(policy_deprecated)
    out = proj.get_policy("p1")
    assert out['status'] == 'deprecated'
    proj.handle(policy_reactivated)
    out = proj.get_policy("p1")
    assert out['status'] == 'active'

def test_course_policy_changed(proj, policy_created, policy2_created, course_policy_changed):
    proj.handle(policy_created)
    proj.handle(policy2_created)
    proj.handle(course_policy_changed)
    p1 = proj.get_policy("p1")
    p2 = proj.get_policy("p2")
    # c1 removed from p1 and added to p2
    assert p1['adoption_count'] == 0
    assert p1['courses_using'] == []
    assert p2['adoption_count'] == 1
    assert p2['courses_using'] == ["c1"]

def test_multiple_policy_assignments(proj, policy_created, policy2_created, course_policy_changed, course_policy_set2):
    proj.handle(policy_created)
    proj.handle(policy2_created)
    # c1 -> p2
    proj.handle(course_policy_changed)
    # c2 -> p1 (from p2)
    proj.handle(course_policy_set2)
    p1 = proj.get_policy("p1")
    p2 = proj.get_policy("p2")
    assert p1['adoption_count'] == 1
    assert p1['courses_using'] == ["c2"]
    assert p2['adoption_count'] == 1
    assert p2['courses_using'] == ["c1"]

def test_policy_not_found(proj):
    assert proj.get_policy("nope") is None
    assert proj.get_all() == {}

def test_get_all(proj, policy_created, policy2_created, course_policy_changed, course_policy_set2):
    proj.handle(policy_created)
    proj.handle(policy2_created)
    proj.handle(course_policy_changed)
    proj.handle(course_policy_set2)
    allp = proj.get_all()
    assert set(allp.keys()) == {"p1", "p2"}
    assert allp['p1']['adoption_count'] == 1
    assert allp['p2']['adoption_count'] == 1
