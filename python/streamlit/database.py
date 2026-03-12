from __future__ import annotations

import importlib

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

st = importlib.import_module("streamlit")

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"
TABLE_NAME = "cookbook_orders"


cache_resource = getattr(st, "cache_resource")


@cache_resource
def get_engine() -> Engine:
    return create_engine(DATABASE_URL)


def run_query(sql: str, params: dict[str, object] | None = None) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as connection:
        return pd.read_sql_query(text(sql), connection, params=params)
