# Java JDBC Examples

Direct CUBRID access from Java using the [CUBRID JDBC Driver](https://www.cubrid.org/manual/en/11.2/api/jdbc.html) — the official JDBC 4.0 compliant driver for CUBRID.

## Features

- JDBC 4.0 compliant — standard `java.sql.*` API
- `PreparedStatement` for safe, parameterized queries
- Batch inserts via `addBatch()` / `executeBatch()`
- Transaction control — `commit()`, `rollback()`, `Savepoint`
- try-with-resources for automatic resource cleanup
- Java 17+ text blocks for clean multiline SQL

## Prerequisites

- Java 17+
- Maven 3.6+
- CUBRID running on `localhost:33000` with database `testdb`

The root project Docker Compose provides CUBRID. Start from the repository root:

```bash
make up
```

## Setup

```bash
mvn compile
```

## Examples

| File | Topic | Key Concepts |
|------|-------|--------------|
| `Connect.java` | Connecting to CUBRID | `DriverManager`, `ResultSet`, `ResultSetMetaData` |
| `Crud.java` | CRUD operations | `PreparedStatement`, batch inserts, parameterized queries |
| `Transactions.java` | Transaction control | `commit()`, `rollback()`, `Savepoint`, auto-commit |

## Run

```bash
# Connect example
mvn exec:java -Dexec.mainClass="cookbook.Connect"

# CRUD example
mvn exec:java -Dexec.mainClass="cookbook.Crud"

# Transactions example
mvn exec:java -Dexec.mainClass="cookbook.Transactions"
```

Each class is self-contained — it creates its own tables, runs examples, and cleans up.

## Code Highlights

### Connecting to CUBRID

```java
import java.sql.*;

// CUBRID JDBC URL: jdbc:cubrid:<host>:<port>:<db>:<user>:<password>:
String url = "jdbc:cubrid:localhost:33000:testdb:dba::";

Class.forName("cubrid.jdbc.driver.CUBRIDDriver");

try (Connection conn = DriverManager.getConnection(url);
     PreparedStatement stmt = conn.prepareStatement("SELECT 1 + 1 AS result");
     ResultSet rs = stmt.executeQuery()) {
    if (rs.next()) {
        System.out.println("1 + 1 = " + rs.getInt("result"));
    }
}
```

### CRUD with PreparedStatement

```java
// Single INSERT with parameterized query
try (PreparedStatement stmt = conn.prepareStatement(
        "INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)")) {
    stmt.setString(1, "Alice");
    stmt.setString(2, "alice@example.com");
    stmt.setInt(3, 30);
    stmt.executeUpdate();
}

// Batch INSERT
try (PreparedStatement stmt = conn.prepareStatement(
        "INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)")) {
    stmt.setString(1, "Bob");   stmt.setString(2, "bob@example.com");   stmt.setInt(3, 25); stmt.addBatch();
    stmt.setString(1, "Charlie"); stmt.setString(2, "charlie@example.com"); stmt.setInt(3, 35); stmt.addBatch();
    stmt.executeBatch();
}
conn.commit();
```

### Transactions with Savepoints

```java
conn.setAutoCommit(false);

// Make changes and create a savepoint
stmt.executeUpdate();
Savepoint sp = conn.setSavepoint("checkpoint");

// More changes...
stmt2.executeUpdate();

// Rollback only the second part
conn.rollback(sp);

// Commit everything up to the savepoint
conn.commit();
```

## Expected Output

Running `Connect.java`:

```
=== Basic Connection ===
1 + 1 = 2

=== Connection Info ===
CUBRID version: 11.2.0.0338
Database: testdb
User: DBA

=== ResultSet Metadata ===
Columns:
  id          type=INTEGER
  name        type=VARCHAR
  value       type=DOUBLE
Row: (1, hello, 3.14)
```

Running `Transactions.java`:

```
=== Commit Example ===
  Balances (before): Alice=$1000.00, Bob=$500.00
  ✓ Transferred $200.00 from Alice to Bob
  Balances (after commit): Alice=$800.00, Bob=$700.00

=== Rollback Example ===
  Balances (before): Alice=$800.00, Bob=$700.00
  Made Alice's balance = 0 (not committed)
  ✓ Rolled back — Alice's balance restored
  Balances (after rollback): Alice=$800.00, Bob=$700.00
```

## JDBC URL Format

| Component | Value |
|-----------|-------|
| Driver class | `cubrid.jdbc.driver.CUBRIDDriver` |
| URL pattern | `jdbc:cubrid:<host>:<port>:<db>:<user>:<password>:` |
| URL (this cookbook) | `jdbc:cubrid:localhost:33000:testdb:dba::` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `No suitable driver found` | Ensure `cubrid-jdbc` is in classpath: run `mvn compile` |
| `Connection refused` | Ensure CUBRID is running: `make up` from repo root |
| `Table already exists` | Tables use `DROP TABLE IF EXISTS` — re-run after cleanup |

## Learn More

- [CUBRID JDBC Documentation](https://www.cubrid.org/manual/en/11.2/api/jdbc.html)
- [JDBC Tutorial](https://docs.oracle.com/javase/tutorial/jdbc/)
- [CUBRID SQL Guide](https://www.cubrid.org/manual/en/11.2/sql/index.html)
