// 02_crud.js — CRUD operations with Drizzle ORM + CUBRID.
//
// Demonstrates:
// - Schema definition with cubridTable
// - INSERT rows (single and batch)
// - SELECT with filtering (eq, gte, like)
// - UPDATE rows
// - DELETE rows
// - DROP TABLE cleanup

import { createClient } from "cubrid-client";
import { drizzle, cubridTable, int, varchar, sql, eq, gte } from "drizzle-cubrid";

// --- Schema ---
const cookbookUsers = cubridTable("cookbook_users", {
  id: int("id").primaryKey().autoincrement(),
  name: varchar("name", { length: 100 }).notNull(),
  email: varchar("email", { length: 200 }),
  age: int("age").default(0),
});

const DB_CONFIG = {
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
  password: "",
};

async function setupTable(db) {
  await db.execute(sql`DROP TABLE IF EXISTS cookbook_users`);
  await db.execute(sql`
    CREATE TABLE cookbook_users (
      id    INT AUTO_INCREMENT PRIMARY KEY,
      name  VARCHAR(100) NOT NULL,
      email VARCHAR(200) UNIQUE,
      age   INT DEFAULT 0
    )
  `);
  console.log("✓ Created table 'cookbook_users'");
}

async function insertRows(db) {
  // Single insert
  await db.insert(cookbookUsers).values({
    name: "Alice",
    email: "alice@example.com",
    age: 30,
  });

  // Batch insert
  const users = [
    { name: "Bob", email: "bob@example.com", age: 25 },
    { name: "Charlie", email: "charlie@example.com", age: 35 },
    { name: "Diana", email: "diana@example.com", age: 28 },
    { name: "Eve", email: "eve@example.com", age: 32 },
  ];
  for (const user of users) {
    await db.insert(cookbookUsers).values(user);
  }
  console.log(`✓ Inserted ${1 + users.length} rows`);
}

async function selectAll(db) {
  const rows = await db.select().from(cookbookUsers).orderBy(cookbookUsers.id);
  console.log(`\nAll users (${rows.length} rows):`);
  console.log(
    `  ${"ID".padStart(3)}  ${"Name".padEnd(12)}  ${"Email".padEnd(25)}  ${"Age".padStart(3)}`,
  );
  console.log(
    `  ${"---".padStart(3)}  ${"----".padEnd(12)}  ${"-----".padEnd(25)}  ${"---".padStart(3)}`,
  );
  for (const row of rows) {
    console.log(
      `  ${String(row.id).padStart(3)}  ${String(row.name).padEnd(12)}  ${String(row.email).padEnd(25)}  ${String(row.age).padStart(3)}`,
    );
  }
}

async function selectFiltered(db) {
  // Filter by age
  const byAge = await db
    .select({ name: cookbookUsers.name, age: cookbookUsers.age })
    .from(cookbookUsers)
    .where(gte(cookbookUsers.age, 30))
    .orderBy(cookbookUsers.age);
  console.log(`\nUsers age >= 30 (${byAge.length} rows):`);
  for (const row of byAge) {
    console.log(`  ${String(row.name).padEnd(12)}  age=${row.age}`);
  }

  // Filter by name pattern
  const byName = await db
    .select({ name: cookbookUsers.name, email: cookbookUsers.email })
    .from(cookbookUsers)
    .where(sql`${cookbookUsers.name} LIKE ${"%" + "li" + "%"}`);
  console.log(`\nUsers with 'li' in name (${byName.length} rows):`);
  for (const row of byName) {
    console.log(`  ${String(row.name).padEnd(12)}  ${row.email}`);
  }
}

async function updateRows(db) {
  // Update single row
  await db
    .update(cookbookUsers)
    .set({ age: 31 })
    .where(eq(cookbookUsers.name, "Alice"));
  console.log("\n✓ Updated Alice's age to 31");

  // Update multiple rows
  await db.execute(
    sql`UPDATE cookbook_users SET age = age + 1 WHERE age < 30`,
  );
  console.log("✓ Incremented age for users younger than 30");
}

async function deleteRows(db) {
  await db.delete(cookbookUsers).where(eq(cookbookUsers.name, "Eve"));
  console.log("\n✓ Deleted Eve");
}

async function cleanup(db) {
  await db.execute(sql`DROP TABLE IF EXISTS cookbook_users`);
  console.log("\n✓ Cleaned up table 'cookbook_users'");
}

async function main() {
  const client = createClient(DB_CONFIG);
  const db = drizzle(client);
  try {
    await setupTable(db);
    await insertRows(db);
    await selectAll(db);
    await selectFiltered(db);
    await updateRows(db);
    await selectAll(db); // Show updated state
    await deleteRows(db);
    await selectAll(db); // Show final state
  } finally {
    await cleanup(db);
    await client.close();
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
