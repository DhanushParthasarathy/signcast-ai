from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Article, BugReport, Feedback, TranslationRating
from app.repositories.user_features import UserFeatureRepository
from app.schemas.feedback import (
    BugReportCreate,
    BugReportItem,
    FeedbackCreate,
    FeedbackItem,
    RatingItem,
    TranslationRatingCreate,
)


class FeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserFeatureRepository(db)

    def create_feedback(self, *, user_id: str, request: FeedbackCreate) -> Feedback:
        self.users.ensure_user(user_id)
        item = Feedback(
            user_id=user_id,
            article_id=self._internal_article_id(request.article_id),
            feedback_type=request.feedback_type.value,
            message=request.message,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_rating(self, *, user_id: str, request: TranslationRatingCreate) -> TranslationRating:
        self.users.ensure_user(user_id)
        item = TranslationRating(
            user_id=user_id,
            article_id=self._internal_article_id(request.article_id),
            translation_quality=request.translation_quality,
            video_quality=request.video_quality,
            comment=request.comment,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_bug_report(self, *, user_id: str, request: BugReportCreate) -> BugReport:
        self.users.ensure_user(user_id)
        item = BugReport(
            user_id=user_id,
            article_id=self._internal_article_id(request.article_id),
            category=request.category.value,
            description=request.description,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_feedback(self, limit: int = 50) -> list[Feedback]:
        return list(self.db.scalars(select(Feedback).order_by(Feedback.created_at.desc()).limit(limit)))

    def list_ratings(self, limit: int = 50) -> list[TranslationRating]:
        return list(self.db.scalars(select(TranslationRating).order_by(TranslationRating.created_at.desc()).limit(limit)))

    def list_bug_reports(self, limit: int = 50) -> list[BugReport]:
        return list(self.db.scalars(select(BugReport).order_by(BugReport.created_at.desc()).limit(limit)))

    def _internal_article_id(self, external_id: str | None) -> str | None:
        if not external_id:
            return None
        article = self.db.scalar(select(Article).where(Article.external_id == external_id))
        return article.id if article else None


def feedback_item(item: Feedback) -> FeedbackItem:
    return FeedbackItem(
        id=item.id,
        type=item.feedback_type,
        article_id=item.article_id,
        message=item.message,
        status=item.status,
        created_at=item.created_at,
    )


def rating_item(item: TranslationRating) -> RatingItem:
    return RatingItem(
        id=item.id,
        article_id=item.article_id,
        translation_quality=item.translation_quality,
        video_quality=item.video_quality,
        comment=item.comment,
        created_at=item.created_at,
    )


def bug_report_item(item: BugReport) -> BugReportItem:
    return BugReportItem(
        id=item.id,
        article_id=item.article_id,
        category=item.category,
        description=item.description,
        status=item.status,
        created_at=item.created_at,
    )
