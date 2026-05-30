from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import Article, Gloss
from app.models.article import NewsCategory


class ArticleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_cached(
        self,
        *,
        category: NewsCategory,
        query: str | None,
        ttl_seconds: int,
        limit: int,
    ) -> list[Article]:
        cutoff = datetime.now(UTC) - timedelta(seconds=ttl_seconds)
        statement = select(Article).where(Article.cached_at >= cutoff)
        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                or_(Article.title.ilike(pattern), Article.description.ilike(pattern))
            )
        else:
            statement = statement.where(Article.category == category.value)

        statement = statement.order_by(Article.published_at.desc()).limit(limit)
        return list(self.db.scalars(statement))

    def list_paginated(
        self,
        *,
        category: NewsCategory | None = None,
        query: str | None,
        country: str | None = None,
        page: int,
        page_size: int,
    ) -> tuple[list[Article], int]:
        statement = select(Article)
        count_statement = select(func.count()).select_from(Article)
        filters = []
        if query:
            pattern = f"%{query}%"
            filters.append(or_(Article.title.ilike(pattern), Article.description.ilike(pattern)))
        if category is not None:
            filters.append(Article.category == category.value)
        if country:
            filters.append(Article.country == country.lower())

        for filter_clause in filters:
            statement = statement.where(filter_clause)
            count_statement = count_statement.where(filter_clause)

        offset = (page - 1) * page_size
        statement = statement.order_by(Article.published_at.desc()).offset(offset).limit(page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def get_by_external_id(self, external_id: str) -> Article | None:
        statement = (
            select(Article)
            .options(joinedload(Article.gloss))
            .where(Article.external_id == external_id)
        )
        return self.db.scalar(statement)

    def upsert_many(self, articles: list[dict]) -> list[Article]:
        saved: list[Article] = []
        for payload in articles:
            article = self.db.scalar(
                select(Article).where(
                    or_(
                        Article.url == payload["url"],
                        Article.external_id == payload["external_id"],
                    )
                )
            )
            if article is None:
                article = Article(**payload)
                self.db.add(article)
            else:
                for key, value in payload.items():
                    setattr(article, key, value)
                article.cached_at = datetime.now(UTC)
            saved.append(article)

        self.db.commit()
        for article in saved:
            self.db.refresh(article)
        return saved

    def save_gloss(
        self,
        *,
        article_id: str,
        summary: str,
        simple_english: str,
        asl_gloss: str,
        model_name: str | None,
    ) -> Gloss:
        gloss = self.db.scalar(select(Gloss).where(Gloss.article_id == article_id))
        if gloss is None:
            gloss = Gloss(
                article_id=article_id,
                summary=summary,
                simple_english=simple_english,
                asl_gloss=asl_gloss,
                model_name=model_name,
            )
            self.db.add(gloss)
        else:
            gloss.summary = summary
            gloss.simple_english = simple_english
            gloss.asl_gloss = asl_gloss
            gloss.model_name = model_name

        self.db.commit()
        self.db.refresh(gloss)
        return gloss
