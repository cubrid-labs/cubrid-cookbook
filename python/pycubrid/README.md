# pycubrid Examples

Direct database access using the [pycubrid](https://github.com/cubrid-labs/pycubrid) DB-API 2.0 driver.

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
| `01_connect.py` | Connecting to CUBRID, basic queries |
| `02_crud.py` | Create, read, update, delete operations |
| `03_transactions.py` | Commit, rollback, autocommit, savepoints |
| `04_prepared.py` | Parameterized queries, batch operations |
| `05_error_handling.py` | Exception hierarchy, error recovery |
| `06_lob.py` | Large objects (BLOB/CLOB) |

## Run

```bash
python 01_connect.py
python 02_crud.py
# ... etc
```

Each script is self-contained — it creates its own tables, runs examples, and cleans up.
