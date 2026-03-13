// 01_connect.js — Connecting to CUBRID with Drizzle ORM.
//
// Demonstrates:
// - Creating a drizzle instance with cubrid-client
// - Running raw SQL with sql template tag
// - Connection metadata (version, database, user)

import { createClient } from "cubrid-client";
import { drizzle } from "drizzle-cubrid";
import { sql } from "drizzle-orm";

const DB_CONFIG = {
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
  password: "",
};

async function basicConnection() {
  console.log("=== Basic Connection ===");
  const client = createClient(DB_CONFIG);
  const db = drizzle(client);

  const rows = await db.execute(sql`SELECT 1 + 1 AS result`);
  console.log(`1 + 1 = ${rows[0].result}`);

  await client.close();
}

async function connectionInfo() {
  console.log("\n=== Connection Info ===");
  const client = createClient(DB_CONFIG);
  const db = drizzle(client);

  const [vrow] = await db.execute(sql`SELECT version() AS version`);
  console.log(`CUBRID version: ${vrow.version}`);

  const [drow] = await db.execute(sql`SELECT database() AS db`);
  console.log(`Database: ${drow.db}`);

  const [urow] = await db.execute(sql`SELECT user() AS u`);
  console.log(`User: ${urow.u}`);

  await client.close();
}

async function multipleQueries() {
  console.log("\n=== Multiple Queries ===");
  const client = createClient(DB_CONFIG);
  const db = drizzle(client);

  const queries = [
    { label: "SELECT 1 AS a", query: sql`SELECT 1 AS a` },
    { label: "SELECT 'hello' AS b", query: sql`SELECT 'hello' AS b` },
    { label: "SELECT CURRENT_DATE AS today", query: sql`SELECT CURRENT_DATE AS today` },
  ];
  for (const { label, query } of queries) {
    const [row] = await db.execute(query);
    const value = Object.values(row)[0];
    console.log(`${label.padEnd(35)} → ${value}`);
  }

  await client.close();
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
