//go:build ignore

// 02_crud.go — CRUD operations with cubrid-go.
//
// Demonstrates:
// - CREATE TABLE
// - INSERT rows (single and batch)
// - SELECT with filtering
// - UPDATE rows
// - DELETE rows
// - DROP TABLE cleanup

package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/cubrid-labs/cubrid-go"
)

const dsn = "cubrid://dba:@localhost:33000/testdb"

func setupTable(db *sql.DB) error {
	if _, err := db.Exec("DROP TABLE IF EXISTS cookbook_users"); err != nil {
		return err
	}

	createTableSQL := `
		CREATE TABLE cookbook_users (
			id    INT AUTO_INCREMENT PRIMARY KEY,
			name  VARCHAR(100) NOT NULL,
			email VARCHAR(200) UNIQUE,
			age   INT DEFAULT 0
		)
	`

	if _, err := db.Exec(createTableSQL); err != nil {
		return err
	}

	fmt.Println("✓ Created table 'cookbook_users'")
	return nil
}

func insertRows(db *sql.DB) error {
	if _, err := db.Exec(
		"INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)",
		"Alice", "alice@example.com", 30,
	); err != nil {
		return err
	}

	users := []struct {
		name  string
		email string
		age   int
	}{
		{name: "Bob", email: "bob@example.com", age: 25},
		{name: "Charlie", email: "charlie@example.com", age: 35},
		{name: "Diana", email: "diana@example.com", age: 28},
		{name: "Eve", email: "eve@example.com", age: 32},
	}

	for _, user := range users {
		if _, err := db.Exec(
			"INSERT INTO cookbook_users (name, email, age) VALUES (?, ?, ?)",
			user.name, user.email, user.age,
		); err != nil {
			return err
		}
	}

	fmt.Printf("✓ Inserted %d rows\n", 1+len(users))
	return nil
}

func selectAll(db *sql.DB) error {
	rows, err := db.Query("SELECT id, name, email, age FROM cookbook_users ORDER BY id")
	if err != nil {
		return err
	}
	defer rows.Close()

	type userRow struct {
		id    int
		name  string
		email sql.NullString
		age   int
	}

	var allUsers []userRow
	for rows.Next() {
		var u userRow
		if err := rows.Scan(&u.id, &u.name, &u.email, &u.age); err != nil {
			return err
		}
		allUsers = append(allUsers, u)
	}

	if err := rows.Err(); err != nil {
		return err
	}

	fmt.Printf("\nAll users (%d rows):\n", len(allUsers))
	fmt.Printf("  %3s  %-12s  %-25s  %3s\n", "ID", "Name", "Email", "Age")
	fmt.Printf("  %3s  %-12s  %-25s  %3s\n", "---", "----", "-----", "---")
	for _, u := range allUsers {
		email := ""
		if u.email.Valid {
			email = u.email.String
		}
		fmt.Printf("  %3d  %-12s  %-25s  %3d\n", u.id, u.name, email, u.age)
	}

	return nil
}

func selectFiltered(db *sql.DB) error {
	rowsByAge, err := db.Query(
		"SELECT name, age FROM cookbook_users WHERE age >= ? ORDER BY age DESC",
		30,
	)
	if err != nil {
		return err
	}
	defer rowsByAge.Close()

	type nameAge struct {
		name string
		age  int
	}

	var olderUsers []nameAge
	for rowsByAge.Next() {
		var row nameAge
		if err := rowsByAge.Scan(&row.name, &row.age); err != nil {
			return err
		}
		olderUsers = append(olderUsers, row)
	}

	if err := rowsByAge.Err(); err != nil {
		return err
	}

	fmt.Printf("\nUsers age >= 30 (%d rows):\n", len(olderUsers))
	for _, row := range olderUsers {
		fmt.Printf("  %-12s  age=%d\n", row.name, row.age)
	}

	rowsByName, err := db.Query(
		"SELECT name, email FROM cookbook_users WHERE name LIKE ? ORDER BY id",
		"%li%",
	)
	if err != nil {
		return err
	}
	defer rowsByName.Close()

	type nameEmail struct {
		name  string
		email sql.NullString
	}

	var matchedUsers []nameEmail
	for rowsByName.Next() {
		var row nameEmail
		if err := rowsByName.Scan(&row.name, &row.email); err != nil {
			return err
		}
		matchedUsers = append(matchedUsers, row)
	}

	if err := rowsByName.Err(); err != nil {
		return err
	}

	fmt.Printf("\nUsers with 'li' in name (%d rows):\n", len(matchedUsers))
	for _, row := range matchedUsers {
		email := ""
		if row.email.Valid {
			email = row.email.String
		}
		fmt.Printf("  %-12s  %s\n", row.name, email)
	}

	return nil
}

func updateRows(db *sql.DB) error {
	if _, err := db.Exec(
		"UPDATE cookbook_users SET age = ? WHERE name = ?",
		31, "Alice",
	); err != nil {
		return err
	}
	fmt.Println("\n✓ Updated Alice's age to 31")

	if _, err := db.Exec(
		"UPDATE cookbook_users SET age = age + 1 WHERE age < ?",
		30,
	); err != nil {
		return err
	}
	fmt.Println("✓ Incremented age for users younger than 30")

	return nil
}

func deleteRows(db *sql.DB) error {
	if _, err := db.Exec("DELETE FROM cookbook_users WHERE name = ?", "Eve"); err != nil {
		return err
	}

	fmt.Println("\n✓ Deleted Eve")
	return nil
}

func cleanup(db *sql.DB) error {
	if _, err := db.Exec("DROP TABLE IF EXISTS cookbook_users"); err != nil {
		return err
	}

	fmt.Println("\n✓ Cleaned up table 'cookbook_users'")
	return nil
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

	if err := setupTable(db); err != nil {
		log.Fatal(err)
	}
	defer func() {
		if err := cleanup(db); err != nil {
			log.Fatal(err)
		}
	}()

	if err := insertRows(db); err != nil {
		log.Fatal(err)
	}
	if err := selectAll(db); err != nil {
		log.Fatal(err)
	}
	if err := selectFiltered(db); err != nil {
		log.Fatal(err)
	}
	if err := updateRows(db); err != nil {
		log.Fatal(err)
	}
	if err := selectAll(db); err != nil {
		log.Fatal(err)
	}
	if err := deleteRows(db); err != nil {
		log.Fatal(err)
	}
	if err := selectAll(db); err != nil {
		log.Fatal(err)
	}
}
