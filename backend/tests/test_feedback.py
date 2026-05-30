from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Article
from app.db.session import Base
from app.repositories.analytics import AnalyticsRepository
from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import BugReportCreate, FeedbackCreate, FeedbackType, TranslationRatingCreate


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(
        Article(
            external_id="article-1",
            source_name="Demo",
            title="NASA launches satellite",
            description="NASA launched a satellite.",
            content="NASA launched a satellite.",
            url="https://example.com/feedback-article-1",
            published_at=datetime.now(UTC),
            category="science",
            country="us",
        )
    )
    session.commit()
    return session


def test_feedback_repository_creates_review_items() -> None:
    repository = FeedbackRepository(make_session())

    feedback = repository.create_feedback(
        user_id="00000000-0000-4000-8000-000000000001",
        request=FeedbackCreate(
            article_id="article-1",
            feedback_type=FeedbackType.incorrect_gloss,
            message="The gloss should keep NASA as a named entity.",
        ),
    )
    rating = repository.create_rating(
        user_id="00000000-0000-4000-8000-000000000001",
        request=TranslationRatingCreate(article_id="article-1", translation_quality=4, video_quality=3),
    )
    bug = repository.create_bug_report(
        user_id="00000000-0000-4000-8000-000000000001",
        request=BugReportCreate(article_id="article-1", category="video", description="Video clip did not load."),
    )

    assert feedback.status == "open"
    assert rating.translation_quality == 4
    assert bug.category == "video"
    assert len(repository.list_feedback()) == 1


def test_search_events_are_normalized() -> None:
    repository = AnalyticsRepository(make_session())

    repository.record_search(query="  Climate   Change  ", user_id="00000000-0000-4000-8000-000000000001")

    assert repository.has_recent_query(query="climate change")
