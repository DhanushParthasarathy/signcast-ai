from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import SignDictionaryEntry
from app.db.session import Base
from app.repositories.sign_dictionary import DuplicateGlossError, SignDictionaryRepository
from app.schemas.sign import SignDictionaryCreate
from app.services.thumbnails import ThumbnailService


def make_repository() -> SignDictionaryRepository:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return SignDictionaryRepository(session)


def test_sign_dictionary_create_normalizes_gloss() -> None:
    payload = SignDictionaryCreate(gloss=" nasa ", video_url="https://example.com/nasa.mp4")

    assert payload.gloss == "NASA"


def test_repository_detects_duplicate_gloss() -> None:
    repository = make_repository()
    repository.create(
        gloss="NASA",
        video_url="https://example.com/nasa.mp4",
        thumbnail_url="https://example.com/nasa.svg",
    )

    try:
        repository.create(
            gloss="nasa",
            video_url="https://example.com/nasa-2.mp4",
            thumbnail_url=None,
        )
    except DuplicateGlossError:
        pass
    else:
        raise AssertionError("Expected duplicate gloss detection")


def test_repository_searches_by_gloss() -> None:
    repository = make_repository()
    repository.create(gloss="NASA", video_url="https://example.com/nasa.mp4", thumbnail_url=None)
    repository.create(
        gloss="SATELLITE",
        video_url="https://example.com/satellite.mp4",
        thumbnail_url=None,
    )

    entries, total = repository.list_entries(q="sat", limit=10, offset=0)

    assert total == 1
    assert entries[0].gloss == "SATELLITE"


def test_repository_maps_gloss_to_video_url() -> None:
    repository = make_repository()
    repository.create(gloss="LAUNCH", video_url="https://example.com/launch.mp4", thumbnail_url=None)

    assert repository.as_mapping()["LAUNCH"] == "https://example.com/launch.mp4"


def test_thumbnail_service_generates_svg_thumbnail() -> None:
    thumbnail = ThumbnailService().generate_svg_thumbnail("NASA")

    assert thumbnail.startswith(b"<svg")
    assert b"NASA" in thumbnail
