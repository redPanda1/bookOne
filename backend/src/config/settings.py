"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from psycopg.conninfo import make_conninfo
from sqlalchemy.engine.url import URL

_BUNDLED_RDS_CA = Path(__file__).resolve().parent.parent / "certs" / "global-bundle.pem"

# libpq only accepts these; common typo "required" breaks verification behavior.
_SSL_MODE_ALIASES = {"required": "require"}


def _normalize_ssl_mode(raw: str) -> str:
    key = raw.strip().lower()
    return _SSL_MODE_ALIASES.get(key, key)


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings for database and auth integration."""

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_ssl_mode: str
    db_ssl_root_cert: str | None
    cognito_user_pool_id: str
    cognito_app_client_id: str
    database_url: str | None

    @property
    def db_dsn(self) -> str:
        """Build PostgreSQL DSN for psycopg (safe quoting via make_conninfo)."""
        kwargs: dict[str, str] = {
            "host": self.db_host,
            "port": str(self.db_port),
            "dbname": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "sslmode": self.db_ssl_mode,
        }
        cert = self.db_ssl_root_cert
        if cert and self.db_ssl_mode in {"verify-ca", "verify-full"}:
            kwargs["sslrootcert"] = cert
        return make_conninfo(**kwargs)

    @property
    def sqlalchemy_database_url(self) -> str:
        """Return SQLAlchemy-compatible database URL."""
        if self.database_url:
            return self.database_url

        query: dict[str, str | list[str]] = {"sslmode": self.db_ssl_mode}
        cert = self.db_ssl_root_cert
        if cert and self.db_ssl_mode in {"verify-ca", "verify-full"}:
            query["sslrootcert"] = cert

        url = URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query=query,
        )
        return url.render_as_string(hide_password=False)


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _resolve_ssl_root_cert() -> str | None:
    """Prefer DB_SSL_ROOT_CERT; otherwise use bundled AWS RDS global-bundle.pem if present."""
    override = os.getenv("DB_SSL_ROOT_CERT", "").strip()
    if override:
        return override
    if _BUNDLED_RDS_CA.is_file():
        return str(_BUNDLED_RDS_CA)
    return None


def _validate_ssl_mode(mode: str) -> None:
    allowed = frozenset(
        {
            "disable",
            "allow",
            "prefer",
            "require",
            "verify-ca",
            "verify-full",
        }
    )
    if mode not in allowed:
        raise RuntimeError(
            f"Invalid DB_SSL_MODE={mode!r}; use one of: {', '.join(sorted(allowed))}"
        )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached settings loaded from environment variables."""
    ssl_mode = _normalize_ssl_mode(os.getenv("DB_SSL_MODE", "require"))
    _validate_ssl_mode(ssl_mode)
    return AppSettings(
        db_host=_require_env("DB_HOST"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=_require_env("DB_NAME"),
        db_user=_require_env("DB_USER"),
        db_password=_require_env("DB_PASSWORD"),
        db_ssl_mode=ssl_mode,
        db_ssl_root_cert=_resolve_ssl_root_cert(),
        cognito_user_pool_id=os.getenv("COGNITO_USER_POOL_ID", ""),
        cognito_app_client_id=os.getenv("COGNITO_APP_CLIENT_ID", ""),
        database_url=os.getenv("DATABASE_URL", "").strip() or None,
    )
