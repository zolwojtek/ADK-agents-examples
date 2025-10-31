# 🧭 IT Developers Platform – Domain-Driven Design Overview

## 1. Purpose
A platform for IT developers to purchase and access online courses.  
The system manages users, courses, orders, refund policies, and course access rights.

---

## 2. Bounded Contexts Overview

| Bounded Context | Core Responsibility |
|-----------------|---------------------|
| **Users** | Manage user identities, profiles, and their basic info |
| **Courses** | Define and manage available courses, pricing, and associated refund policies |
| **Orders** | Handle purchasing and payment flow, and trigger access granting after successful payment |
| **Policies** | Define refund and platform policies (e.g., refund duration, eligibility) |
| **Access** | Represent and manage a user’s ownership and progress for purchased courses |

---

## 3. Relationships Between Contexts

[Users] ── places order ──► [Orders]
│ │
│ │ references
│ ▼
│ [Courses] ── references ──► [Policies]
│
└──── receives course access ──────── [Access]


### Summary
- A **User** places an **Order** for a **Course**.
- Each **Course** has a **Refund Policy**.
- After a successful order, **Access** is granted to the user for that course.
- **Access** tracks progress and expiration.

---

## 4. Bounded Context Details

### 4.1 Users Context
**Purpose:**  
Manage user identity and profile data. Owns user lifecycle.

**Responsibilities:**
- Create and manage user profiles.
- Verify user identity for orders and access rights.
- Receive course access from Access context.

**Core Concepts:**
- **User (Aggregate Root)**  
  - Holds identity and user info.
  - May reference Access IDs (for access records).

**Interfaces & Layers:**
- **Repository:** `UserRepository`
- **Application Services:** `RegisterUser`, `GetUserProfile`, `UpdateUserProfile`
- **Domain Events:** `UserRegistered`, `UserProfileUpdated`, `UserEmailChanged`

---

### 4.2 Courses Context
**Purpose:**  
Define and manage courses available for purchase.

**Responsibilities:**
- Maintain catalog of courses with details and pricing.
- Associate each course with a refund policy.
- Expose read operations for Orders and Access contexts.

**Core Concepts:**
- **Course (Aggregate Root)**  
  - Attributes: title, description, price, policy reference, access type (limited/unlimited).
  - Behavior: update details, change policy, retire course.

**Interfaces & Layers:**
- **Repository:** `CourseRepository`
- **Application Services:** `CreateCourse`, `AttachRefundPolicy`, `UpdateCourseDetails`
- **Domain Events:** `CourseCreated`, `CourseUpdated`, `CoursePolicyChanged`, `CourseDeprecated`

---

### 4.3 Policies Context
**Purpose:**  
Define and manage platform policies, focusing on refund policies.

**Responsibilities:**
- Define refund rules (e.g., 30 days, 60 days, no refund).
- Make policies available to other contexts via reference.

**Core Concepts:**
- **RefundPolicy (Aggregate Root)**  
  - Attributes: name, refund period, conditions.
  - Behavior: determine refund eligibility based on time since purchase.

**Interfaces & Layers:**
- **Repository:** `PolicyRepository`
- **Application Services:** `CreateRefundPolicy`, `UpdateRefundPolicy`, `DeprecatePolicy`
- **Domain Events:** `PolicyCreated`, `PolicyUpdated`, `PolicyDeprecated`

---

### 4.4 Orders Context
**Purpose:**  
Manage the process of purchasing a course.

**Responsibilities:**
- Handle order creation and payment confirmation.
- Validate course existence and user before placing order.
- Trigger granting of access after successful payment.
- Handle refund requests through the Policies context.

**Core Concepts:**
- **Order (Aggregate Root)**  
  - Attributes: user ID, course ID, status, payment info, timestamps.
  - Behavior: confirm payment, cancel order, request refund.

**Interfaces & Layers:**
- **Repository:** `OrderRepository`
- **Domain Services:**  
  - `OrderPlacementService` — handles order rules and validation.  
  - `RefundService` — applies policy rules from Policies context.
- **Application Services:**  
  - `PlaceOrder`, `ConfirmPayment`, `RequestRefund`
- **Domain Events:**  
  - `OrderPlaced`, `OrderPaid`, `OrderRefunded`, `OrderCancelled`

