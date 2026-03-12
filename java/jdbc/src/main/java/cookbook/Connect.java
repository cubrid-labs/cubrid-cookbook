package cookbook;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;

/**
 * Connect.java — Connecting to CUBRID with JDBC.
 *
 * <p>Demonstrates:
 * <ul>
 *   <li>Basic connection with try-with-resources
 *   <li>Running a simple query
 *   <li>Connection metadata (version, database, user)
 *   <li>Inspecting ResultSetMetaData for column information
 * </ul>
 */
public class Connect {

    // CUBRID JDBC URL format: jdbc:cubrid:<host>:<port>:<db>:<user>:<password>:
    static final String URL = "jdbc:cubrid:localhost:33000:testdb:dba::";

    static {
        try {
            Class.forName("cubrid.jdbc.driver.CUBRIDDriver");
        } catch (ClassNotFoundException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    static void basicConnection() throws SQLException {
        System.out.println("=== Basic Connection ===");
        try (Connection conn = DriverManager.getConnection(URL);
                PreparedStatement stmt = conn.prepareStatement("SELECT 1 + 1 AS result");
                ResultSet rs = stmt.executeQuery()) {
            if (rs.next()) {
                System.out.printf("1 + 1 = %d%n", rs.getInt("result"));
            }
        }
    }

    static void connectionInfo() throws SQLException {
        System.out.println("\n=== Connection Info ===");
        try (Connection conn = DriverManager.getConnection(URL)) {
            // Server version
            try (PreparedStatement stmt = conn.prepareStatement("SELECT version() AS version");
                    ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) System.out.println("CUBRID version: " + rs.getString("version"));
            }

            // Current database
            try (PreparedStatement stmt = conn.prepareStatement("SELECT database() AS db");
                    ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) System.out.println("Database: " + rs.getString("db"));
            }

            // Current user
            try (PreparedStatement stmt = conn.prepareStatement("SELECT user() AS u");
                    ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) System.out.println("User: " + rs.getString("u"));
            }
        }
    }

    static void resultSetMetadata() throws SQLException {
        System.out.println("\n=== ResultSet Metadata ===");
        try (Connection conn = DriverManager.getConnection(URL);
                PreparedStatement stmt = conn.prepareStatement(
                        "SELECT 1 AS id, 'hello' AS name, CAST(3.14 AS DOUBLE) AS value");
                ResultSet rs = stmt.executeQuery()) {
            ResultSetMetaData meta = rs.getMetaData();
            int cols = meta.getColumnCount();
            System.out.println("Columns:");
            for (int i = 1; i <= cols; i++) {
                System.out.printf("  %-10s  type=%s%n",
                        meta.getColumnLabel(i),
                        meta.getColumnTypeName(i));
            }
            if (rs.next()) {
                System.out.printf("Row: (%d, %s, %.2f)%n",
                        rs.getInt("id"),
                        rs.getString("name"),
                        rs.getDouble("value"));
            }
        }
    }

    public static void main(String[] args) throws SQLException {
        basicConnection();
        connectionInfo();
        resultSetMetadata();
    }
}
