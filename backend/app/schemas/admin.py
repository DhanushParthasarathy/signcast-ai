from datetime import datetime

from pydantic import BaseModel

from app.schemas.sign import SignDictionaryEntry


class AdminMetric(BaseModel):
    label: str
    value: int


class AdminCategoryUsage(BaseModel):
    category: str
    views: int


class ArticleViewMetric(BaseModel):
    article_id: str
    title: str
    views: int


class SearchTopicMetric(BaseModel):
    query: str
    searches: int


class MissingGloss(BaseModel):
    gloss: str
    occurrences: int


class GenerationFailure(BaseModel):
    id: str
    gloss_tokens: list[str]
    error_message: str | None
    attempts: int
    updated_at: datetime


class AdminAnalyticsResponse(BaseModel):
    metrics: list[AdminMetric]
    category_usage: list[AdminCategoryUsage]
    most_viewed: list[ArticleViewMetric]
    search_topics: list[SearchTopicMetric]
    engagement: list[AdminMetric]
    recent_failures: list[GenerationFailure]


class AdminReviewQueueResponse(BaseModel):
    entries: list[SignDictionaryEntry]
    total: int


class MissingGlossResponse(BaseModel):
    items: list[MissingGloss]
    total: int
