import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SignSequenceJob


class SignSequenceJobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, job_id: str) -> SignSequenceJob | None:
        return self.db.get(SignSequenceJob, job_id)

    def get_by_hash(self, sequence_hash: str) -> SignSequenceJob | None:
        return self.db.scalar(
            select(SignSequenceJob).where(SignSequenceJob.sequence_hash == sequence_hash)
        )

    def create_or_get(self, *, sequence_hash: str, gloss_tokens: list[str]) -> tuple[SignSequenceJob, bool]:
        existing = self.get_by_hash(sequence_hash)
        if existing is not None:
            return existing, True

        job = SignSequenceJob(
            sequence_hash=sequence_hash,
            gloss_tokens=json.dumps(gloss_tokens),
            status="queued",
            progress=0,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job, False

    def mark_running(self, job: SignSequenceJob) -> SignSequenceJob:
        job.status = "running"
        job.progress = max(job.progress, 10)
        job.attempts += 1
        job.error_message = None
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_progress(self, job: SignSequenceJob, progress: int) -> SignSequenceJob:
        job.progress = min(max(progress, 0), 99)
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_completed(self, job: SignSequenceJob, output_url: str) -> SignSequenceJob:
        job.status = "completed"
        job.progress = 100
        job.output_url = output_url
        job.error_message = None
        job.completed_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_failed(self, job: SignSequenceJob, error_message: str) -> SignSequenceJob:
        job.status = "failed"
        job.error_message = error_message
        self.db.commit()
        self.db.refresh(job)
        return job
