# Security Review

## Implemented

- Admin APIs require `X-Admin-Token`.
- Production startup validates required secrets.
- CORS is restricted by `FRONTEND_ORIGIN`.
- Rate limiting is enabled on news endpoints.
- Supabase service role key remains backend-only.

## Required Before Public Account Launch

- Replace `X-User-Id` with Supabase JWT validation.
- Add CSRF-safe auth flows for any cookie-based sessions.
- Restrict `/metrics` to trusted IPs or monitoring credentials.
- Add malware/content review for uploaded sign videos.
- Add storage bucket policies that prevent unreviewed uploads from becoming public.

## Secret Handling

- Store secrets only in Vercel, Render/Railway, Supabase, and GitHub Actions secret managers.
- Do not commit `.env` files.
- Rotate `ADMIN_API_TOKEN`, Supabase service role key, and OpenAI key after any accidental exposure.
