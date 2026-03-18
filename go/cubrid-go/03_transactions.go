//go:build ignore

// 03_transactions.go — Transaction control with cubrid-go.
//
// Demonstrates:
// - Begin/commit transaction for money transfer
// - Begin/rollback transaction on simulated failure
// - Multiple statements committed atomically

package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/cubrid-labs/cubrid-go"
)

const dsn = "cubrid://dba:@localhost:33000/testdb"

func setupTable(db *sql.DB) error {
	if _, err := db.Exec("DROP TABLE IF EXISTS cookbook_accounts"); err != nil {
		return err
	}

	createTableSQL := `
		CREATE TABLE cookbook_accounts (
			id      INT AUTO_INCREMENT PRIMARY KEY,
			name    VARCHAR(100) NOT NULL,
			balance DOUBLE DEFAULT 0.0
		)
	`

	if _, err := db.Exec(createTableSQL); err != nil {
		return err
	}

	if _, err := db.Exec(
		"INSERT INTO cookbook_accounts (name, balance) VALUES (?, ?)",
		"Alice", 1000.0,
	); err != nil {
		return err
	}

	if _, err := db.Exec(
		"INSERT INTO cookbook_accounts (name, balance) VALUES (?, ?)",
		"Bob", 500.0,
	); err != nil {
		return err
	}

	return nil
}

func showBalances(db *sql.DB, label string) error {
	rows, err := db.Query("SELECT name, balance FROM cookbook_accounts ORDER BY id")
	if err != nil {
		return err
	}
	defer rows.Close()

	type account struct {
		name    string
		balance float64
	}

	var accounts []account
	for rows.Next() {
		var a account
		if err := rows.Scan(&a.name, &a.balance); err != nil {
			return err
		}
		accounts = append(accounts, a)
	}

	if err := rows.Err(); err != nil {
		return err
	}

	if len(accounts) == 0 {
		fmt.Printf("  Balances (%s): no rows\n", label)
		return nil
	}

	fmt.Printf("  Balances (%s): ", label)
	for i, account := range accounts {
		if i > 0 {
			fmt.Print(", ")
		}
		fmt.Printf("%s=$%.2f", account.name, account.balance)
	}
	fmt.Println()

	return nil
}

func commitExample(db *sql.DB) error {
	fmt.Println("\n=== Commit Example ===")
	if err := showBalances(db, "before"); err != nil {
		return err
	}

	amount := 200.0
	tx, err := db.Begin()
	if err != nil {
		return err
	}

	if _, err := tx.Exec(
		"UPDATE cookbook_accounts SET balance = balance - ? WHERE name = ?",
		amount, "Alice",
	); err != nil {
		_ = tx.Rollback()
		return err
	}

	if _, err := tx.Exec(
		"UPDATE cookbook_accounts SET balance = balance + ? WHERE name = ?",
		amount, "Bob",
	); err != nil {
		_ = tx.Rollback()
		return err
	}

	if err := tx.Commit(); err != nil {
		_ = tx.Rollback()
		return err
	}

	fmt.Printf("  ✓ Transferred $%.2f from Alice to Bob\n", amount)
	return showBalances(db, "after commit")
}

func rollbackExample(db *sql.DB) error {
	fmt.Println("\n=== Rollback Example ===")
	if err := showBalances(db, "before"); err != nil {
		return err
	}

	tx, err := db.Begin()
	if err != nil {
		return err
	}

	if _, err := tx.Exec(
		"UPDATE cookbook_accounts SET balance = 0 WHERE name = ?",
		"Alice",
	); err != nil {
		_ = tx.Rollback()
		return err
	}

	fmt.Println("  Made Alice's balance = 0 (within transaction)")

	if err := tx.Rollback(); err != nil {
		return err
	}

	fmt.Println("  ✓ Transaction rolled back")
	return showBalances(db, "after rollback")
}

func multiStatementTransaction(db *sql.DB) error {
	fmt.Println("\n=== Multi-Statement Transaction ===")
	if err := showBalances(db, "before"); err != nil {
		return err
	}

	tx, err := db.Begin()
	if err != nil {
		return err
	}

	if _, err := tx.Exec(
		"UPDATE cookbook_accounts SET balance = balance + ? WHERE name = ?",
		100.0, "Alice",
	); err != nil {
		_ = tx.Rollback()
		return err
	}

	if _, err := tx.Exec(
		"UPDATE cookbook_accounts SET balance = balance + ? WHERE name = ?",
		50.0, "Bob",
	); err != nil {
		_ = tx.Rollback()
		return err
	}

	if err := tx.Commit(); err != nil {
		_ = tx.Rollback()
		return err
	}

	fmt.Println("  Applied bonuses: Alice +$100, Bob +$50")
	return showBalances(db, "after bonuses")
}

func cleanup(db *sql.DB) error {
	if _, err := db.Exec("DROP TABLE IF EXISTS cookbook_accounts"); err != nil {
		return err
	}

	fmt.Println("\n✓ Cleaned up table 'cookbook_accounts'")
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

	if err := commitExample(db); err != nil {
		log.Fatal(err)
	}
	if err := rollbackExample(db); err != nil {
		log.Fatal(err)
	}
	if err := multiStatementTransaction(db); err != nil {
		log.Fatal(err)
	}
}
