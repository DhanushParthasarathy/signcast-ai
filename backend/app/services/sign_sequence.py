import asyncio
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

import httpx

from app.core.config import Settings
from app.db.session import SessionLocal
from app.models.article import SignSequenceItem, SignSequenceResponse
from app.repositories.sign_dictionary import SignDictionaryRepository
from app.repositories.sign_sequences import SignSequenceJobRepository
from app.services.storage import SupabaseStorageService


DEFAULT_SIGN_DICTIONARY: dict[str, str] = {
    "NASA": "/signs/nasa.mp4",
    "LAUNCH": "/signs/launch.mp4",
    "SATELLITE": "/signs/satellite.mp4",
    "CLIMATE": "/signs/climate.mp4",
    "WATCH": "/signs/watch.mp4",
    "EARTH": "/signs/earth.mp4",
    "STUDENT": "/signs/student.mp4",
    "ACCESSIBILITY": "/signs/accessibility.mp4",
    "NEWS": "/signs/news.mp4",
    "CITY": "/signs/city.mp4",
    "TRAIN": "/signs/train.mp4",
    "BUS": "/signs/bus.mp4",
}


class SignSequenceError(RuntimeError):
    pass


class MissingSignClipError(SignSequenceError):
    def __init__(self, missing_tokens: list[str]) -> None:
        self.missing_tokens = missing_tokens
        super().__init__(f"Missing sign clips for: {', '.join(missing_tokens)}")


