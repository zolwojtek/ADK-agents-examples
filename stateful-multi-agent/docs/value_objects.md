# Step 1 — Value Object Design (DDD Platform)

## 🎯 Purpose
Value Objects (VOs) express **domain meaning**, enforce **invariants**, and remain **immutable**.  
They give type safety and prevent mixing primitive types (e.g., `float`, `str`) with semantic business data.

---

## 🧱 Shared / Core Value Objects

| Value Object | Description | Used In | Key Rules / Invariants |
|---------------|--------------|----------|--------------------------|
| **UserId** | Unique user identity | All contexts | Must be valid UUID or numeric |
| **CourseId** | Unique course identity | Courses, Orders, Access | Immutable |
| **OrderId** | Unique order identity | Orders | Immutable |
| **PolicyId** | Unique refund policy identity | Policies, Courses | Immutable |
| **AccessId** | Unique course access identity | Access | Immutable |
| **Money (amount, currency)** | Represents value with currency | Orders | Non-negative; supports math ops |
| **RefundPeriod (days)** | Refund time window | Policies | ≥ 0 |
| **Progress (percent)** | Course completion percent | Access | Between 0–100 inclusive |
| **DateRange (start, end)** | Valid date span | Courses, Access | `end ≥ start` |
| **EmailAddress** | Validated email | Users | Must be valid RFC 5322 format |
| **Name** | User or course display name | Users, Courses | Not empty |
| **PolicyType (enum)** | STANDARD, EXTENDED, NO_REFUND | Policies | Immutable once assigned |
| **AccessRef** | Reference to AccessRecord ID | Users | Immutable, only stores ID |
| **PolicyRef** | Reference to RefundPolicy ID | Courses | Immutable, only stores ID |
| **PriceSnapshot** | Price at time of purchase | Orders | Immutable, preserves historical pricing |
| **PaymentInfo** | Payment method and transaction details | Orders | Contains payment_id, method |
| **AccessStatus (enum)** | ACTIVE, EXPIRED, REVOKED, PENDING | Access | Immutable state transitions |
| **OrderStatus (enum)** | PENDING, PAID, FAILED, REFUNDED, CANCELLED | Orders | Immutable state transitions |
| **AccessType (enum)** | UNLIMITED, LIMITED | Courses | Determines expiration behavior |

---

## 💡 Design Notes
- VOs are **immutable** — updates produce a *new instance*.  
- All invariants are checked at creation time.  
- VOs are defined within **their domain modules** (e.g., `users/domain/value_objects.py`).  
- No persistence logic inside VOs — they’re pure domain concepts.

---

## ✅ Example Usage (Conceptual)
- `Money(49.99, "USD")`
- `Progress(85.0)`
- `RefundPeriod(days=30)`
- `DateRange(start=2025-01-01, end=2025-12-31)`
- `EmailAddress("user@example.com")`

---

## 📘 Summary
> Value Objects provide a **rich domain language** that ensures correctness, readability, and isolation of business rules.  
> They form the **foundation** of every aggregate and service in the system.
