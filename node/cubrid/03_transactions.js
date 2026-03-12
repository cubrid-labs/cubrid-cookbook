// 03_transactions.js — Transaction management with @cubrid/client.
//
// Demonstrates:
// - Automatic commit on success with db.transaction()
// - Automatic rollback on error with db.transaction()
// - Multiple statements within a single transaction

import { createClient } from "@cubrid/client";

const DB_CONFIG = {
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
  password: "",
};

async function setup(db) {
  await db.query("DROP TABLE IF EXISTS cookbook_accounts");
  await db.query(`
    CREATE TABLE cookbook_accounts (
      id      INT AUTO_INCREMENT PRIMARY KEY,
      name    VARCHAR(100) NOT NULL,
      balance DOUBLE DEFAULT 0.0
    )
  `);
  await db.query(
    "INSERT INTO cookbook_accounts (name, balance) VALUES (?, ?)",
    ["Alice", 1000.0],
  );
  await db.query(
    "INSERT INTO cookbook_accounts (name, balance) VALUES (?, ?)",
    ["Bob", 500.0],
  );
}

async function showBalances(db, label = "") {
  const rows = await db.query(
    "SELECT name, balance FROM cookbook_accounts ORDER BY id",
  );
  const tag = label ? ` (${label})` : "";
  const balances = rows
    .map((r) => `${r.name}=$${Number(r.balance).toFixed(2)}`)
    .join(", ");
  console.log(`  Balances${tag}: ${balances}`);
}

async function commitExample(db) {
  console.log("\n=== Commit Example ===");
  await showBalances(db, "before");

  const amount = 200.0;

  // transaction() auto-commits on success, auto-rolls back on error
  await db.transaction(async (tx) => {
    await tx.query(
      "UPDATE cookbook_accounts SET balance = balance - ? WHERE name = ?",
      [amount, "Alice"],
    );
    await tx.query(
      "UPDATE cookbook_accounts SET balance = balance + ? WHERE name = ?",
      [amount, "Bob"],
    );
  });

  console.log(`  ✓ Transferred $${amount.toFixed(2)} from Alice to Bob`);
  await showBalances(db, "after commit");
}

async function rollbackExample(db) {
  console.log("\n=== Rollback Example ===");
  await showBalances(db, "before");

  try {
    await db.transaction(async (tx) => {
      await tx.query(
        "UPDATE cookbook_accounts SET balance = 0 WHERE name = 'Alice'",
      );
      console.log("  Made Alice's balance = 0 (within transaction)");

      // Throwing inside the callback triggers automatic rollback
      throw new Error("Something went wrong — rolling back!");
    });
  } catch (_err) {
    console.log("  ✓ Transaction rolled back automatically on error");
  }

  await showBalances(db, "after rollback");
}

async function multiStatementTransaction(db) {
  console.log("\n=== Multi-Statement Transaction ===");
  await showBalances(db, "before");

  // All three updates commit together or not at all
  await db.transaction(async (tx) => {
    await tx.query(
      "UPDATE cookbook_accounts SET balance = balance + 100 WHERE name = 'Alice'",
    );
    await tx.query(
      "UPDATE cookbook_accounts SET balance = balance + 50 WHERE name = 'Bob'",
    );
    console.log("  Applying bonuses: Alice +$100, Bob +$50");
  });

  await showBalances(db, "after bonuses");
}

async function cleanup(db) {
  await db.query("DROP TABLE IF EXISTS cookbook_accounts");
  console.log("\n✓ Cleaned up");
}

async function main() {
  const db = createClient(DB_CONFIG);
  try {
    await setup(db);
    await commitExample(db);
    await rollbackExample(db);
    await multiStatementTransaction(db);
  } finally {
    await cleanup(db);
    await db.close();
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
