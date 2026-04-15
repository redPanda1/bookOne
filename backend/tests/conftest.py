"""Pytest configuration for backend test suite."""

from __future__ import annotations

import os
import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def pytest_configure() -> None:
    """Provide defaults for required environment settings."""
    os.environ.setdefault("DB_HOST", "localhost")
    os.environ.setdefault("DB_PORT", "5432")
    os.environ.setdefault("DB_NAME", "bookone")
    os.environ.setdefault("DB_USER", "bookone")
    os.environ.setdefault("DB_PASSWORD", "bookone")
    os.environ.setdefault("DB_SSL_MODE", "disable")
