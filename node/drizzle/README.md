# Drizzle ORM Examples

Type-safe CUBRID access from Node.js using [drizzle-cubrid](https://github.com/cubrid-labs/drizzle-cubrid) — the Drizzle ORM dialect for CUBRID, built on top of [cubrid-client](https://github.com/cubrid-labs/cubrid-client).

## Features

- Type-safe schema definitions with `cubridTable`, `int`, `varchar`, and more
- Drizzle query builder — `select()`, `insert()`, `update()`, `delete()` with full type inference
- Transaction support — automatic commit on success, rollback on error
- CUBRID-specific types — `SET`, `MULTISET`, `SEQUENCE`, `MONETARY`
- Raw SQL via `sql` template tag when you need full control
- ESM module — modern `import` syntax

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
| `01_connect.js` | Connecting to CUBRID | `drizzle()`, `sql` template tag, connection metadata |
| `02_crud.js` | CRUD operations | Schema definition, `insert()`, `select()`, `update()`, `delete()`, filtering |
| `03_transactions.js` | Transaction control | `db.transaction()`, automatic commit/rollback on error |
| `04_custom_types.js` | CUBRID-specific types | `SET`, `MULTISET`, `SEQUENCE`, `MONETARY`, collection queries |

## Run

```bash
node 01_connect.js
node 02_crud.js
node 03_transactions.js
node 04_custom_types.js
```

Each script is self-contained — it creates its own tables, runs examples, and cleans up.

## Code Highlights

### Connecting with Drizzle

```js
import { createClient } from "cubrid-client";
import { drizzle } from "drizzle-cubrid";
import { sql } from "drizzle-orm";

const client = createClient({
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
  password: "",
});
const db = drizzle(client);

const rows = await db.execute(sql`SELECT 1 + 1 AS result`);
console.log(rows[0].result); // 2
await client.close();
```

### Schema Definition + CRUD

```js
import { drizzle, cubridTable, int, varchar, sql, eq, gte } from "drizzle-cubrid";

const cookbookUsers = cubridTable("cookbook_users", {
  id: int("id").primaryKey().autoincrement(),
  name: varchar("name", { length: 100 }).notNull(),
  email: varchar("email", { length: 200 }),
  age: int("age").default(0),
});

// INSERT
await db.insert(cookbookUsers).values({ name: "Alice", email: "alice@example.com", age: 30 });

// SELECT with filtering
const rows = await db
  .select({ name: cookbookUsers.name, age: cookbookUsers.age })
  .from(cookbookUsers)
  .where(gte(cookbookUsers.age, 30));
for (const row of rows) {
  console.log(`${row.name}: age ${row.age}`);
}

// UPDATE
await db.update(cookbookUsers).set({ age: 31 }).where(eq(cookbookUsers.name, "Alice"));

// DELETE
await db.delete(cookbookUsers).where(eq(cookbookUsers.name, "Alice"));
```

### Transactions

```js
// Automatic commit on success, rollback on error
await db.transaction(async (tx) => {
  await tx
    .update(cookbookAccounts)
    .set({ balance: sql`balance - ${200}` })
    .where(eq(cookbookAccounts.name, "Alice"));
  await tx
    .update(cookbookAccounts)
    .set({ balance: sql`balance + ${200}` })
    .where(eq(cookbookAccounts.name, "Bob"));
});
```

### CUBRID Collection Types

```js
import { set, multiset, sequence, monetary } from "drizzle-cubrid";

const cookbookProducts = cubridTable("cookbook_products", {
  id: int("id").primaryKey().autoincrement(),
  name: varchar("name", { length: 100 }).notNull(),
  tags: set("tags", { type: "VARCHAR", length: 50 }),
  categories: multiset("categories", { type: "VARCHAR", length: 50 }),
  rankings: sequence("rankings", { type: "INTEGER" }),
  price: monetary("price"),
});

// Query with collection filter
const rows = await db.execute(
  sql`SELECT name, tags, price FROM cookbook_products WHERE 'electronics' IN tags`,
);
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

=== Multi-Statement Transaction ===
  Balances (before): Alice=$800.00, Bob=$700.00
  Applying bonuses: Alice +$100, Bob +$50
  Balances (after bonuses): Alice=$900.00, Bob=$750.00
```

## API Quick Reference

| Method | Description |
|--------|-------------|
| `drizzle(client)` | Create a Drizzle instance from a `cubrid-client` client |
| `cubridTable(name, columns)` | Define a typed table schema |
| `db.select().from(table)` | Type-safe SELECT with column inference |
| `db.insert(table).values(data)` | INSERT one or more rows |
| `db.update(table).set(data)` | UPDATE rows (chain `.where()` to filter) |
| `db.delete(table)` | DELETE rows (chain `.where()` to filter) |
| `db.execute(sql`...`)` | Execute raw SQL via template tag |
| `db.transaction(callback)` | Run queries in a transaction; auto-commit/rollback |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ConnectionError: Failed to connect` | Ensure CUBRID is running: `make up` from repo root |
| `Cannot find package 'drizzle-cubrid'` | Run `npm install` in this directory |
| `Cannot find package 'cubrid-client'` | Run `npm install` in this directory |
| `SyntaxError: Cannot use import statement` | Requires Node.js 18+ with `"type": "module"` in `package.json` |

## Learn More

- [drizzle-cubrid documentation](https://github.com/cubrid-labs/drizzle-cubrid)
- [cubrid-client documentation](https://github.com/cubrid-labs/cubrid-client)
- [Drizzle ORM documentation](https://orm.drizzle.team/)
- [CUBRID SQL Guide](https://www.cubrid.org/manual/en/11.2/sql/index.html)
