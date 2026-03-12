package cookbook;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Savepoint;

/**
 * Transactions.java — Transaction management with CUBRID JDBC.
 *
 * <p>Demonstrates:
 * <ul>
 *   <li>Manual commit/rollback with setAutoCommit(false)
 *   <li>Savepoints — SAVEPOINT and ROLLBACK TO SAVEPOINT
 *   <li>Auto-commit mode
 * </ul>
 */
public class Transactions {

    static final String URL = "jdbc:cubrid:localhost:33000:testdb:dba::";

    static {
        try {
            Class.forName("cubrid.jdbc.driver.CUBRIDDriver");
        } catch (ClassNotFoundException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    static void setup(Connection conn) throws SQLException {
        try (PreparedStatement stmt = conn.prepareStatement(
                "DROP TABLE IF EXISTS cookbook_accounts")) {
            stmt.executeUpdate();
        }
        try (PreparedStatement stmt = conn.prepareStatement("""
                CREATE TABLE cookbook_accounts (
                    id      INT AUTO_INCREMENT PRIMARY KEY,
                    name    VARCHAR(100) NOT NULL,
                    balance DOUBLE DEFAULT 0.0
                )
                """)) {
            stmt.executeUpdate();
        }
        try (PreparedStatement stmt = conn.prepareStatement(
                "INSERT INTO cookbook_accounts (name, balance) VALUES (?, ?)")) {
            stmt.setString(1, "Alice");
            stmt.setDouble(2, 1000.0);
            stmt.executeUpdate();
            stmt.setString(1, "Bob");
            stmt.setDouble(2, 500.0);
            stmt.executeUpdate();
        }
        conn.commit();
    }

    static void showBalances(Connection conn, String label) throws SQLException {
        try (PreparedStatement stmt = conn.prepareStatement(
                "SELECT name, balance FROM cookbook_accounts ORDER BY id");
                ResultSet rs = stmt.executeQuery()) {
            StringBuilder sb = new StringBuilder();
            while (rs.next()) {
                if (sb.length() > 0) sb.append(", ");
                sb.append(String.format("%s=$%.2f",
                        rs.getString("name"), rs.getDouble("balance")));
            }
            String tag = (label != null && !label.isEmpty()) ? " (" + label + ")" : "";
            System.out.println("  Balances" + tag + ": " + sb);
        }
    }

    static void commitExample(Connection conn) throws SQLException {
        System.out.println("\n=== Commit Example ===");
        showBalances(conn, "before");

        double amount = 200.0;

        try (PreparedStatement debit = conn.prepareStatement(
                "UPDATE cookbook_accounts SET balance = balance - ? WHERE name = ?");
                PreparedStatement credit = conn.prepareStatement(
                        "UPDATE cookbook_accounts SET balance = balance + ? WHERE name = ?")) {
            debit.setDouble(1, amount);
            debit.setString(2, "Alice");
            debit.executeUpdate();

            credit.setDouble(1, amount);
            credit.setString(2, "Bob");
            credit.executeUpdate();
        }

        conn.commit();
        System.out.printf("  ✓ Transferred $%.2f from Alice to Bob%n", amount);
        showBalances(conn, "after commit");
    }

    static void rollbackExample(Connection conn) throws SQLException {
        System.out.println("\n=== Rollback Example ===");
        showBalances(conn, "before");

        try (PreparedStatement stmt = conn.prepareStatement(
                "UPDATE cookbook_accounts SET balance = 0 WHERE name = 'Alice'")) {
            stmt.executeUpdate();
        }
        System.out.println("  Made Alice's balance = 0 (not committed)");

        conn.rollback();
        System.out.println("  ✓ Rolled back — Alice's balance restored");
        showBalances(conn, "after rollback");
    }

    static void savepointExample(Connection conn) throws SQLException {
        System.out.println("\n=== Savepoint Example ===");
        showBalances(conn, "before");

        // Step 1: Give Alice a bonus
        try (PreparedStatement stmt = conn.prepareStatement(
                "UPDATE cookbook_accounts SET balance = balance + 100 WHERE name = 'Alice'")) {
            stmt.executeUpdate();
        }
        System.out.println("  Step 1: Alice +$100");

        // Create savepoint after step 1
        Savepoint sp = conn.setSavepoint("after_alice_bonus");
        System.out.println("  ✓ Created savepoint 'after_alice_bonus'");

        // Step 2: Give Bob a large bonus (we'll undo this)
        try (PreparedStatement stmt = conn.prepareStatement(
                "UPDATE cookbook_accounts SET balance = balance + 999 WHERE name = 'Bob'")) {
            stmt.executeUpdate();
        }
        System.out.println("  Step 2: Bob +$999 (will be rolled back)");

        // Rollback to savepoint — undoes step 2 but keeps step 1
        conn.rollback(sp);
        System.out.println("  ✓ Rolled back to savepoint — Bob's $999 undone, Alice's $100 kept");

        conn.commit();
        showBalances(conn, "after savepoint rollback + commit");
    }

    static void autocommitExample() throws SQLException {
        System.out.println("\n=== Auto-Commit Example ===");
        try (Connection conn = DriverManager.getConnection(URL)) {
            // Auto-commit is on by default
            System.out.printf("  autoCommit = %b%n", conn.getAutoCommit());

            try (PreparedStatement stmt = conn.prepareStatement(
                    "UPDATE cookbook_accounts SET balance = balance + 50 WHERE name = 'Alice'")) {
                stmt.executeUpdate();
            }
            System.out.println("  ✓ Updated Alice +$50 (auto-committed immediately)");
            showBalances(conn, "autocommit");
        }
    }

    static void cleanup(Connection conn) throws SQLException {
        try (PreparedStatement stmt = conn.prepareStatement(
                "DROP TABLE IF EXISTS cookbook_accounts")) {
            stmt.executeUpdate();
        }
        conn.commit();
        System.out.println("\n✓ Cleaned up");
    }

    public static void main(String[] args) throws SQLException {
        try (Connection conn = DriverManager.getConnection(URL)) {
            conn.setAutoCommit(false);
            try {
                setup(conn);
                commitExample(conn);
                rollbackExample(conn);
                savepointExample(conn);
                autocommitExample();
            } finally {
                cleanup(conn);
            }
        }
    }
}
