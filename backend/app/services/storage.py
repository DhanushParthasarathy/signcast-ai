from dataclasses import dataclass
from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import UploadFile
from supabase import Client, create_client

from app.core.config import Settings


ALLOWED_VIDEO_CONTENT_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
MAX_VIDEO_BYTES = 50 * 1024 * 1024


class StorageConfigurationError(RuntimeError):
    pass


class UploadValidationError(ValueError):
    pass


@dataclass(frozen=True)
class StoredObject:
    path: str
    public_url: str


class SupabaseStorageService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.bucket = settings.supabase_sign_bucket
        self.client: Client | None = None
        if settings.supabase_url and settings.supabase_service_role_key:
            self.client = create_client(str(settings.supabase_url), settings.supabase_service_role_key)

    async def upload_video(self, gloss: str, file: UploadFile) -> StoredObject:
        self._validate_video(file)
        data = await file.read()
        if len(data) > MAX_VIDEO_BYTES:
            raise UploadValidationError("Video file must be 50 MB or smaller")
        extension = self._extension(file.filename or "video.mp4")
        path = f"videos/{gloss.lower().replace(' ', '-')}-{uuid4().hex}{extension}"
        return self.upload_bytes(path, data, file.content_type or "video/mp4")

    def upload_thumbnail(self, gloss: str, data: bytes) -> StoredObject:
        path = f"thumbnails/{gloss.lower().replace(' ', '-')}-{uuid4().hex}.svg"
        return self.upload_bytes(path, data, "image/svg+xml")

    def upload_bytes(self, path: str, data: bytes, content_type: str) -> StoredObject:
        if self.client is None:
            return StoredObject(path=path, public_url=f"/storage/{path}")

        self.client.storage.from_(self.bucket).upload(
            path,
            data,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        public_url = self.client.storage.from_(self.bucket).get_public_url(path)
        return StoredObject(path=path, public_url=public_url)

    def _validate_video(self, file: UploadFile) -> None:
        if file.content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
            raise UploadValidationError("Only MP4, WebM, and QuickTime videos are supported")

    def _extension(self, filename: str) -> str:
        suffix = PurePosixPath(filename).suffix.lower()
        return suffix if suffix in {".mp4", ".webm", ".mov"} else ".mp4"
