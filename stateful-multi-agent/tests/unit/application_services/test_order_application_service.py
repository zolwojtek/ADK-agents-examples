import pytest
from unittest.mock import Mock, call
from application_services.order_application_service import (
    OrderApplicationService, PlaceOrderCommand, RequestRefundCommand, CancelOrderCommand,
    PlaceOrderResult, RefundResult, CancelOrderResult
)

@pytest.fixture
def order_repo():
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
def service(order_repo, user_repo, course_repo, event_bus):
    return OrderApplicationService(order_repo, user_repo, course_repo, event_bus)

# --- Place Order ---
def test_place_order_happy_path(service, order_repo, user_repo, course_repo, event_bus):
    # Arrange
    user_repo.get_by_id.return_value = Mock(id="u1")
    course_repo.get_by_ids.return_value = [Mock(id="c1"), Mock(id="c2")]
    order_aggregate = Mock(id="order-123", status="PAID")
    order_repo.save.return_value = order_aggregate
    cmd = PlaceOrderCommand(user_id="u1", course_ids=["c1", "c2"], total_amount=120, payment_info={})
    # Patch actual domain orchestration path
    service._create_order_aggregate = lambda *a, **kw: order_aggregate
    # Act
    result = service.place_order(cmd)
    # Assert
    assert isinstance(result, PlaceOrderResult)
    assert result.status == order_aggregate.status
    assert result.order_id == order_aggregate.id
    order_repo.save.assert_called_once_with(order_aggregate)
    event_bus.publish.assert_called()

# --- Place Order errors ---
def test_place_order_user_not_found(service, user_repo):
    user_repo.get_by_id.return_value = None
    cmd = PlaceOrderCommand(user_id="u_x", course_ids=["c1"], total_amount=12, payment_info={})
    with pytest.raises(ValueError):
        service.place_order(cmd)

def test_place_order_course_not_found(service, user_repo, course_repo):
    user_repo.get_by_id.return_value = Mock(id="u1")
    course_repo.get_by_ids.return_value = []
    cmd = PlaceOrderCommand(user_id="u1", course_ids=["c99"], total_amount=122, payment_info={})
    with pytest.raises(ValueError):
        service.place_order(cmd)

# --- Refund ---
def test_request_refund_happy_path(service, order_repo, event_bus):
    order = Mock(id="o1", status="PAID")
    order_repo.get_by_id.return_value = order
    cmd = RequestRefundCommand(order_id="o1", refund_reason="Too hard")
    # Patch domain logic
    order.can_be_refunded.return_value = True
    service._process_refund = lambda o, c: ("REFUND_REQUESTED", "ok")
    result = service.request_refund(cmd)
    assert isinstance(result, RefundResult)
    assert result.order_id == "o1"
    assert result.status == "REFUND_REQUESTED"
    order_repo.save.assert_called_with(order)
    event_bus.publish.assert_called()

def test_request_refund_order_not_found(service, order_repo):
    order_repo.get_by_id.return_value = None
    cmd = RequestRefundCommand(order_id="bad", refund_reason="Fraud")
    with pytest.raises(ValueError):
        service.request_refund(cmd)

def test_request_refund_not_eligible(service, order_repo):
    order = Mock(id="o2", status="REFUND_REQUESTED")
    order_repo.get_by_id.return_value = order
    order.can_be_refunded.return_value = False
    cmd = RequestRefundCommand(order_id="o2", refund_reason="Already refunded")
    with pytest.raises(ValueError):
        service.request_refund(cmd)

# --- Cancel Order ---
def test_cancel_order_happy_path(service, order_repo, event_bus):
    order = Mock(id="o3", status="PAID")
    order_repo.get_by_id.return_value = order
    service._cancel_order_aggregate = lambda o: ("CANCELLED", "done")
    cmd = CancelOrderCommand(order_id="o3")
    result = service.cancel_order(cmd)
    assert isinstance(result, CancelOrderResult)
    assert result.status == "CANCELLED"
    order_repo.save.assert_called_with(order)
    event_bus.publish.assert_called()

def test_cancel_order_not_found(service, order_repo):
    order_repo.get_by_id.return_value = None
    cmd = CancelOrderCommand(order_id="bad")
    with pytest.raises(ValueError):
        service.cancel_order(cmd)

def test_cancel_order_already_cancelled(service, order_repo):
    order = Mock(id="o4", status="CANCELLED")
    order_repo.get_by_id.return_value = order
    service._cancel_order_aggregate = lambda o: ("CANCELLED", "already")
    cmd = CancelOrderCommand(order_id="o4")
    with pytest.raises(ValueError):
        service.cancel_order(cmd)
