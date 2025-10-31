import pytest
from datetime import datetime, timedelta
from read_models.order_history_projection import OrderHistoryProjection

class Dummy:
    def __init__(self, value):
        self.value = value

class DummyEvent:
    def __init__(self, __event_type__, **kwargs):
        self.__event_type__ = __event_type__
        self.__dict__.update(kwargs)

@pytest.fixture
def now():
    return datetime.now()

@pytest.fixture
def proj():
    return OrderHistoryProjection()

@pytest.fixture
def order_id():
    return "o1"

@pytest.fixture
def user_id():
    return "u1"

@pytest.fixture
def placed(now, order_id, user_id):
    return DummyEvent(
        "OrderPlaced",
        order_id=Dummy(order_id),
        user_id=Dummy(user_id),
        course_ids=[Dummy("c1"), Dummy("c2")],
        total_amount=133.7,
        occurred_on=now,
    )

@pytest.fixture
def paid(now, order_id):
    return DummyEvent(
        "OrderPaid",
        order_id=Dummy(order_id),
        payment_id="payment-x",
        occurred_on=now + timedelta(minutes=1),
    )

@pytest.fixture
def refund_requested(now, order_id):
    return DummyEvent(
        "OrderRefundRequested",
        order_id=Dummy(order_id),
        refund_reason="wrong course",
        occurred_on=now + timedelta(minutes=2),
    )

@pytest.fixture
def refunded(now, order_id):
    return DummyEvent(
        "OrderRefunded",
        order_id=Dummy(order_id),
        refund_amount=133.7,
        occurred_on=now + timedelta(minutes=3),
    )

@pytest.fixture
def cancelled(now, order_id):
    return DummyEvent(
        "OrderCancelled",
        order_id=Dummy(order_id),
        occurred_on=now + timedelta(minutes=4),
    )

@pytest.fixture
def payment_failed(now, order_id):
    return DummyEvent(
        "OrderPaymentFailed",
        order_id=Dummy(order_id),
        reason="credit card error",
        occurred_on=now + timedelta(minutes=5),
    )

def test_order_placed(proj, placed, user_id, order_id):
    proj.handle(placed)
    res = proj.get_orders_for_user(user_id)
    assert len(res) == 1
    assert res[0]['order_id'] == order_id
    assert res[0]['user_id'] == user_id
    assert res[0]['status'] == 'PLACED'
    assert res[0]['course_ids'] == ['c1', 'c2']
    assert res[0]['total_amount'] == 133.7
    out = proj.get_order(order_id)
    assert out['order_id'] == order_id

def test_order_paid(proj, placed, paid, user_id, order_id):
    proj.handle(placed)
    proj.handle(paid)
    out = proj.get_order(order_id)
    assert out['status'] == 'PAID'
    assert out['payment_id'] == 'payment-x'
    assert 'paid_at' in out

def test_refund_requested_and_refunded(proj, placed, paid, refund_requested, refunded, order_id):
    proj.handle(placed)
    proj.handle(paid)
    proj.handle(refund_requested)
    o = proj.get_order(order_id)
    assert o['status'] == 'REFUND_REQUESTED'
    assert o['refund_reason'] == 'wrong course'
    assert 'refund_requested_at' in o
    # now refunded
    proj.handle(refunded)
    o2 = proj.get_order(order_id)
    assert o2['status'] == 'REFUNDED'
    assert o2['refund_amount'] == 133.7
    assert 'refunded_at' in o2

def test_cancelled(proj, placed, cancelled, order_id):
    proj.handle(placed)
    proj.handle(cancelled)
    out = proj.get_order(order_id)
    assert out['status'] == 'CANCELLED'
    assert 'cancelled_at' in out

def test_payment_failed(proj, placed, payment_failed, order_id):
    proj.handle(placed)
    proj.handle(payment_failed)
    out = proj.get_order(order_id)
    assert out['status'] == 'PAYMENT_FAILED'
    assert out['failed_reason'] == 'credit card error'
    assert 'failed_at' in out

def test_full_sequence(proj, placed, paid, refund_requested, refunded, cancelled, payment_failed, order_id, user_id):
    # Place
    proj.handle(placed)
    assert proj.get_order(order_id)['status'] == 'PLACED'
    # Pay
    proj.handle(paid)
    assert proj.get_order(order_id)['status'] == 'PAID'
    # Refund requested
    proj.handle(refund_requested)
    assert proj.get_order(order_id)['status'] == 'REFUND_REQUESTED'
    # Refunded
    proj.handle(refunded)
    assert proj.get_order(order_id)['status'] == 'REFUNDED'
    # Now cancel (should be possible in theory, test last-event-wins logic)
    proj.handle(cancelled)
    assert proj.get_order(order_id)['status'] == 'CANCELLED'
    # Now payment failed (should also overwrite status)
    proj.handle(payment_failed)
    assert proj.get_order(order_id)['status'] == 'PAYMENT_FAILED'
    # Events history remains sequential
    assert len(proj.get_order(order_id)['events']) == 6
    # User query
    user_orders = proj.get_orders_for_user(user_id)
    assert any(o['order_id'] == order_id for o in user_orders)

def test_order_not_found(proj):
    assert proj.get_order('zzz') is None
    assert proj.get_orders_for_user('nobody') == []

def test_duplicate_placement(proj, placed, order_id, user_id):
    proj.handle(placed)
    proj.handle(placed)  # Should result in duplicate in user_orders for demo; order_id unique
    assert len(proj.get_orders_for_user(user_id)) == 2
    # But .orders dict only holds latest
    assert len(proj.orders) == 1
    assert proj.get_order(order_id)['order_id'] == order_id
