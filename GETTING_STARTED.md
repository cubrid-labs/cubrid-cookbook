# CUBRID in 5 Minutes — Getting Started Guide

> Pick your language. Connect to CUBRID. Build something. All in 5 minutes.

This guide gets you from zero to a working CUBRID application in your language of choice. No prior CUBRID experience needed.

## Prerequisites

```bash
# Start a CUBRID database with Docker (one command)
docker run -d --name cubrid -p 33000:33000 -e CUBRID_DB=testdb cubrid/cubrid:11.2
```

Wait ~10 seconds for startup, then choose your language below.

---

## 🐍 Python

### Option A: SQLAlchemy ORM (Recommended)

```bash
pip install sqlalchemy-cubrid[pycubrid]
```

```python
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)

engine = create_engine("cubrid+pycubrid://dba@localhost:33000/testdb")
Base.metadata.create_all(engine)

with Session(engine) as session:
    # Create
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()

    # Read
    users = session.query(User).all()
    for u in users:
        print(f"{u.name} ({u.email})")
```

### Option B: Direct Driver

```bash
pip install pycubrid
```

```python
import pycubrid

conn = pycubrid.connect(host="localhost", port=33000, database="testdb", user="dba")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DOUBLE
    )
""")

cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("Widget", 9.99))
conn.commit()

cursor.execute("SELECT * FROM products")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
```

**More**: [Full Python examples →](python/)

---

## 🟦 TypeScript / Node.js

### Option A: Drizzle ORM (Recommended)

```bash
npm install drizzle-cubrid drizzle-orm cubrid-client
```

```typescript
import { createClient } from "cubrid-client";
import { drizzle } from "drizzle-cubrid";
import { cubridTable, varchar, integer, serial } from "drizzle-cubrid/columns";

// Define schema
const users = cubridTable("users", {
  id: serial("id").primaryKey(),
  name: varchar("name", { length: 100 }).notNull(),
  email: varchar("email", { length: 200 }).unique(),
});

// Connect
const client = createClient({
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
});
const db = drizzle(client);

// Create table
await db.execute(sql`CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(200) UNIQUE
)`);

// Insert
await db.insert(users).values({ name: "Alice", email: "alice@example.com" });

// Query
const allUsers = await db.select().from(users);
console.log(allUsers);

await client.close();
```

### Option B: Direct Client

```bash
npm install cubrid-client
```

```typescript
import { createClient } from "cubrid-client";

const db = createClient({
  host: "localhost",
  port: 33000,
  database: "testdb",
  user: "dba",
});

type User = { id: number; name: string; email: string };

// Typed query results
const users = await db.query<User>("SELECT * FROM users WHERE name = ?", ["Alice"]);
console.log(users); // User[] with full type safety

// Transactions with auto-rollback
await db.transaction(async (tx) => {
  await tx.query("INSERT INTO orders (item) VALUES (?)", ["Widget"]);
  await tx.query("UPDATE inventory SET qty = qty - 1 WHERE item = ?", ["Widget"]);
});

await db.close();
```

**More**: [Full Node.js examples →](node/)

---

## 🐹 Go

### Option A: GORM (Recommended)

```bash
go get github.com/cubrid-labs/cubrid-go
```

```go
package main

import (
    "fmt"
    "log"

    "gorm.io/gorm"
    cubrid "github.com/cubrid-labs/cubrid-go/dialector"
)

type User struct {
    ID    int    `gorm:"primaryKey;autoIncrement"`
    Name  string `gorm:"size:100;not null"`
    Email string `gorm:"size:200;uniqueIndex"`
}

func main() {
    db, err := gorm.Open(cubrid.Open("cubrid://dba:@localhost:33000/testdb"), &gorm.Config{})
    if err != nil {
        log.Fatal(err)
    }

    // Auto-create table
    db.AutoMigrate(&User{})

    // Create
    db.Create(&User{Name: "Alice", Email: "alice@example.com"})

    // Read
    var users []User
    db.Find(&users)
    for _, u := range users {
        fmt.Printf("%s (%s)\n", u.Name, u.Email)
    }
}
```

### Option B: database/sql

```bash
go get github.com/cubrid-labs/cubrid-go
```

```go
package main

import (
    "database/sql"
    "fmt"
    "log"

    _ "github.com/cubrid-labs/cubrid-go"
)

func main() {
    db, err := sql.Open("cubrid", "cubrid://dba:@localhost:33000/testdb")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Verify connection
    if err := db.Ping(); err != nil {
        log.Fatal(err)
    }

    // Query with parameters
    rows, err := db.Query("SELECT name, email FROM users WHERE name = ?", "Alice")
    if err != nil {
        log.Fatal(err)
    }
    defer rows.Close()

    for rows.Next() {
        var name, email string
        rows.Scan(&name, &email)
        fmt.Printf("%s (%s)\n", name, email)
    }
}
```

**More**: [Full Go examples →](go/)

---

## What's Next?

| Want to... | Go here |
|---|---|
| Build a REST API | [FastAPI example](python/fastapi/) · [Flask example](python/flask/) |
| Use an ORM | [SQLAlchemy](python/sqlalchemy/) · [Drizzle](node/drizzle/) · [GORM](go/gorm/) |
| Analyze data | [Pandas example](python/pandas/) |
| Build a dashboard | [Streamlit example](python/streamlit/) |
| Run background tasks | [Celery example](python/celery/) |
| Use Django | [Django example](python/django/) |

## CUBRID vs. Other Databases

| Feature | CUBRID | MySQL | PostgreSQL |
|---|---|---|---|
| Open source | ✅ MIT-like | ✅ GPL | ✅ PostgreSQL |
| ACID transactions | ✅ | ✅ | ✅ |
| MVCC | ✅ | ✅ (InnoDB) | ✅ |
| Collection types (SET) | ✅ Native | ❌ | ✅ (ARRAY) |
| JSON support | ❌ | ✅ | ✅ |
| Window functions | ✅ | ✅ (8.0+) | ✅ |
| Docker image | ✅ `cubrid/cubrid` | ✅ | ✅ |
| Default port | 33000 | 3306 | 5432 |

## Cleanup

```bash
docker stop cubrid && docker rm cubrid
```

---

## Ecosystem at a Glance

```mermaid
flowchart TD
    C[(CUBRID Database<br/>cubrid/cubrid:11.2<br/>TCP :33000)]

    PY[Python] --> PYD[pycubrid (DB-API)] --> PYO[sqlalchemy-cubrid (ORM)] --> C
    TS[TypeScript] --> TSD[cubrid-client (Native)] --> TSO[drizzle-cubrid (ORM)] --> C
    GO[Go] --> GOD[cubrid-go (database/sql)] --> GOO[GORM dialector (ORM)] --> C

    PY --> PYF[FastAPI]
    PY --> PYJ[Django]
    PY --> PYL[Flask]
    PY --> PYP[Pandas]
    PY --> PYS[Streamlit]
    PY --> PYC[Celery]
```

All packages: [github.com/cubrid-labs](https://github.com/cubrid-labs)
