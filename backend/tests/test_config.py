import pytest

from app.core.config import Settings, normalize_database_url


def test_normalize_railway_postgres_url_to_psycopg_driver() -> None:
    url = normalize_database_url("postgres://user:pass@host.railway.internal:5432/railway")

    assert url == "postgresql+psycopg://user:pass@host.railway.internal:5432/railway"


def test_normalize_plain_postgresql_url_to_psycopg_driver() -> None:
    url = normalize_database_url("postgresql://user:pass@host:5432/signcast")

    assert url == "postgresql+psycopg://user:pass@host:5432/signcast"


def test_settings_normalizes_database_url_from_environment_value() -> None:
    settings = Settings(database_url="postgres://user:pass@localhost:5432/signcast")

    assert settings.database_url == "postgresql+psycopg://user:pass@localhost:5432/signcast"


def test_settings_reads_database_url_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@railway.internal:5432/railway")

    settings = Settings(_env_file=None)

    assert settings.database_url == "postgresql+psycopg://user:pass@railway.internal:5432/railway"


def test_invalid_database_url_has_clear_error() -> None:
    with pytest.raises(ValueError, match="Invalid DATABASE_URL"):
        normalize_database_url("not a database url")
