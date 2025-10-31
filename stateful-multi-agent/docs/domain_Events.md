# Step 3 — Domain Events & Integration Contracts (DDD Platform)

## 🎯 Purpose
Domain Events capture **meaningful business occurrences** within the domain.  
They:
- Represent **facts that have already happened**  
- Enable **communication between bounded contexts**  
- Allow for **event-driven integration** and **asynchronous workflows**

Each event:
- Is **immutable**
- Contains **value objects only**
- Is named in the **past tense**
- Has a clear **publisher** and **subscribers**

---

## 🧱 Event Structure Convention

| Field | Description |
|--------|--------------|
| `event_id` | Unique ID of the event (for deduplication) |
| `occurred_on` | Timestamp of the event |
| `aggregate_type` | Name of aggregate that raised it |
| `aggregate_id` | ID of the aggregate instance |
| `payload` | Business data (value objects only) |

---

## 📦 Core Domain Events

### 👤 User Context

| Event | Published By | Payload | Consumed By |
|--------|---------------|----------|--------------|
| **UserRegistered** | `User` aggregate | `{ user_id, email, name }` | Analytics, Notifications |
| **UserProfileUpdated** | `User` aggregate | `{ user_id, profile_data }` | Analytics, Notifications |
| **UserEmailChanged** | `User` aggregate | `{ user_id, old_email, new_email }` | Notifications, Security |

---

### 🎓 Course Context

| Event | Published By | Payload | Consumed By |
|--------|---------------|----------|--------------|
| **CourseCreated** | `Course` aggregate | `{ course_id, title, instructor_id, policy_id }` | Catalog projection |
| **CourseUpdated** | `Course` aggregate | `{ course_id, title, description, price }` | Catalog projection |
| **CourseDeprecated** | `Course` aggregate | `{ course_id, title }` | Catalog cleanup, Search indexing |
| **CoursePolicyChanged** | `Course` aggregate | `{ course_id, old_policy_id, new_policy_id }` | Policy service consistency |

---

### ⚖️ Refund Policy Context

| Event | Published By | Payload | Consumed By |
|--------|---------------|----------|--------------|
| **PolicyCreated** | `RefundPolicy` aggregate | `{ policy_id, name, type, refund_period_days }` | Courses, Policies projection |
| **PolicyDeprecated** | `RefundPolicy` aggregate | `{ policy_id, name }` | Courses (validation), Admin UI |
| **PolicyUpdated** | `RefundPolicy` aggregate | `{ policy_id, new_conditions }` | Courses (for mapping updates) |

---

### 💰 Orders Context

| Event | Published By | Payload | Consumed By |
|--------|---------------|----------|--------------|
| **OrderPlaced** | `Order` aggregate | `{ order_id, user_id, course_ids, total_amount }` | Payment service |
| **OrderPaid** | `Order` aggregate | `{ order_id, user_id, course_ids, payment_id }` | Access context (grant access) |
| **OrderRefunded** | `Order` aggregate | `{ order_id, user_id, course_ids, refund_reason }` | Access context (revoke access) |
| **OrderCancelled** | `Order` aggregate | `{ order_id, user_id }` | Analytics, Notifications |

---

### 🎟️ Access Context

| Event | Published By | Payload | Consumed By |
|--------|---------------|----------|--------------|
| **CourseAccessGranted** | `AccessRecord` aggregate | `{ access_id, user_id, course_id }` | Notifications, Analytics |
| **AccessRevoked** | `AccessRecord` aggregate | `{ access_id, user_id, course_id, reason }` | Notifications, Audit logs |
| **AccessExpired** | `AccessRecord` aggregate | `{ access_id, user_id, course_id, expired_at }` | Notifications |
| **ProgressUpdated** | `AccessRecord` aggregate | `{ access_id, user_id, course_id, progress }` | Analytics, Certificates |
| **CourseCompleted** | `AccessRecord` aggregate | `{ access_id, user_id, course_id }` | Achievements, Certificates |

---

## 🔄 Event Flow Summary (Cross-Context)

| Source | Event | Destination | Purpose |
|---------|--------|--------------|----------|
| Orders → Access | `OrderPaid` | Grant course access |
| Orders → Access | `OrderRefunded` | Revoke access |
| Policies → Courses | `PolicyDeprecated` | Validate / reassign policies |
| Access → Analytics | `ProgressUpdated`, `CourseCompleted` | Update statistics |
| Users → Notifications | `UserRegistered` | Send welcome message |

---

## 🧩 Event Delivery Mechanisms

| Layer | Responsibility |
|--------|----------------|
| **Domain Layer** | Defines event classes and raises them |
| **Application Layer** | Publishes events to message bus or event log |
| **Infrastructure Layer** | Implements actual event transport (e.g., Kafka, RabbitMQ, Redis Stream) |

---

## ⚙️ Event Handling Guidelines

- Events are **immutable** and **append-only**
- Consumers should be **idempotent**
- Use **event versioning** for backward compatibility
- Use **transactional outbox** pattern to ensure reliable delivery
- Store events for **audit and replay**

---

## 📘 Summary
> Domain Events form the **nervous system** of the platform.  
> They connect aggregates and bounded contexts in a **loosely coupled**, **asynchronous** way.  
> The entire system reacts to *facts*, not commands.
