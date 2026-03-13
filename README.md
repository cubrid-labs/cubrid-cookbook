# CUBRID Cookbook 🍳

**Production-ready examples for using CUBRID with Python, Node.js, and Go** — SQLAlchemy, FastAPI, Django, Flask, Drizzle ORM, GORM, and more.

<!-- BADGES:START -->
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUBRID 11.2](https://img.shields.io/badge/CUBRID-11.2-green.svg)](https://www.cubrid.org/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18%2B-brightgreen.svg)](https://nodejs.org/)
[![Go 1.21+](https://img.shields.io/badge/go-1.21%2B-00ADD8.svg)](https://go.dev)
[![GitHub stars](https://img.shields.io/github/stars/cubrid-labs/cubrid-cookbook)](https://github.com/cubrid-labs/cubrid-cookbook)
<!-- BADGES:END -->

---

## What is this?

Copy-paste friendly, **runnable** examples showing how to use [CUBRID](https://www.cubrid.org/) with popular frameworks and drivers across multiple languages. Every example connects to a real CUBRID database via Docker.

## Examples

### 🐍 Python

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

### 🟩 Node.js

| Example | Driver | Description |
|---------|--------|-------------|
| [cubrid](node/cubrid/) | cubrid-client | Modern Promise-based client — connect, query, CRUD, transactions |
| [drizzle](node/drizzle/) | Drizzle ORM | Type-safe ORM — schema, query builder, CRUD, transactions, custom types |

### 🐹 Go

| Example | Driver | Description |
|---------|--------|-------------|
| [cubrid-go](go/cubrid-go/) | cubrid-go | Pure Go `database/sql` driver — connect, query, CRUD, transactions |
| [gorm](go/gorm/) | GORM | GORM ORM — AutoMigrate, models, CRUD, relationships, advanced queries |

## Quick Start

### 1. Start CUBRID

```bash
docker compose up -d
# Wait for CUBRID to be ready
make up
```

### 2. Pick an example

**Python:**
```bash
cd python/fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Node.js:**
```bash
cd node/cubrid
npm install
node 01_connect.js
```

**Go:**
```bash
cd go/cubrid-go
go run 01_connect.go
```

Every example has its own `README.md` with setup instructions.

### 3. Clean up

```bash
make clean
```

## Prerequisites

- **Docker** and **Docker Compose** (for the CUBRID database)
- **Python 3.10+** (for Python examples)
- **Node.js 18+** (for Node.js examples)
- Each example lists its own dependencies in `requirements.txt` or `package.json` or `go.mod`
- **Go 1.21+** (for Go examples)

## Project Structure

```
cubrid-cookbook/
├── docker-compose.yml          # Shared CUBRID database
├── .env.example                # Connection settings template
├── Makefile                    # Docker shortcuts
├── python/
│   ├── pycubrid/               # Direct driver usage
│   │   ├── 01_connect.py
│   │   ├── 02_crud.py
│   │   ├── 03_transactions.py
│   │   ├── 04_prepared.py
│   │   ├── 05_error_handling.py
│   │   ├── 06_lob.py
│   │   └── requirements.txt
│   ├── sqlalchemy/             # SQLAlchemy Core + ORM
│   ├── fastapi/                # FastAPI REST API
│   ├── django/                 # Django integration
│   ├── flask/                  # Flask + Flask-SQLAlchemy
│   ├── pandas/                 # Data analysis
│   ├── streamlit/              # Data dashboard
│   └── celery/                 # Async tasks
├── node/
│   ├── cubrid/                 # cubrid-client direct usage
│   │   ├── 01_connect.js
│   │   ├── 02_crud.js
│   │   ├── 03_transactions.js
│   │   └── package.json
│   └── drizzle/                # Drizzle ORM + cubrid-client
│       ├── 01_connect.js
│       ├── 02_crud.js
│       ├── 03_transactions.js
│       ├── 04_custom_types.js
│       └── package.json
├── go/
│   ├── cubrid-go/             # database/sql driver
│   │   ├── 01_connect.go
│   │   ├── 02_crud.go
│   │   ├── 03_transactions.go
│   │   └── go.mod
│   └── gorm/                  # GORM ORM
│       ├── 01_connect.go
│       ├── 02_crud.go
│       ├── 03_relationships.go
│       ├── 04_advanced.go
│       └── go.mod
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

**Python (pycubrid)**:
```python
import pycubrid
conn = pycubrid.connect(host="localhost", port=33000, database="testdb", user="dba")
```

**Python (SQLAlchemy)**:
```python
from sqlalchemy import create_engine
engine = create_engine("cubrid+pycubrid://dba@localhost:33000/testdb")
```

**Node.js (cubrid-client)**:
```js
import { createClient } from "cubrid-client";
const db = createClient({ host: "localhost", port: 33000, database: "testdb", user: "dba" });
```

**Node.js (Drizzle ORM)**:
```js
import { createClient } from "cubrid-client";
import { drizzle } from "drizzle-cubrid";
const client = createClient({ host: "localhost", port: 33000, database: "testdb", user: "dba" });
const db = drizzle(client);
```

**Go (database/sql)**:
```go
import (
    "database/sql"
    _ "github.com/cubrid-labs/cubrid-go"
)
db, _ := sql.Open("cubrid", "cubrid://dba:@localhost:33000/testdb")
```

**Go (GORM)**:
```go
import (
    "gorm.io/gorm"
    cubrid "github.com/cubrid-labs/cubrid-go/dialector"
)
db, _ := gorm.Open(cubrid.Open("cubrid://dba:@localhost:33000/testdb"), &gorm.Config{})
```

## Related Projects

- [pycubrid](https://github.com/cubrid-labs/pycubrid) — Pure Python DB-API 2.0 driver for CUBRID
- [sqlalchemy-cubrid](https://github.com/cubrid-labs/sqlalchemy-cubrid) — SQLAlchemy 2.0 dialect for CUBRID
- [cubrid-client](https://github.com/cubrid-labs/cubrid-client) — Modern TypeScript-first Node.js client for CUBRID
- [drizzle-cubrid](https://github.com/cubrid-labs/drizzle-cubrid) — Drizzle ORM dialect for CUBRID
- [cubrid-go](https://github.com/cubrid-labs/cubrid-go) — Pure Go CUBRID driver (`database/sql` + GORM)
- [CUBRID](https://www.cubrid.org/) — The CUBRID database

## FAQ

### How do I use CUBRID with Python?

See the [pycubrid examples](python/pycubrid/) for direct driver usage or [SQLAlchemy examples](python/sqlalchemy/) for ORM usage. Install: `pip install pycubrid` or `pip install sqlalchemy-cubrid`.

### How do I use CUBRID with Node.js / TypeScript?

See the [cubrid-client examples](node/cubrid/) for direct driver usage or [Drizzle ORM examples](node/drizzle/) for ORM usage. Install: `npm install cubrid-client` or `npm install drizzle-cubrid drizzle-orm cubrid-client`.

### How do I use CUBRID with Go?

See the [cubrid-go examples](go/cubrid-go/) for `database/sql` usage or [GORM examples](go/gorm/) for ORM usage. Install: `go get github.com/cubrid-labs/cubrid-go`.

### How do I start a CUBRID database for testing?

```bash
docker compose up -d
```

This starts CUBRID 11.2 on `localhost:33000` with database `testdb` and user `dba`.

### How do I use CUBRID with FastAPI?

See the [FastAPI example](python/fastapi/) — a complete REST API with automatic OpenAPI docs, dependency injection, and CRUD operations using sqlalchemy-cubrid.

### How do I use CUBRID with Django?

See the [Django example](python/django/) — Django project using CUBRID via SQLAlchemy bridge since there is no native Django CUBRID backend.

### How do I use CUBRID with Pandas?

See the [Pandas example](python/pandas/) — data analysis pipeline with `read_sql`, DataFrame transforms, and visualization using pycubrid or sqlalchemy-cubrid.


## Contributing

Found a bug or want to add an example? PRs welcome! Each example should be self-contained and independently runnable.

## License

[Apache License 2.0](LICENSE)
