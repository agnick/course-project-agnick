from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.db_config import DATABASE_URL, SQLITE_CONNECT_ARGS

engine = create_engine(DATABASE_URL, connect_args=SQLITE_CONNECT_ARGS)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
