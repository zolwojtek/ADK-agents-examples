## Access Stories and Flows

### 1) Grant course access
- Intent: Provide a user with access to a specific course after purchase.
- Actions:
  - System calls `AccessRecord.grant_access(user_id, course_id, purchase_date, access_expires_at)`.
- Domain behavior:
  - New `AccessRecord` instantiated with `id: AccessId`, `status: ACTIVE`, and provided attributes.
  - `CourseAccessGranted` event raised with access, user, and course details.
  - Timestamps set in `Entity` (`created_at`, `updated_at`).
- Repository behavior:
  - `AccessRepository.save(access_record)` persists the access record and indexes by user, course, and status.
  - User index: `user_id -> [access_id]`.
  - Course index: `course_id -> [access_id]`.
  - Status index: `ACTIVE -> [access_id]`.
  - User-course index: `(user_id, course_id) -> access_id`.

### 2) Update course progress
- Intent: Track user's progress through the course content.
- Actions: `access_record.update_progress(new_progress)` then `save`.
- Domain behavior:
  - If `status != ACTIVE`, raises `ValueError`.
  - If `new_progress < current_progress`, raises `ValueError`.
  - Updates `progress`, raises `ProgressUpdated` event; `touch()`.
  - If progress reaches 100%, automatically calls `mark_completed()`.
- Repository behavior:
  - Save to persist updated progress. No index changes needed.

### 3) Mark course as completed
- Intent: Record that user has finished the entire course.
- Actions: `access_record.mark_completed()` then `save`.
- Domain behavior:
  - If `status != ACTIVE`, raises `ValueError`.
  - Sets `progress = 100.0`, raises `CourseCompleted` event; `touch()`.
- Repository behavior:
  - Save to persist updated progress. No index changes needed.

### 4) Record user activity
- Intent: Track specific user actions within the course.
- Actions: `access_record.record_activity(activity_type, timestamp, metadata)` then `save`.
- Domain behavior:
  - If `status != ACTIVE`, raises `ValueError`.
  - Adds `ActivityRecord` to activities list; `touch()`.
- Repository behavior:
  - Save to persist updated activities. No index changes needed.

### 5) Revoke access
- Intent: Permanently remove user's access to the course.
- Actions: `access_record.revoke_access(reason)` then `save`.
- Domain behavior:
  - If already `REVOKED`, raises `ValueError`.
  - Sets `status = REVOKED`, raises `AccessRevoked` event; `touch()`.
- Repository behavior:
  - `save(access_record)` updates status index: removes from `ACTIVE`, adds to `REVOKED`.

### 6) Expire access
- Intent: Automatically expire access when expiration date is reached.
- Actions: `access_record.expire_access(current_time)` then `save`.
- Domain behavior:
  - If `status != ACTIVE`, no-op.
  - If `current_time >= access_expires_at`, sets `status = EXPIRED`, raises `AccessExpired` event; `touch()`.
- Repository behavior:
  - `save(access_record)` updates status index: removes from `ACTIVE`, adds to `EXPIRED`.

### 7) Reactivate access
- Intent: Restore access for previously expired or revoked users.
- Actions: `access_record.reactivate_access(new_expiration)` then `save`.
- Domain behavior:
  - If `status not in [EXPIRED, REVOKED]`, raises `ValueError`.
  - Sets `status = ACTIVE`, updates `access_expires_at`; `touch()`.
- Repository behavior:
  - `save(access_record)` updates status index: removes from current status, adds to `ACTIVE`.

### 8) Check refund eligibility
- Intent: Determine if access can be refunded based on policy rules.
- Actions: `access_record.can_be_refunded(current_time, refund_policy)`.
- Domain behavior:
  - If `status != ACTIVE`, returns `False`.
  - Delegates to `refund_policy.is_refund_allowed()` with purchase date, current date, and progress.
- Repository behavior: No persistence needed; read-only operation.

### 9) Check access status
- Intent: Verify if user currently has active access to the course.
- Actions: `access_record.is_active()`.
- Domain behavior:
  - Returns `True` only if `status == ACTIVE` and not expired.
  - Checks expiration: `current_time < access_expires_at` (if set).
- Repository behavior: No persistence needed; read-only operation.

### 10) Check if access has expired
- Intent: Determine if access has passed its expiration date.
- Actions: `access_record.has_expired()`.
- Domain behavior:
  - Returns `True` if `status == EXPIRED` or `current_time >= access_expires_at`.
- Repository behavior: No persistence needed; read-only operation.

### 11) Query access by user
- Intent: Find all access records for a specific user.
- Actions: `repo.get_by_user(user_id)`.
- Repository behavior:
  - Uses user index to efficiently find all access records for the user.
  - Returns list of `AccessRecord` objects.

### 12) Query access by course
- Intent: Find all access records for a specific course.
- Actions: `repo.get_by_course(course_id)`.
- Repository behavior:
  - Uses course index to efficiently find all access records for the course.
  - Returns list of `AccessRecord` objects.

