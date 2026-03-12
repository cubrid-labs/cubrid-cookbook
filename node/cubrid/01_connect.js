// 01_connect.js — Connecting to CUBRID with @cubrid/client.
//
// Demonstrates:
// - Basic connection
// - Running a simple query
// - Connection metadata (version, database, user)
// - Reusing a client for multiple queries

import { createClient } from "@cubrid/client";

const DB_CONFIG = {
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
  password: "",
};

async function basicConnection() {
  console.log("=== Basic Connection ===");
  const db = createClient(DB_CONFIG);
  try {
    const rows = await db.query("SELECT 1 + 1 AS result");
    console.log(`1 + 1 = ${rows[0].result}`);
  } finally {
    await db.close();
  }
}

async function connectionInfo() {
  console.log("\n=== Connection Info ===");
  const db = createClient(DB_CONFIG);
  try {
    // Server version
    const [vrow] = await db.query("SELECT version() AS version");
    console.log(`CUBRID version: ${vrow.version}`);

    // Current database
    const [drow] = await db.query("SELECT database() AS db");
    console.log(`Database: ${drow.db}`);

    // Current user
    const [urow] = await db.query("SELECT user() AS u");
    console.log(`User: ${urow.u}`);
  } finally {
    await db.close();
  }
}

async function multipleQueries() {
  console.log("\n=== Multiple Queries ===");
  const db = createClient(DB_CONFIG);
  try {
    const queries = [
      "SELECT 1 AS a",
      "SELECT 'hello' AS b",
      "SELECT CURRENT_DATE AS today",
    ];
    for (const sql of queries) {
      const [row] = await db.query(sql);
      const value = Object.values(row)[0];
      console.log(`${sql.padEnd(35)} → ${value}`);
    }
  } finally {
    await db.close();
  }
}

async function main() {
  await basicConnection();
  await connectionInfo();
  await multipleQueries();
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
