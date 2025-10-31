## Policy Stories and Flows

### 1) Create a new refund policy
- Intent: Define refund eligibility rules for courses.
- Actions:
  - System calls `RefundPolicy.create_policy(name, policy_type, refund_period, conditions)`.
- Domain behavior:
  - New `RefundPolicy` instantiated with `id: PolicyId`, `status: ACTIVE`, and provided attributes.
  - `PolicyCreated` event raised with policy details and refund period.
  - Timestamps set in `Entity` (`created_at`, `updated_at`).
- Repository behavior:
  - `PolicyRepository.save(policy)` persists the policy and indexes by name, type, and status.
  - Name index: `name -> policy_id` (enforce uniqueness across policies).
  - Type index: `policy_type -> [policy_id]`.
  - Status index: `ACTIVE -> [policy_id]`.

### 2) Update policy terms
- Intent: Modify refund period and conditions for an existing policy.
- Actions: `policy.update_terms(new_refund_period, new_conditions)` then `save`.
- Domain behavior:
  - If `status != ACTIVE`, raises `ValueError`.
  - Updates `refund_period` and `conditions`, raises `PolicyUpdated` event; `touch()`.
- Repository behavior:
  - Save to persist updated fields. No index changes needed.

### 3) Rename policy
- Intent: Change the policy name for better identification.
- Actions: `policy.rename(new_name)` then `save`.
- Domain behavior:
  - If `status != ACTIVE`, raises `ValueError`.
  - Updates `name` and calls `touch()`.
- Repository behavior:
  - If name changed, ensure new name is not used by a different policy.
  - Remove previous name mapping for same policy id, re-index new name.

### 4) Deprecate policy
- Intent: Mark policy as deprecated to prevent new course assignments.
- Actions: `policy.deprecate(reason)` then `save`.
- Domain behavior:
  - If already `DEPRECATED`, raises `ValueError`.
  - If `status == ARCHIVED`, raises `ValueError`.
  - Sets `status = DEPRECATED`, raises `PolicyDeprecated` event; `touch()`.
- Repository behavior:
  - `save(policy)` updates status index: removes from `ACTIVE`, adds to `DEPRECATED`.

### 5) Reactivate policy
- Intent: Restore a deprecated policy to active status.
- Actions: `policy.reactivate()` then `save`.
- Domain behavior:
  - If `status != DEPRECATED`, raises `ValueError`.
  - Sets `status = ACTIVE`, raises `PolicyReactivated` event; `touch()`.
- Repository behavior:
  - `save(policy)` updates status index: removes from `DEPRECATED`, adds to `ACTIVE`.

### 6) Archive policy
- Intent: Permanently remove policy from use (final state).
- Actions: `policy.archive()` then `save`.
- Domain behavior:
  - If already `ARCHIVED`, raises `ValueError`.
  - Sets `status = ARCHIVED`; `touch()`.
- Repository behavior:
  - `save(policy)` updates status index: removes from current status, adds to `ARCHIVED`.

### 7) Check refund eligibility
- Intent: Determine if a refund is allowed based on policy rules.
- Actions: `policy.is_refund_allowed(purchase_date, current_date, progress)`.
- Domain behavior:
  - If `status != ACTIVE`, returns `False`.
  - Checks time window: `(current_date - purchase_date).days <= refund_period.days`.
  - For `NO_REFUND` policy type, returns `False`.
  - For other types, allows refund if `progress < 100.0`.
- Repository behavior: No persistence needed; read-only operation.

### 8) Check policy assignment eligibility
- Intent: Verify if policy can be assigned to new courses.
- Actions: `policy.can_be_assigned()`.
- Domain behavior:
  - Returns `True` only if `status == ACTIVE`.
- Repository behavior: No persistence needed; read-only operation.

### 9) Query policies by type
- Intent: Find policies of a specific type (standard, extended, no_refund).
- Actions: `repo.get_by_type(policy_type)`.
- Repository behavior:
  - Uses type index to efficiently find policies by type.
  - Returns list of `RefundPolicy` objects.

### 10) Query policies by status
- Intent: Find policies in a specific status (active, deprecated, archived).
- Actions: `repo.get_by_status(status)` or specific methods like `get_active_policies()`.
- Repository behavior:
  - Uses status index for efficient querying.
  - Returns list of `RefundPolicy` objects.

### 11) Query policy by name
- Intent: Find a specific policy by its name.
- Actions: `repo.get_by_name(name)`.
- Repository behavior:
  - Uses name index for efficient lookup.
  - Returns single `RefundPolicy` or `None`.

### 12) Query policy by refund period
- Intent: Find policies with a specific refund period.
- Actions: `repo.get_policy_by_refund_period(refund_period)`.
- Repository behavior:
  - Iterates through all policies to find matching refund period.
  - Returns single `RefundPolicy` or `None`.

### Policy Status Transitions
- **ACTIVE** → **DEPRECATED** (via `deprecate`)
- **DEPRECATED** → **ACTIVE** (via `reactivate`)
- **ACTIVE/DEPRECATED** → **ARCHIVED** (via `archive`)

### Invariants and Constraints
- Identity via `id: PolicyId` (an `Identifier`); equality by `id`.
- Timestamps managed by `Entity`; `touch()` updates `updated_at`.
- Events buffered via `add_domain_event` and later dispatched.
- Name uniqueness enforced in repository across creates/updates.
- Only `ACTIVE` policies can be assigned to courses.
- Only `ACTIVE` policies allow refunds.
- Status transitions are strictly controlled by business rules.

### Integration Notes
- Event bus: consume `PolicyCreated`, `PolicyUpdated`, `PolicyDeprecated`, `PolicyReactivated` for:
  - Course policy assignment updates
  - Policy catalog maintenance
  - Audit trails and compliance reporting
  - Notification systems for policy changes
- Read models: maintain query-optimized views (by name, by type, by status, by refund period).
- Application services: orchestrate policy lifecycle management and cross-aggregate rules.

### Error Cases (expected)
- Create or update with duplicate name (used by different policy) → `ValueError`.
- Update terms on non-active policy → `ValueError`.
- Rename non-active policy → `ValueError`.
- Deprecate already deprecated policy → `ValueError`.
- Deprecate archived policy → `ValueError`.
- Reactivate non-deprecated policy → `ValueError`.
- Archive already archived policy → `ValueError`.

### Business Rules
- Policies start in `ACTIVE` status and can transition to `DEPRECATED` or `ARCHIVED`.
- Only `ACTIVE` policies can be assigned to courses.
- Only `ACTIVE` policies allow refunds.
- `DEPRECATED` policies cannot be assigned to new courses but existing assignments remain valid.
- `ARCHIVED` policies are permanently removed from use.
- Policy names must be unique across all policies.
- Refund periods cannot be negative.
- Policy conditions have a maximum length limit (1000 characters).
- Policy names have a maximum length limit (100 characters).

### Policy Types and Their Behavior
- **STANDARD**: Standard refund policy with time window and progress checks.
- **EXTENDED**: Extended refund policy with longer time windows or special conditions.
- **NO_REFUND**: Policy that never allows refunds regardless of other conditions.

### Refund Eligibility Logic
- Time window check: `days_since_purchase <= refund_period.days`
- Progress check: `progress < 100.0` (course not completed)
- Policy type check: `policy_type != NO_REFUND`
- Status check: `status == ACTIVE`
- All conditions must be met for refund to be allowed.
