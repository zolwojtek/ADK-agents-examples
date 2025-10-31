# Step 5 — Domain Tests Plan (DDD Platform)

## 🎯 Purpose
Domain tests verify **aggregate invariants**, **business rules**, and **edge cases** without relying on infrastructure.  
They ensure that **core domain logic is correct and protected** before persistence or UI interaction.

---

## 🧪 Testing Strategy

- **Unit tests** for each aggregate root.
- Focus on **state changes and invariants**.
- **Edge case coverage** (boundaries, invalid input, conflicting actions).
- **Event emission validation** (correct domain events are raised).
- **No direct DB calls** — pure domain logic only.

---

## 🧾 Aggregate Test Plan

### 1. User Aggregate

| Test | Description |
|------|-------------|
| `create_user_valid_data` | Verify valid user creation |
| `create_user_invalid_email` | Raise error for invalid email format |
| `create_user_empty_name` | Raise error for empty name |
| `change_email` | Updates email and emits `UserEmailChanged` |
| `duplicate_email` | Ensure domain rule prevents duplicate registration |

---

### 2. Course Aggregate

| Test | Description |
|------|-------------|
| `create_course_valid_data` | Verify course creation with valid policy |
| `assign_deprecated_policy` | Raise error when course uses deprecated policy |
| `update_course_details` | Updates title, description, price |
| `policy_change_event` | Emits `CoursePolicyChanged` on policy reassignment |

---

### 3. RefundPolicy Aggregate

| Test | Description |
|------|-------------|
| `create_policy` | Verify correct creation with refund period and type |
| `deprecated_policy_usage` | Cannot assign deprecated policy to new courses |
| `is_refund_allowed_within_period` | Returns true if within refund period and progress limits |
| `is_refund_disallowed_after_period` | Returns false if outside refund window |
| `immutable_policy_type` | Ensure type cannot be changed after creation |

---

### 4. Order Aggregate

| Test | Description |
|------|-------------|
| `create_order_valid_items` | Order created with items and total calculated |
| `cannot_add_items_after_payment` | Adding items after payment raises error |
| `confirm_payment_emits_event` | `OrderPaid` event emitted on payment confirmation |
| `request_refund_with_valid_policy` | Refund allowed if policy permits |
| `request_refund_disallowed_by_policy` | Refund rejected if policy forbids |
| `cannot_cancel_paid_order` | Cancel fails if already paid |
| `cannot_double_refund` | Prevent multiple refunds for same order |

---

### 5. CourseAccess Aggregate

| Test | Description |
|------|-------------|
| `grant_access_creates_record` | Access created after order payment |
| `revoke_access_updates_status` | Status becomes revoked on refund or admin action |
| `update_progress_valid_range` | Progress between 0–100 only |
| `cannot_update_progress_revoked` | Raise error if access revoked |
| `expire_access_changes_status` | Status transitions to expired after end date |
| `mark_completed_when_full_progress` | Emits `CourseCompleted` when progress = 100 |
| `can_be_refunded_checks_policy` | Evaluates eligibility using attached policy |

---

## ⚙️ Test Implementation Notes

- Use **Value Objects** consistently in tests (UserId, CourseId, Money, Progress).  
- Assert both **state changes** and **domain events emitted**.  
- Use **factory methods** for aggregate setup to reduce boilerplate.  
- For **edge cases**, include:
  - Progress boundaries (0, 100, -1, 101)  
  - Refund eligibility at day limits  
  - Expired access transitions  

---

## ✅ Summary
> Domain tests are the **safeguard of business rules**.  
> They validate invariants, lifecycle transitions, and cross-aggregate behaviors in isolation.  
> Following this plan ensures a **robust, reliable, and expressive domain model** before touching persistence or UI layers.
