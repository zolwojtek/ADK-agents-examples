# OrderHistoryProjection

**Purpose:**
Tracks all orders per user and their lifecycle (placed, paid, refunded, cancelled, failed) as a denormalized event-driven history.

## Consumed Events
- `OrderPlaced`
- `OrderPaid`
- `OrderRefundRequested`
- `OrderRefunded`
- `OrderCancelled`
- `OrderPaymentFailed`

## Projection Structure
- Per `user_id`, list of orders:
  - `order_id`, `placed_at`, `course_ids`, `total_amount`, `status`, `payment_id`, `refund_amount`, `refund_reason`, `events` (chronological)
- Flat lookup by `order_id`

## Provided Queries
- `get_orders_for_user(user_id)` – all orders for a user
- `get_order(order_id)` – detailed info for a specific order

## Example Usage
```python
projection.handle(OrderPlaced(...))
orders = projection.get_orders_for_user("user_123")
```

---
Enables order history views, refunds/audit, and user/account support tools.
