use cubrid_tokio::Client;

const DSN: &str = "cubrid://dba:@localhost:33000/testdb";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = Client::connect(DSN).await?;

    client.execute("DROP TABLE IF EXISTS cookbook_rust_users", &[]).await?;
    client
        .execute(
            "CREATE TABLE cookbook_rust_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(200) UNIQUE,
                age INT DEFAULT 0
            )",
            &[],
        )
        .await?;

    client
        .execute(
            "INSERT INTO cookbook_rust_users (name, email, age) VALUES ('Alice', 'alice@example.com', 30)",
            &[],
        )
        .await?;
    client
        .execute(
            "INSERT INTO cookbook_rust_users (name, email, age) VALUES ('Bob', 'bob@example.com', 25)",
            &[],
        )
        .await?;
    client
        .execute(
            "INSERT INTO cookbook_rust_users (name, email, age) VALUES ('Charlie', 'charlie@example.com', 35)",
            &[],
        )
        .await?;

    println!("=== Rows After Insert ===");
    let rows = client
        .query(
            "SELECT id, name, email, age FROM cookbook_rust_users ORDER BY id",
            &[],
        )
        .await?;
    println!("{rows:#?}");

    client
        .execute(
            "UPDATE cookbook_rust_users SET age = 31 WHERE name = 'Alice'",
            &[],
        )
        .await?;

    println!("\n=== Rows After Update ===");
    let updated = client
        .query(
            "SELECT id, name, email, age FROM cookbook_rust_users ORDER BY id",
            &[],
        )
        .await?;
    println!("{updated:#?}");

    client
        .execute("DELETE FROM cookbook_rust_users WHERE name = 'Bob'", &[])
        .await?;

    println!("\n=== Rows After Delete ===");
    let deleted = client
        .query(
            "SELECT id, name, email, age FROM cookbook_rust_users ORDER BY id",
            &[],
        )
        .await?;
    println!("{deleted:#?}");

    client.execute("DROP TABLE IF EXISTS cookbook_rust_users", &[]).await?;

    Ok(())
}
