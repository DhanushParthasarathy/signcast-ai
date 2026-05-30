import json

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Header, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.cache import RedisCache, get_cache
from app.core.config import Settings, get_settings
from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.models.article import (
    ArticleDetailResponse,
    ArticleListResponse,
    NewsCategory,
    SignSequenceRequest,
    SignSequenceResponse,
    SummarizeRequest,
    SummarizeResponse,
    TranslateRequest,
    TranslateResponse,
)
from app.models.sign import (
    SignDictionaryCreate,
    SignDictionaryEntry,
    SignDictionaryListResponse,
    SignDictionaryUpdate,
)
from app.repositories.articles import ArticleRepository
from app.repositories.admin import AdminRepository
from app.repositories.analytics import AnalyticsRepository
from app.repositories.feedback import FeedbackRepository, bug_report_item, feedback_item, rating_item
from app.repositories.sign_dictionary import SignDictionaryRepository
from app.repositories.sign_sequences import SignSequenceJobRepository
from app.repositories.user_features import (
    ArticleNotFoundError,
    UserFeatureRepository,
    preferences_response,
    saved_response,
    watch_response,
)
from app.schemas.user_features import (
    BookmarkRequest,
    SaveArticleRequest,
    SavedArticlesResponse,
    UserPreferencesResponse,
    UserPreferencesUpdate,
    WatchHistoryCreate,
    WatchHistoryListResponse,
)
from app.schemas.admin import AdminAnalyticsResponse, AdminReviewQueueResponse, GenerationFailure, MissingGlossResponse
from app.schemas.feedback import (
    BugReportCreate,
    BugReportItem,
    FeedbackCreate,
    FeedbackItem,
    RatingItem,
    TranslationRatingCreate,
)
from app.services.gloss import ASLGlossService
from app.services.llm import build_llm_client
from app.services.news import NewsQuery, NewsService
from app.services.sign_dictionary import SignDictionaryService
from app.services.sign_sequence import MissingSignClipError, SignSequenceService, job_response
from app.services.storage import SupabaseStorageService, UploadValidationError
from app.services.summarizer import ArticleSummary, SummarizerService
from app.services.thumbnails import ThumbnailService

router = APIRouter()
news_router = APIRouter(prefix="/news", tags=["news"], dependencies=[Depends(rate_limit)])


def article_repository(db: Session = Depends(get_db)) -> ArticleRepository:
    return ArticleRepository(db)


def admin_repository(db: Session = Depends(get_db)) -> AdminRepository:
    return AdminRepository(db)


def analytics_repository(db: Session = Depends(get_db)) -> AnalyticsRepository:
    return AnalyticsRepository(db)


def sign_dictionary_repository(db: Session = Depends(get_db)) -> SignDictionaryRepository:
    return SignDictionaryRepository(db)


def sign_sequence_repository(db: Session = Depends(get_db)) -> SignSequenceJobRepository:
    return SignSequenceJobRepository(db)


def user_feature_repository(db: Session = Depends(get_db)) -> UserFeatureRepository:
    return UserFeatureRepository(db)


def feedback_repository(db: Session = Depends(get_db)) -> FeedbackRepository:
    return FeedbackRepository(db)


