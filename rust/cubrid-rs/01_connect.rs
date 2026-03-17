use cubrid_tokio::Client;

const DSN: &str = "cubrid://dba:@localhost:33000/testdb";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = Client::connect(DSN).await?;

    println!("=== Basic Connection ===");
    let ping = client.query("SELECT 1 + 1 AS result", &[]).await?;
    println!("{ping:#?}");

    println!("\n=== Connection Info ===");
    let info = client
        .query(
            "SELECT version() AS version, database() AS db, user() AS user_name",
            &[],
        )
        .await?;
    println!("{info:#?}");

    Ok(())
}
