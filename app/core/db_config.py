from __future__ import annotations

import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

SQLITE_CONNECT_ARGS = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
