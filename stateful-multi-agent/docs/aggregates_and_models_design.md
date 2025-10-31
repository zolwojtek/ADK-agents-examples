# Aggregates & Domain Model Design
*IT Developers Platform — Aggregates, Entities, Value Objects, Domain Services, Repositories, and Events*

---

## Design principles used
- **Aggregate** = consistency boundary; only aggregate roots are referenced from other aggregates.
- Keep invariants inside aggregates (or domain services if they span aggregates).
- Use **Value Objects** for typed primitives (IDs, Money, DateRange, Progress).
- Repositories provide persistence for aggregate roots only.
- Domain events capture important state changes.

---

## Overview of Aggregate Roots by Bounded Context

- **Users Context**
  - Aggregate roots: `User`
- **Courses Context**
  - Aggregate roots: `Course`
- **Policies Context**
  - Aggregate roots: `RefundPolicy`
- **Orders Context**
  - Aggregate roots: `Order`
- **Access Context**
  - Aggregate roots: `AccessRecord`

---

## 1. USERS CONTEXT

### Aggregate Root
**User**
- Responsibility: identity, credentials/profile, references to access records (IDs), user-level preferences.
- Primary identity: `UserId` (Value Object).

#### Behaviors
- `register(email, name)`
- `verify_identity()`
- `update_profile(profile_data)`
- `change_email(new_email)`
- `activate()`
- `deactivate(reason)`
- `ban(reason)`
- `mark_as_deleted()`
- `can_place_order()`
- `has_verified_email()`

### Entities / Value Objects inside `User`
- `UserId` (VO) — typed identifier.
- `Email` (VO) — validated email.
- `UserProfile` (VO) — display name, bio, avatar.
- `AccessRef` (VO) — reference to `AccessRecord` id(s) (only IDs; no direct object graph).

### Invariants
- Email must be valid and unique (uniqueness enforced at repository/application boundary).
- UserId is immutable.
- A user cannot have duplicate AccessRef for the same course (enforced by Access context when granting).
- Status must be one of the defined domain states
- A deactivated or banned user cannot place new orders
- Verified users cannot revert to unverified status

### Domain Services (within Users)
- None required for core invariants. `User` exposes behaviors like `update_profile()`.

### Repository (interface)
- `UserRepository`
  - `save(user: User) -> None`
  - `find_by_id(user_id: UserId) -> Optional[User]`
  - `find_by_email(email: Email) -> Optional[User]`
Note that the repository decides internally whether that’s an insert or an update.

### Key Domain Events
- `UserRegistered(user_id)`
- `UserProfileUpdated(user_id)`

---

## 2. COURSES CONTEXT

### Aggregate Root
**Course**
- Responsibility: course metadata, price, access type (limited/unlimited), reference to refund policy.
- Primary identity: `CourseId` (VO).

#### Behaviors
- create_course(title, description, price, author)
- update_details(title, description, price)
- assign_refund_policy(policy_id)
- set_access_type(access_type)
- change_price(new_price)
- has_refund_policy()

### Entities / Value Objects inside `Course`
- `CourseId` (VO)
- `Title`, `Description` (VOs)
- `Price` (VO) — currency + amount
- `AccessType` (VO or Enum) — `UNLIMITED` or `LIMITED`
- `PolicyRef` (VO) — `RefundPolicyId`

### Invariants
- Course must reference a valid `RefundPolicyId` (existence check by application service at create/update).
- Title and price are required
- Price must be non-negative.
- AccessType determines whether `access_expiration` is permitted (e.g., unlimited courses must not set expiration on grant).

### Domain Services
- `CoursePolicyService` (domain-level coordinator) — validates that attached policy is compatible (e.g., policy not deprecated).

### Repository (interface)
- `CourseRepository`
  - `save(course: Course) -> None`
  - `find_by_id(course_id: CourseId) -> Optional[Course]`
  - `list_by_policy(policy_id: RefundPolicyId) -> List[Course]`
  - `search_by_criteria(criteria) -> List[Course]` (domain-oriented query)

### Key Domain Events
- `CourseCreated(course_id)`
- `CoursePolicyChanged(course_id, old_policy_id, new_policy_id)`

---

## 3. POLICIES CONTEXT

### Aggregate Root
**RefundPolicy**
- Responsibility: express refund eligibility rules (time-window, conditions, exceptions).
- Primary identity: `RefundPolicyId` (VO).

### Behaviors
- create_policy(name, period_days, condition, type)
- update_terms(new_period_days, new_condition)
- rename(new_name)
- deprecate(reason)
- archive()
- is_refund_allowed(purchase_date, current_date, progress)
- can_be_assigned()

