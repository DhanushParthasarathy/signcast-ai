# API

Base URL: `http://localhost:8000`

## `GET /news`

Query parameters:

- `category`: `general`, `business`, `entertainment`, `health`, `science`, `sports`, `technology`
- `q`: optional search term
- `country`: two-letter country code, defaults to `us`
- `page`: page number, defaults to `1`
- `page_size`: page size from `1` to `100`, defaults to `12`

Returns paginated cached articles. The backend refreshes PostgreSQL from NewsAPI when the cache is empty and stores response payloads in Redis.

## `GET /news/trending`

Returns top general headlines for a country.

## `GET /news/search?q=`

Searches headlines and article descriptions by keyword.

## `GET /news/category/{category}`

Returns headlines for a NewsAPI category.

News endpoints are rate limited by client IP using Redis.

## `GET /news/{id}`

Returns article details plus generated accessibility outputs:

- `simplified_summary`
- `asl_gloss`
- `sign_sequence`

## `POST /summarize`

```json
{
  "text": "NASA successfully launched a climate monitoring satellite."
}
```

## `POST /translate`

```json
{
  "text": "NASA launched a new satellite. It will watch Earth's climate."
}
```

## `POST /generate-sign-sequence`

```json
{
  "gloss_tokens": ["NASA", "LAUNCH", "SATELLITE"]
}
```

Creates or reuses a background render job. The worker looks up dictionary clips, merges them with FFmpeg, uploads the final MP4, and tracks progress.

Returns:

```json
{
  "id": "job-id",
  "status": "queued",
  "progress": 0,
  "output_url": null,
  "sequence": [],
  "missing_tokens": [],
  "cached": false
}
```

Legacy requests with `"gloss": "NASA LAUNCH SATELLITE"` are also accepted.

## `GET /sequence/{id}`

Returns render status, progress, ordered clip sequence, missing tokens, error message, and final `output_url` when complete.

## `GET /sign-dictionary`

Query parameters:

- `q`: optional gloss search
- `limit`: `1` to `100`, defaults to `50`
- `offset`: defaults to `0`

Returns:

```json
{
  "entries": [
    {
      "id": "uuid",
      "gloss": "NASA",
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "created_at": "2026-05-30T00:00:00Z"
    }
  ],
  "total": 1
}
```

## `POST /sign-dictionary`

Creates a sign dictionary entry and uploads a video when `video` is provided. Use `multipart/form-data`.

Fields:

- `gloss`: required
- `video`: optional MP4/WebM/MOV file, max 50 MB
- `video_url`: optional existing video URL, required when `video` is absent
- `thumbnail_url`: optional; generated automatically when absent

## `PUT /sign-dictionary/{id}`

Updates a dictionary entry using JSON:

```json
{
  "gloss": "LAUNCH",
  "video_url": "https://...",
  "thumbnail_url": "https://..."
}
```

## `DELETE /sign-dictionary/{id}`

Deletes a dictionary entry.

## User Features

MVP user APIs accept `X-User-Id`. The frontend creates a stable local UUID and sends it with each request.

### `GET /me/saved-articles`

Query parameters:

- `bookmarked`: optional boolean filter
- `limit`: defaults to `50`
- `offset`: defaults to `0`

### `POST /me/saved-articles`

```json
{
  "article_id": "external-news-id",
  "bookmarked": false
}
```

### `DELETE /me/saved-articles/{article_id}`

Removes a saved article.

### `PUT /me/saved-articles/{article_id}/bookmark`

```json
{
  "bookmarked": true
}
```

### `POST /me/watch-history`

```json
{
  "article_id": "external-news-id",
  "completed": true,
  "duration_seconds": 42
}
```

### `GET /me/watch-history`

Returns full watch history.

### `GET /me/recently-viewed`

Returns the most recent watch history entries.

### `GET /me/preferences`

Returns favorite categories, preferred language, caption setting, and playback speed.

### `PUT /me/preferences`

```json
{
  "favorite_categories": ["science", "health"],
  "preferred_language": "en",
  "captions_enabled": true,
  "playback_speed": 1.25
}
```

## Admin

### `GET /admin/analytics`

Returns dashboard metrics, category usage bars, and recent generation failures.

### `GET /admin/missing-glosses`

Returns gloss tokens found in failed sequence jobs because dictionary clips were missing.

### `GET /admin/generation-failures`

Returns failed sequence jobs, attempts, error messages, and gloss tokens.

### `GET /admin/review-queue`

Returns recently uploaded sign dictionary entries for admin review.
