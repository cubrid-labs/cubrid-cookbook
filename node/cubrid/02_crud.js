// 02_crud.js — CRUD operations with @cubrid/client.
//
// Demonstrates:
// - CREATE TABLE
// - INSERT rows (single and batch)
// - SELECT with filtering
// - UPDATE rows
// - DELETE rows
// - DROP TABLE cleanup

import { createClient } from "@cubrid/client";

const DB_CONFIG = {
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
  password: "",
};

async function setupTable(db) {
  await db.query("DROP TABLE IF EXISTS cookbook_users");
  await db.query(`
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
  // Single insert with parameterized query
  await db.query(
    "INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)",
    ["Alice", "alice@example.com", 30],
  );

  // Multiple inserts
  const users = [
    ["Bob", "bob@example.com", 25],
    ["Charlie", "charlie@example.com", 35],
    ["Diana", "diana@example.com", 28],
    ["Eve", "eve@example.com", 32],
  ];
  for (const user of users) {
    await db.query(
      "INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)",
      user,
    );
  }
  console.log(`✓ Inserted ${1 + users.length} rows`);
}

async function selectAll(db) {
  const rows = await db.query(
    "SELECT id, name, email, age FROM cookbook_users ORDER BY id",
  );
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
  const byAge = await db.query(
    "SELECT name, age FROM cookbook_users WHERE age >= ? ORDER BY age DESC",
    [30],
  );
  console.log(`\nUsers age >= 30 (${byAge.length} rows):`);
  for (const row of byAge) {
    console.log(`  ${String(row.name).padEnd(12)}  age=${row.age}`);
  }

  // Filter by name pattern
  const byName = await db.query(
    "SELECT name, email FROM cookbook_users WHERE name LIKE ?",
    ["%li%"],
  );
  console.log(`\nUsers with 'li' in name (${byName.length} rows):`);
  for (const row of byName) {
    console.log(`  ${String(row.name).padEnd(12)}  ${row.email}`);
  }
}

async function updateRows(db) {
  // Update single row
  await db.query(
    "UPDATE cookbook_users SET age = ? WHERE name = ?",
    [31, "Alice"],
  );
  console.log("\n✓ Updated Alice's age to 31");

  // Update multiple rows
  await db.query(
    "UPDATE cookbook_users SET age = age + 1 WHERE age < ?",
    [30],
  );
  console.log("✓ Incremented age for users younger than 30");
}

async function deleteRows(db) {
  await db.query("DELETE FROM cookbook_users WHERE name = ?", ["Eve"]);
  console.log("\n✓ Deleted Eve");
}

async function cleanup(db) {
  await db.query("DROP TABLE IF EXISTS cookbook_users");
  console.log("\n✓ Cleaned up table 'cookbook_users'");
}

async function main() {
  const db = createClient(DB_CONFIG);
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
    await db.close();
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
