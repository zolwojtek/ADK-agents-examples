## Order Stories and Flows

### 1) Create a new order
- Intent: Customer initiates a purchase for one or more courses.
- Actions:
  - System calls `Order.create_order(user_id, items, total_amount)`.
- Domain behavior:
  - New `Order` instantiated with `id: OrderId`, `status: PENDING`, `user_id`, `items`, `total_amount`.
  - `OrderPlaced` event raised with course IDs and total amount.
  - Timestamps set in `Entity` (`created_at`, `updated_at`).
- Repository behavior:
  - `OrderRepository.save(order)` persists the order and indexes by user, course, and status.
  - User index: `user_id -> [order_id]`.
  - Course index: `course_id -> [order_id]` for each item.
  - Status index: `PENDING -> [order_id]`.

### 2) Confirm payment
- Intent: Process successful payment for a pending order.
- Actions: `order.confirm_payment(payment_info)`.
- Domain behavior:
  - If `status != PENDING`, raises `ValueError`.
  - Sets `status = PAID`, stores `payment_info`, calls `touch()`.
  - Raises `OrderPaid` event with payment details.
- Repository behavior:
  - `save(order)` updates status index: removes from `PENDING`, adds to `PAID`.
  - Payment info persisted for future reference.

### 3) Mark payment as failed
- Intent: Handle payment processing failures.
- Actions: `order.mark_payment_failed(failure_reason)`.
- Domain behavior:
  - If `status != PENDING`, raises `ValueError`.
  - Sets `status = FAILED`, stores `failure_reason`, calls `touch()`.
  - Raises `OrderPaymentFailed` event with failure details.
- Repository behavior:
  - `save(order)` updates status index: removes from `PENDING`, adds to `FAILED`.

### 4) Cancel order
- Intent: Cancel a pending order before payment.
- Actions: `order.cancel(reason)`.
- Domain behavior:
  - If `status != PENDING`, raises `ValueError`.
  - Sets `status = CANCELLED`, stores `cancellation_reason`, calls `touch()`.
  - Raises `OrderCancelled` event.
- Repository behavior:
  - `save(order)` updates status index: removes from `PENDING`, adds to `CANCELLED`.

### 5) Expire order
- Intent: Automatically cancel orders that have been pending too long.
- Actions: `order.expire_order()`.
- Domain behavior:
  - If `status != PENDING`, raises `ValueError`.
  - Sets `status = CANCELLED`, calls `touch()`.
- Repository behavior:
  - `save(order)` updates status index: removes from `PENDING`, adds to `CANCELLED`.

### 6) Request refund
- Intent: Customer requests refund for a paid order.
- Actions: `order.request_refund(reason)`.
- Domain behavior:
  - If `status != PAID`, raises `ValueError`.
  - Sets `status = REFUND_REQUESTED`, stores `refund_reason`, calls `touch()`.
  - Raises `OrderRefundRequested` event with refund reason.
- Repository behavior:
  - `save(order)` updates status index: removes from `PAID`, adds to `REFUND_REQUESTED`.

### 7) Approve refund
- Intent: Admin approves a refund request and processes payment.
- Actions: `order.approve_refund(refund_amount)`.
- Domain behavior:
  - If `status != REFUND_REQUESTED`, raises `ValueError`.
  - If no `refund_reason`, raises `ValueError`.
  - Sets `status = REFUNDED`, stores `refund_amount`, calls `touch()`.
  - Raises `OrderRefunded` event with refund details.
- Repository behavior:
  - `save(order)` updates status index: removes from `REFUND_REQUESTED`, adds to `REFUNDED`.

### 8) Reject refund
- Intent: Admin rejects a refund request.
- Actions: `order.reject_refund(reason)`.
- Domain behavior:
  - If `status != REFUND_REQUESTED`, raises `ValueError`.
  - If no `refund_reason`, raises `ValueError`.
  - Clears `refund_reason`, calls `touch()`.
  - Order remains in current status.
- Repository behavior:
  - `save(order)` persists the rejection; no status change.

### 9) Query orders by user
- Intent: Retrieve all orders for a specific user.
- Actions: `repo.get_by_user(user_id)`.
- Repository behavior:
  - Uses user index to efficiently find all orders for the user.
  - Returns list of `Order` objects.

### 10) Query orders by course
- Intent: Find all orders containing a specific course.
- Actions: `repo.get_by_course(course_id)`.
- Repository behavior:
  - Uses course index to find orders containing the course.
  - Returns list of `Order` objects.

### 11) Query orders by status
- Intent: Find orders in a specific status (pending, paid, failed, etc.).
- Actions: `repo.get_by_status(status)` or specific methods like `get_pending_orders()`.
- Repository behavior:
  - Uses status index for efficient querying.
  - Returns list of `Order` objects.

### 12) Find user-course order
- Intent: Check if user has already purchased a specific course.
- Actions: `repo.get_user_course_order(user_id, course_id)`.
- Repository behavior:
  - Gets user orders, then searches items for matching course.
  - Returns single `Order` or `None`.

### Order Status Transitions
- **PENDING** → **PAID** (via `confirm_payment`)
- **PENDING** → **FAILED** (via `mark_payment_failed`)
- **PENDING** → **CANCELLED** (via `cancel` or `expire_order`)
- **PAID** → **REFUND_REQUESTED** (via `request_refund`)
- **REFUND_REQUESTED** → **REFUNDED** (via `approve_refund`)

### Invariants and Constraints
- Identity via `id: OrderId` (an `Identifier`); equality by `id`.
- Timestamps managed by `Entity`; `touch()` updates `updated_at`.
- Events buffered via `add_domain_event` and later dispatched.
- Status transitions are strictly controlled by business rules.
- Orders can only be paid when in `PENDING` status.
- Orders can only be refunded when in `PAID` status.
- Orders can only be cancelled when in `PENDING` status.

### Integration Notes
- Event bus: consume `OrderPlaced`, `OrderPaid`, `OrderPaymentFailed`, `OrderCancelled`, `OrderRefundRequested`, `OrderRefunded` for:
  - Access record creation (on `OrderPaid`)
  - Email notifications
  - Analytics and reporting
  - Inventory management
- Read models: maintain query-optimized views (by user, by course, by status, by date).
- Application services: orchestrate payment processing, refund workflows, and cross-aggregate rules.

### Error Cases (expected)
- Confirm payment on non-pending order → `ValueError`.
- Mark payment failed on non-pending order → `ValueError`.
- Cancel non-pending order → `ValueError`.
- Request refund on non-paid order → `ValueError`.
- Approve refund without refund request → `ValueError`.
- Approve refund on non-refund-requested order → `ValueError`.
- Reject refund on non-refund-requested order → `ValueError`.
- Expire non-pending order → `ValueError`.

### Business Rules
- Orders start in `PENDING` status and can transition to `PAID`, `FAILED`, or `CANCELLED`.
- Only `PAID` orders can request refunds (transition to `REFUND_REQUESTED`).
- Only `REFUND_REQUESTED` orders can be approved for refund (transition to `REFUNDED`).
- Payment failures are terminal (no retry mechanism in domain).
- Order cancellation is only allowed for `PENDING` orders.
- Each order can contain multiple course items.
- Order total amount is calculated from item prices at order time.
