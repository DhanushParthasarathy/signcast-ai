# Sign Dictionary

The MVP animation system maps ASL gloss tokens to prerecorded video clips.

Example:

```text
NASA -> nasa.mp4
LAUNCH -> launch.mp4
SATELLITE -> satellite.mp4
```

The `sign_dictionary` table stores:

```text
id
gloss
video_url
thumbnail_url
created_at
```

The backend returns a sequence like:

```json
[
  { "token": "NASA", "clip_url": "/signs/nasa.mp4", "status": "ready" },
  { "token": "LAUNCH", "clip_url": "/signs/launch.mp4", "status": "ready" }
]
```

Missing tokens are surfaced to admins so the dictionary can be expanded.

Video upload uses Supabase Storage when `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and
`SUPABASE_SIGN_BUCKET` are configured. A thumbnail is generated automatically when one is not provided.
