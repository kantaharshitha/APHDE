# Stratify Multi-User Authentication & Tenant Isolation PRD

## 1. Executive Summary
Stratify is evolving from a single-user deterministic decision intelligence engine into a secure multi-user application with strict tenant isolation.
This release adds account authentication, user-scoped data access, and per-user governance continuity while preserving all deterministic decision logic and formulas.

This PRD covers:
- Authentication (signup/login/logout)
- Multi-tenant schema + query isolation
- Migration from existing single-user data
- Streamlit UX updates
- Security, testing, and rollout

## 2. Goals / Non-Goals

### Goals
- Add user accounts with secure password auth.
- Isolate all data and evaluations per `user_id`.
- Ensure all reads/writes are user-scoped.
- Preserve deterministic behavior per user.
- Keep decision engine formulas unchanged.
- Keep branding consistent as Stratify across UI/docs.

### Non-Goals
- No ML/prediction features.
- No changes to scoring/confidence/context formulas.
- No multi-organization RBAC in this phase.
- No major backend framework rewrite.

## 3. Auth Approach Decision

### Selected Option: Custom Auth in Existing Python App (SQLite + Argon2/Bcrypt)
Reasoning:
- Fastest path with current Streamlit + SQLite architecture.
- Minimal moving parts, no external auth dependency.
- Full control over deterministic user scoping and session behavior.
- Keeps architecture coherent for portfolio/interview defense.

### Deferred Alternatives
- Supabase Auth: stronger production path, but introduces external dependency and migration complexity.
- streamlit-authenticator: fast UI integration but less control over long-term auth model and DB coupling.

## 4. Personas & User Stories

### Persona A: Individual User
- As a user, I can sign up and log in.
- I only see my logs, evaluations, recommendations, and history.
- My runs are deterministic for my data and selected versions.

### Persona B: Product Admin/Developer
- As a maintainer, I can verify no cross-user data leakage.
- I can migrate old single-user data safely to a default account.
- I can audit per-user versioned runs and hashes.

## 5. Architecture Overview (with Auth + Isolation)

### Existing Layers (unchanged logic)
- Data Layer (SQLite)
- Signal Engine
- Goal Strategy Layer
- Decision Engine
- Confidence Layer
- Context Engine
- Governance Layer
- Streamlit UI

### New Additions
- Auth Layer (users + password verification + session binding)
- User Scope Guard in service/repository interfaces:
  - all calls require `user_id`
  - no “global latest” queries without user filter

### Key Rule
Auth/session management remains separate from decision logic modules.

## 6. Data Model Changes (ERD-style)

### New Table: `users`
- `id` (PK)
- `email` (unique, indexed)
- `password_hash`
- `display_name` (nullable)
- `created_at`
- `last_login_at` (nullable)
- `is_active` (default true)

### Existing Tables (add `user_id` FK + index)
Apply to all user-owned entities:
- weight/calorie/workout logs
- context inputs
- goals/configurations
- decision runs/evaluations
- recommendations
- confidence outputs/breakdowns
- stagnation alerts
- weekly insights/history
- governance metadata records

### Indexing
For each user-scoped table:
- composite index: `(user_id, created_at/log_date)`
- optional query-specific indexes for run lookups `(user_id, decision_id)`

## 7. Auth Flows

### Signup
1. Enter email, password, optional display name.
2. Validate email uniqueness.
3. Hash password with Argon2id (preferred) or bcrypt.
4. Create user row.
5. Initialize authenticated session.

### Login
1. Enter email/password.
2. Lookup user by email.
3. Verify password hash.
4. Set `st.session_state.user_id`, `email`, `display_name`.
5. Update `last_login_at`.

### Logout
1. Clear auth keys from `session_state`.
2. Redirect to login screen.

### Optional (Phase 1.1)
- Password reset token flow via email provider.

## 8. Streamlit UI Changes

### Entry Gate
- If unauthenticated: render login/signup page only.
- If authenticated: render full app.

### Sidebar
Show:
- Logged-in user display/email
- Active goal for current user
- Logout button
- Version footer remains visible

### Page Scope
All pages/services must read/write using current session `user_id` only.

## 9. Migration Plan (Single-user to Multi-user)

1. Add `users` table.
2. Create `default_migrated_user` (from existing local user profile).
3. Add nullable `user_id` columns to scoped tables.
4. Backfill all existing rows with `default_migrated_user.id`.
5. Set `user_id` to NOT NULL.
6. Add FKs + indexes.
7. Refactor repositories/services to require `user_id`.
8. Run data leakage validation queries.
9. Enable auth gate in UI.

## 10. Determinism & Governance Considerations

- Determinism remains defined per user:
  - same user
  - same inputs
  - same versions
  - same output hash
- `decision_runs` and governance records must include `user_id`.
- Version triad (`engine_version`, `confidence_version`, `context_version`) remains unchanged.
- Output hashing must use user-scoped payload only.

## 11. Security Requirements

### Mandatory
- Password hashes only (no plaintext ever).
- Argon2id or bcrypt with safe parameters.
- Session keys server-side only in Streamlit session state.
- All repository methods enforce `user_id` filter.
- Reject/ignore client-supplied arbitrary `user_id`.

### Recommended
- Basic login attempt throttling.
- Audit auth events (login success/failure, signup).

## 12. Testing Strategy

### Unit
- Password hash/verify
- Auth validators
- User-scoped repository filters

### Integration
- Signup/login/logout flow
- User A cannot access User B records (all key services/pages)
- Migration backfill correctness
- Determinism unchanged for same user/same inputs

### Regression
- Existing decision outputs unchanged after scoping for migrated default user.

## 13. Risks & Mitigations

- Risk: missed unscoped query leaks data
  - Mitigation: repository contract change + test coverage + query audit checklist.

- Risk: migration mistakes orphan data
  - Mitigation: transactional migration + backup + verification script.

- Risk: session handling bugs in Streamlit reruns
  - Mitigation: centralized auth guard utility and page-level entry checks.

## 14. Rollout Plan

1. Implement schema + migration scripts.
2. Refactor repositories/services for mandatory `user_id`.
3. Add auth UI gate + session management.
4. Run test suite + leakage checks.
5. Complete Stratify branding alignment in UI/docs.
6. Deploy locally/staging and validate with two test accounts.
7. Release.

## 15. Rename Plan (Stratify Branding)

Update:
- UI labels, headers, sidebar text
- README and architecture docs
- PRD and implementation plan documents
- Static copy strings in Streamlit pages

(Keep code package/module names unchanged in this phase unless needed for compatibility.)

## 16. Definition of Done

- [ ] Signup/login/logout functional
- [ ] Secure password hashing in place
- [ ] All user-owned tables have `user_id` + indexes
- [ ] All queries and services are user-scoped
- [ ] User A/B isolation verified by tests
- [ ] Determinism hash remains valid per-user
- [ ] Migration completed with default user backfill
- [ ] No cross-user leakage in UI
- [ ] Stratify naming is consistent in UI/docs
- [ ] Documentation updated with auth + tenant model
