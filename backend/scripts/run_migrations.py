"""Minimal local migration runner for numbered SQL files."""

import os
from pathlib import Path
import sys

import psycopg


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
MIGRATIONS_DIR = BASE_DIR / "db" / "migrations"
ENV_FILE = BASE_DIR / ".env"


def load_dotenv(path):
    """Load KEY=VALUE pairs from a .env file into process env."""
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def validate_required_env():
    required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        missing_csv = ", ".join(missing)
        raise RuntimeError(
            f"Missing required DB env vars: {missing_csv}. "
            "Set them in shell or backend/.env."
        )

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config.settings import get_settings  # noqa: E402


def ensure_schema_migrations_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )


def load_applied_versions(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations")
        return {row[0] for row in cur.fetchall()}


def run():
    load_dotenv(ENV_FILE)
    validate_required_env()

    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migrations:
        print("No migration files found.")
        return

    settings = get_settings()

    with psycopg.connect(settings.db_dsn) as conn:
        ensure_schema_migrations_table(conn)
        applied = load_applied_versions(conn)

        for migration_file in migrations:
            version = migration_file.name
            if version in applied:
                print(f"Skipping {version} (already applied)")
                continue

            sql = migration_file.read_text()
            print(f"Applying {version}...")

            with conn.cursor() as cur:
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (version,),
                )

            conn.commit()
            print(f"Applied {version}")

    print("Migration run complete.")


if __name__ == "__main__":
    run()
