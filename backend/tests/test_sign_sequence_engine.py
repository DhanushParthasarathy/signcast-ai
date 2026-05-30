import json

from app.services.sign_sequence import (
    MissingSignClipError,
    SignSequenceService,
    job_response,
    sequence_cache_key,
)


class FakeJob:
    def __init__(self) -> None:
        self.id = "job-1"
        self.status = "queued"
        self.progress = 0
        self.output_url = None
        self.error_message = None
        self.attempts = 0
        self.gloss_tokens = json.dumps(["NASA", "LAUNCH"])


class FakeJobs:
    def __init__(self) -> None:
        self.job: FakeJob | None = None

    def create_or_get(self, *, sequence_hash: str, gloss_tokens: list[str]):
        if self.job is None:
            self.job = FakeJob()
            self.job.sequence_hash = sequence_hash
            self.job.gloss_tokens = json.dumps(gloss_tokens)
            return self.job, False
        return self.job, True


def test_sequence_cache_key_normalizes_tokens() -> None:
    assert sequence_cache_key([" nasa ", "launch"]) == sequence_cache_key(["NASA", "LAUNCH"])


def test_create_job_detects_missing_clips() -> None:
    service = SignSequenceService(dictionary={"NASA": "/signs/nasa.mp4"}, jobs=FakeJobs())

    try:
        service.create_job(["NASA", "SATELLITE"])
    except MissingSignClipError as exc:
        assert exc.missing_tokens == ["SATELLITE"]
    else:
        raise AssertionError("Expected missing clip error")


def test_create_job_reuses_cached_sequence() -> None:
    jobs = FakeJobs()
    service = SignSequenceService(
        dictionary={"NASA": "/signs/nasa.mp4", "LAUNCH": "/signs/launch.mp4"},
        jobs=jobs,
    )

    first, first_cached = service.create_job(["NASA", "LAUNCH"])
    second, second_cached = service.create_job(["NASA", "LAUNCH"])

    assert first.id == second.id
    assert first_cached is False
    assert second_cached is True


def test_job_response_contains_progress_and_output() -> None:
    job = FakeJob()
    job.status = "completed"
    job.progress = 100
    job.output_url = "https://example.com/sequence.mp4"

    response = job_response(job, [], [], cached=True)

    assert response.id == "job-1"
    assert response.status == "completed"
    assert response.output_url == "https://example.com/sequence.mp4"
    assert response.cached is True
