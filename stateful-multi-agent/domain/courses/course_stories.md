## Course Stories and Flows

### 1) Create a new course
- Intent: Publish a course with metadata, price and access type.
- Actions:
  - System calls `Course.create_course(title, description, price, access_type, policy_ref)`.
- Domain behavior:
  - New `Course` instantiated with `id: CourseId` and provided attributes.
  - `CourseCreated` event raised with `policy_id = policy_ref.policy_id`.
  - Timestamps handled by `Entity`; event buffered via `add_domain_event`.
- Repository behavior:
  - `CourseRepository.save(course)` persists the course.
  - Title index updated: `title -> course.id` (enforce uniqueness across courses).
  - Policy index updated: `policy_ref.policy_id -> [course.id, ...]`.

### 2) Update title and description
- Intent: Improve course presentation.
- Actions: `course.update_details(new_title, new_description)` then `save`.
- Domain behavior:
  - Updates `title`, `description` and raises `CourseUpdated` event; `touch()`.
- Repository behavior:
  - If title changed, ensure new title is not used by a different course.
  - Remove previous title mapping for same course id, re-index new title.

### 3) Assign/Change refund policy
- Intent: Attach a policy or change to a different one.
- Actions: `course.assign_refund_policy(policy_ref)` then `save`.
- Domain behavior:
  - No-op if unchanged.
  - Raises `CoursePolicyChanged` with old/new policy ids; `touch()`.
- Repository behavior:
  - Policy index updated: remove prior mapping and add new mapping keyed by `policy_ref.policy_id`.

### 4) Set access type
- Intent: Switch between limited/unlimited (or other) access types.
- Actions: `course.set_access_type(access_type)` then `save`.
- Domain behavior: updates field and calls `touch()`.
- Repository behavior: persist only; no index changes.

### 5) Change price
- Intent: Adjust course price without currency change.
- Actions: `course.change_price(new_price)` then `save`.
- Domain behavior:
  - If currency differs from current, raises `ValueError`.
  - Otherwise updates price and calls `touch()`.
- Repository behavior: persist only; no index changes.

### 6) Query by policy
- Intent: List courses associated with a policy.
- Actions: `repo.get_by_policy(PolicyId | PolicyRef)`.
- Repository behavior:
  - Accepts either `PolicyId` or `PolicyRef`, normalizes to `PolicyId`.
  - Returns courses by consulting the policy index.

### Invariants and Constraints
- Identity via `id: CourseId` (an `Identifier`); equality by `id`.
- Timestamps managed by `Entity`; `touch()` updates `updated_at`.
- Events buffered via `add_domain_event` and later dispatched.
- Title uniqueness enforced in repository across creates/updates.
- Policy index keyed strictly by `PolicyId`.

### Integration Notes
- Event bus: consume `CourseCreated`, `CourseUpdated`, `CoursePolicyChanged` for projections (catalog listings, search indices).
- Read models: maintain query-optimized views (by title, by policy, by access type).
- Application services: orchestrate create/update flows; enforce cross-aggregate rules outside the aggregate.

### Error Cases (expected)
- Create or update with duplicate title (used by different course) → `ValueError`.
- Change price with mismatched currency → `ValueError`.

