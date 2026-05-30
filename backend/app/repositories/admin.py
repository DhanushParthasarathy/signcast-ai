import json
import re
from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import (
    Article,
    BugReport,
    Feedback,
    SavedArticle,
    SearchEvent,
    SignDictionaryEntry,
    SignSequenceJob,
    TranslationRating,
    WatchHistory,
)
from app.schemas.admin import (
    AdminAnalyticsResponse,
    AdminCategoryUsage,
    AdminMetric,
    ArticleViewMetric,
    GenerationFailure,
    MissingGloss,
    MissingGlossResponse,
    SearchTopicMetric,
)


class AdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def analytics(self) -> AdminAnalyticsResponse:
        dictionary_count = self._count(SignDictionaryEntry)
        saved_count = self._count(SavedArticle)
        watch_count = self._count(WatchHistory)
        completed_sequences = self._count_sequence_status("completed")
        failed_sequences = self._count_sequence_status("failed")
        feedback_count = self._count(Feedback)
        rating_count = self._count(TranslationRating)
        bug_count = self._count(BugReport)

        usage_rows = self.db.execute(
            select(Article.category, func.count(WatchHistory.id))
            .join(WatchHistory, WatchHistory.article_id == Article.id)
            .group_by(Article.category)
            .order_by(func.count(WatchHistory.id).desc())
            .limit(8)
        ).all()

        viewed_rows = self.db.execute(
            select(Article.external_id, Article.title, func.count(WatchHistory.id).label("views"))
            .join(WatchHistory, WatchHistory.article_id == Article.id)
            .group_by(Article.external_id, Article.title)
            .order_by(func.count(WatchHistory.id).desc())
            .limit(8)
        ).all()

        search_rows = self.db.execute(
            select(SearchEvent.query, func.count(SearchEvent.id).label("searches"))
            .group_by(SearchEvent.query)
            .order_by(func.count(SearchEvent.id).desc())
            .limit(8)
        ).all()

        return AdminAnalyticsResponse(
            metrics=[
                AdminMetric(label="Dictionary clips", value=dictionary_count),
                AdminMetric(label="Saved articles", value=saved_count),
                AdminMetric(label="Watch events", value=watch_count),
                AdminMetric(label="Completed renders", value=completed_sequences),
                AdminMetric(label="Generation failures", value=failed_sequences),
                AdminMetric(label="Feedback items", value=feedback_count),
            ],
            category_usage=[
                AdminCategoryUsage(category=category, views=int(views))
                for category, views in usage_rows
            ],
            most_viewed=[
                ArticleViewMetric(article_id=article_id, title=title, views=int(views))
                for article_id, title, views in viewed_rows
            ],
            search_topics=[
                SearchTopicMetric(query=query, searches=int(searches))
                for query, searches in search_rows
            ],
            engagement=[
                AdminMetric(label="Translation ratings", value=rating_count),
                AdminMetric(label="Bug reports", value=bug_count),
                AdminMetric(label="Search events", value=self._count(SearchEvent)),
            ],
            recent_failures=self.generation_failures(limit=5),
        )

    def missing_glosses(self, limit: int = 50) -> MissingGlossResponse:
        counter: Counter[str] = Counter()
        rows = self.db.scalars(
            select(SignSequenceJob).where(SignSequenceJob.status == "failed")
        )
        for row in rows:
            error = row.error_message or ""
            if "Missing sign clips for:" not in error:
                continue
            missing = re.sub(r"^.*Missing sign clips for:\s*", "", error)
            for token in missing.split(","):
                gloss = token.strip().upper()
                if gloss:
                    counter[gloss] += 1

        items = [
            MissingGloss(gloss=gloss, occurrences=count)
            for gloss, count in counter.most_common(limit)
        ]
        return MissingGlossResponse(items=items, total=len(items))

    def generation_failures(self, limit: int = 20) -> list[GenerationFailure]:
        rows = self.db.scalars(
            select(SignSequenceJob)
            .where(SignSequenceJob.status == "failed")
            .order_by(SignSequenceJob.updated_at.desc())
            .limit(limit)
        )
        return [
            GenerationFailure(
                id=row.id,
                gloss_tokens=json.loads(row.gloss_tokens),
                error_message=row.error_message,
                attempts=row.attempts,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    def review_queue(self, limit: int = 50, offset: int = 0) -> tuple[list[SignDictionaryEntry], int]:
        statement = (
            select(SignDictionaryEntry)
            .order_by(SignDictionaryEntry.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count = int(self.db.scalar(select(func.count()).select_from(SignDictionaryEntry)) or 0)
        return list(self.db.scalars(statement)), count

    def _count(self, model) -> int:
        return int(self.db.scalar(select(func.count()).select_from(model)) or 0)

    def _count_sequence_status(self, status: str) -> int:
        return int(
            self.db.scalar(
                select(func.count())
                .select_from(SignSequenceJob)
                .where(SignSequenceJob.status == status)
            )
            or 0
        )