def current_user_id(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str:
    return x_user_id or "00000000-0000-4000-8000-000000000001"


def require_admin(
    settings: Settings = Depends(get_settings),
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> None:
    if not settings.admin_api_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access is not configured",
        )
    if x_admin_token != settings.admin_api_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


def sign_dictionary_service(
    settings: Settings = Depends(get_settings),
    repository: SignDictionaryRepository = Depends(sign_dictionary_repository),
) -> SignDictionaryService:
    return SignDictionaryService(
        repository=repository,
        storage=SupabaseStorageService(settings),
        thumbnails=ThumbnailService(),
    )


def news_service(
    settings: Settings = Depends(get_settings),
    repository: ArticleRepository = Depends(article_repository),
    cache: RedisCache = Depends(get_cache),
) -> NewsService:
    return NewsService(settings, repository, cache)


def gloss_service() -> ASLGlossService:
    return ASLGlossService()


def sign_service(
    settings: Settings = Depends(get_settings),
    repository: SignDictionaryRepository = Depends(sign_dictionary_repository),
    jobs: SignSequenceJobRepository = Depends(sign_sequence_repository),
) -> SignSequenceService:
    return SignSequenceService(
        dictionary=repository.as_mapping(),
        settings=settings,
        storage=SupabaseStorageService(settings),
        jobs=jobs,
    )


@news_router.get("", response_model=ArticleListResponse)
async def get_news(
    category: NewsCategory | None = None,
    q: str | None = Query(default=None, min_length=2, max_length=80),
    country: str = Query(default="us", min_length=2, max_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    user_id: str = Depends(current_user_id),
    analytics: AnalyticsRepository = Depends(analytics_repository),
    service: NewsService = Depends(news_service),
) -> ArticleListResponse:
    if q:
        analytics.record_search(query=q, user_id=user_id)
    return await service.get_news(
        NewsQuery(category=category, keyword=q, country=country, page=page, page_size=page_size)
    )


@news_router.get("/trending", response_model=ArticleListResponse)
async def get_trending_news(
    country: str = Query(default="us", min_length=2, max_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    service: NewsService = Depends(news_service),
) -> ArticleListResponse:
    return await service.get_news(
        NewsQuery(category=NewsCategory.general, country=country, page=page, page_size=page_size)
    )


@news_router.get("/search", response_model=ArticleListResponse)
async def search_news(
    q: str = Query(min_length=2, max_length=80),
    country: str = Query(default="us", min_length=2, max_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    user_id: str = Depends(current_user_id),
    analytics: AnalyticsRepository = Depends(analytics_repository),
    service: NewsService = Depends(news_service),
) -> ArticleListResponse:
    analytics.record_search(query=q, user_id=user_id)
    return await service.get_news(
        NewsQuery(keyword=q, country=country, page=page, page_size=page_size)
    )


@news_router.get("/category/{category}", response_model=ArticleListResponse)
async def get_news_by_category(
    category: NewsCategory,
    country: str = Query(default="us", min_length=2, max_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    service: NewsService = Depends(news_service),
) -> ArticleListResponse:
    return await service.get_news(
        NewsQuery(category=category, country=country, page=page, page_size=page_size)
    )


@news_router.get("/{article_id}", response_model=ArticleDetailResponse)
async def get_article(
    article_id: str,
    service: NewsService = Depends(news_service),
    settings: Settings = Depends(get_settings),
    articles: ArticleRepository = Depends(article_repository),
    signs: SignSequenceService = Depends(sign_service),
) -> ArticleDetailResponse:
    article_model = await service.fetch_article_model(article_id)
    if article_model is None:
        raise HTTPException(status_code=404, detail="Article not found")

    source_text = article_model.content or article_model.description or article_model.title
    if article_model.gloss is None:
        llm = build_llm_client(settings)
        gloss_generator = ASLGlossService()
        llm_result = await llm.summarize_for_accessibility(source_text)
        gloss, _ = gloss_generator.generate(llm_result.simple_english)
        gloss_model = articles.save_gloss(
            article_id=article_model.id,
            summary=llm_result.summary,
            simple_english=llm_result.simple_english,
            asl_gloss=gloss,
            model_name=llm_result.model_name,
        )
    else:
        gloss_model = article_model.gloss

    sequence, _ = signs.generate(gloss_model.asl_gloss)
    article = await service.fetch_article(article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleDetailResponse(
        article=article,
        simplified_summary=gloss_model.simple_english,
        asl_gloss=gloss_model.asl_gloss,
        sign_sequence=sequence,
    )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(
    request: SummarizeRequest,
    settings: Settings = Depends(get_settings),
    articles: ArticleRepository = Depends(article_repository),
) -> SummarizeResponse:
    llm = build_llm_client(settings)
    result = await SummarizerService(llm).summarize_article(request.text)
    if request.article_id:
        article = articles.get_by_external_id(request.article_id)
        if article is not None:
            gloss, _ = ASLGlossService().generate(result.simple_english)
            articles.save_gloss(
                article_id=article.id,
                summary=result.summary,
                simple_english=result.simple_english,
                asl_gloss=gloss,
                model_name=result.model_name,
            )
    summary, simple = result.summary, result.simple_english
    return SummarizeResponse(summary=summary, simple_english=simple)


@router.post("/llm/summarize", response_model=ArticleSummary)
async def summarize_article_with_llm(
    request: SummarizeRequest,
    settings: Settings = Depends(get_settings),
) -> ArticleSummary:
    return await SummarizerService(build_llm_client(settings)).summarize_article(request.text)


@router.post("/translate", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest,
    service: ASLGlossService = Depends(gloss_service),
) -> TranslateResponse:
    result = service.translate(request.text)
    return TranslateResponse(
        gloss=result.gloss,
        tokens=result.gloss_tokens,
        gloss_tokens=result.gloss_tokens,
        confidence=result.confidence,
        unknown_tokens=result.unknown_tokens,
    )


@router.post("/feedback", response_model=FeedbackItem, status_code=201)
async def create_feedback(
    request: FeedbackCreate,
    user_id: str = Depends(current_user_id),
    repository: FeedbackRepository = Depends(feedback_repository),
) -> FeedbackItem:
    return feedback_item(repository.create_feedback(user_id=user_id, request=request))


@router.post("/translation-ratings", response_model=RatingItem, status_code=201)
async def create_translation_rating(
    request: TranslationRatingCreate,
    user_id: str = Depends(current_user_id),
    repository: FeedbackRepository = Depends(feedback_repository),
) -> RatingItem:
    return rating_item(repository.create_rating(user_id=user_id, request=request))


@router.post("/bug-reports", response_model=BugReportItem, status_code=201)
async def create_bug_report(
    request: BugReportCreate,
    user_id: str = Depends(current_user_id),
    repository: FeedbackRepository = Depends(feedback_repository),
) -> BugReportItem:
    return bug_report_item(repository.create_bug_report(user_id=user_id, request=request))


@router.post("/generate-sign-sequence", response_model=SignSequenceResponse)
async def generate_sign_sequence(
    request: SignSequenceRequest,
    background_tasks: BackgroundTasks,
    signs: SignSequenceService = Depends(sign_service),
) -> SignSequenceResponse:
    tokens = request.gloss_tokens or (request.gloss.split() if request.gloss else [])
    if not tokens:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="gloss or gloss_tokens is required")
    try:
        response, cached = signs.create_job(tokens)
    except MissingSignClipError as exc:
        sequence, missing = signs.generate(" ".join(tokens))
        return SignSequenceResponse(
            sequence=sequence,
            missing_tokens=missing,
            status="failed",
            progress=0,
            error_message=str(exc),
        )

    if not cached or response.status in {"queued", "failed"}:
        background_tasks.add_task(signs.render_job, response.id)
    return response


@router.get("/sequence/{sequence_id}", response_model=SignSequenceResponse)
async def get_sign_sequence_job(
    sequence_id: str,
    repository: SignSequenceJobRepository = Depends(sign_sequence_repository),
    dictionary: SignDictionaryRepository = Depends(sign_dictionary_repository),
) -> SignSequenceResponse:
    job = repository.get(sequence_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sequence job not found")

    tokens = json.loads(job.gloss_tokens)
    sequence_service = SignSequenceService(dictionary.as_mapping())
    sequence, missing = sequence_service.generate(" ".join(tokens))
    return job_response(job, sequence, missing, cached=True)


def sign_entry_response(entry) -> SignDictionaryEntry:
    return SignDictionaryEntry(
        id=entry.id,
        gloss=entry.gloss,
        video_url=entry.video_url,
        thumbnail_url=entry.thumbnail_url,
        created_at=entry.created_at,
    )


@router.get("/admin/analytics", response_model=AdminAnalyticsResponse)
async def get_admin_analytics(
    _: None = Depends(require_admin),
    repository: AdminRepository = Depends(admin_repository),
) -> AdminAnalyticsResponse:
    return repository.analytics()


@router.get("/admin/missing-glosses", response_model=MissingGlossResponse)
async def get_missing_glosses(
    limit: int = Query(default=50, ge=1, le=100),
    _: None = Depends(require_admin),
    repository: AdminRepository = Depends(admin_repository),
) -> MissingGlossResponse:
    return repository.missing_glosses(limit=limit)


@router.get("/admin/generation-failures", response_model=list[GenerationFailure])
async def get_generation_failures(
    limit: int = Query(default=20, ge=1, le=100),
    _: None = Depends(require_admin),
    repository: AdminRepository = Depends(admin_repository),
) -> list[GenerationFailure]:
    return repository.generation_failures(limit=limit)


@router.get("/admin/review-queue", response_model=AdminReviewQueueResponse)
async def get_review_queue(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: None = Depends(require_admin),
    repository: AdminRepository = Depends(admin_repository),
) -> AdminReviewQueueResponse:
    entries, total = repository.review_queue(limit=limit, offset=offset)
    return AdminReviewQueueResponse(
        entries=[sign_entry_response(entry) for entry in entries],
        total=total,
    )


@router.get("/admin/feedback", response_model=list[FeedbackItem])
async def get_feedback_queue(
    limit: int = Query(default=50, ge=1, le=100),
    _: None = Depends(require_admin),
    repository: FeedbackRepository = Depends(feedback_repository),
) -> list[FeedbackItem]:
    return [feedback_item(item) for item in repository.list_feedback(limit=limit)]


@router.get("/admin/translation-ratings", response_model=list[RatingItem])
async def get_translation_rating_queue(
    limit: int = Query(default=50, ge=1, le=100),
    _: None = Depends(require_admin),
    repository: FeedbackRepository = Depends(feedback_repository),
) -> list[RatingItem]:
    return [rating_item(item) for item in repository.list_ratings(limit=limit)]


@router.get("/admin/bug-reports", response_model=list[BugReportItem])
async def get_bug_report_queue(
    limit: int = Query(default=50, ge=1, le=100),
    _: None = Depends(require_admin),
    repository: FeedbackRepository = Depends(feedback_repository),
) -> list[BugReportItem]:
    return [bug_report_item(item) for item in repository.list_bug_reports(limit=limit)]


@router.get("/sign-dictionary", response_model=SignDictionaryListResponse)
async def list_sign_dictionary(
    q: str | None = Query(default=None, min_length=1, max_length=80),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repository: SignDictionaryRepository = Depends(sign_dictionary_repository),
) -> SignDictionaryListResponse:
    entries, total = repository.list_entries(q=q, limit=limit, offset=offset)
    return SignDictionaryListResponse(
        entries=[sign_entry_response(entry) for entry in entries],
        total=total,
    )


@router.post("/sign-dictionary/json", response_model=SignDictionaryEntry, status_code=201)
async def create_sign_dictionary_entry_json(
    request: SignDictionaryCreate,
    _: None = Depends(require_admin),
    repository: SignDictionaryRepository = Depends(sign_dictionary_repository),
) -> SignDictionaryEntry:
    try:
        entry = repository.create(
            gloss=request.gloss,
            video_url=str(request.video_url),
            thumbnail_url=str(request.thumbnail_url) if request.thumbnail_url else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return sign_entry_response(entry)


@router.post("/sign-dictionary", response_model=SignDictionaryEntry, status_code=201)
async def upload_sign_dictionary_entry(
    gloss: str = Form(...),
    video: UploadFile | None = File(default=None),
    video_url: str | None = Form(default=None),
    thumbnail_url: str | None = Form(default=None),
    _: None = Depends(require_admin),
    service: SignDictionaryService = Depends(sign_dictionary_service),
) -> SignDictionaryEntry:
    try:
        entry = await service.create_from_upload(
            gloss=gloss,
            video=video,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
        )
    except UploadValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ValueError as exc:
        status_code = status.HTTP_409_CONFLICT if "already exists" in str(exc) else status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return sign_entry_response(entry)


@router.put("/sign-dictionary/{entry_id}", response_model=SignDictionaryEntry)
async def update_sign_dictionary_entry(
    entry_id: str,
    request: SignDictionaryUpdate,
    _: None = Depends(require_admin),
    repository: SignDictionaryRepository = Depends(sign_dictionary_repository),
) -> SignDictionaryEntry:
    entry = repository.get(entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sign dictionary entry not found")
    try:
        updated = repository.update(
            entry,
            gloss=request.gloss,
            video_url=str(request.video_url) if request.video_url else None,
            thumbnail_url=str(request.thumbnail_url) if request.thumbnail_url else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return sign_entry_response(updated)


@router.put("/sign-dictionary/{entry_id}/upload", response_model=SignDictionaryEntry)
async def update_sign_dictionary_entry_upload(
    entry_id: str,
    gloss: str | None = Form(default=None),
    video: UploadFile | None = File(default=None),
    video_url: str | None = Form(default=None),
    thumbnail_url: str | None = Form(default=None),
    _: None = Depends(require_admin),
    service: SignDictionaryService = Depends(sign_dictionary_service),
) -> SignDictionaryEntry:
    payload = SignDictionaryUpdate(
        gloss=gloss,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
    )
    try:
        entry = await service.update_from_upload(entry_id=entry_id, payload=payload, video=video)
    except UploadValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sign dictionary entry not found")
    return sign_entry_response(entry)


@router.delete("/sign-dictionary/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sign_dictionary_entry(
    entry_id: str,
    _: None = Depends(require_admin),
    repository: SignDictionaryRepository = Depends(sign_dictionary_repository),
) -> None:
    entry = repository.get(entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sign dictionary entry not found")
    repository.delete(entry)


@router.get("/me/saved-articles", response_model=SavedArticlesResponse)
async def list_saved_articles(
    bookmarked: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> SavedArticlesResponse:
    items, total = repository.list_saved_articles(
        user_id=user_id,
        bookmarked=bookmarked,
        limit=limit,
        offset=offset,
    )
    return SavedArticlesResponse(items=[saved_response(item) for item in items], total=total)


@router.post("/me/saved-articles", response_model=SavedArticlesResponse, status_code=201)
async def save_article(
    request: SaveArticleRequest,
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> SavedArticlesResponse:
    try:
        saved = repository.save_article(
            user_id=user_id,
            external_article_id=request.article_id,
            bookmarked=request.bookmarked,
        )
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return SavedArticlesResponse(items=[saved_response(saved)], total=1)


@router.delete("/me/saved-articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_article(
    article_id: str,
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> None:
    try:
        repository.remove_saved_article(user_id=user_id, external_article_id=article_id)
    except ArticleNotFoundError:
        return


@router.put("/me/saved-articles/{article_id}/bookmark", response_model=SavedArticlesResponse)
async def bookmark_article(
    article_id: str,
    request: BookmarkRequest,
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> SavedArticlesResponse:
    try:
        saved = repository.set_bookmark(
            user_id=user_id,
            external_article_id=article_id,
            bookmarked=request.bookmarked,
        )
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return SavedArticlesResponse(items=[saved_response(saved)], total=1)


@router.post("/me/watch-history", response_model=WatchHistoryListResponse, status_code=201)
async def add_watch_history(
    request: WatchHistoryCreate,
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> WatchHistoryListResponse:
    try:
        item = repository.add_watch_history(
            user_id=user_id,
            external_article_id=request.article_id,
            completed=request.completed,
            duration_seconds=request.duration_seconds,
        )
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return WatchHistoryListResponse(items=[watch_response(item)], total=1)


@router.get("/me/watch-history", response_model=WatchHistoryListResponse)
async def list_watch_history(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> WatchHistoryListResponse:
    items, total = repository.list_watch_history(user_id=user_id, limit=limit, offset=offset)
    return WatchHistoryListResponse(items=[watch_response(item) for item in items], total=total)


@router.get("/me/recently-viewed", response_model=WatchHistoryListResponse)
async def recently_viewed(
    limit: int = Query(default=10, ge=1, le=50),
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> WatchHistoryListResponse:
    items, total = repository.list_watch_history(user_id=user_id, limit=limit, offset=0)
    return WatchHistoryListResponse(items=[watch_response(item) for item in items], total=total)


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> UserPreferencesResponse:
    return preferences_response(repository.get_preferences(user_id))


@router.put("/me/preferences", response_model=UserPreferencesResponse)
async def update_preferences(
    request: UserPreferencesUpdate,
    user_id: str = Depends(current_user_id),
    repository: UserFeatureRepository = Depends(user_feature_repository),
) -> UserPreferencesResponse:
    return preferences_response(repository.update_preferences(user_id=user_id, update=request))


router.include_router(news_router)
