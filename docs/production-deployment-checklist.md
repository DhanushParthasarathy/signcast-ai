# Production Deployment Checklist

## Backend

- Set `APP_ENV=production`.
- Set `DATABASE_URL` to Supabase pooled PostgreSQL.
- Set `NEWS_API_KEY`, `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `ADMIN_API_TOKEN`.
- Set `LLM_PROVIDER=openai`.
- Set `FRONTEND_ORIGIN` to the Vercel production URL.
- Confirm `/health` returns `{"status":"ok"}`.
- Confirm `/metrics` is reachable only from trusted monitoring infrastructure.

## Frontend

- Set `NEXT_PUBLIC_API_BASE_URL` to the backend HTTPS origin.
- Set Supabase public URL and anon key.
- Run `npm run build` in CI.
- Verify Home, Article, Dashboard, Admin, About, Accessibility, Privacy, Terms, Contact, and FAQ pages.

## Database and Storage

- Apply `database/migrations/001_initial_schema.sql`.
- Enable Supabase Auth and configure redirect URLs.
- Create Supabase Storage buckets for sign clips and generated sequences.
- Verify RLS policies for user-owned feedback, ratings, bug reports, saves, watch history, and preferences.

## Operations

- Enable GitHub Actions secrets.
- Configure Render or Railway backend service.
- Configure Vercel frontend project.
- Configure daily PostgreSQL backups.
- Configure log drains and uptime checks.