### Entities / Value Objects inside `RefundPolicy`
- `RefundPolicyId` (VO)
- `RefundPeriod` (VO) — e.g., 30 days, 60 days, 0 (none)
- `Conditions` (VO) — textual or structured rules (e.g., "no refund after content consumed X%")
- `Status` (VO/Enum) — `ACTIVE`, `DEPRECATED`, `ARCHIVED`

### Invariants
- RefundPeriod must be >= 0.
- If `Status == DEPRECATED` or `ARCHIVED`, new Courses should not attach this policy (enforced by application service).
- Policy cannot be changed if deprecated or archived

### Domain Services
- `RefundEligibilityService` — determines if a given purchase is eligible for refund given purchase date, progress, other conditions.

### Repository (interface)
- `PolicyRepository`
  - `save(policy: RefundPolicy) -> None`
  - `find_by_id(policy_id: RefundPolicyId) -> Optional[RefundPolicy]`
  - `list_active() -> List[RefundPolicy]`

### Key Domain Events
- `PolicyCreated(policy_id)`
- `PolicyUpdated(policy_id)`
- `PolicyDeprecated(policy_id)`

---

## 4. ORDERS CONTEXT

### Aggregate Root
**Order**
- Responsibility: represent the purchase transaction lifecycle and its items; manage statuses (placed, paid, refunded, cancelled).
- Primary identity: `OrderId` (VO).

#### Behaviors
- create_order(user_id, items)
- add_item(course_id, price, policy_id)
- remove_item(course_id)
- confirm_payment(payment_id)
- complete_order()
- cancel_order()
- expire_order()
- can_be_refunded()
- is_payment_pending()
- request_refund(reason)
- approve_refund()
- reject_refund(reason)

### Entities / Value Objects inside `Order`
- `OrderId` (VO)
- `OrderItem` (VO) — references `CourseId`, price at purchase, quantity (usually 1 for course).
- `Money` / `PriceSnapshot` (VO) — records price at time of purchase.
- `OrderStatus` (Enum) — `PENDING`, `PAID`, `FAILED`, `REFUNDED`, `CANCELLED`
- `PaymentInfo` (VO) — payment method reference, transaction id (infrastructure-safe)

### Invariants
- An order must contain at least one course
- Order total must match sum of order item prices (internal invariant).
- An order can only be paid once
- Cannot transition from `REFUNDED` back to `PAID`.
- Refund request must be routed to `RefundService` to evaluate policy (invariant validation via domain service).
- Access can only be granted after successful payment

### Domain Services
- `OrderPlacementService` (domain-level)  
  - Coordinates checks: course existence (query Courses), user existence (query Users), pricing, and creates the order in `PENDING` state.
- `RefundService`  
  - Uses `RefundEligibilityService` from Policies context to decide refund; coordinates state changes and emits events.

### Repository (interface)
- `OrderRepository`
  - `save(order: Order) -> None`
  - `find_by_id(order_id: OrderId) -> Optional[Order]`
  - `list_by_user(user_id: UserId) -> List[Order]`
  - `find_by_payment_id(payment_id: OrderId) -> Optional[Order]`

### Key Domain Events
- `OrderPlaced(order_id, user_id, course_id)`
- `OrderPaid(order_id, payment_ref)`
- `OrderRefunded(order_id, reason)`

---

## 5. ACCESS CONTEXT

### Aggregate Root
**AccessRecord** (a.k.a. Enrollment)
- Responsibility: represent granted access to a specific course for a specific user; control progress and expiration; be the canonical source for whether access is active.
- Primary identity: `AccessId` (VO)

#### Behaviors
- `grant_access(...)`
- `revoke_access(reason)`
- `expire_access(current_time)`
- `reactivate_access(new_expiration)`
- `update_progress(new_progress)`
- `mark_completed()`
- `record_activity(activity_type, timestamp)`
- `can_be_refunded(current_time, refund_policy)`
- `is_active()`
- `has_expired()`
- `is_revoked()`

### Entities / Value Objects inside `AccessRecord`
- `AccessId` (VO)
- `UserId` (VO)
- `CourseId` (VO)
- `PurchaseDate` (VO)
- `AccessExpiresAt` (optional VO)
- `Progress` (VO) — 0..100 float or percentage
- `AccessStatus` (Enum) — `ACTIVE`, `EXPIRED`, `REVOKED`, `PENDING`

