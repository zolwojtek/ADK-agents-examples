import pytest
from datetime import datetime, timedelta, date
from read_models.revenue_summary_projection import RevenueSummaryProjection

class DummyEvent:
    def __init__(self, __event_type__, occurred_on, **kwargs):
        self.__event_type__ = __event_type__
        self.occurred_on = occurred_on
        self.__dict__.update(kwargs)

@pytest.fixture
def now():
    return datetime(2025, 10, 30, 12, 0, 0)

@pytest.fixture
def proj():
    return RevenueSummaryProjection()

def test_empty(proj):
    assert proj.get_total()['paid'] == 0.0
    assert proj.get_by_day(date(2023,1,1))['paid'] == 0.0
    assert proj.get_by_month('2025-10')['orders'] == 0
    assert proj.get_by_week('2025-W44')['orders'] == 0

def test_single_payment(proj, now):
    e = DummyEvent("OrderPaid", now, amount=100)
    proj.handle(e)
    out = proj.get_total()
    assert out['paid'] == 100.0
    assert out['net'] == 100.0
    assert out['orders'] == 1
    # By day, month, week
    by_day = proj.get_by_day(now.date())
    assert by_day['paid'] == 100.0
    assert by_day['orders'] == 1
    by_month = proj.get_by_month('2025-10')
    assert by_month['paid'] == 100.0
    assert by_month['orders'] == 1
    by_week = proj.get_by_week('2025-W44')
    assert by_week['orders'] == 1

def test_multiple_payments_refunds(proj, now):
    e1 = DummyEvent("OrderPaid", now, amount=200)
    e2 = DummyEvent("OrderPaid", now + timedelta(days=1), amount=150)
    e3 = DummyEvent("OrderRefunded", now + timedelta(days=1), refund_amount=50)
    e4 = DummyEvent("OrderPaid", now + timedelta(days=30), amount=60)
    e5 = DummyEvent("OrderRefunded", now + timedelta(days=30), amount=30)
    for e in [e1, e2, e3, e4, e5]:
        proj.handle(e)
    # Totals
    t = proj.get_total()
    assert t['paid'] == 410.0
    assert t['refunded'] == 80.0
    assert t['net'] == 330.0
    assert t['orders'] == 3
    assert t['refunds'] == 2
    # By day
    d0 = proj.get_by_day(now.date())
    assert d0['paid'] == 200.0
    d1 = proj.get_by_day((now + timedelta(days=1)).date())
    assert d1['paid'] == 150.0
    assert d1['refunded'] == 50.0
    d2 = proj.get_by_day((now + timedelta(days=30)).date())
    assert d2['paid'] == 60.0
    assert d2['refunded'] == 30.0
    # By month
    m1 = proj.get_by_month('2025-10')
    assert m1['paid'] == 350.0
    m2 = proj.get_by_month('2025-11')
    assert m2['paid'] == 60.0
    assert m2['refunded'] == 30.0
    # By week
    w1 = proj.get_by_week('2025-W44')
    w2 = proj.get_by_week('2025-W48')
    assert w1['paid'] >= 200.0  # some in first week
    assert w2['paid'] == 60.0
    assert w2['refunds'] == 1

def test_refund_without_payment(proj, now):
    e1 = DummyEvent("OrderRefunded", now, refund_amount=50)
    proj.handle(e1)
    t = proj.get_total()
    assert t['refunded'] == 50.0
    assert t['net'] == -50.0
    assert t['refunds'] == 1
    # Also check by period
    by_day = proj.get_by_day(now.date())
    assert by_day['refunded'] == 50.0
    assert by_day['net'] == -50.0

# Edge: negative and missing amounts

def test_negative_and_missing(proj, now):
    e1 = DummyEvent("OrderPaid", now, amount=-20)
    e2 = DummyEvent("OrderPaid", now, )  # no amount, should use 0
    e3 = DummyEvent("OrderRefunded", now, ) # No amount/refund_amount
    for e in [e1, e2, e3]:
        proj.handle(e)
    t = proj.get_total()
    assert t['paid'] == -20.0
    assert t['orders'] == 2
    assert t['refunded'] == 0.0
    assert t['refunds'] == 1
    assert t['net'] == -20.0
