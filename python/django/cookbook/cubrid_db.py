from __future__ import annotations

import os
from contextlib import contextmanager
from collections.abc import Iterator
from importlib import import_module
from typing import Callable, Protocol, cast

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_CUBRID_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


class CursorLike(Protocol):
    def execute(self, operation: str, parameters: tuple[object, ...] | None = None) -> object: ...

    def fetchone(self) -> tuple[object, ...] | None: ...

    def fetchall(self) -> list[tuple[object, ...]]: ...

    def close(self) -> object: ...


class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...

    def commit(self) -> object: ...

    def rollback(self) -> object: ...

    def close(self) -> object: ...


def get_cubrid_url() -> str:
    return os.getenv("CUBRID_SQLALCHEMY_URL", DEFAULT_CUBRID_URL)


def get_engine() -> Engine:
    global _engine, _session_factory
    if _engine is None:
        _engine = create_engine(get_cubrid_url(), future=True, pool_pre_ping=True)
        _session_factory = sessionmaker(
            bind=_engine, autoflush=False, autocommit=False, future=True
        )
    return _engine


def get_session() -> Session:
    if _session_factory is None:
        _ = get_engine()
    assert _session_factory is not None
    return _session_factory()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_pycubrid_connection() -> ConnectionLike:
    pycubrid = import_module("pycubrid")
    connect = cast(Callable[..., ConnectionLike], getattr(pycubrid, "connect"))
    return connect(
        host=os.getenv("CUBRID_HOST", "localhost"),
        port=int(os.getenv("CUBRID_PORT", "33000")),
        database=os.getenv("CUBRID_DB", "testdb"),
        user=os.getenv("CUBRID_USER", "dba"),
        password=os.getenv("CUBRID_PASSWORD", ""),
    )


@contextmanager
def pycubrid_cursor() -> Iterator[CursorLike]:
    connection = get_pycubrid_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        _ = connection.commit()
    except Exception:
        _ = connection.rollback()
        raise
    finally:
        _ = cursor.close()
        _ = connection.close()
