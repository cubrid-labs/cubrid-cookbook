use sea_orm::{ConnectionTrait, Statement};

const DSN: &str = "cubrid://dba:@localhost:33000/testdb";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let db = sea_orm_cubrid::connect(DSN).await?;
    let backend = db.get_database_backend();

    println!("=== Basic Connection ===");
    let result = db
        .query_one(Statement::from_string(
            backend,
            "SELECT 1 + 1 AS result".to_owned(),
        ))
        .await?;
    println!("{result:#?}");

    println!("\n=== Connection Info ===");
    let info = db
        .query_one(Statement::from_string(
            backend,
            "SELECT version() AS version, database() AS db, user() AS user_name".to_owned(),
        ))
        .await?;
    println!("{info:#?}");

    Ok(())
}
