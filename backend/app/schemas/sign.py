from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator


def normalize_gloss(value: str) -> str:
    gloss = " ".join(value.strip().upper().split())
    if not gloss:
        raise ValueError("Gloss is required")
    if len(gloss) > 80:
        raise ValueError("Gloss must be 80 characters or fewer")
    if not all(character.isalnum() or character in {" ", "-"} for character in gloss):
        raise ValueError("Gloss may contain only letters, numbers, spaces, and hyphens")
    return gloss


class SignDictionaryEntry(BaseModel):
    id: str
    gloss: str
    video_url: HttpUrl | str
    thumbnail_url: HttpUrl | str | None = None
    created_at: datetime


class SignDictionaryCreate(BaseModel):
    gloss: str = Field(min_length=1, max_length=80)
    video_url: HttpUrl | str
    thumbnail_url: HttpUrl | str | None = None

    @field_validator("gloss")
    @classmethod
    def validate_gloss(cls, value: str) -> str:
        return normalize_gloss(value)


class SignDictionaryUpdate(BaseModel):
    gloss: str | None = Field(default=None, min_length=1, max_length=80)
    video_url: HttpUrl | str | None = None
    thumbnail_url: HttpUrl | str | None = None

    @field_validator("gloss")
    @classmethod
    def validate_gloss(cls, value: str | None) -> str | None:
        return normalize_gloss(value) if value is not None else None


class SignDictionaryListResponse(BaseModel):
    entries: list[SignDictionaryEntry]
    total: int
