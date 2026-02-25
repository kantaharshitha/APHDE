# Stratify Multi-User + Authentication Implementation Plan

## Objective
Implement multi-user authentication and strict tenant isolation in Stratify while preserving deterministic decision behavior and existing engine formulas.

## Guiding Constraints
- No ML additions.
- No decision/scoring/confidence/context formula changes.
- All user data must be isolated by `user_id`.
- Auth/session logic must remain separate from decision engine logic.
- Determinism must hold per-user.

## Delivery Model
Workstreams run in sequence with controlled overlap.
- A: Data model and migration
- B: Auth and session layer
- C: Repository/service scoping
- D: UI auth gate + user-aware navigation
- E: Governance determinism + isolation validation
- F: Stratify branding alignment
- G: Test hardening + release prep

---

## Workstream A: Data Model + Migration

### Scope
- Create `users` table.
- Add `user_id` to all user-owned tables.
- Backfill existing data to a default migrated user.
- Add foreign keys + performance indexes.

### Tasks
1. Create schema migration script `scripts/migrations/00X_multi_user_auth.sql`.
2. Add `users` table:
   - `id`, `email`, `password_hash`, `display_name`, `created_at`, `last_login_at`, `is_active`.
3. For each user-owned table:
   - Add nullable `user_id`.
   - Backfill using default user id.
   - Enforce `NOT NULL`.
   - Add `(user_id, created_at/log_date)` index.
4. Add FK constraints to `users(id)`.
5. Add migration verification script to count null `user_id` rows.

### Exit Criteria
- All scoped tables include non-null `user_id`.
- Migration runs idempotently on clean + existing DB copies.
- Zero orphan rows.

---

## Workstream B: Auth + Session Layer

### Scope
- Add signup/login/logout with hashed passwords.
- Add auth guard utilities.

### Tasks
1. Add auth module:
   - `core/auth/passwords.py` (Argon2id preferred; fallback bcrypt if needed)
   - `core/auth/service.py` (create_user, authenticate_user, logout)
   - `core/auth/session.py` (set/get/clear auth session keys)
2. Add users repository:
   - `core/data/repositories/user_repo.py`
3. Implement login state contract in `st.session_state`:
   - `auth_user_id`, `auth_email`, `auth_display_name`, `is_authenticated`.
4. Add auth event timestamps (`last_login_at`).

### Exit Criteria
- User can sign up, log in, log out.
- Passwords are hashed and verified (no plaintext at rest).

---

## Workstream C: Repository + Service User Scoping

### Scope
- Refactor all repositories and services to require `user_id`.
- Eliminate global/non-scoped reads.

### Tasks
1. Audit repositories/services for missing `user_id` filters.
2. Update method signatures to include `user_id`.
3. Enforce user scoping in SQL queries:
   - `WHERE user_id = ?` for every read/write on user-owned data.
4. Refactor service layer wrappers (`run_evaluation`, insights, action center, governance).
5. Add guard assertions for missing user context.

### Exit Criteria
- No user-owned query executes without `user_id`.
- No cross-user rows returned in service outputs.

---

## Workstream D: Streamlit UI Auth + User Context

### Scope
- Add pre-auth gate and authenticated app shell.
- Display user identity and per-user goal in sidebar.

### Tasks
1. Add login/signup page (single entry route before app pages).
2. Add auth guard at page entry:
   - redirect unauthenticated users to login screen.
3. Update sidebar:
   - logged-in user display
   - per-user active goal
   - logout action
4. Ensure all page actions pass session `user_id` to services.
5. Keep current visual hierarchy + palette unchanged.

### Exit Criteria
- Unauthenticated users cannot access app pages.
- Authenticated users only view their own data.

---

## Workstream E: Determinism + Governance Alignment

### Scope
- Maintain per-user determinism and governance trace consistency.

### Tasks
1. Ensure `decision_runs` and governance artifacts include `user_id`.
2. Ensure output hash inputs are user-scoped only.
3. Ensure history analytics and diffs are user-scoped.
4. Add determinism replay test for same user/same inputs.
5. Add negative test for different users with different data.

### Exit Criteria
- Determinism verifier passes per-user replay.
- Governance panels never show other users’ run metadata.

---

## Workstream F: Stratify Branding Alignment

### Scope
- Replace visible product naming in UI/docs.

### Tasks
1. Update Streamlit UI strings and headers.
2. Update README and docs references.
3. Update PRD and implementation docs names where needed.
4. Keep package/module internals stable unless required.

### Exit Criteria
- User-visible surfaces consistently say “Stratify”.

---

## Workstream G: Testing + Release Preparation

### Test Matrix

#### Unit Tests
- password hash/verify behavior
- user repo CRUD + uniqueness
- auth session set/clear helpers

#### Integration Tests
- signup -> login -> logout flow
- user A data isolation from user B on:
  - logs
  - decisions
  - recommendations
  - insights
  - governance history
- migration backfill correctness on legacy DB

#### Determinism Tests
- same user/same inputs/version triad => identical output hash
- verify no hash pollution from other users

### Release Tasks
1. Backup current sqlite DB.
2. Run migration in staging copy.
3. Run full test suite.
4. Manual smoke with 2 accounts.
5. Roll out and monitor logs.

### Exit Criteria
- All tests pass.
- Manual two-user isolation confirmed.
- Migration verification checklist complete.

---

## Suggested File-Level Changes

### New
- `core/auth/passwords.py`
- `core/auth/service.py`
- `core/auth/session.py`
- `core/data/repositories/user_repo.py`
- `scripts/migrations/00X_multi_user_auth.sql`
- `tests/integration/test_auth_flow.py`
- `tests/integration/test_multi_user_isolation.py`
- `tests/integration/test_migration_backfill.py`

### Modified (examples)
- `core/data/repositories/*.py` (user scope)
- `core/services/*.py` (require/pass `user_id`)
- `app/main.py` (auth gate)
- `app/ui/layout.py` (identity/logout)
- `app/pages/*.py` (user-scoped data access)
- `README.md` (Stratify naming + auth usage)

---

## Milestones

### M1 — Schema Ready
- Users table + user_id columns + indexes + backfill script done.

### M2 — Auth Ready
- Signup/login/logout functional, secure password hashing active.

### M3 — Scoped Engine Ready
- All services/repositories user-scoped.

### M4 — UI Ready
- Auth gate + user-aware sidebar + page scoping complete.

### M5 — Governance + Determinism Ready
- Per-user hashes/history/diff verified.

### M6 — Release Ready
- Rename complete, tests green, migration validated, docs updated.

---

## Rollback Strategy
- Keep DB backup before migration.
- Migration script wrapped in transaction where possible.
- If rollback needed:
  - restore sqlite backup
  - revert auth gate entrypoint
  - redeploy previous commit.

---

## Definition of Done Checklist
- [ ] Multi-user auth implemented (signup/login/logout)
- [ ] Password hashing secure and verified
- [ ] Data isolation enforced for every user-owned entity
- [ ] Service/repository interfaces require `user_id`
- [ ] No cross-user leakage in UI or APIs
- [ ] Per-user determinism preserved and tested
- [ ] Legacy data migrated to default user safely
- [ ] Stratify naming is consistent in user-visible surfaces/docs
- [ ] Documentation updated with setup + migration instructions
- [ ] Release smoke tests completed successfully
