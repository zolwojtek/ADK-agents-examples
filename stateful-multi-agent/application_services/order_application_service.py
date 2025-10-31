from dataclasses import dataclass
from typing import List, Optional, Any
from datetime import datetime

# --- Command/DTOs ---
@dataclass
class PlaceOrderCommand:
    user_id: str
    course_ids: List[str]
    total_amount: float
    payment_info: Any  # For real: would be a concrete DTO

@dataclass
class PlaceOrderResult:
    order_id: str
    status: str
    message: Optional[str] = None

@dataclass
class RequestRefundCommand:
    order_id: str
    refund_reason: str

@dataclass
class RefundResult:
    order_id: str
    status: str
    message: Optional[str] = None

@dataclass
class CancelOrderCommand:
    order_id: str

@dataclass
class CancelOrderResult:
    order_id: str
    status: str
    message: Optional[str] = None

class _V:
    def __init__(self, value):
        self.value = value

class _E:
    def __init__(self, event_type: str, **kwargs):
        self.__event_type__ = event_type
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'occurred_on'):
            self.occurred_on = datetime.now()

# --- Application Service Scaffold ---
class OrderApplicationService:
    def __init__(self, order_repo, user_repo, course_repo, event_bus):
        self.order_repo = order_repo
        self.user_repo = user_repo
        self.course_repo = course_repo
        self.event_bus = event_bus

    def place_order(self, cmd: PlaceOrderCommand) -> PlaceOrderResult:
        """Validate input, check user and courses, orchestrate order creation, save and emit event."""
        user = self.user_repo.get_by_id(cmd.user_id)
        if not user:
            raise ValueError("User not found")
        courses = self.course_repo.get_by_ids(cmd.course_ids)
        if not courses or len(courses) < len(cmd.course_ids):
            raise ValueError("One or more courses not found")
        # Domain orchestration stub (use mock in tests or replace in prod)
        order = getattr(self, '_create_order_aggregate', None)
        if order:
            order = order(user, courses, cmd)
        else:
            raise NotImplementedError("Order aggregate creation not implemented")
        self.order_repo.save(order)
        # Publish OrderPlaced to projections
        ev = _E(
            'OrderPlaced',
            order_id=_V(order.id), user_id=_V(cmd.user_id),
            course_ids=[_V(cid) for cid in cmd.course_ids], total_amount=cmd.total_amount,
        )
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return PlaceOrderResult(order_id=order.id, status=order.status)

    def request_refund(self, cmd: RequestRefundCommand) -> RefundResult:
        """Orchestrate refund request, validate order and eligibility, save and emit event."""
        order = self.order_repo.get_by_id(cmd.order_id)
        if not order:
            raise ValueError("Order not found")
        if not getattr(order, 'can_be_refunded', lambda: False)():
            raise ValueError("Refund not eligible for this order")
        # Domain stub
        proc = getattr(self, '_process_refund', None)
        if proc:
            status, msg = proc(order, cmd)
        else:
            status, msg = ("REFUND_REQUESTED", "Stub")
        self.order_repo.save(order)
        ev = _E('OrderRefundRequested', order_id=_V(cmd.order_id), refund_reason=cmd.refund_reason)
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return RefundResult(order_id=order.id, status=status, message=msg)

    def cancel_order(self, cmd: CancelOrderCommand) -> CancelOrderResult:
        """Orchestrate order cancellation. Validate order and guard against double-cancel."""
        order = self.order_repo.get_by_id(cmd.order_id)
        if not order:
            raise ValueError("Order not found")
        if getattr(order, 'status', None) == "CANCELLED":
            raise ValueError("Order already cancelled")
        # Domain stub
        cancel = getattr(self, '_cancel_order_aggregate', None)
        if cancel:
            status, msg = cancel(order)
        else:
            status, msg = ("CANCELLED", "Stub")
        self.order_repo.save(order)
        ev = _E('OrderCancelled', order_id=_V(cmd.order_id))
        self.event_bus.publish(ev)
        self.event_bus.publish_sync(ev)
        return CancelOrderResult(order_id=order.id, status=status, message=msg)
