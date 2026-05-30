# SignCast AI

SignCast AI converts everyday news into simplified, sign-language-friendly article experiences. It fetches headlines, summarizes articles, converts summaries into simple English, translates that text into ASL gloss, and plays a sequence of prerecorded sign clips from a managed sign dictionary.

## Project Layout

```text
frontend/   Next.js 15, React, TypeScript, Tailwind CSS, Framer Motion
backend/    FastAPI, Python 3.12, NewsAPI, AI pipeline, Supabase access
database/   Supabase PostgreSQL schema and migrations
docs/       Architecture, API, and deployment documentation
```

## Quick Start

1. Copy environment files:

```bash
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
```

2. Fill in Supabase and NewsAPI credentials.

3. Run with Docker:

```bash
docker compose up --build
```

Frontend: http://localhost:3000  
Backend: http://localhost:8000/docs

## Development

Backend:

```bash
cd backend
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload
```

Backend architecture:

```text
app/api/            REST route handlers
app/core/           settings and environment config
app/db/             SQLAlchemy engine, session, PostgreSQL models
app/repositories/   article cache and sign dictionary persistence
app/schemas/        Pydantic request and response schemas
app/services/       NewsAPI, scheduled refresh, LLM abstraction, ASL gloss, sign sequencing
```

The news service uses PostgreSQL for durable article caching, Redis for response caching and rate limiting, and a 30-minute background refresh job for default headline feeds.

Frontend:

```bash
cd frontend
npm install
npm run dev
npm test
```

## MVP Features

- Trending news, search, and category filtering
- Article detail page with simplified summary and ASL gloss
- Dictionary-driven sign clip player
- Supabase Auth login/signup screen
- Admin sign dictionary management scaffold
- Saved news and watch history dashboard scaffold
- Supabase PostgreSQL schema with RLS policies
- Docker Compose setup for local full-stack development
