# Application Services Overview

The Application Service layer orchestrates all business use cases and workflow in the DDD architecture. Each service encapsulates use case APIs for its own domain, working with aggregates, repositories, and the event bus for transactional, business-meaningful operations.

---

## 1. OrderApplicationService
**Purpose:** Coordinates all order lifecycle workflows: place/pay order, request/cancel/refund.
- **Main Methods:**
    - `place_order`
    - `request_refund`
    - `cancel_order`
- **Relationships:** Uses `Order`, `User`, and `Course` aggregates via their repositories; triggers domain events (via `event_bus`).
- **Usage:**
```python
app_service = OrderApplicationService(order_repo, user_repo, course_repo, event_bus)
result = app_service.place_order(PlaceOrderCommand(...))
```

## 2. UserApplicationService
**Purpose:** Manages registration, profile updates, and email changes for users.
- **Main Methods:**
    - `register_user`
    - `update_profile`
    - `change_email`
- **Relationships:** Uses `User` aggregate/repo; triggers user/domain events.
- **Usage:**
```python
user_service = UserApplicationService(user_repo, event_bus)
result = user_service.register_user(RegisterUserCommand(...))
```

## 3. AccessApplicationService
**Purpose:** Grants, revokes, and refreshes user access to courses.
- **Main Methods:**
    - `grant_access`
    - `revoke_access`
    - `refresh_access`
- **Relationships:** Works with `AccessRecord`, `User`, `Course` via repos; domain events for access lifecycle.
- **Usage:**
```python
access_service = AccessApplicationService(access_repo, user_repo, course_repo, event_bus)
res = access_service.grant_access(GrantAccessCommand(...))
```

## 4. CourseApplicationService
**Purpose:** Course lifecycle management: create, update, deprecate, and policy change.
- **Main Methods:**
    - `create_course`
    - `update_course`
    - `deprecate_course`
    - `change_policy`
- **Relationships:** Relies on `Course` and `Policy` aggregates/repos; fires course-related events.
- **Usage:**
```python
course_service = CourseApplicationService(course_repo, policy_repo, event_bus)
res = course_service.create_course(CreateCourseCommand(...))
```

## 5. PolicyApplicationService
**Purpose:** Management of refund/usage policies.
- **Main Methods:**
    - `create_policy`
    - `update_policy`
    - `deprecate_policy`
    - `reactivate_policy`
- **Relationships:** Handles `Policy` aggregates/repo, fires policy-change events.
- **Usage:**
```python
policy_service = PolicyApplicationService(policy_repo, event_bus)
res = policy_service.create_policy(CreatePolicyCommand(...))
```

---

## Orchestrating Services Together
Each application service can be instantiated with repository and event bus implementations (real, in-memory, or mocked).

Example wiring for a production/composed system:
```python
# (Assume proper implementations for all repos/event_bus)
order_service = OrderApplicationService(order_repo, user_repo, course_repo, event_bus)
user_service = UserApplicationService(user_repo, event_bus)
access_service = AccessApplicationService(access_repo, user_repo, course_repo, event_bus)
course_service = CourseApplicationService(course_repo, policy_repo, event_bus)
policy_service = PolicyApplicationService(policy_repo, event_bus)

# Typical use case: User places an order, receives course access upon payment
result = order_service.place_order(PlaceOrderCommand(...))
# Event handlers or subsequent service methods act based on events/side effects
```

---
**Note:**
- Each service method maps to a business transaction or "application command"
- They are pure orchestrators and should not carry business state or perform direct I/O
- Integration or API boundaries call only these service interfaces
