import json
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import Article, SavedArticle, User, UserPreference, WatchHistory
from app.schemas.article import Article as ArticleSchema, NewsCategory
from app.schemas.user_features import (
    SavedArticleResponse,
    UserPreferencesResponse,
    UserPreferencesUpdate,
    WatchHistoryResponse,
)


class ArticleNotFoundError(ValueError):
    pass


class UserFeatureRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ensure_user(self, user_id: str) -> User:
        user = self.db.get(User, user_id)
        if user is None:
            user = User(id=user_id, email=f"{user_id}@local.signcast", display_name="SignCast Reader")
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def save_article(self, *, user_id: str, external_article_id: str, bookmarked: bool) -> SavedArticle:
        self.ensure_user(user_id)
        article = self._article_by_external_id(external_article_id)
        saved = self.db.scalar(
            select(SavedArticle).where(
                SavedArticle.user_id == user_id,
                SavedArticle.article_id == article.id,
            )
        )
        if saved is None:
            saved = SavedArticle(user_id=user_id, article_id=article.id, bookmarked=bookmarked)
            self.db.add(saved)
        else:
            saved.bookmarked = bookmarked or saved.bookmarked
        self.db.commit()
        self.db.refresh(saved)
        return saved

    def set_bookmark(self, *, user_id: str, external_article_id: str, bookmarked: bool) -> SavedArticle:
        saved = self.save_article(
            user_id=user_id,
            external_article_id=external_article_id,
            bookmarked=bookmarked,
        )
        saved.bookmarked = bookmarked
        self.db.commit()
        self.db.refresh(saved)
        return saved

    def remove_saved_article(self, *, user_id: str, external_article_id: str) -> None:
        article = self._article_by_external_id(external_article_id)
        saved = self.db.scalar(
            select(SavedArticle).where(
                SavedArticle.user_id == user_id,
                SavedArticle.article_id == article.id,
            )
        )
        if saved is not None:
            self.db.delete(saved)
            self.db.commit()

    def list_saved_articles(self, *, user_id: str, bookmarked: bool | None, limit: int, offset: int) -> tuple[list[SavedArticle], int]:
        self.ensure_user(user_id)
        statement = (
            select(SavedArticle)
            .options(joinedload(SavedArticle.article))
            .where(SavedArticle.user_id == user_id)
        )
        count_statement = select(func.count()).select_from(SavedArticle).where(SavedArticle.user_id == user_id)
        if bookmarked is not None:
            statement = statement.where(SavedArticle.bookmarked == bookmarked)
            count_statement = count_statement.where(SavedArticle.bookmarked == bookmarked)
        statement = statement.order_by(SavedArticle.updated_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def add_watch_history(
        self,
        *,
        user_id: str,
        external_article_id: str,
        completed: bool,
        duration_seconds: int,
    ) -> WatchHistory:
        self.ensure_user(user_id)
        article = self._article_by_external_id(external_article_id)
        history = WatchHistory(
            user_id=user_id,
            article_id=article.id,
            completed=completed,
            duration_seconds=duration_seconds,
            watched_at=datetime.now(UTC),
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def list_watch_history(self, *, user_id: str, limit: int, offset: int) -> tuple[list[WatchHistory], int]:
        self.ensure_user(user_id)
        statement = (
            select(WatchHistory)
            .options(joinedload(WatchHistory.article))
            .where(WatchHistory.user_id == user_id)
            .order_by(WatchHistory.watched_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count_statement = select(func.count()).select_from(WatchHistory).where(WatchHistory.user_id == user_id)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def get_preferences(self, user_id: str) -> UserPreference:
        self.ensure_user(user_id)
        preferences = self.db.scalar(select(UserPreference).where(UserPreference.user_id == user_id))
        if preferences is None:
            preferences = UserPreference(user_id=user_id)
            self.db.add(preferences)
            self.db.commit()
            self.db.refresh(preferences)
        return preferences

    def update_preferences(self, *, user_id: str, update: UserPreferencesUpdate) -> UserPreference:
        preferences = self.get_preferences(user_id)
        if update.favorite_categories is not None:
            preferences.favorite_categories = json.dumps([category.value for category in update.favorite_categories])
        if update.preferred_language is not None:
            preferences.preferred_language = update.preferred_language
        if update.captions_enabled is not None:
            preferences.captions_enabled = update.captions_enabled
        if update.playback_speed is not None:
            preferences.playback_speed = str(update.playback_speed)
        self.db.commit()
        self.db.refresh(preferences)
        return preferences

    def _article_by_external_id(self, external_article_id: str) -> Article:
        article = self.db.scalar(select(Article).where(Article.external_id == external_article_id))
        if article is None:
            raise ArticleNotFoundError("Article must be loaded before it can be saved or tracked")
        return article


def article_response(article: Article) -> ArticleSchema:
    return ArticleSchema(
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


def saved_response(saved: SavedArticle) -> SavedArticleResponse:
    return SavedArticleResponse(
        id=saved.id,
        article=article_response(saved.article),
        bookmarked=saved.bookmarked,
        created_at=saved.created_at,
        updated_at=saved.updated_at,
    )


def watch_response(history: WatchHistory) -> WatchHistoryResponse:
    return WatchHistoryResponse(
        id=history.id,
        article=article_response(history.article),
        completed=history.completed,
        duration_seconds=history.duration_seconds,
        watched_at=history.watched_at,
    )


def preferences_response(preferences: UserPreference) -> UserPreferencesResponse:
    categories = json.loads(preferences.favorite_categories or "[]")
    allowed = {category.value for category in NewsCategory}
    return UserPreferencesResponse(
        favorite_categories=[NewsCategory(category) for category in categories if category in allowed],
        preferred_language=preferences.preferred_language,
        captions_enabled=preferences.captions_enabled,
        playback_speed=float(preferences.playback_speed),
    )
