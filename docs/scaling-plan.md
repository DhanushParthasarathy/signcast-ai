# Scaling Plan

## First 1,000 Users

- Run one FastAPI web service and Redis cache.
- Use Supabase pooled connections.
- Keep sequence rendering in background tasks for short videos.
- Cache news lists for 5 minutes and article details for 15 minutes.

## 10,000+ Users

- Split FastAPI API and FFmpeg rendering workers.
- Move sign sequence generation to a queue such as Redis Queue, Celery, or Cloud Tasks.
- Store generated MP4 outputs behind a CDN.
- Add database indexes for article popularity, feedback status, and search events.
- Add per-user and per-IP rate limits.

## High Availability

- Deploy at least two backend instances.
- Use managed Redis with persistence where available.
- Run database backups daily and before migrations.
- Keep storage lifecycle policies for temporary render files.
