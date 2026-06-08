import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError
from .config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def wait_for_database(max_attempts: int = 20, delay_seconds: float = 1.5) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect():
                return
        except OperationalError:
            if attempt == max_attempts:
                raise
            time.sleep(delay_seconds)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