class SignSequenceService:
    def __init__(
        self,
        dictionary: dict[str, str] | None = None,
        settings: Settings | None = None,
        storage: SupabaseStorageService | None = None,
        jobs: SignSequenceJobRepository | None = None,
    ) -> None:
        self.dictionary = dictionary or DEFAULT_SIGN_DICTIONARY
        self.settings = settings
        self.storage = storage
        self.jobs = jobs

    def generate(self, gloss: str) -> tuple[list[SignSequenceItem], list[str]]:
        sequence: list[SignSequenceItem] = []
        missing: list[str] = []
        for token in normalize_tokens(gloss.split()):
            clip_url = self.dictionary.get(token)
            status = "ready" if clip_url else "missing"
            if not clip_url:
                missing.append(token)
            sequence.append(SignSequenceItem(token=token, clip_url=clip_url, status=status))
        return sequence, missing

    def create_job(self, tokens: list[str]) -> tuple[SignSequenceResponse, bool]:
        if self.jobs is None:
            raise SignSequenceError("Sequence job repository is not configured")
        normalized = normalize_tokens(tokens)
        sequence, missing = self._lookup_sequence(normalized)
        if missing:
            raise MissingSignClipError(missing)

        sequence_hash = sequence_cache_key(normalized)
        job, cached = self.jobs.create_or_get(sequence_hash=sequence_hash, gloss_tokens=normalized)
        return job_response(job, sequence, [], cached=cached), cached

    async def render_job(self, job_id: str) -> None:
        if self.settings is None:
            raise SignSequenceError("Settings are required to render a sign sequence")

        for _ in range(self.settings.sequence_max_retries):
            db = SessionLocal()
            try:
                jobs = SignSequenceJobRepository(db)
                dictionary = SignDictionaryRepository(db).as_mapping()
                job = jobs.get(job_id)
                if job is None or job.status == "completed":
                    return

                jobs.mark_running(job)
                tokens = json.loads(job.gloss_tokens)
                sequence_service = SignSequenceService(dictionary=dictionary)
                sequence, missing = sequence_service._lookup_sequence(tokens)
                if missing:
                    raise MissingSignClipError(missing)

                jobs.update_progress(job, 25)
                output_path = await self._merge_sequence(job.id, sequence, jobs, job)
                jobs.update_progress(job, 85)

                storage = self.storage or SupabaseStorageService(self.settings)
                output_url = storage.upload_bytes(
                    f"sequences/{job.id}.mp4",
                    output_path.read_bytes(),
                    "video/mp4",
                ).public_url
                jobs.mark_completed(job, output_url)
                return
            except Exception as exc:
                if "job" in locals():
                    attempts = getattr(job, "attempts", 0)
                    if attempts >= self.settings.sequence_max_retries:
                        jobs.mark_failed(job, str(exc))
                        return
                    jobs.mark_failed(job, str(exc))
                await asyncio.sleep(0.5)
            finally:
                db.close()

    async def _merge_sequence(
        self,
        job_id: str,
        sequence: list[SignSequenceItem],
        jobs: SignSequenceJobRepository,
        job,
    ) -> Path:
        ffmpeg = (self.settings.ffmpeg_path if self.settings else "ffmpeg")
        if shutil.which(ffmpeg) is None and not Path(ffmpeg).exists():
            raise SignSequenceError(f"FFmpeg executable not found: {ffmpeg}")

        with TemporaryDirectory(prefix=f"signcast-{job_id}-") as temp_dir:
            temp_path = Path(temp_dir)
            clip_paths = await self._materialize_clips(sequence, temp_path)
            jobs.update_progress(job, 55)
            concat_file = temp_path / "clips.txt"
            concat_file.write_text(
                "\n".join(f"file '{path.as_posix()}'" for path in clip_paths),
                encoding="utf-8",
            )
            output_path = temp_path / "sequence.mp4"
            command = [
                ffmpeg,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(output_path),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                raise SignSequenceError(result.stderr.strip() or "FFmpeg merge failed")
            permanent_path = Path(temp_dir).parent / f"{job_id}.mp4"
            shutil.copyfile(output_path, permanent_path)
            return permanent_path

    async def _materialize_clips(
        self,
        sequence: list[SignSequenceItem],
        temp_path: Path,
    ) -> list[Path]:
        paths: list[Path] = []
        async with httpx.AsyncClient(timeout=30) as client:
            for index, item in enumerate(sequence):
                if not item.clip_url:
                    raise MissingSignClipError([item.token])
                suffix = Path(urlparse(item.clip_url).path).suffix or ".mp4"
                destination = temp_path / f"{index:03d}-{item.token}{suffix}"
                if item.clip_url.startswith("http://") or item.clip_url.startswith("https://"):
                    response = await client.get(item.clip_url)
                    response.raise_for_status()
                    destination.write_bytes(response.content)
                else:
                    source = resolve_local_clip(item.clip_url)
                    if source is None:
                        raise SignSequenceError(f"Clip file not found for {item.token}: {item.clip_url}")
                    shutil.copyfile(source, destination)
                paths.append(destination)
        return paths

    def _lookup_sequence(self, tokens: list[str]) -> tuple[list[SignSequenceItem], list[str]]:
        sequence: list[SignSequenceItem] = []
        missing: list[str] = []
        for token in normalize_tokens(tokens):
            clip_url = self.dictionary.get(token)
            status = "ready" if clip_url else "missing"
            if not clip_url:
                missing.append(token)
            sequence.append(SignSequenceItem(token=token, clip_url=clip_url, status=status))
        return sequence, missing


def normalize_tokens(tokens: list[str]) -> list[str]:
    return [" ".join(token.upper().strip().split()) for token in tokens if token and token.strip()]


def sequence_cache_key(tokens: list[str]) -> str:
    return hashlib.sha256("|".join(normalize_tokens(tokens)).encode("utf-8")).hexdigest()


def job_response(
    job,
    sequence: list[SignSequenceItem],
    missing_tokens: list[str],
    *,
    cached: bool,
) -> SignSequenceResponse:
    return SignSequenceResponse(
        id=job.id,
        status=job.status,
        progress=job.progress,
        output_url=job.output_url,
        error_message=job.error_message,
        attempts=job.attempts,
        sequence=sequence,
        missing_tokens=missing_tokens,
        cached=cached,
    )


def resolve_local_clip(clip_url: str) -> Path | None:
    candidates = [
        Path(clip_url),
        Path.cwd() / clip_url.lstrip("/"),
        Path.cwd().parent / "frontend" / "public" / clip_url.lstrip("/"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None
