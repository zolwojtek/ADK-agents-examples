## User Stories and Flows

### 1) Register a new user
- Intent: Create an account with email and profile details.
- Actions:
  - Client submits email and profile.
  - System calls `User.create_user(email, profile)`.
- Domain behavior:
  - New `User` is instantiated with `id: UserId`, `status: INACTIVE`, `email_verified: False`.
  - `UserRegistered` event is raised via `add_domain_event`.
  - Timestamps set in `Entity` (`created_at`, `updated_at`).
- Repository behavior:
  - `UserRepository.save(user)` persists the user and indexes `email -> user.id`.
  - If email already exists for a different user, raise `ValueError`.

### 2) Verify email (identity)
- Intent: Confirm ownership of the email.
- Actions:
  - System calls `user.verify_identity()` after successful verification flow.
- Domain behavior:
  - If already verified, raises `ValueError`.
  - Sets `email_verified = True`, `status = ACTIVE`, calls `touch()`.
- Repository behavior:
  - Save to persist updated fields. No email index changes.

### 3) Update profile
- Intent: Change first/last name or profile data.
- Actions:
  - System calls `user.update_profile(new_profile)`.
- Domain behavior:
  - If `status in {BANNED, DELETED}`, raises `ValueError`.
  - Updates profile; raises `UserProfileUpdated` event; calls `touch()`.
- Repository behavior:
  - Save to persist updated profile. No email index changes.

### 4) Change email
- Intent: Use a new email address.
- Actions:
  - System calls `user.change_email(new_email)`.
- Domain behavior:
  - If `status in {BANNED, DELETED}`, raises `ValueError`.
  - If `new_email == current`, no-op.
  - Sets `email = new_email`, `email_verified = False`.
  - Raises `UserEmailChanged` event; calls `touch()`.
- Repository behavior:
  - `save(user)` enforces uniqueness: if `new_email` is mapped to a different `user.id`, raises `ValueError`.
  - On update, removes previous email mapping for the same `user.id` and re-indexes the new email.

### 5) Activate account
- Intent: Enable account usage.
- Actions: `user.activate()`.
- Domain behavior:
  - If `status == ACTIVE`, raises `ValueError`.
  - If `status == DELETED`, raises `ValueError`.
  - Sets `status = ACTIVE`; `touch()`.

### 6) Deactivate account
- Intent: Temporarily disable account.
- Actions: `user.deactivate(reason)`.
- Domain behavior:
  - If `status == DELETED`, raises `ValueError`.
  - Sets `status = INACTIVE`; `touch()`.

### 7) Ban account
- Intent: Permanently block due to violations.
- Actions: `user.ban(reason)`.
- Domain behavior:
  - If `status == DELETED`, raises `ValueError`.
  - Sets `status = BANNED`; `touch()`.

### 8) Soft delete account
- Intent: Mark as deleted without physical removal.
- Actions: `user.mark_as_deleted()`.
- Domain behavior:
  - Sets `status = DELETED`; `touch()`.
  - Subsequent mutations (activate/deactivate/ban/profile/email) are restricted per invariants.

### 9) Manage access references
- Intent: Link to course access records stored elsewhere.
- Actions:
  - Add: `user.add_access_ref(access_ref)` prevents duplicates.
  - Remove: `user.remove_access_ref(access_id)` drops by `AccessId` value.
- Domain behavior:
  - Both operations call `touch()`.

### Invariants and Constraints
- Identity is represented by `id: UserId` (an `Identifier`), equality by `id`.
- Timestamps managed by `Entity` base class; `touch()` updates `updated_at`.
- Events are buffered on the aggregate via `add_domain_event` and later dispatched.
- Email uniqueness is enforced in `UserRepository.save` across both creates and updates.
- Mutations blocked for `BANNED`/`DELETED` users where applicable.

### Integration Notes
- Event bus: consume `UserRegistered`, `UserProfileUpdated`, `UserEmailChanged` for projections (e.g., read models, notifications).
- Read models: maintain query-optimized views (by email, by name, by status).
- Application services: orchestrate flows (registration, verification, profile edits) without embedding domain rules.

### Error Cases (expected)
- Register with existing email → `ValueError`.
- Verify already-verified email → `ValueError`.
- Update profile when `BANNED`/`DELETED` → `ValueError`.
- Change email to one used by a different user → `ValueError`.
- Activate when already `ACTIVE` or when `DELETED` → `ValueError`.

