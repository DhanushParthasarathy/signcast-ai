import asyncio

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.cache import get_cache
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.repositories.articles import ArticleRepository
from app.services.news import NewsService


def refresh_news_job() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        service = NewsService(settings, ArticleRepository(db), get_cache())
        asyncio.run(service.refresh_default_feeds())
    finally:
        db.close()


def create_news_scheduler() -> BackgroundScheduler:
    settings = get_settings()
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        refresh_news_job,
        trigger="interval",
        minutes=settings.news_refresh_interval_minutes,
        id="news-refresh",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    return scheduler
