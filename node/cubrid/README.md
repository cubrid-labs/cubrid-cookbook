# cubrid-client Examples

Direct CUBRID access from Node.js using the [cubrid-client](https://github.com/cubrid-labs/cubrid-client) package — a modern, TypeScript-first Promise-based client using the native CAS protocol.

## Features

- Modern `async`/`await` API — no callbacks
- Typed query results — row objects keyed by column name
- Built-in transaction support — automatic commit on success, rollback on error
- Structured error classes (`ConnectionError`, `QueryError`, `TransactionError`)
- ESM and CommonJS output — works with `import` or `require`

## Prerequisites

- Node.js 18+
- CUBRID running on `localhost:33000` with database `testdb`

The root project Docker Compose provides CUBRID. Start from the repository root:

```bash
make up
```

## Setup

```bash
npm install
```

## Examples

| File | Topic | Key Concepts |
|------|-------|--------------|
| `01_connect.js` | Connecting to CUBRID | `createClient()`, basic query, connection metadata |
| `02_crud.js` | CRUD operations | INSERT, SELECT, UPDATE, DELETE, parameterized queries |
| `03_transactions.js` | Transaction control | `transaction()`, automatic commit/rollback on error |

## Run

```bash
node 01_connect.js
node 02_crud.js
node 03_transactions.js
```

Each script is self-contained — it creates its own tables, runs examples, and cleans up.

## Code Highlights

### Connecting to CUBRID

```js
import { createClient } from "cubrid-client";

const db = createClient({
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
  password: "",
});

const rows = await db.query("SELECT 1 + 1 AS result");
console.log(rows[0].result); // 2
await db.close();
```

### CRUD with Parameterized Queries

```js
// INSERT — ? placeholders
await db.query(
  "INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)",
  ["Alice", "alice@example.com", 30],
);

// SELECT with filtering
const rows = await db.query(
  "SELECT name, age FROM cookbook_users WHERE age >= ?",
  [30],
);
for (const row of rows) {
  console.log(`${row.name}: age ${row.age}`);
}
```

### Transactions

```js
// Automatic commit on success, rollback on error
await db.transaction(async (tx) => {
  await tx.query(
    "UPDATE cookbook_accounts SET balance = balance - ? WHERE name = ?",
    [200, "Alice"],
  );
  await tx.query(
    "UPDATE cookbook_accounts SET balance = balance + ? WHERE name = ?",
    [200, "Bob"],
  );
});
```

## Expected Output

Running `01_connect.js`:

```
=== Basic Connection ===
1 + 1 = 2

=== Connection Info ===
CUBRID version: 11.2.0.0338
Database: testdb
User: DBA

=== Multiple Queries ===
SELECT 1 AS a                       → 1
SELECT 'hello' AS b                 → hello
SELECT CURRENT_DATE AS today        → 2025-01-15
```

Running `03_transactions.js`:

```
=== Commit Example ===
  Balances (before): Alice=$1000.00, Bob=$500.00
  ✓ Transferred $200.00 from Alice to Bob
  Balances (after commit): Alice=$800.00, Bob=$700.00

=== Rollback Example ===
  Balances (before): Alice=$800.00, Bob=$700.00
  Made Alice's balance = 0 (within transaction)
  ✓ Transaction rolled back automatically on error
  Balances (after rollback): Alice=$800.00, Bob=$700.00
```

## API Quick Reference

| Method | Description |
|--------|-------------|
| `createClient(options)` | Create a reusable database client |
| `db.query(sql, params?)` | Execute a query; returns an array of row objects |
| `db.transaction(callback)` | Run multiple queries in a transaction; auto-commit/rollback |
| `db.close()` | Close the shared connection |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ConnectionError: Failed to connect` | Ensure CUBRID is running: `make up` from repo root |
| `Cannot find package 'cubrid-client'` | Run `npm install` in this directory |
| `SyntaxError: Cannot use import statement` | Requires Node.js 18+ with `"type": "module"` in `package.json` |

## Learn More

- [cubrid-client documentation](https://github.com/cubrid-labs/cubrid-client)
- [CUBRID SQL Guide](https://www.cubrid.org/manual/en/11.2/sql/index.html)
