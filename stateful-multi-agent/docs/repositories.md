# Step 2 — Repository Interfaces and Contracts (DDD Platform)

## 🎯 Purpose
Repositories are abstractions that allow the **domain layer** to retrieve and persist **aggregate roots**  
without knowing how data is stored (SQL, NoSQL, event store, etc.).

Each **aggregate** owns its own repository.

Repositories:
- Provide access to **aggregate roots only** (not inner entities)
- Return **domain objects**, not raw data
- Enforce **aggregate consistency boundaries**

---

## 🧾 UserRepository

| Method | Description | Possible Failures / Exceptions |
|---------|--------------|--------------------------------|
| `save(user: User)` | Persist or update user | `RepositoryError`, `ConcurrencyError` |
| `find_by_id(user_id: UserId) -> Optional[User]` | Retrieve user by ID | - |
| `find_by_email(email: EmailAddress) -> Optional[User]` | Find user by email | - |
| `delete(user_id: UserId)` | Remove user (if allowed) | `NotFoundError` |

---

## 🎓 CourseRepository

| Method | Description | Possible Failures / Exceptions |
|---------|--------------|--------------------------------|
| `save(course: Course)` | Persist or update course | `RepositoryError` |
| `find_by_id(course_id: CourseId) -> Optional[Course]` | Retrieve course by ID | - |
| `list_by_policy(policy_id: PolicyId) -> List[Course]` | Find all courses using specific refund policy | - |
| `search(criteria: CourseSearchCriteria) -> List[Course]` | Domain search (e.g. by tags, difficulty, author) | - |

---

## ⚖️ RefundPolicyRepository

| Method | Description | Possible Failures / Exceptions |
|---------|--------------|--------------------------------|
| `save(policy: RefundPolicy)` | Persist or update refund policy | `RepositoryError` |
| `find_by_id(policy_id: PolicyId) -> Optional[RefundPolicy]` | Retrieve by ID | - |
| `find_by_name(name: str) -> Optional[RefundPolicy]` | Ensure name uniqueness | - |

---

## 🧾 OrderRepository

| Method | Description | Possible Failures / Exceptions |
|---------|--------------|--------------------------------|
| `save(order: Order)` | Persist new or updated order | `RepositoryError` |
| `find_by_id(order_id: OrderId) -> Optional[Order]` | Retrieve order by ID | - |
| `find_by_payment_id(payment_id: str) -> Optional[Order]` | Used to reconcile with payment gateway | - |
| `list_by_user(user_id: UserId) -> List[Order]` | Retrieve user order history | - |

---

## 🎟️ AccessRepository

| Method | Description | Possible Failures / Exceptions |
|---------|--------------|--------------------------------|
| `save(access: AccessRecord)` | Persist or update access record | `RepositoryError` |
| `find_by_id(access_id: AccessId) -> Optional[AccessRecord]` | Retrieve by ID | - |
| `find_by_user_and_course(user_id: UserId, course_id: CourseId) -> Optional[AccessRecord]` | For checking if user already owns a course | - |
| `list_by_user(user_id: UserId) -> List[AccessRecord]` | For dashboard / access checks | - |
| `revoke(access_id: AccessId, reason) -> None` | Revoke access with reason | `NotFoundError` |

---

## ⚠️ Error Semantics

| Error | Meaning | Example Scenario |
|--------|----------|------------------|
| **RepositoryError** | General persistence issue | DB unavailable, write failure |
| **ConcurrencyError** | Optimistic lock violation | Two concurrent updates to same aggregate |
| **NotFoundError** | Entity not found | `delete()` called for non-existing entity |

---

## 🧩 Placement

| Layer | Responsibility |
|--------|----------------|
| **Domain Layer** | Defines repository **interfaces** |
| **Infrastructure Layer** | Implements them (e.g., using ORM, document DB, or event store) |
| **Application Layer** | Uses repositories to coordinate aggregates in services or use cases |

---

## 📘 Summary
> Repositories are the **gatekeepers** between the domain and persistence world.  
> They ensure aggregates remain **pure**, **consistent**, and **isolated** from storage details.  
> Each aggregate has **one repository** managing its complete lifecycle.
