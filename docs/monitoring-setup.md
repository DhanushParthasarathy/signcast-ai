# Monitoring Setup

## Health Checks

- Backend: `GET /health`
- Metrics: `GET /metrics`
- Frontend: Vercel deployment status and synthetic page checks.

## Alerts

- Backend health check failure for 3 consecutive checks.
- API p95 latency above 2 seconds.
- 5xx rate above 2 percent.
- Sign sequence failures above 5 per hour.
- Missing gloss count spike.
- OpenAI or NewsAPI request failures.

## Logs

- Backend emits structured request logs with method, path, status, and duration.
- Configure Render/Railway log drains to a provider such as Better Stack, Datadog, or Grafana Cloud.
- Keep admin actions and upload failures searchable.
