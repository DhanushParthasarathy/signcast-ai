from fastapi import UploadFile

from app.repositories.sign_dictionary import DuplicateGlossError, SignDictionaryRepository
from app.schemas.sign import SignDictionaryCreate, SignDictionaryUpdate, normalize_gloss
from app.services.storage import SupabaseStorageService
from app.services.thumbnails import ThumbnailService


class SignDictionaryService:
    def __init__(
        self,
        repository: SignDictionaryRepository,
        storage: SupabaseStorageService,
        thumbnails: ThumbnailService,
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.thumbnails = thumbnails

    async def create_from_upload(
        self,
        *,
        gloss: str,
        video: UploadFile | None,
        video_url: str | None,
        thumbnail_url: str | None,
    ):
        normalized = normalize_gloss(gloss)
        if self.repository.get_by_gloss(normalized) is not None:
            raise DuplicateGlossError(f"Gloss '{normalized}' already exists")
        if video is None and not video_url:
            raise ValueError("Either a video file or video_url is required")

        final_video_url = video_url
        if video is not None:
            final_video_url = (await self.storage.upload_video(normalized, video)).public_url

        final_thumbnail_url = thumbnail_url
        if final_thumbnail_url is None:
            thumbnail = self.thumbnails.generate_svg_thumbnail(normalized)
            final_thumbnail_url = self.storage.upload_thumbnail(normalized, thumbnail).public_url

        return self.repository.create(
            gloss=normalized,
            video_url=final_video_url or "",
            thumbnail_url=final_thumbnail_url,
        )

    async def update_from_upload(
        self,
        *,
        entry_id: str,
        payload: SignDictionaryUpdate,
        video: UploadFile | None = None,
    ):
        entry = self.repository.get(entry_id)
        if entry is None:
            return None

        normalized_gloss = normalize_gloss(payload.gloss) if payload.gloss else None
        final_video_url = str(payload.video_url) if payload.video_url else None
        if video is not None:
            final_video_url = (await self.storage.upload_video(normalized_gloss or entry.gloss, video)).public_url

        thumbnail_url = str(payload.thumbnail_url) if payload.thumbnail_url else None
        if thumbnail_url is None and (video is not None or normalized_gloss is not None):
            thumbnail = self.thumbnails.generate_svg_thumbnail(normalized_gloss or entry.gloss)
            thumbnail_url = self.storage.upload_thumbnail(normalized_gloss or entry.gloss, thumbnail).public_url

        return self.repository.update(
            entry,
            gloss=normalized_gloss,
            video_url=final_video_url,
            thumbnail_url=thumbnail_url,
        )
