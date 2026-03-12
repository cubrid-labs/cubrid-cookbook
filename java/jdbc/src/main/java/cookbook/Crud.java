package cookbook;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Crud.java — CRUD operations with CUBRID JDBC.
 *
 * <p>Demonstrates:
 * <ul>
 *   <li>CREATE TABLE
 *   <li>INSERT rows — single and batch via addBatch/executeBatch
 *   <li>SELECT with WHERE filtering and LIKE pattern matching
 *   <li>UPDATE rows
 *   <li>DELETE rows
 *   <li>DROP TABLE cleanup
 * </ul>
 */
public class Crud {

    static final String URL = "jdbc:cubrid:localhost:33000:testdb:dba::";

    static {
        try {
            Class.forName("cubrid.jdbc.driver.CUBRIDDriver");
        } catch (ClassNotFoundException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    static void setupTable(Connection conn) throws SQLException {
        try (PreparedStatement stmt = conn.prepareStatement("DROP TABLE IF EXISTS cookbook_users")) {
            stmt.executeUpdate();
        }
        try (PreparedStatement stmt = conn.prepareStatement("""
                CREATE TABLE cookbook_users (
                    id    INT AUTO_INCREMENT PRIMARY KEY,
                    name  VARCHAR(100) NOT NULL,
                    email VARCHAR(200) UNIQUE,
                    age   INT DEFAULT 0
                )
                """)) {
            stmt.executeUpdate();
        }
        conn.commit();
        System.out.println("✓ Created table 'cookbook_users'");
    }

    static void insertRows(Connection conn) throws SQLException {
        // Single insert with parameterized query
        try (PreparedStatement stmt = conn.prepareStatement(
                "INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)")) {
            stmt.setString(1, "Alice");
            stmt.setString(2, "alice@example.com");
            stmt.setInt(3, 30);
            stmt.executeUpdate();
        }

        // Batch insert
        Object[][] users = {
            {"Bob",     "bob@example.com",     25},
            {"Charlie", "charlie@example.com", 35},
            {"Diana",   "diana@example.com",   28},
            {"Eve",     "eve@example.com",     32},
        };
        try (PreparedStatement stmt = conn.prepareStatement(
                "INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)")) {
            for (Object[] user : users) {
                stmt.setString(1, (String) user[0]);
                stmt.setString(2, (String) user[1]);
                stmt.setInt(3, (Integer) user[2]);
                stmt.addBatch();
            }
            stmt.executeBatch();
        }
        conn.commit();
        System.out.printf("✓ Inserted %d rows%n", 1 + users.length);
    }

    static void selectAll(Connection conn) throws SQLException {
        try (PreparedStatement stmt = conn.prepareStatement(
                "SELECT id, name, email, age FROM cookbook_users ORDER BY id");
                ResultSet rs = stmt.executeQuery()) {
            System.out.println("\nAll users:");
            System.out.printf("  %3s  %-12s  %-25s  %3s%n", "ID", "Name", "Email", "Age");
            System.out.printf("  %3s  %-12s  %-25s  %3s%n", "---", "----", "-----", "---");
            while (rs.next()) {
                System.out.printf("  %3d  %-12s  %-25s  %3d%n",
                        rs.getInt("id"),
                        rs.getString("name"),
                        rs.getString("email"),
                        rs.getInt("age"));
            }
        }
    }

    static void selectFiltered(Connection conn) throws SQLException {
        // Filter by age
        try (PreparedStatement stmt = conn.prepareStatement(
                "SELECT name, age FROM cookbook_users WHERE age >= ? ORDER BY age DESC")) {
            stmt.setInt(1, 30);
            try (ResultSet rs = stmt.executeQuery()) {
                System.out.println("\nUsers age >= 30:");
                while (rs.next()) {
                    System.out.printf("  %-12s  age=%d%n",
                            rs.getString("name"), rs.getInt("age"));
                }
            }
        }

        // Filter by name pattern
        try (PreparedStatement stmt = conn.prepareStatement(
                "SELECT name, email FROM cookbook_users WHERE name LIKE ?")) {
            stmt.setString(1, "%li%");
            try (ResultSet rs = stmt.executeQuery()) {
                System.out.println("\nUsers with 'li' in name:");
                while (rs.next()) {
                    System.out.printf("  %-12s  %s%n",
                            rs.getString("name"), rs.getString("email"));
                }
            }
        }
    }

    static void updateRows(Connection conn) throws SQLException {
        // Update single row
        try (PreparedStatement stmt = conn.prepareStatement(
                "UPDATE cookbook_users SET age = ? WHERE name = ?")) {
            stmt.setInt(1, 31);
            stmt.setString(2, "Alice");
            int affected = stmt.executeUpdate();
            System.out.printf("%n✓ Updated Alice's age (rows affected: %d)%n", affected);
        }

        // Update multiple rows
        try (PreparedStatement stmt = conn.prepareStatement(
                "UPDATE cookbook_users SET age = age + 1 WHERE age < ?")) {
            stmt.setInt(1, 30);
            int affected = stmt.executeUpdate();
            System.out.printf("✓ Incremented age for young users (rows affected: %d)%n", affected);
        }
        conn.commit();
    }

    static void deleteRows(Connection conn) throws SQLException {
        try (PreparedStatement stmt = conn.prepareStatement(
                "DELETE FROM cookbook_users WHERE name = ?")) {
            stmt.setString(1, "Eve");
            int affected = stmt.executeUpdate();
            System.out.printf("%n✓ Deleted Eve (rows affected: %d)%n", affected);
        }
        conn.commit();
    }

    static void cleanup(Connection conn) throws SQLException {
        try (PreparedStatement stmt = conn.prepareStatement(
                "DROP TABLE IF EXISTS cookbook_users")) {
            stmt.executeUpdate();
        }
        conn.commit();
        System.out.println("\n✓ Cleaned up table 'cookbook_users'");
    }

    public static void main(String[] args) throws SQLException {
        try (Connection conn = DriverManager.getConnection(URL)) {
            conn.setAutoCommit(false);
            try {
                setupTable(conn);
                insertRows(conn);
                selectAll(conn);
                selectFiltered(conn);
                updateRows(conn);
                selectAll(conn); // Show updated state
                deleteRows(conn);
                selectAll(conn); // Show final state
            } finally {
                cleanup(conn);
            }
        }
    }
}
