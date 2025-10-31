from typing import Dict, Any, List

class OrderHistoryProjection:
    """
    Read model: maintains order history per user, reflecting all order lifecycle events.
    Denormalized structure allows rapid queries by user or order.
    """
    def __init__(self):
        # user_id -> List[order dicts]
        self.user_orders: Dict[str, List[Dict[str, Any]]] = {}
        # order_id -> order dict
        self.orders: Dict[str, Dict[str, Any]] = {}

    def handle(self, event: Any) -> None:
        event_type = getattr(event, "__event_type__", event.__class__.__name__)
        if event_type == "OrderPlaced":
            self._on_placed(event)
        elif event_type == "OrderPaid":
            self._on_paid(event)
        elif event_type == "OrderRefundRequested":
            self._on_refund_requested(event)
        elif event_type == "OrderRefunded":
            self._on_refunded(event)
        elif event_type == "OrderCancelled":
            self._on_cancelled(event)
        elif event_type == "OrderPaymentFailed":
            self._on_payment_failed(event)

    def _on_placed(self, event):
        order_id = event.order_id.value
        user_id = event.user_id.value
        courses = [c.value for c in getattr(event, "course_ids", []) or []]
        total_amount = getattr(event, "total_amount", None)
        placed_at = event.occurred_on
        order = {
            "order_id": order_id,
            "user_id": user_id,
            "placed_at": placed_at,
            "course_ids": courses,
            "total_amount": total_amount,
            "status": "PLACED",
            "events": [
                {"event_type": "OrderPlaced", "date": placed_at}
            ],
        }
        self.orders[order_id] = order
        if user_id not in self.user_orders:
            self.user_orders[user_id] = []
        self.user_orders[user_id].append(order)

    def _on_paid(self, event):
        order_id = event.order_id.value
        order = self.orders.get(order_id)
        if order:
            order["status"] = "PAID"
            order["payment_id"] = getattr(event, "payment_id", None)
            order["paid_at"] = event.occurred_on
            order["events"].append({"event_type": "OrderPaid", "date": event.occurred_on})

    def _on_refund_requested(self, event):
        order_id = event.order_id.value
        order = self.orders.get(order_id)
        if order:
            order["status"] = "REFUND_REQUESTED"
            order["refund_reason"] = getattr(event, "refund_reason", None)
            order["refund_requested_at"] = event.occurred_on
            order["events"].append({"event_type": "OrderRefundRequested", "date": event.occurred_on})

    def _on_refunded(self, event):
        order_id = event.order_id.value
        order = self.orders.get(order_id)
        if order:
            order["status"] = "REFUNDED"
            order["refund_amount"] = getattr(event, "refund_amount", None)
            order["refunded_at"] = event.occurred_on
            order["events"].append({"event_type": "OrderRefunded", "date": event.occurred_on})

    def _on_cancelled(self, event):
        order_id = event.order_id.value
        order = self.orders.get(order_id)
        if order:
            order["status"] = "CANCELLED"
            order["cancelled_at"] = event.occurred_on
            order["events"].append({"event_type": "OrderCancelled", "date": event.occurred_on})

    def _on_payment_failed(self, event):
        order_id = event.order_id.value
        order = self.orders.get(order_id)
        if order:
            order["status"] = "PAYMENT_FAILED"
            order["failed_reason"] = getattr(event, "reason", None)
            order["failed_at"] = event.occurred_on
            order["events"].append({"event_type": "OrderPaymentFailed", "date": event.occurred_on})

    def get_orders_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        return list(self.user_orders.get(user_id, []))

    def get_order(self, order_id: str) -> Dict[str, Any]:
        return self.orders.get(order_id)
