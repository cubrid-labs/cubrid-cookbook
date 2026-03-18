//go:build ignore

// 01_connect.go — Connecting to CUBRID with cubrid-go.
//
// Demonstrates:
// - Basic connection
// - Running a simple query
// - Connection metadata (version, database, user)
// - Reusing one connection for multiple queries

package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/cubrid-labs/cubrid-go"
)

const dsn = "cubrid://dba:@localhost:33000/testdb"

func basicConnection(db *sql.DB) {
	fmt.Println("=== Basic Connection ===")

	var result int
	if err := db.QueryRow("SELECT 1 + 1 AS result").Scan(&result); err != nil {
		log.Fatal(err)
	}

	fmt.Printf("1 + 1 = %d\n", result)
}

func connectionInfo(db *sql.DB) {
	fmt.Println("\n=== Connection Info ===")

	var version string
	if err := db.QueryRow("SELECT version() AS version").Scan(&version); err != nil {
		log.Fatal(err)
	}
	fmt.Printf("CUBRID version: %s\n", version)

	var database string
	if err := db.QueryRow("SELECT database() AS db").Scan(&database); err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Database: %s\n", database)

	var user string
	if err := db.QueryRow("SELECT user() AS u").Scan(&user); err != nil {
		log.Fatal(err)
	}
	fmt.Printf("User: %s\n", user)
}

func multipleQueries(db *sql.DB) {
	fmt.Println("\n=== Multiple Queries ===")

	if _, err := db.Exec("DROP TABLE IF EXISTS cookbook_connect_demo"); err != nil {
		log.Fatal(err)
	}
	if _, err := db.Exec("CREATE TABLE cookbook_connect_demo (id INT, note VARCHAR(50))"); err != nil {
		log.Fatal(err)
	}
	if _, err := db.Exec("DROP TABLE cookbook_connect_demo"); err != nil {
		log.Fatal(err)
	}

	type queryExample struct {
		sql   string
	}

	queries := []queryExample{
		{sql: "SELECT 1 AS a"},
		{sql: "SELECT 'hello' AS b"},
		{sql: "SELECT CURRENT_DATE AS today"},
	}

	for _, q := range queries {
		var value any
		if err := db.QueryRow(q.sql).Scan(&value); err != nil {
			log.Fatal(err)
		}
		fmt.Printf("%-35s -> %v\n", q.sql, value)
	}
}

func main() {
	db, err := sql.Open("cubrid", dsn)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatal(err)
	}

	basicConnection(db)
	connectionInfo(db)
	multipleQueries(db)
}
