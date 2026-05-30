import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from math import ceil
from urllib.parse import urlparse

import httpx

from app.core.cache import RedisCache
from app.core.config import Settings
from app.db.models import Article as ArticleModel
from app.models.article import Article, ArticleListResponse, NewsCategory
from app.repositories.articles import ArticleRepository


@dataclass(frozen=True)
class NewsQuery:
    category: NewsCategory | None = None
    keyword: str | None = None
    country: str = "us"
    page: int = 1
    page_size: int = 12
    force_refresh: bool = False


class NewsAPIError(RuntimeError):
    pass


class NewsService:
    def __init__(
        self,
        settings: Settings,
        repository: ArticleRepository,
        cache: RedisCache | None = None,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.cache = cache

    async def get_news(self, query: NewsQuery) -> ArticleListResponse:
        normalized = self._normalize_query(query)
        cache_key = self._cache_key(normalized)
        if self.cache and not normalized.force_refresh:
            cached_payload = self.cache.get_json(cache_key)
            if cached_payload:
                return ArticleListResponse.model_validate(cached_payload)

        if normalized.force_refresh or self._should_refresh(normalized):
            await self.refresh(query=normalized)

        articles, total = self.repository.list_paginated(
            category=normalized.category,
            query=normalized.keyword,
            country=normalized.country,
            page=normalized.page,
            page_size=normalized.page_size,
        )
        response = ArticleListResponse(
            articles=[self._to_schema(article) for article in articles],
            page=normalized.page,
            page_size=normalized.page_size,
            total=total,
            total_pages=ceil(total / normalized.page_size) if total else 0,
        )
        if self.cache:
            self.cache.set_json(cache_key, response.model_dump(mode="json"))
        return response

    async def fetch_headlines(
        self,
        category: NewsCategory = NewsCategory.general,
        query: str | None = None,
        page_size: int = 12,
        country: str | None = None,
    ) -> list[Article]:
        response = await self.get_news(
            NewsQuery(
                category=category,
                keyword=query,
                country=country or self.settings.news_default_country,
                page=1,
                page_size=page_size,
            )
        )
        return response.articles

    async def refresh(self, query: NewsQuery | None = None) -> int:
        normalized = self._normalize_query(query or NewsQuery())
        payloads = (
            self._mock_articles(normalized)
            if not self.settings.news_api_key
            else await self._fetch_from_newsapi(normalized)
        )
        saved = self.repository.upsert_many(payloads)
        if self.cache:
            self.cache.delete_prefix("news:")
        return len(saved)

    async def refresh_default_feeds(self) -> int:
        total = 0
        for category in (
            NewsCategory.general,
            NewsCategory.business,
            NewsCategory.health,
            NewsCategory.science,
            NewsCategory.technology,
        ):
            total += await self.refresh(
                NewsQuery(category=category, country=self.settings.news_default_country, page_size=50)
            )
        return total

    async def fetch_article(self, article_id: str) -> Article | None:
        article = self.repository.get_by_external_id(article_id)
        if article is None:
            await self.refresh()
            article = self.repository.get_by_external_id(article_id)
        return self._to_schema(article) if article else None

    async def fetch_article_model(self, article_id: str) -> ArticleModel | None:
        article = self.repository.get_by_external_id(article_id)
        if article is None:
            await self.refresh()
            article = self.repository.get_by_external_id(article_id)
        return article

    async def _fetch_from_newsapi(self, query: NewsQuery) -> list[dict]:
        params: dict[str, str | int] = {
            "apiKey": self.settings.news_api_key,
            "language": "en",
            "pageSize": min(query.page_size, 100),
        }
        if query.keyword:
            endpoint = "https://newsapi.org/v2/everything"
            params["q"] = query.keyword
            params["sortBy"] = "publishedAt"
            params["page"] = query.page
        else:
            endpoint = "https://newsapi.org/v2/top-headlines"
            params["country"] = query.country
            params["page"] = query.page
            if query.category:
                params["category"] = query.category.value

        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.get(endpoint, params=params)

        if response.status_code >= 400:
            raise NewsAPIError(f"NewsAPI request failed with status {response.status_code}")

        payload = response.json()
        return [
            self._from_newsapi(item, category=query.category, country=query.country)
            for item in payload.get("articles", [])
            if self._valid_article(item)
        ]

    def _from_newsapi(
        self,
        item: dict,
        category: NewsCategory | None,
        country: str,
    ) -> dict:
        url = item["url"]
        external_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        return {
            "external_id": external_id,
            "source_name": item.get("source", {}).get("name") or self._source_from_url(url),
            "author": item.get("author"),
            "title": item.get("title") or "Untitled article",
            "description": item.get("description"),
            "content": item.get("content"),
            "url": url,
            "image_url": item.get("urlToImage"),
            "published_at": self._parse_datetime(item.get("publishedAt")),
            "category": (category or NewsCategory.general).value,
            "country": country.lower(),
        }

    def _mock_articles(self, query: NewsQuery) -> list[dict]:
        topics = [
            ("NASA launches climate satellite", "NASA launched a new satellite to watch Earth climate."),
            ("Students build accessibility app", "Students created an app that helps people read news."),
            ("City expands transit alerts", "The city added simple alerts for train and bus delays."),
            ("Hospital tests caption tools", "A hospital tested caption tools for patient visits."),
            ("New classroom signs added", "A school added sign language resources for students."),
        ]
        if query.keyword:
            topics = [item for item in topics if query.keyword.lower() in " ".join(item).lower()] or []

        return [
            {
                "external_id": hashlib.sha256(f"https://example.com/news/{index}".encode("utf-8")).hexdigest()[
                    :16
                ],
                "source_name": "SignCast Demo News",
                "title": title,
                "description": description,
                "content": description,
                "url": f"https://example.com/news/{index}",
                "image_url": None,
                "published_at": datetime.now(UTC),
                "category": (query.category or NewsCategory.general).value,
                "country": query.country,
            }
            for index, (title, description) in enumerate(topics, start=1)
        ]

    def _to_schema(self, article: ArticleModel) -> Article:
        return Article(
            id=article.external_id,
            source_name=article.source_name,
            author=article.author,
            title=article.title,
            description=article.description,
            content=article.content,
            url=article.url,
            image_url=article.image_url,
            published_at=article.published_at,
            category=NewsCategory(article.category),
            country=article.country,
        )

    def _normalize_query(self, query: NewsQuery) -> NewsQuery:
        return NewsQuery(
            category=query.category,
            keyword=query.keyword.strip() if query.keyword else None,
            country=(query.country or self.settings.news_default_country).lower(),
            page=max(query.page, 1),
            page_size=min(max(query.page_size, 1), 100),
            force_refresh=query.force_refresh,
        )

    def _should_refresh(self, query: NewsQuery) -> bool:
        articles, total = self.repository.list_paginated(
            category=query.category,
            query=query.keyword,
            country=query.country,
            page=query.page,
            page_size=query.page_size,
        )
        return total == 0 or not articles

    def _cache_key(self, query: NewsQuery) -> str:
        return (
            "news:"
            f"country={query.country}:category={query.category or 'all'}:"
            f"keyword={query.keyword or ''}:page={query.page}:size={query.page_size}"
        )

    def _valid_article(self, item: dict) -> bool:
        title = item.get("title") or ""
        return bool(item.get("url")) and title != "[Removed]"

    def _parse_datetime(self, value: str | None) -> datetime:
        if not value:
            return datetime.now(UTC)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _source_from_url(self, url: str) -> str:
        return urlparse(url).netloc.replace("www.", "") or "Unknown"
