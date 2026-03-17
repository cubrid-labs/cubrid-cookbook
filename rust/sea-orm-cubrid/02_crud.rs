use sea_orm::entity::prelude::*;
use sea_orm::{ActiveModelTrait, ColumnTrait, ConnectionTrait, EntityTrait, QueryFilter, QueryOrder, Set, Statement};

const DSN: &str = "cubrid://dba:@localhost:33000/testdb";

mod user {
    use sea_orm::entity::prelude::*;

    #[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
    #[sea_orm(table_name = "cookbook_seaorm_users")]
    pub struct Model {
        #[sea_orm(primary_key)]
        pub id: i32,
        pub name: String,
        pub email: String,
        pub age: i32,
    }

    #[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
    pub enum Relation {}

    impl ActiveModelBehavior for ActiveModel {}
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let db = sea_orm_cubrid::connect(DSN).await?;
    let backend = db.get_database_backend();

    db.execute(Statement::from_string(
        backend,
        "DROP TABLE IF EXISTS cookbook_seaorm_users".to_owned(),
    ))
    .await?;
    db.execute(Statement::from_string(
        backend,
        "CREATE TABLE cookbook_seaorm_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(200) UNIQUE,
            age INT DEFAULT 0
        )"
        .to_owned(),
    ))
    .await?;

    let alice = user::ActiveModel {
        name: Set("Alice".to_owned()),
        email: Set("alice@example.com".to_owned()),
        age: Set(30),
        ..Default::default()
    };
    let bob = user::ActiveModel {
        name: Set("Bob".to_owned()),
        email: Set("bob@example.com".to_owned()),
        age: Set(25),
        ..Default::default()
    };

    alice.insert(&db).await?;
    bob.insert(&db).await?;

    println!("=== Rows After Insert ===");
    let users = user::Entity::find()
        .order_by_asc(user::Column::Id)
        .all(&db)
        .await?;
    println!("{users:#?}");

    if let Some(model) = user::Entity::find()
        .filter(user::Column::Name.eq("Alice"))
        .one(&db)
        .await?
    {
        let mut active: user::ActiveModel = model.into();
        active.age = Set(31);
        active.update(&db).await?;
    }

    println!("\n=== Rows After Update ===");
    let updated = user::Entity::find()
        .order_by_asc(user::Column::Id)
        .all(&db)
        .await?;
    println!("{updated:#?}");

    user::Entity::delete_many()
        .filter(user::Column::Name.eq("Bob"))
        .exec(&db)
        .await?;

    println!("\n=== Rows After Delete ===");
    let deleted = user::Entity::find()
        .order_by_asc(user::Column::Id)
        .all(&db)
        .await?;
    println!("{deleted:#?}");

    db.execute(Statement::from_string(
        backend,
        "DROP TABLE IF EXISTS cookbook_seaorm_users".to_owned(),
    ))
    .await?;

    Ok(())
}
