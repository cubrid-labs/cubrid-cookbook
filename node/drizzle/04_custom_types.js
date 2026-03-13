// 04_custom_types.js — CUBRID-specific types with Drizzle ORM.
//
// Demonstrates:
// - SET, MULTISET, SEQUENCE collection types
// - MONETARY type
// - Schema definition with custom types
// - Insert and query with collection data

import { createClient } from "cubrid-client";
import { drizzle, cubridTable, int, varchar, sql } from "drizzle-cubrid";
import { set, multiset, sequence, monetary } from "drizzle-cubrid";

// --- Schema ---
const cookbookProducts = cubridTable("cookbook_products", {
  id: int("id").primaryKey().autoincrement(),
  name: varchar("name", { length: 100 }).notNull(),
  tags: set("tags", { type: "VARCHAR", length: 50 }),
  categories: multiset("categories", { type: "VARCHAR", length: 50 }),
  rankings: sequence("rankings", { type: "INTEGER" }),
  price: monetary("price"),
});

const DB_CONFIG = {
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
  password: "",
};

async function setup(db) {
  await db.execute(sql`DROP TABLE IF EXISTS cookbook_products`);
  await db.execute(sql`
    CREATE TABLE cookbook_products (
      id         INT AUTO_INCREMENT PRIMARY KEY,
      name       VARCHAR(100) NOT NULL,
      tags       SET(VARCHAR(50)),
      categories MULTISET(VARCHAR(50)),
      rankings   SEQUENCE(INTEGER),
      price      MONETARY
    )
  `);
  console.log("✓ Created table 'cookbook_products'");
}

async function insertProducts(db) {
  // Insert using raw SQL (collection literals use CUBRID syntax)
  await db.execute(sql`
    INSERT INTO cookbook_products (name, tags, categories, rankings, price)
    VALUES ('Laptop', {'electronics','portable','computing'}, {'tech','office','tech'}, {1,3,5}, 999.99)
  `);

  await db.execute(sql`
    INSERT INTO cookbook_products (name, tags, categories, rankings, price)
    VALUES ('Headphones', {'electronics','audio'}, {'tech','music','tech'}, {2,4}, 149.99)
  `);

  await db.execute(sql`
    INSERT INTO cookbook_products (name, tags, categories, rankings, price)
    VALUES ('Notebook', {'stationery','office'}, {'office','school'}, {10,20,30}, 12.50)
  `);

  console.log("✓ Inserted 3 products");
}

async function queryProducts(db) {
  console.log("\n=== All Products ===");
  const rows = await db
    .select()
    .from(cookbookProducts)
    .orderBy(cookbookProducts.id);

  for (const row of rows) {
    console.log(`\n  ${row.name} (id=${row.id})`);
    console.log(`    Tags:       ${row.tags}`);
    console.log(`    Categories: ${row.categories}`);
    console.log(`    Rankings:   ${row.rankings}`);
    console.log(`    Price:      $${row.price}`);
  }
}

async function queryWithFilter(db) {
  console.log("\n\n=== Filter: Products with 'electronics' tag ===");
  const rows = await db.execute(
    sql`SELECT name, tags, price FROM cookbook_products WHERE 'electronics' IN tags`,
  );

  for (const row of rows) {
    console.log(`  ${row.name} — $${row.price}`);
  }
}

async function cleanup(db) {
  await db.execute(sql`DROP TABLE IF EXISTS cookbook_products`);
  console.log("\n✓ Cleaned up table 'cookbook_products'");
}

async function main() {
  const client = createClient(DB_CONFIG);
  const db = drizzle(client);
  try {
    await setup(db);
    await insertProducts(db);
    await queryProducts(db);
    await queryWithFilter(db);
  } finally {
    await cleanup(db);
    await client.close();
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
