from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import REQUEST_COUNTER, configure_logging, request_logging_middleware
from app.db.models import (
    Article,
    BugReport,
    Feedback,
    Gloss,
    SavedArticle,
    SearchEvent,
    SignDictionaryEntry,
    SignSequenceJob,
    User,
    UserPreference,
    TranslationRating,
    WatchHistory,
)
from app.db.session import Base, engine
from app.services.news_scheduler import create_news_scheduler


def create_app() -> FastAPI:
    settings = get_settings()
    settings.validate_production()
    configure_logging()
    app = FastAPI(
        title="SignCast AI API",
        version="0.1.0",
        description="News-to-ASL-gloss API with sign clip sequence generation.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_logging_middleware)
    app.include_router(router)

    @app.on_event("startup")
    def create_database_tables() -> None:
        # Migrations are preferred in production; this keeps local/Docker starts usable.
        _ = (
            Article,
            BugReport,
            Feedback,
            Gloss,
            SavedArticle,
            SearchEvent,
            SignDictionaryEntry,
            SignSequenceJob,
            TranslationRating,
            User,
            UserPreference,
            WatchHistory,
        )
        Base.metadata.create_all(bind=engine)
        if not hasattr(app.state, "news_scheduler"):
            app.state.news_scheduler = create_news_scheduler()
            app.state.news_scheduler.start()

    @app.on_event("shutdown")
    def stop_schedulers() -> None:
        scheduler = getattr(app.state, "news_scheduler", None)
        if scheduler and scheduler.running:
            scheduler.shutdown(wait=False)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    @app.get("/metrics")
    async def metrics() -> dict[str, object]:
        return {
            "status": "ok",
            "requests": dict(REQUEST_COUNTER),
        }

    return app


app = create_app()
