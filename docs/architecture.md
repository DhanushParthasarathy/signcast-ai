# Architecture

SignCast AI is a monorepo with four top-level workspaces:

```text
frontend/   Next.js 15 application and typed UI components
backend/    FastAPI service for news, summarization, gloss, and sign sequence APIs
database/   Supabase PostgreSQL schema, RLS policies, and migrations
docs/       Product, deployment, and API documentation
```

## Request Flow

1. The frontend calls `GET /news` to load trending or searched headlines.
2. The article page calls `GET /news/{id}`.
3. The backend creates a concise summary, simplifies it, translates simple English into ASL gloss, and maps each gloss token to a sign clip.
4. The frontend renders the original article metadata, simplified text, ASL gloss, and a clip-by-clip player.

## AI Boundary

The MVP does not generate motion. AI is only used for text transformation:

- summarization
- simple English rewriting
- ASL gloss generation

Animation is deterministic and dictionary-driven through `sign_dictionary`.

## Production Notes

- Use Supabase Auth for users and admin identity.
- Store video clips in Supabase Storage or another CDN and save URLs in `sign_dictionary`.
- Queue high-volume summarization jobs before moving beyond MVP traffic.
- Keep ASL gloss reviewed by fluent signers before public release.
