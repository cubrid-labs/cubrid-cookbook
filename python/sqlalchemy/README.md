# SQLAlchemy Examples

SQLAlchemy Core + ORM examples with CUBRID using [sqlalchemy-cubrid](https://github.com/cubrid-labs/sqlalchemy-cubrid).

## Setup

```bash
pip install -r requirements.txt
```

Make sure CUBRID is running:

```bash
# From the repo root
make up
```

## Examples

| File | Topic |
|------|-------|
| `01_engine.py` | Engine creation, connection URLs, pool settings |
| `02_core.py` | SQLAlchemy Core — Table, select, insert, text() |
| `03_orm.py` | ORM — DeclarativeBase, mapped_column, Session, CRUD |
| `04_relationships.py` | ORM relationships — one-to-many, many-to-many, eager loading |
| `05_dml_extensions.py` | CUBRID-specific DML — ON DUPLICATE KEY UPDATE, MERGE, REPLACE |
| `06_reflection.py` | Schema reflection — inspect tables, columns, indexes |

## Run

```bash
python 01_engine.py
python 02_core.py
# ... etc
```

Each script is self-contained — it creates its own tables and cleans up after.
