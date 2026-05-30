from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Article
from app.db.session import Base
from app.repositories.user_features import UserFeatureRepository, preferences_response
from app.schemas.user_features import UserPreferencesUpdate


def make_repository() -> UserFeatureRepository:
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
            url="https://example.com/article-1",
            published_at=datetime.now(UTC),
            category="science",
            country="us",
        )
    )
    session.commit()
    return UserFeatureRepository(session)


def test_save_article_and_bookmark() -> None:
    repository = make_repository()

    saved = repository.save_article(
        user_id="00000000-0000-4000-8000-000000000001",
        external_article_id="article-1",
        bookmarked=False,
    )
    bookmarked = repository.set_bookmark(
        user_id="00000000-0000-4000-8000-000000000001",
        external_article_id="article-1",
        bookmarked=True,
    )

    assert saved.id == bookmarked.id
    assert bookmarked.bookmarked is True


def test_watch_history_and_recently_viewed() -> None:
    repository = make_repository()

    repository.add_watch_history(
        user_id="00000000-0000-4000-8000-000000000001",
        external_article_id="article-1",
        completed=True,
        duration_seconds=42,
    )
    items, total = repository.list_watch_history(
        user_id="00000000-0000-4000-8000-000000000001",
        limit=10,
        offset=0,
    )

    assert total == 1
    assert items[0].duration_seconds == 42


def test_user_preferences_update() -> None:
    repository = make_repository()

    preferences = repository.update_preferences(
        user_id="00000000-0000-4000-8000-000000000001",
        update=UserPreferencesUpdate(favorite_categories=["science", "health"], playback_speed=1.25),
    )
    response = preferences_response(preferences)

    assert response.favorite_categories == ["science", "health"]
    assert response.playback_speed == 1.25