---

### 4.5 Access Context
**Purpose:**  
Represent and manage the user’s right to access purchased courses.

**Responsibilities:**
- Maintain records of course access per user.
- Track progress and expiration.
- Enforce access validity (expiration, revocation, refund).
- Expose progress and access data to the UI or agents.

**Core Concepts:**
- **AccessRecord (Aggregate Root)**  
  - Attributes: user ID, course ID, purchase date, expiration date, progress.
  - Behavior: update progress, check expiration, revoke access.

**Interfaces & Layers:**
- **Repository:** `AccessRepository`
- **Domain Services:**  
  - `AccessValidationService` — check if user has valid access.  
  - `ProgressTrackingService` — manage progress updates.
- **Application Services:**  
  - `GrantCourseAccess` (triggered by Order context)  
  - `UpdateProgress`  
  - `ExpireAccess`
- **Domain Events:**  
  - `CourseAccessGranted`, `ProgressUpdated`, `AccessExpired`, `AccessRevoked`, `CourseCompleted`

---

## 5. Cross-Context Interactions

| From | To | Type | Description |
|------|----|------|--------------|
| Users → Orders | Command | Place order on behalf of a user |
| Orders → Courses | Query | Verify course details and policy |
| Orders → Policies | Query | Evaluate refund eligibility |
| Orders → Access | Event | Grant access after payment |
| Access → Users | Notification | Inform user about new access |
| Access → Orders | Event | Notify about access revocation (e.g., refund) |

---

## 6. Layering Inside Each Context

Each bounded context follows Clean Architecture layering:

┌───────────────────────────┐
│ Application Layer │ ← orchestrates use cases, handles transactions, emits domain events
├───────────────────────────┤
│ Domain Layer │ ← aggregates, entities, value objects, domain services, rules
├───────────────────────────┤
│ Infrastructure Layer │ ← repositories, mappers, database, external APIs, event buses
└───────────────────────────┘


**Responsibilities by layer:**
- **Domain Layer:** Business rules and invariants.
- **Application Layer:** Orchestrates workflows and coordinates domain logic.
- **Infrastructure Layer:** Implements persistence and messaging.

---

## 7. Domain Event Flow (High-Level Example)

**Purchase flow:**
1. `User` places an order → `OrderPlaced`
2. `Orders` validates via `Courses` and `Policies`
3. `PaymentConfirmed` triggers `CourseAccessGranted`
4. `Access` context grants course access and emits `AccessGranted`
5. `Users` context updates user’s access list (optional)

---

## 8. Ownership Summary

| Concept | Context | Notes |
|----------|----------|-------|
| User | Users | Core identity |
| Course | Courses | Defines offering and price |
| RefundPolicy | Policies | Defines refund rules |
| Order | Orders | Transaction and payment flow |
| AccessRecord | Access | Represents user’s ownership and progress |

---

## 9. Error Handling & Validation

### Domain-Level Validation
- **Value Objects** enforce basic invariants (email format, positive amounts, valid ranges)
- **Aggregates** enforce business rules and state transitions
- **Domain Services** handle cross-aggregate validation

### Application-Level Error Handling
- **Repository Errors**: `RepositoryError`, `ConcurrencyError`, `NotFoundError`
- **Domain Violations**: `DomainError`, `BusinessRuleViolation`
- **External Service Errors**: `PaymentError`, `NotificationError`

### Error Recovery Strategies
- **Retry Logic**: For transient failures (network, database)
- **Compensation**: For distributed transactions (refund on payment failure)
- **Eventual Consistency**: For cross-context updates via domain events

---

## 10. Guiding Principles

- Each bounded context owns its own model and persistence.
- Repositories only express persistence of aggregates.
- Business logic resides in domain layer, not in repositories or application services.
- Cross-context communication via domain events or explicit APIs.
- Value Objects replace primitive IDs where meaningful (e.g., `UserId`, `CourseId`).
- Complex reads and searches handled by dedicated Query Services (read models).
- All domain events are immutable and contain only value objects.
- Aggregate boundaries enforce consistency and prevent data corruption.

---

**Document Version:** v1.0  
**Purpose:** Foundational structure for the IT Developers Platform based on Domain-Driven Design and Clean Architecture principles.
