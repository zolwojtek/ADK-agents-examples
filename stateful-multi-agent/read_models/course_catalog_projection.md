# CourseCatalogProjection

**Purpose:**
Maintains a complete, denormalized catalog of available courses, including pricing, policy links, and status, driven by domain events.

## Consumed Events
- `CourseCreated`
- `CourseUpdated`
- `CoursePolicyChanged`
- `PolicyUpdated`

## Projection Structure
- Keys: `course_id`
- Values: dict with:
  - `title`, `description`, `price`, `policy` (dict: `policy_id`, `type`, `refund_period_days`), `instructor_id`, `status` (active/deprecated)

## Provided Queries
- `get_course(course_id)` – lookup by course
- `get_all()` – returns all catalog data (fast)

## Example Usage
```python
projection.handle(CourseCreated(...))
catalog = projection.get_all()
```

---
Optimized for discovery, recommendation, and display in user-facing apps.
