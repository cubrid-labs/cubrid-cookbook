"""01_connection.py — Connection patterns: Java JDBC → Python pycubrid.

Demonstrates the equivalent of Java JDBC connection patterns in Python.

Java JDBC (what you're used to):
─────────────────────────────────
    // 1. Load driver
    Class.forName("cubrid.jdbc.driver.CUBRIDDriver");

    // 2. Get connection
    String url = "jdbc:cubrid:localhost:33000:testdb:::";
    Connection conn = DriverManager.getConnection(url, "dba", "");

    // 3. Use connection
    Statement stmt = conn.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT 1 + 1 AS result");
    rs.next();
    System.out.println("Result: " + rs.getInt("result"));

    // 4. Cleanup (in finally block!)
    rs.close();
    stmt.close();
    conn.close();

Python pycubrid (what you'll write instead):
─────────────────────────────────────────────
    See functions below — 75% less code, same protocol.
"""

from __future__ import annotations

import pycubrid

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Java:  jdbc:cubrid:localhost:33000:testdb:::
# Python: keyword arguments (no URL parsing needed)
DB_CONFIG = {
    "host": "localhost",
    "port": 33000,
    "database": "testdb",
    "user": "dba",
    "password": "",
}


# ---------------------------------------------------------------------------
# Pattern 1: Basic connection (replaces DriverManager.getConnection)
# ---------------------------------------------------------------------------
def basic_connection() -> None:
    """Connect, query, close.

    Java equivalent:
        Connection conn = DriverManager.getConnection(url, "dba", "");
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT 1 + 1 AS result");
        rs.next();
        System.out.println(rs.getInt(1));
        rs.close(); stmt.close(); conn.close();
    """
    conn = pycubrid.connect(**DB_CONFIG)

    cursor = conn.cursor()
    cursor.execute("SELECT 1 + 1 AS result")
    row = cursor.fetchone()
    print(f"1 + 1 = {row[0]}")

    cursor.close()
    conn.close()


# ---------------------------------------------------------------------------
# Pattern 2: Context manager (replaces try/finally)
# ---------------------------------------------------------------------------
def context_manager_connection() -> None:
    """Use connection as context manager — auto-closes on exit.

    Java equivalent:
        // Java 7+ try-with-resources
        try (Connection conn = DriverManager.getConnection(url, "dba", "")) {
            try (Statement stmt = conn.createStatement()) {
                ResultSet rs = stmt.executeQuery("SELECT version()");
                rs.next();
                System.out.println(rs.getString(1));
            }
        }
        // conn auto-closed

    Python advantage:
        No try-with-resources ceremony. Just `with`.
    """
    conn = pycubrid.connect(**DB_CONFIG)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"CUBRID version: {version[0]}")
        cursor.close()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Pattern 3: Connection metadata (replaces DatabaseMetaData)
# ---------------------------------------------------------------------------
def connection_metadata() -> None:
    """Inspect server info.

    Java equivalent:
        DatabaseMetaData meta = conn.getMetaData();
        System.out.println("DB: " + meta.getDatabaseProductName());
        System.out.println("Version: " + meta.getDatabaseProductVersion());
        System.out.println("User: " + meta.getUserName());
    """
    conn = pycubrid.connect(**DB_CONFIG)

    cursor = conn.cursor()

    cursor.execute("SELECT version()")
    print(f"Version:  {cursor.fetchone()[0]}")

    cursor.execute("SELECT database()")
    print(f"Database: {cursor.fetchone()[0]}")

    cursor.execute("SELECT user()")
    print(f"User:     {cursor.fetchone()[0]}")

    cursor.close()
    conn.close()


# ---------------------------------------------------------------------------
# Pattern 4: Auto-commit control
# ---------------------------------------------------------------------------
def autocommit_control() -> None:
    """Toggle auto-commit mode.

    Java equivalent:
        conn.setAutoCommit(true);   // Each statement commits immediately
        conn.setAutoCommit(false);  // Manual commit required

    Key difference:
        Java defaults to auto-commit ON.
        Python (DB-API 2.0) defaults to auto-commit OFF.
        Always be explicit to avoid surprises during migration.
    """
    conn = pycubrid.connect(**DB_CONFIG)

    # Check default (OFF in Python, unlike Java's ON)
    print(f"Default autocommit: {conn.autocommit}")  # False

    # Enable auto-commit (matches Java default behavior)
    conn.autocommit = True
    print(f"After enable:       {conn.autocommit}")  # True

    # Back to manual mode
    conn.autocommit = False
    print(f"After disable:      {conn.autocommit}")  # False

    conn.close()


# ---------------------------------------------------------------------------
# Pattern 5: Multiple connections (replaces connection pooling)
# ---------------------------------------------------------------------------
def multiple_connections() -> None:
    """Open multiple connections.

    Java equivalent:
        // Typically uses a DataSource / connection pool
        DataSource ds = new CUBRIDDataSource();
        Connection conn1 = ds.getConnection();
        Connection conn2 = ds.getConnection();

    Note:
        For production connection pooling in Python, see:
        ../../performance/connection-pooling/
    """
    conn1 = pycubrid.connect(**DB_CONFIG)
    conn2 = pycubrid.connect(**DB_CONFIG)

    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    cursor1.execute("SELECT 'conn1' AS src")
    cursor2.execute("SELECT 'conn2' AS src")

    print(f"Connection 1: {cursor1.fetchone()[0]}")
    print(f"Connection 2: {cursor2.fetchone()[0]}")

    cursor1.close()
    cursor2.close()
    conn1.close()
    conn2.close()


if __name__ == "__main__":
    print("=== Basic Connection ===")
    basic_connection()

    print("\n=== Context Manager ===")
    context_manager_connection()

    print("\n=== Connection Metadata ===")
    connection_metadata()

    print("\n=== Auto-commit Control ===")
    autocommit_control()

    print("\n=== Multiple Connections ===")
    multiple_connections()
