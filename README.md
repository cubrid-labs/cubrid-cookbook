# CUBRID Cookbook 🍳

**Production-ready examples for CUBRID with Python.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUBRID 11.2](https://img.shields.io/badge/CUBRID-11.2-green.svg)](https://www.cubrid.org/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

---

## What is this?

Copy-paste friendly, **runnable** examples showing how to use [CUBRID](https://www.cubrid.org/) with popular Python frameworks. Every example connects to a real CUBRID database via Docker.

## Examples

| Example | Framework | Description |
|---------|-----------|-------------|
| [pycubrid](python/pycubrid/) | pycubrid | Direct DB-API 2.0 driver — connect, query, transactions, prepared statements, LOBs |
| [sqlalchemy](python/sqlalchemy/) | SQLAlchemy | Core + ORM — engine, models, CRUD, DML extensions (ODKU, MERGE, REPLACE) |
| [fastapi](python/fastapi/) | FastAPI | REST API with automatic docs, dependency injection, async-ready |
| [django](python/django/) | Django | Django project with CUBRID via SQLAlchemy bridge |
| [flask](python/flask/) | Flask | Flask + Flask-SQLAlchemy — blueprints, models, CRUD routes |
| [pandas](python/pandas/) | Pandas | Data analysis pipeline — read_sql, transforms, visualization |
| [streamlit](python/streamlit/) | Streamlit | Interactive data dashboard with live CUBRID queries |
| [celery](python/celery/) | Celery | Async task queue — background jobs backed by CUBRID |

## Quick Start

### 1. Start CUBRID

```bash
docker compose up -d
# Wait for CUBRID to be ready
make up
```

### 2. Pick an example

```bash
cd python/fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Every example has its own `README.md` with setup instructions.

### 3. Clean up

```bash
make clean
```

## Prerequisites

- **Docker** and **Docker Compose** (for the CUBRID database)
- **Python 3.10+**
- Each example lists its own dependencies in `requirements.txt`

## Project Structure

```
cubrid-cookbook/
├── docker-compose.yml          # Shared CUBRID database
├── .env.example                # Connection settings template
├── Makefile                    # Docker shortcuts
└── python/
    ├── pycubrid/               # Direct driver usage
    │   ├── 01_connect.py
    │   ├── 02_crud.py
    │   ├── 03_transactions.py
    │   ├── 04_prepared.py
    │   ├── 05_error_handling.py
    │   ├── 06_lob.py
    │   └── requirements.txt
    ├── sqlalchemy/             # SQLAlchemy Core + ORM
    │   ├── 01_engine.py
    │   ├── 02_core.py
    │   ├── 03_orm.py
    │   ├── 04_relationships.py
    │   ├── 05_dml_extensions.py
    │   ├── 06_reflection.py
    │   └── requirements.txt
    ├── fastapi/                # FastAPI REST API
    │   ├── app/
    │   │   ├── main.py
    │   │   ├── database.py
    │   │   ├── models.py
    │   │   ├── schemas.py
    │   │   └── routes/
    │   ├── tests/
    │   └── requirements.txt
    ├── django/                 # Django integration
    ├── flask/                  # Flask + Flask-SQLAlchemy
    ├── pandas/                 # Data analysis
    ├── streamlit/              # Data dashboard
    └── celery/                 # Async tasks
```

## Connection

All examples connect to the same CUBRID instance:

| Setting | Value |
|---------|-------|
| Host | `localhost` |
| Port | `33000` |
| Database | `testdb` |
| User | `dba` |
| Password | *(empty)* |

**pycubrid (direct)**:
```python
import pycubrid
conn = pycubrid.connect(host="localhost", port=33000, database="testdb", user="dba")
```

**SQLAlchemy**:
```python
from sqlalchemy import create_engine
engine = create_engine("cubrid+pycubrid://dba@localhost:33000/testdb")
```

## Related Projects

- [pycubrid](https://github.com/cubrid-labs/pycubrid) — Pure Python DB-API 2.0 driver for CUBRID
- [sqlalchemy-cubrid](https://github.com/cubrid-labs/sqlalchemy-cubrid) — SQLAlchemy 2.0 dialect for CUBRID
- [CUBRID](https://www.cubrid.org/) — The CUBRID database

## Contributing

Found a bug or want to add an example? PRs welcome! Each example should be self-contained and independently runnable.

## License

[Apache License 2.0](LICENSE)
