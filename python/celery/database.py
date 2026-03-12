from __future__ import annotations
# pyright: reportMissingImports=false, reportImplicitRelativeImport=false

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import create_engine  # type: ignore[import-not-found]
from sqlalchemy.orm import Session, sessionmaker  # type: ignore[import-not-found]

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from models import Base

    Base.metadata.create_all(bind=engine)
