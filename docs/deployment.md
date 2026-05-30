# Deployment Guide

This guide covers three supported production paths:

1. Single-server Docker Compose with Nginx and HTTPS
2. Vercel frontend plus Render backend
3. Vercel frontend plus Railway backend

## Environment Variables

Copy the production template:

```bash
cp .env.production.example .env.production
```

Backend variables:

- `APP_ENV=production`
- `FRONTEND_ORIGIN`
- `DATABASE_URL`
- `REDIS_URL`
- `NEWS_API_KEY`
- `OPENAI_API_KEY`
- `LLM_PROVIDER`
- `LLM_MODEL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_SIGN_BUCKET`
- `FFMPEG_PATH`
- `ADMIN_API_TOKEN`
- `REQUIRE_PRODUCTION_SECRETS=true`

Frontend variables:

- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

Never commit `.env.production`, Supabase service keys, OpenAI keys, NewsAPI keys, or database passwords.

## Docker Compose Production

Production files:

- `docker-compose.prod.yml`
- `.env.production.example`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `nginx/templates/signcast.conf.template`
- `nginx/snippets/*`

Start services:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

Check health:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
curl https://your-domain.com/health
```

## HTTPS

Nginx is configured for Let's Encrypt certificates under:

```text
certbot/conf
certbot/www
```

First certificate issue flow:

1. Point DNS `A` record to the server.
2. Temporarily run an HTTP-only Nginx config, or render `nginx/templates/signcast.local.conf.template`.
3. Request a certificate:

```bash
docker run --rm \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d your-domain.com \
  --email admin@your-domain.com \
  --agree-tos \
  --no-eff-email
```

4. Set `DOMAIN=your-domain.com` in `.env.production`.
5. Start production compose.

Renewal:

```bash
docker run --rm \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot renew
docker compose --env-file .env.production -f docker-compose.prod.yml exec nginx nginx -s reload
```

Schedule renewal with cron twice daily.

## CI/CD

GitHub Actions workflows:

- `.github/workflows/ci.yml`: backend lint/tests, frontend lint/tests/build, Docker build
- `.github/workflows/deploy-vercel.yml`: frontend deploy to Vercel
- `.github/workflows/deploy-backend-render.yml`: backend deploy hook for Render
- `.github/workflows/deploy-backend-railway.yml`: manual Railway backend deploy

Required GitHub secrets:

Vercel:

- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `VERCEL_TOKEN`

Render:

- `RENDER_DEPLOY_HOOK_URL`

Railway:

- `RAILWAY_TOKEN`
- `RAILWAY_BACKEND_SERVICE`

## Vercel Frontend

Recommended settings:

- Project root: repository root
- Framework: Next.js
- Build command: `cd frontend && npm install && npm run build`
- Output: `frontend/.next`

Environment variables:

- `NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com` or `https://your-render-service.onrender.com`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

The `vercel.json` file documents the expected build behavior.

## Render Backend

Use `render.yaml` as the blueprint.

Render provisions:

- Docker web service from `backend/Dockerfile`
- PostgreSQL database
- Redis instance

Set secrets in Render:

- `FRONTEND_ORIGIN`
- `NEWS_API_KEY`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ADMIN_API_TOKEN`
- `LLM_PROVIDER=openai`

Health check path:

```text
/health
```

## Railway Backend

Use `railway.json`.

Create services:

- Backend service from `backend/Dockerfile`
- PostgreSQL plugin
- Redis plugin

Set variables:

- `DATABASE_URL`
- `REDIS_URL`
- `FRONTEND_ORIGIN`
- `NEWS_API_KEY`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ADMIN_API_TOKEN`
- `LLM_PROVIDER=openai`

Deploy manually:

```bash
railway up --service signcast-ai-backend
```

## Monitoring

Built-in endpoints:

- `GET /health`: liveness and environment
- `GET /metrics`: simple request counters

Recommended production monitoring:

- UptimeRobot, Better Stack, or Pingdom against `/health`
- Render/Railway service metrics for CPU, memory, restart count
- Supabase dashboard for storage and auth activity
- Postgres alerts for disk usage and connection count
- Redis memory usage alerts

Recommended alert thresholds:

- `/health` unavailable for 2 minutes
- Backend restarts more than 3 times in 10 minutes
- Postgres disk above 80 percent
- Redis memory above 80 percent
- Sequence generation failures above normal baseline

## Logging

Backend logs are structured with method, path, status, and duration.

Docker Compose logging uses `json-file` rotation:

```yaml
max-size: "10m"
max-file: "5"
```

Useful commands:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml logs -f backend
docker compose --env-file .env.production -f docker-compose.prod.yml logs -f nginx
```

For hosted providers, stream logs from Render/Railway and connect them to Better Stack, Datadog, Logtail, or another log drain.

## Backup Strategy

Database backups:

- Managed providers: enable daily automated backups and point-in-time recovery when available.
- Docker Compose: use `scripts/backup_postgres.sh`.

Manual backup:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec postgres sh /scripts/backup_postgres.sh
```

Alternative from host:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > backups/signcast-manual.sql.gz
```

Retention:

- Keep daily backups for 14 days.
- Keep weekly backups for 8 weeks.
- Keep monthly backups for 12 months.

Storage backups:

- Supabase Storage sign clips should be treated as production assets.
- Mirror the `sign-videos` bucket weekly to object storage such as S3, R2, or another Supabase project.

Restore drill:

1. Create a fresh database.
2. Restore the latest backup.
3. Run backend health checks.
4. Verify sign dictionary entries and sequence generation.
5. Document restore time and any missing assets.

## Release Checklist

1. CI passes on `main`.
2. Environment variables are present in target platform.
3. Database migration has been applied.
4. Supabase Storage bucket exists.
5. `/health` responds.
6. Frontend can reach backend.
7. News fetch works.
8. Sign clip upload works.
9. Sequence generation works with FFmpeg.
10. Backups are enabled and tested.
11. Admin dashboard access works with `X-Admin-Token`.
12. Supabase JWT verification is enabled before real user account launch.
