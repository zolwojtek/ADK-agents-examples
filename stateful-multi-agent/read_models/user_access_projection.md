# UserAccessProjection

**Purpose:**
Provides a denormalized, query-optimized view of each user's access to courses, including progress and status, derived from domain events.

## Consumed Events
- `CourseAccessGranted`
- `AccessRevoked`
- `AccessExpired`
- `ProgressUpdated`
- `CourseCompleted`

## Projection Structure
- Keys: `user_id`
- Values: dict with:
  - `courses`: List of dicts:
    - `course_id`, `status` (active/completed/expired/revoked), `progress`, `expires_at` (if any)
  - `last_activity`: timestamp

## Provided Queries
- `get_user_access(user_id)` – returns all access info for a user
- `get_all()` – returns entire access projection

## Example Usage
```python
projection.handle(CourseAccessGranted(...))
data = projection.get_user_access("user_123")
```

---
This enables fast access checks, progress analytics, and UI personalization.
