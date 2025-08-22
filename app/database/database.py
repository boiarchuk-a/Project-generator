from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Engine

from .config import get_settings

def get_engine():
    settings = get_settings()

    engine = create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine


engine = get_engine()


def get_session():
    with Session(engine) as session:
        yield session


def init_db(base_cls, drop_all: bool = False) -> Engine:
    engine = get_engine()
    if drop_all:
        base_cls.metadata.drop_all(engine)
    base_cls.metadata.create_all(engine)
    return engine
