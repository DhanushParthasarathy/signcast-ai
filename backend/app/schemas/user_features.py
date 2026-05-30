from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.article import Article, NewsCategory


class SaveArticleRequest(BaseModel):
    article_id: str
    bookmarked: bool = False


class BookmarkRequest(BaseModel):
    bookmarked: bool = True


class SavedArticleResponse(BaseModel):
    id: str
    article: Article
    bookmarked: bool
    created_at: datetime
    updated_at: datetime


class SavedArticlesResponse(BaseModel):
    items: list[SavedArticleResponse]
    total: int


class WatchHistoryCreate(BaseModel):
    article_id: str
    completed: bool = False
    duration_seconds: int = Field(default=0, ge=0)


class WatchHistoryResponse(BaseModel):
    id: str
    article: Article
    completed: bool
    duration_seconds: int
    watched_at: datetime


class WatchHistoryListResponse(BaseModel):
    items: list[WatchHistoryResponse]
    total: int


class UserPreferencesResponse(BaseModel):
    favorite_categories: list[NewsCategory] = Field(default_factory=list)
    preferred_language: str = "en"
    captions_enabled: bool = True
    playback_speed: float = 1.0


class UserPreferencesUpdate(BaseModel):
    favorite_categories: list[NewsCategory] | None = None
    preferred_language: str | None = Field(default=None, min_length=2, max_length=20)
    captions_enabled: bool | None = None
    playback_speed: float | None = Field(default=None, ge=0.5, le=2.0)

    @field_validator("favorite_categories")
    @classmethod
    def dedupe_categories(cls, value: list[NewsCategory] | None) -> list[NewsCategory] | None:
        if value is None:
            return None
        return list(dict.fromkeys(value))
