// 04_custom_types.js — CUBRID-specific types with Drizzle ORM.
//
// Demonstrates:
// - SET, MULTISET, SEQUENCE collection types in DDL
// - Insert and query with collection data
// - Filtering with the IN operator on SET columns
// - Collection modification (add/remove elements)
//
// NOTE: cubrid-client does not fully decode collection-typed columns in SELECT
// results yet. This example inserts collection data using raw SQL literals
// and queries scalar columns while filtering on collections.

import { createClient } from "cubrid-client";
import { drizzle, sql } from "drizzle-cubrid";

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
      price      DOUBLE
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
  // Select scalar columns only (collection columns are not fully decoded by cubrid-client in SELECT results)
  const rows = await db.execute(
    sql`SELECT id, name, price FROM cookbook_products ORDER BY id`,
  );

  for (const row of rows) {
    console.log(`  ${row.name} (id=${row.id}) — $${Number(row.price).toFixed(2)}`);
  }
}

async function queryWithSetFilter(db) {
  console.log("\n=== Filter: Products with 'electronics' tag ===");
  const rows = await db.execute(
    sql`SELECT name, price FROM cookbook_products WHERE 'electronics' IN tags`,
  );

  for (const row of rows) {
    console.log(`  ${row.name} — $${Number(row.price).toFixed(2)}`);
  }
}

async function queryWithMultipleFilters(db) {
  console.log("\n=== Filter: Products with 'office' category ===");
  const rows = await db.execute(
    sql`SELECT name, price FROM cookbook_products WHERE 'office' IN categories`,
  );

  for (const row of rows) {
    console.log(`  ${row.name} — $${Number(row.price).toFixed(2)}`);
  }
}

async function modifyCollection(db) {
  console.log("\n=== Modify Collection ===");

  // Add element to SET
  await db.execute(
    sql`UPDATE cookbook_products SET tags = tags + {'discounted'} WHERE name = 'Laptop'`,
  );
  console.log("  ✓ Added 'discounted' tag to Laptop");

  // Remove element from SET
  await db.execute(
    sql`UPDATE cookbook_products SET tags = tags - {'portable'} WHERE name = 'Laptop'`,
  );
  console.log("  ✓ Removed 'portable' tag from Laptop");

  // Verify filter still works
  const rows = await db.execute(
    sql`SELECT name FROM cookbook_products WHERE 'discounted' IN tags`,
  );
  console.log(`  Products with 'discounted' tag: ${rows.map((r) => r.name).join(", ")}`);
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
    await queryWithSetFilter(db);
    await queryWithMultipleFilters(db);
    await modifyCollection(db);
  } finally {
    await cleanup(db);
    await client.close();
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
