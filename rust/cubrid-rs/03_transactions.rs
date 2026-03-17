use cubrid_tokio::Client;

const DSN: &str = "cubrid://dba:@localhost:33000/testdb";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = Client::connect(DSN).await?;

    client
        .execute("DROP TABLE IF EXISTS cookbook_rust_accounts", &[])
        .await?;
    client
        .execute(
            "CREATE TABLE cookbook_rust_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                balance DOUBLE DEFAULT 0.0
            )",
            &[],
        )
        .await?;

    client
        .execute(
            "INSERT INTO cookbook_rust_accounts (name, balance) VALUES ('Alice', 1000.0)",
            &[],
        )
        .await?;
    client
        .execute(
            "INSERT INTO cookbook_rust_accounts (name, balance) VALUES ('Bob', 500.0)",
            &[],
        )
        .await?;

    println!("=== Commit Example ===");
    client.execute("BEGIN WORK", &[]).await?;
    client
        .execute(
            "UPDATE cookbook_rust_accounts SET balance = balance - 200.0 WHERE name = 'Alice'",
            &[],
        )
        .await?;
    client
        .execute(
            "UPDATE cookbook_rust_accounts SET balance = balance + 200.0 WHERE name = 'Bob'",
            &[],
        )
        .await?;
    client.commit().await?;

    let after_commit = client
        .query(
            "SELECT name, balance FROM cookbook_rust_accounts ORDER BY id",
            &[],
        )
        .await?;
    println!("{after_commit:#?}");

    println!("\n=== Rollback Example ===");
    client.execute("BEGIN WORK", &[]).await?;
    client
        .execute(
            "UPDATE cookbook_rust_accounts SET balance = 0 WHERE name = 'Alice'",
            &[],
        )
        .await?;
    client.rollback().await?;

    let after_rollback = client
        .query(
            "SELECT name, balance FROM cookbook_rust_accounts ORDER BY id",
            &[],
        )
        .await?;
    println!("{after_rollback:#?}");

    client
        .execute("DROP TABLE IF EXISTS cookbook_rust_accounts", &[])
        .await?;

    Ok(())
}