### Invariants
- Progress must be between 0 and 100 (enforced inside aggregate).
- If access status is `REVOKED` or `EXPIRED`, progress cannot be changed
- If `AccessExpiresAt` is set, `AccessExpiresAt` >= `PurchaseDate`.
- Access can be revoked only by authorized domain action (refund accepted, admin revoke).
- For courses with `UNLIMITED` access type, `AccessExpiresAt` must be `null` (validated against Course's AccessType at grant time).
- Cannot create duplicate active AccessRecord for same (user, course) pair (enforced at application/service level; AccessRepository should support find_by_user_and_course).

### Domain Services
- `AccessValidationService` — checks if access is active and valid; used by application layer for authorization decisions.
- `ProgressTrackingService` — aggregates or interprets progress updates (e.g., do not allow progress rollback unless explicitly permitted).

### Repository (interface)
- `AccessRepository`
  - `save(access: AccessRecord) -> None`
  - `find_by_id(access_id: AccessId) -> Optional[AccessRecord]`
  - `find_by_user_and_course(user_id: UserId, course_id: CourseId) -> Optional[AccessRecord]`
  - `list_by_user(user_id: UserId) -> List[AccessRecord]`
  - `revoke(access_id: AccessId, reason) -> None` (or model revoke via save)

### Key Domain Events
- `CourseAccessGranted(access_id, user_id, course_id)`
- `ProgressUpdated(access_id, progress)`
- `AccessRevoked(access_id, reason)`
- `AccessExpired(access_id)`

---

## Cross-Aggregate/domain services and decisions

### RefundEligibilityService (Policies context)
- Pure domain evaluator; given `(policy, purchase_date, now, progress, other conditions)` returns `Eligible|NotEligible|Partial` + reasons.
- Used by `RefundService` in Orders context.

### OrderPlacementService (Orders context)
- Coordinates with `CourseRepository` (to get Price & PolicyRef) and `UserRepository` (to check existence).
- Decides price snapshot and creates `Order`.

### GrantAccess Workflow / Decision
- After `OrderPaid`:
  1. Orders context emits `OrderPaid` event including `order_id`, `user_id`, `course_id`, `price_snapshot`.
  2. Access context receives event and:
     - Fetches `Course` to check `AccessType` and `PolicyRef` if necessary (or Orders included necessary snapshot).
     - Creates `AccessRecord` with correct `AccessExpiresAt` if course access is limited.
     - Emits `CourseAccessGranted`.

**Decision rationale:** Keep Access creation and invariants inside Access context so Access is authoritative for permission checks & progress.

---

## Example Use Case Mappings (happy path)

### Place order & grant access
- Actor: User
- Flow:
  1. Application `PlaceOrder` orchestrator -> `OrderPlacementService` (Orders)
  2. `Order` created in `PENDING` with price snapshot; `OrderPlaced` event emitted.
  3. Payment processed (external), upon success `ConfirmPayment` -> `OrderPaid` event.
  4. `OrderPaid` triggers Access context to `GrantCourseAccess`.
  5. Access context creates `AccessRecord` and emits `CourseAccessGranted`.
  6. `Users` optionally stores `AccessRef` or reads from `Access` read-model.

### Request refund within policy
- Actor: User
- Flow:
  1. User requests refund -> `RequestRefund` application service (Orders)
  2. `RefundService` consults `RefundEligibilityService` (Policies) with purchase date, progress, policy.
  3. If eligible:
     - `Order` transitions to `REFUNDED`.
     - `Access` receives `AccessRevoked` or `AccessRevocationRequested` (depending on timing), removes access or sets `REVOKED`.
     - Emit `OrderRefunded`, `AccessRevoked`.

---

## Read-models vs Aggregates (short note)
- Use **Query Services** or **Read Models** for complex search, filtering, or reporting (e.g., find all active access for user, or search courses by text). Do **not** put these in aggregate repositories if they are purely read-optimized queries.
- Repositories expose domain-oriented queries only (e.g., find_by_user_and_course), not paginated/filter-by-arbitrary-field APIs used by UI.

---

## Migration / Evolution considerations
- `RefundPolicy` may evolve: keep policy versioning or snapshots in `Order` and `AccessRecord` to ensure historical consistency (price snapshot already implied).
- When policy changes, existing `AccessRecord` and `Order` should preserve snapshot of policy/version used at purchase time.

---

## Rationale summary & key decisions
- **Access is its own bounded context** and the canonical place for access validity and progress (keeps Users aggregate small and focused).  
- **Orders do not directly mutate `User` access state**; they produce events that Access context consumes — this keeps transactional scopes reasonable and responsibilities separated.  
- **Refund eligibility lives in Policies**; Orders use that service to decide refunds. This avoids policy logic duplication.  
- **Value Objects** for typed ids & money reduce primitive obsession and centralize validation.  
- **Events** are used to decouple synchronous transactions (OrderPaid -> CourseAccessGranted).

---

**End of Aggregates & Domain Model Design**
