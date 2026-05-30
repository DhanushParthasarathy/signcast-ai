# Infrastructure Diagram

```mermaid
flowchart LR
    User["User browser"] --> Vercel["Vercel: Next.js 15 frontend"]
    Vercel --> API["Render/Railway: FastAPI backend"]
    API --> SupabaseDB["Supabase PostgreSQL"]
    API --> SupabaseStorage["Supabase Storage"]
    API --> Redis["Redis cache"]
    API --> NewsAPI["NewsAPI"]
    API --> OpenAI["OpenAI API"]
    API --> FFmpeg["FFmpeg worker process"]
    GitHub["GitHub Actions"] --> Vercel
    GitHub --> API
    Monitor["Uptime + log monitoring"] --> API
    Backup["Scheduled backups"] --> SupabaseDB
```

## Runtime Boundaries

- Browser calls the backend over HTTPS.
- Backend owns all service-role secrets.
- Frontend only receives public Supabase values and backend URL.
- Sign clip uploads and generated sequence outputs are stored in Supabase Storage.
- Avatar research remains outside production routing.
