# Step 4 — Read Models / Projections (DDD Platform)

## 🎯 Purpose
Read Models (projections) are **denormalized views** of the domain designed for:
- **UI consumption**
- **Analytics**
- **AI agent tools**
- **Reporting and dashboards**

They are **separate from the domain model**, optimized for queries rather than enforcing business rules.  
They **react to domain events** and maintain **eventual consistency** with aggregates.

---

## 🧾 Core Read Models

### 1. UserAccessProjection
**Purpose:** Show all courses a user can currently access, including status, progress, and expiration.

| Field | Description |
|--------|-------------|
| user_id | UserId |
| courses | List of `{ course_id, access_id, status, progress, expires_at }` |
| last_activity | Latest interaction timestamp |

**Events Consumed:**  
- `CourseAccessGranted` → Add new course access  
- `AccessRevoked` → Mark access revoked  
- `AccessExpired` → Mark access expired  
- `ProgressUpdated` → Update progress  
- `CourseCompleted` → Update completion status

---

### 2. CourseCatalogProjection
**Purpose:** Provide a catalog of all available courses with pricing, policies, and metadata.

| Field | Description |
|--------|-------------|
| course_id | CourseId |
| title | Course name |
| description | Course description |
| price | Money |
| policy | `{ policy_id, type, refund_period_days }` |
| instructor_id | Reference to instructor |
| status | Active / Deprecated |

**Events Consumed:**  
- `CourseCreated`  
- `CourseUpdated`  
- `CoursePolicyChanged`  
- `PolicyUpdated`  

---

### 3. OrderHistoryProjection
**Purpose:** Show all orders for a user for history, status tracking, and AI queries.

| Field | Description |
|--------|-------------|
| order_id | OrderId |
| user_id | UserId |
| course_ids | List of courses purchased |
| total_amount | Money |
| status | PendingPayment / Paid / Completed / Refunded / Cancelled |
| created_at | Timestamp |
| payment_id | Optional external reference |
| refund_reason | Optional text |

**Events Consumed:**  
- `OrderPlaced`  
- `OrderPaid`  
- `OrderRefunded`  
- `OrderCancelled`  

---

### 4. PolicyUsageProjection
**Purpose:** Map which courses are using which refund policies (helps with deprecation).

| Field | Description |
|--------|-------------|
| policy_id | PolicyId |
| policy_name | Name |
| courses | List of course_ids using this policy |

**Events Consumed:**  
- `PolicyDeprecated`  
- `CoursePolicyChanged`  
- `CourseCreated`  

---

### 5. RevenueSummaryProjection
**Purpose:** Aggregate revenue for analytics, dashboards, or AI agents.

| Field | Description |
|--------|-------------|
| course_id | CourseId |
| total_revenue | Sum of all completed orders (Money) |
| refunds | Sum of refunded amounts (Money) |
| net_revenue | total_revenue − refunds |

**Events Consumed:**  
- `OrderPaid` → add revenue  
- `OrderRefunded` → subtract refunded amount  

---

## ⚙️ Design Guidelines

- Projections are **read-only** from the domain perspective.  
- Updates happen via **event handlers** reacting to domain events.  
- Multiple projections can subscribe to the same events, allowing **different views** of the same data.  
- Use **event versioning** and **idempotent handlers** for safety.  

---

## ✅ Summary
> Read Models provide **query-optimized representations** of the system state.  
> They decouple **domain logic** from **UI/AI consumption**, enabling scalability and flexibility.  
> Each projection corresponds to a **specific use case** or **dashboard/agent need**.
