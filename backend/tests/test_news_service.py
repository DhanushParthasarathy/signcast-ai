from datetime import UTC, datetime

import pytest

from app.core.config import Settings
from app.models.article import NewsCategory
from app.services.news import NewsQuery, NewsService


class FakeRepository:
    def __init__(self) -> None:
        self.rows: list[object] = []
        self.upsert_calls = 0

    def list_paginated(self, *, category, query, country, page, page_size):
        rows = [
            row
            for row in self.rows
            if (category is None or row.category == category.value)
            and (not query or query.lower() in row.title.lower() or query.lower() in (row.description or "").lower())
            and row.country == country
        ]
        start = (page - 1) * page_size
        return rows[start : start + page_size], len(rows)

    def get_by_external_id(self, external_id):
        return next((row for row in self.rows if row.external_id == external_id), None)

    def upsert_many(self, articles):
        self.upsert_calls += 1
        for payload in articles:
            existing = next(
                (
                    row
                    for row in self.rows
                    if row.url == payload["url"] or row.external_id == payload["external_id"]
                ),
                None,
            )
            if existing is None:
                self.rows.append(SimpleArticle(**payload))
            else:
                for key, value in payload.items():
                    setattr(existing, key, value)
        return self.rows


class FakeCache:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}
        self.deleted_prefixes: list[str] = []

    def get_json(self, key):
        return self.values.get(key)

    def set_json(self, key, value, ttl_seconds=None):
        self.values[key] = value

    def delete_prefix(self, prefix):
        self.deleted_prefixes.append(prefix)
        self.values = {key: value for key, value in self.values.items() if not key.startswith(prefix)}


class SimpleArticle:
    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id", kwargs["external_id"])
        self.external_id = kwargs["external_id"]
        self.source_name = kwargs["source_name"]
        self.author = kwargs.get("author")
        self.title = kwargs["title"]
        self.description = kwargs.get("description")
        self.content = kwargs.get("content")
        self.url = kwargs["url"]
        self.image_url = kwargs.get("image_url")
        self.published_at = kwargs.get("published_at", datetime.now(UTC))
        self.category = kwargs.get("category", "general")
        self.country = kwargs.get("country", "us")
        self.gloss = None


@pytest.mark.asyncio
async def test_get_news_refreshes_and_paginates_from_postgres_cache() -> None:
    repository = FakeRepository()
    service = NewsService(Settings(news_api_key=""), repository, FakeCache())

    response = await service.get_news(
        NewsQuery(category=NewsCategory.general, country="us", page=1, page_size=2)
    )

    assert response.page == 1
    assert response.page_size == 2
    assert response.total == 5
    assert len(response.articles) == 2
    assert repository.upsert_calls == 1


@pytest.mark.asyncio
async def test_get_news_uses_redis_response_cache() -> None:
    repository = FakeRepository()
    cache = FakeCache()
    service = NewsService(Settings(news_api_key=""), repository, cache)

    first = await service.get_news(NewsQuery(country="us", page=1, page_size=1))
    second = await service.get_news(NewsQuery(country="us", page=1, page_size=1))

    assert first.articles[0].id == second.articles[0].id
    assert repository.upsert_calls == 1


def test_repository_style_upsert_prevents_duplicates() -> None:
    repository = FakeRepository()
    payload = {
        "external_id": "abc",
        "source_name": "Demo",
        "title": "Same story",
        "description": "Same story",
        "content": "Same story",
        "url": "https://example.com/story",
        "image_url": None,
        "published_at": datetime.now(UTC),
        "category": "general",
        "country": "us",
    }

    repository.upsert_many([payload])
    repository.upsert_many([{**payload, "title": "Updated story"}])

    assert len(repository.rows) == 1
    assert repository.rows[0].title == "Updated story"
