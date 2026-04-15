"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings for database and auth integration."""

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_ssl_mode: str
    cognito_user_pool_id: str
    cognito_app_client_id: str
    database_url: str | None

    @property
    def db_dsn(self) -> str:
        """Build PostgreSQL DSN for psycopg."""
        return (
            f"host={self.db_host} "
            f"port={self.db_port} "
            f"dbname={self.db_name} "
            f"user={self.db_user} "
            f"password={self.db_password} "
            f"sslmode={self.db_ssl_mode}"
        )

    @property
    def sqlalchemy_database_url(self) -> str:
        """Return SQLAlchemy-compatible database URL."""
        if self.database_url:
            return self.database_url

        return (
            "postgresql+psycopg://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?sslmode={self.db_ssl_mode}"
        )


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached settings loaded from environment variables."""
    return AppSettings(
        db_host=_require_env("DB_HOST"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=_require_env("DB_NAME"),
        db_user=_require_env("DB_USER"),
        db_password=_require_env("DB_PASSWORD"),
        db_ssl_mode=os.getenv("DB_SSL_MODE", "require"),
        cognito_user_pool_id=os.getenv("COGNITO_USER_POOL_ID", ""),
        cognito_app_client_id=os.getenv("COGNITO_APP_CLIENT_ID", ""),
        database_url=os.getenv("DATABASE_URL", "").strip() or None,
    )
