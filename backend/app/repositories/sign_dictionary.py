from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import SignDictionaryEntry
from app.schemas.sign import normalize_gloss
from app.services.sign_sequence import DEFAULT_SIGN_DICTIONARY


class DuplicateGlossError(ValueError):
    pass


class SignDictionaryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def as_mapping(self) -> dict[str, str]:
        entries = self.db.scalars(select(SignDictionaryEntry)).all()
        if not entries:
            return DEFAULT_SIGN_DICTIONARY
        return {entry.gloss.upper(): entry.video_url for entry in entries}

    def list_entries(self, *, q: str | None = None, limit: int = 50, offset: int = 0) -> tuple[list[SignDictionaryEntry], int]:
        statement = select(SignDictionaryEntry)
        count_statement = select(func.count()).select_from(SignDictionaryEntry)
        if q:
            pattern = f"%{normalize_gloss(q)}%"
            statement = statement.where(SignDictionaryEntry.gloss.ilike(pattern))
            count_statement = count_statement.where(SignDictionaryEntry.gloss.ilike(pattern))

        statement = statement.order_by(SignDictionaryEntry.gloss.asc()).offset(offset).limit(limit)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def get(self, entry_id: str) -> SignDictionaryEntry | None:
        return self.db.get(SignDictionaryEntry, entry_id)

    def get_by_gloss(self, gloss: str) -> SignDictionaryEntry | None:
        return self.db.scalar(
            select(SignDictionaryEntry).where(SignDictionaryEntry.gloss == normalize_gloss(gloss))
        )

    def create(
        self,
        *,
        gloss: str,
        video_url: str,
        thumbnail_url: str | None,
    ) -> SignDictionaryEntry:
        normalized = normalize_gloss(gloss)
        if self.get_by_gloss(normalized) is not None:
            raise DuplicateGlossError(f"Gloss '{normalized}' already exists")

        entry = SignDictionaryEntry(
            gloss=normalized,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def update(
        self,
        entry: SignDictionaryEntry,
        *,
        gloss: str | None = None,
        video_url: str | None = None,
        thumbnail_url: str | None = None,
    ) -> SignDictionaryEntry:
        if gloss is not None:
            normalized = normalize_gloss(gloss)
            duplicate = self.get_by_gloss(normalized)
            if duplicate is not None and duplicate.id != entry.id:
                raise DuplicateGlossError(f"Gloss '{normalized}' already exists")
            entry.gloss = normalized
        if video_url is not None:
            entry.video_url = video_url
        if thumbnail_url is not None:
            entry.thumbnail_url = thumbnail_url

        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete(self, entry: SignDictionaryEntry) -> None:
        self.db.delete(entry)
        self.db.commit()

    def upsert(
        self,
        *,
        gloss_token: str,
        clip_url: str,
        handshape: str | None = None,
        region: str | None = "US-ASL",
    ) -> SignDictionaryEntry:
        existing = self.get_by_gloss(gloss_token)
        if existing is None:
            return self.create(gloss=gloss_token, video_url=clip_url, thumbnail_url=None)
        return self.update(existing, video_url=clip_url)
