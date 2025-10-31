# PolicyUsageProjection

**Purpose:**
Aggregates policy usage/adoption statistics and details, showing which courses reference each policy, metadata, and status changes.

## Consumed Events
- `PolicyCreated`
- `PolicyUpdated`
- `CoursePolicyChanged`

## Projection Structure
- Per `policy_id`, info dict:
  - `type`, `refund_period_days`, `name`, `status`, `adoption_count`, `courses_using`
- Maintains an index mapping courses ➔ policies

## Provided Queries
- `get_policy(policy_id)` – metadata and usage stats for one policy
- `get_all()` – all known policies and their usage

## Example Usage
```python
projection.handle(CoursePolicyChanged(...))
usage = projection.get_policy("policy_789")
```

---
Use for admin dashboards, policy management, and analytics.
