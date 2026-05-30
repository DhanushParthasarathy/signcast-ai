# Cost Estimate

Actual cost depends on traffic, clip storage, OpenAI model usage, and NewsAPI tier.

## MVP Launch

- Vercel frontend: free to low-cost hobby/pro tier.
- Render or Railway backend: one small web service plus optional worker.
- Supabase: free or pro tier depending on database size, auth volume, and storage.
- Redis: managed add-on or platform service.
- OpenAI: variable by article volume and prompt size.
- NewsAPI: tier depends on production licensing and request volume.

## Cost Controls

- Cache NewsAPI responses in PostgreSQL and Redis.
- Reuse saved glosses and sign sequence render jobs.
- Track LLM token cost per request.
- Cap article refresh frequency and page sizes.
- Prefer background sequence generation for repeated glosses.
