from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class NewsCategory(StrEnum):
    general = "general"
    business = "business"
    entertainment = "entertainment"
    health = "health"
    science = "science"
    sports = "sports"
    technology = "technology"


class Article(BaseModel):
    id: str
    source_name: str
    author: str | None = None
    title: str
    description: str | None = None
    content: str | None = None
    url: HttpUrl
    image_url: HttpUrl | None = None
    published_at: datetime
    category: NewsCategory = NewsCategory.general
    country: str = "us"


class ArticleListResponse(BaseModel):
    articles: list[Article]
    page: int = 1
    page_size: int | None = None
    total: int | None = None
    total_pages: int | None = None


class ArticleDetailResponse(BaseModel):
    article: Article
    simplified_summary: str | None = None
    asl_gloss: str | None = None
    sign_sequence: list["SignSequenceItem"] = Field(default_factory=list)


class SummarizeRequest(BaseModel):
    article_id: str | None = None
    text: str


class SummarizeResponse(BaseModel):
    summary: str
    simple_english: str


class TranslateRequest(BaseModel):
    text: str


class TranslateResponse(BaseModel):
    gloss: str
    tokens: list[str]
    gloss_tokens: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    unknown_tokens: list[str] = Field(default_factory=list)


class SignSequenceRequest(BaseModel):
    gloss: str | None = None
    gloss_tokens: list[str] | None = None


class SignSequenceItem(BaseModel):
    token: str
    clip_url: str | None = None
    status: str


class SignSequenceResponse(BaseModel):
    sequence: list[SignSequenceItem]
    missing_tokens: list[str]
    id: str | None = None
    status: str | None = None
    progress: int = 0
    output_url: str | None = None
    error_message: str | None = None
    attempts: int = 0
    cached: bool = False


ArticleDetailResponse.model_rebuild()
