# Production Readiness Audit

Date: 2026-05-30

## Critical Issues Fixed

- Admin endpoints and sign dictionary write operations now require `X-Admin-Token`.
- Production startup now fails when required secrets are missing or when SQLite/rule-based LLM settings are used in production.
- User feedback, translation ratings, bug reports, search events, and analytics tables are represented in SQLAlchemy and SQL migrations.
- Feedback APIs, admin review APIs, and analytics aggregation were added.
- The Nginx HTTPS redirect template now preserves runtime `$host` and `$request_uri` variables after envsubst.

## Remaining Launch Blockers

- Supabase Auth JWT verification is still represented by the MVP `X-User-Id` bridge. Replace this with JWT verification before collecting real user data.
- `pytest` is not installed in the local runtime, so the test suite could not be executed in this workspace.
- `npm` is unavailable on PATH, so frontend typecheck/build could not be run locally.
- A Git repository is not initialized in this workspace, so `feature/avatar-research` could not be created locally.

## Audit Findings

### TODOs and Mock Implementations

- The NewsAPI mock fallback is acceptable only for local development. Production validation now requires `NEWS_API_KEY`.
- The LLM rule-based fallback is acceptable only for local development. Production validation now requires `LLM_PROVIDER=openai`.

### Hardcoded Values

- Local defaults remain in `.env.example` and development configs.
- Production configs must set `FRONTEND_ORIGIN`, `NEXT_PUBLIC_API_BASE_URL`, `DATABASE_URL`, and `ADMIN_API_TOKEN`.

### Security

- Admin APIs are token gated.
- CORS is environment-driven.
- Service role keys must stay backend-only.
- Replace `X-User-Id` with Supabase JWT validation before public account launch.

### Error Handling and Loading States

- Admin dashboard now handles failed admin loads with a visible message.
- Feedback submission has disabled submit and visible success/error states.

### Tests

- Added feedback and search analytics repository tests.
- Existing Python modules compile successfully with `python -m compileall app tests`.
- Full unit test execution is blocked by missing `pytest`.

## Verification

- Passed: `python -m compileall app tests`
- Blocked: `python -m pytest` because `pytest` is not installed.
- Blocked: frontend build/typecheck because `npm` is not available on PATH.
