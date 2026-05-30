from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class FeedbackType(StrEnum):
    incorrect_gloss = "incorrect_gloss"
    incorrect_sign = "incorrect_sign"
    general = "general"


class BugCategory(StrEnum):
    ui = "ui"
    translation = "translation"
    video = "video"
    account = "account"
    other = "other"


class FeedbackCreate(BaseModel):
    article_id: str | None = None
    feedback_type: FeedbackType
    message: str = Field(min_length=5, max_length=2000)


class TranslationRatingCreate(BaseModel):
    article_id: str | None = None
    translation_quality: int = Field(ge=1, le=5)
    video_quality: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class BugReportCreate(BaseModel):
    article_id: str | None = None
    category: BugCategory
    description: str = Field(min_length=5, max_length=3000)


class FeedbackItem(BaseModel):
    id: str
    type: str
    article_id: str | None = None
    message: str
    status: str
    created_at: datetime


class RatingItem(BaseModel):
    id: str
    article_id: str | None = None
    translation_quality: int
    video_quality: int
    comment: str | None = None
    created_at: datetime


class BugReportItem(BaseModel):
    id: str
    article_id: str | None = None
    category: str
    description: str
    status: str
    created_at: datetime
