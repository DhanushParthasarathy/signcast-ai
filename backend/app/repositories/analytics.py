from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SearchEvent
from app.repositories.user_features import UserFeatureRepository


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserFeatureRepository(db)

    def record_search(self, *, query: str, user_id: str | None = None) -> None:
        normalized = " ".join(query.strip().lower().split())
        if not normalized:
            return
        if user_id:
            self.users.ensure_user(user_id)
        self.db.add(SearchEvent(query=normalized, user_id=user_id))
        self.db.commit()

    def has_recent_query(self, *, query: str, user_id: str | None = None) -> bool:
        normalized = " ".join(query.strip().lower().split())
        statement = select(SearchEvent).where(SearchEvent.query == normalized)
        if user_id:
            statement = statement.where(SearchEvent.user_id == user_id)
        return self.db.scalar(statement.limit(1)) is not None
