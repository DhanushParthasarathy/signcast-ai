from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def uuid_str() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(32), default="reader", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    watch_history: Mapped[list["WatchHistory"]] = relationship(back_populates="user")
    saved_articles: Mapped[list["SavedArticle"]] = relationship(back_populates="user")
    preferences: Mapped["UserPreference | None"] = relationship(back_populates="user", uselist=False)


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        Index("articles_category_published_idx", "category", "published_at"),
        Index("articles_external_id_idx", "external_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    external_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(160), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(40), default="general", nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="us", nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    gloss: Mapped["Gloss | None"] = relationship(back_populates="article", uselist=False)
    watch_history: Mapped[list["WatchHistory"]] = relationship(back_populates="article")
    saved_by: Mapped[list["SavedArticle"]] = relationship(back_populates="article")


class Gloss(Base):
    __tablename__ = "glosses"
    __table_args__ = (UniqueConstraint("article_id", name="uq_gloss_article_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    simple_english: Mapped[str] = mapped_column(Text, nullable=False)
    asl_gloss: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    article: Mapped[Article] = relationship(back_populates="gloss")


class SignDictionaryEntry(Base):
    __tablename__ = "sign_dictionary"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    gloss: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class SignSequenceJob(Base):
    __tablename__ = "sign_sequence_jobs"
    __table_args__ = (
        Index("sign_sequence_jobs_sequence_hash_idx", "sequence_hash"),
        UniqueConstraint("sequence_hash", name="uq_sign_sequence_jobs_sequence_hash"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    sequence_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    gloss_tokens: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_url: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SavedArticle(Base):
    __tablename__ = "saved_articles"
    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="uq_saved_articles_user_article"),
        Index("saved_articles_user_created_idx", "user_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    bookmarked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="saved_articles")
    article: Mapped[Article] = relationship(back_populates="saved_by")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    favorite_categories: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    captions_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    playback_speed: Mapped[str] = mapped_column(String(10), default="1", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="preferences")


class SearchEvent(Base):
    __tablename__ = "search_events"
    __table_args__ = (Index("search_events_query_created_idx", "query", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    query: Mapped[str] = mapped_column(String(120), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    article_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("articles.id", ondelete="SET NULL"))
    feedback_type: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class TranslationRating(Base):
    __tablename__ = "translation_ratings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    article_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("articles.id", ondelete="SET NULL"))
    translation_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    video_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class BugReport(Base):
    __tablename__ = "bug_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    article_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("articles.id", ondelete="SET NULL"))
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class WatchHistory(Base):
    __tablename__ = "watch_history"
    __table_args__ = (Index("watch_history_user_watched_idx", "user_id", "watched_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    watched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="watch_history")
    article: Mapped[Article] = relationship(back_populates="watch_history")
