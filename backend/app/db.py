from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def session_factory(database_url: str) -> sessionmaker[Session]:
    engine = create_engine(database_url, pool_pre_ping=True, connect_args={"connect_timeout": 5})
    return sessionmaker(engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    factory = session_factory(get_settings().database_url)
    with factory() as session:
        yield session