### 13) Query access by status
- Intent: Find access records in a specific status (active, expired, revoked, pending).
- Actions: `repo.get_by_status(status)` or specific methods like `get_active_access()`.
- Repository behavior:
  - Uses status index for efficient querying.
  - Returns list of `AccessRecord` objects.

### 14) Query user-course access
- Intent: Check if a specific user has access to a specific course.
- Actions: `repo.get_user_course_access(user_id, course_id)`.
- Repository behavior:
  - Uses user-course index for efficient lookup.
  - Returns single `AccessRecord` or `None`.

### 15) Query active access records
- Intent: Find all currently active access records.
- Actions: `repo.get_active_access()`.
- Repository behavior:
  - Uses status index to find all `ACTIVE` access records.
  - Returns list of `AccessRecord` objects.

### 16) Query expired access records
- Intent: Find all expired access records.
- Actions: `repo.get_expired_access()`.
- Repository behavior:
  - Uses status index to find all `EXPIRED` access records.
  - Returns list of `AccessRecord` objects.

### 17) Query revoked access records
- Intent: Find all revoked access records.
- Actions: `repo.get_revoked_access()`.
- Repository behavior:
  - Uses status index to find all `REVOKED` access records.
  - Returns list of `AccessRecord` objects.

### 18) Query user's active courses
- Intent: Find all courses a user currently has active access to.
- Actions: `repo.get_user_active_courses(user_id)`.
- Repository behavior:
  - Gets user access records, filters for `ACTIVE` status.
  - Returns list of `AccessRecord` objects.

### 19) Query course's active users
- Intent: Find all users who currently have active access to a course.
- Actions: `repo.get_course_active_users(course_id)`.
- Repository behavior:
  - Gets course access records, filters for `ACTIVE` status.
  - Returns list of `AccessRecord` objects.

### Access Status Transitions
- **ACTIVE** → **REVOKED** (via `revoke_access`)
- **ACTIVE** → **EXPIRED** (via `expire_access`)
- **EXPIRED/REVOKED** → **ACTIVE** (via `reactivate_access`)

### Invariants and Constraints
- Identity via `id: AccessId` (an `Identifier`); equality by `id`.
- Timestamps managed by `Entity`; `touch()` updates `updated_at`.
- Events buffered via `add_domain_event` and later dispatched.
- Progress cannot decrease (enforced in `update_progress`).
- Only `ACTIVE` access allows progress updates and activity recording.
- Access expiration must be after purchase date (enforced in `grant_access`).
- Status transitions are strictly controlled by business rules.

### Integration Notes
- Event bus: consume `CourseAccessGranted`, `AccessRevoked`, `AccessExpired`, `ProgressUpdated`, `CourseCompleted` for:
  - User dashboard updates
  - Course analytics and reporting
  - Progress tracking and notifications
  - Access control and security
  - Refund processing workflows
- Read models: maintain query-optimized views (by user, by course, by status, by progress).
- Application services: orchestrate access management, progress tracking, and cross-aggregate rules.

### Error Cases (expected)
- Update progress on inactive access → `ValueError`.
- Decrease progress → `ValueError`.
- Record activity on inactive access → `ValueError`.
- Mark completed on inactive access → `ValueError`.
- Revoke already revoked access → `ValueError`.
- Reactivate non-expired/non-revoked access → `ValueError`.
- Grant access with expiration before purchase date → `ValueError`.

### Business Rules
- Access records start in `ACTIVE` status and can transition to `REVOKED` or `EXPIRED`.
- Only `ACTIVE` access allows progress updates and activity recording.
- Progress cannot decrease (monotonic increase only).
- Access expiration is optional but must be after purchase date if set.
- Course completion automatically sets progress to 100%.
- Activity recording is only allowed for active access.
- Refund eligibility depends on access status and policy rules.

### Activity Types and Tracking
- **LOGIN**: User logs into the course platform
- **VIDEO_WATCHED**: User watches course videos
- **QUIZ_COMPLETED**: User completes course quizzes
- **LESSON_COMPLETED**: User completes course lessons
- **ASSIGNMENT_SUBMITTED**: User submits course assignments
- **FORUM_POST**: User posts in course forums
- **DOWNLOAD**: User downloads course materials

### Progress and Completion Logic
- Progress is tracked as a percentage (0.0 to 100.0).
- Progress updates trigger `ProgressUpdated` events.
- When progress reaches 100%, `CourseCompleted` event is automatically raised.
- Progress cannot decrease to maintain data integrity.
- Course completion is a terminal state for progress tracking.

### Access Expiration Logic
- Expiration is optional (can be `None` for unlimited access).
- If set, expiration must be after purchase date.
- Expired access cannot be used for progress updates or activity recording.
- Expired access can be reactivated with new expiration date.
- Access expiration is checked against current time, not stored status.
