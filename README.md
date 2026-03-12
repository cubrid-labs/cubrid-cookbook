# CUBRID Cookbook 🍳

**Production-ready examples for CUBRID across multiple languages.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUBRID 11.2](https://img.shields.io/badge/CUBRID-11.2-green.svg)](https://www.cubrid.org/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18%2B-brightgreen.svg)](https://nodejs.org/)
[![Java 17+](https://img.shields.io/badge/java-17%2B-orange.svg)](https://adoptium.net/)

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
| [cubrid](node/cubrid/) | @cubrid/client | Modern Promise-based client — connect, query, CRUD, transactions |

### ☕ Java

| Example | Driver | Description |
|---------|--------|-------------|
| [jdbc](java/jdbc/) | CUBRID JDBC | Standard JDBC 4.0 — connect, query, CRUD, transactions, savepoints |

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

**Java:**
```bash
cd java/jdbc
mvn compile
mvn exec:java -Dexec.mainClass="cookbook.Connect"
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
- **Java 17+** and **Maven 3.6+** (for Java examples)
- Each example lists its own dependencies in `requirements.txt` or `package.json` or `pom.xml`

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
│   └── cubrid/                 # @cubrid/client direct usage
│       ├── 01_connect.js
│       ├── 02_crud.js
│       ├── 03_transactions.js
│       └── package.json
└── java/
    └── jdbc/                   # CUBRID JDBC direct usage
        ├── src/main/java/cookbook/
        │   ├── Connect.java
        │   ├── Crud.java
        │   └── Transactions.java
        └── pom.xml
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

**Node.js (@cubrid/client)**:
```js
import { createClient } from "@cubrid/client";
const db = createClient({ host: "localhost", port: 33000, database: "testdb", user: "dba" });
```

**Java (JDBC)**:
```java
Connection conn = DriverManager.getConnection("jdbc:cubrid:localhost:33000:testdb:dba::");
```

## Related Projects

- [pycubrid](https://github.com/cubrid-labs/pycubrid) — Pure Python DB-API 2.0 driver for CUBRID
- [sqlalchemy-cubrid](https://github.com/cubrid-labs/sqlalchemy-cubrid) — SQLAlchemy 2.0 dialect for CUBRID
- [@cubrid/client](https://github.com/cubrid-labs/cubrid-client) — Modern TypeScript-first Node.js client for CUBRID
- [CUBRID JDBC](https://www.cubrid.org/manual/en/11.2/api/jdbc.html) — Official JDBC 4.0 driver for CUBRID
- [CUBRID](https://www.cubrid.org/) — The CUBRID database

## Contributing

Found a bug or want to add an example? PRs welcome! Each example should be self-contained and independently runnable.

## License

[Apache License 2.0](LICENSE)
