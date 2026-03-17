# cubrid-rs Examples

Direct CUBRID access from Rust using [cubrid-tokio](https://github.com/cubrid-labs/cubrid-rs), the async native Rust driver.

## Features

- Async connection workflow with `Client::connect()`
- Full CRUD flow with executable SQL examples
- Explicit transaction handling with commit and rollback
- Self-contained scripts that create tables, run demos, and clean up

## Prerequisites

- Rust 1.70+
- CUBRID running on `localhost:33000` with database `testdb`

The root project Docker Compose provides CUBRID. Start from the repository root:

```bash
make up
```

## Setup

```bash
cargo build
```

## Examples

| File | Topic | Key Concepts |
|------|-------|--------------|
| `01_connect.rs` | Connecting to CUBRID | `Client::connect`, async query, metadata query |
| `02_crud.rs` | CRUD operations | CREATE TABLE, INSERT/SELECT/UPDATE/DELETE |
| `03_transactions.rs` | Transaction control | `BEGIN WORK`, `commit()`, `rollback()` |

## Run

```bash
cargo run --bin 01_connect
cargo run --bin 02_crud
cargo run --bin 03_transactions
```

## Connection DSN

```text
cubrid://dba:@localhost:33000/testdb
```

## Learn More

- [cubrid-rs repository](https://github.com/cubrid-labs/cubrid-rs)
- [CUBRID SQL Guide](https://www.cubrid.org/manual/en/11.2/sql/index.html)
