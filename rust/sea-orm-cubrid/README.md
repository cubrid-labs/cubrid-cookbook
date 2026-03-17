# SeaORM + CUBRID Examples

Practical CUBRID access from Rust using [SeaORM](https://www.sea-ql.org/SeaORM/) with the [sea-orm-cubrid](https://github.com/cubrid-labs/sea-orm-cubrid) backend.

## Features

- Async connection with `sea_orm_cubrid::connect()`
- SeaORM entity-based CRUD flow
- CUBRID DDL/DML with SeaORM query APIs
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
| `01_connect.rs` | Connecting to CUBRID | `sea_orm_cubrid::connect`, `query_one`, backend-aware statements |
| `02_crud.rs` | SeaORM CRUD | entity model, insert, find, update, delete |

## Run

```bash
cargo run --bin 01_connect
cargo run --bin 02_crud
```

## Connection DSN

```text
cubrid://dba:@localhost:33000/testdb
```

## Learn More

- [sea-orm-cubrid repository](https://github.com/cubrid-labs/sea-orm-cubrid)
- [SeaORM documentation](https://www.sea-ql.org/SeaORM/docs/)
- [CUBRID SQL Guide](https://www.cubrid.org/manual/en/11.2/sql/index.html)
