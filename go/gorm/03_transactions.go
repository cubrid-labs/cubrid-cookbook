//go:build ignore

// 03_transactions.go — Transactions with GORM + CUBRID.
//
// Demonstrates:
// - Commit flow using db.Transaction()
// - Rollback flow by returning an error
// - Manual transaction control with Begin/Commit/Rollback
// - Balance checks before and after each transaction

package main

import (
	"errors"
	"fmt"
	"log"

	cubrid "github.com/cubrid-labs/cubrid-go/dialector"
	"gorm.io/gorm"
)

const txnDSN = "cubrid://dba:@localhost:33000/testdb"

type CookbookAccount struct {
	ID      uint    `gorm:"primaryKey;autoIncrement"`
	Name    string  `gorm:"size:100;not null"`
	Balance float64 `gorm:"default:0"`
}

func (CookbookAccount) TableName() string {
	return "cookbook_accounts"
}

func openTxnDB() *gorm.DB {
	db, err := gorm.Open(cubrid.Open(txnDSN), &gorm.Config{})
	if err != nil {
		log.Fatal(err)
	}
	return db
}

func setup(db *gorm.DB) {
	if err := db.Migrator().DropTable(&CookbookAccount{}); err != nil {
		log.Fatal(err)
	}
	if err := db.AutoMigrate(&CookbookAccount{}); err != nil {
		log.Fatal(err)
	}

	seed := []CookbookAccount{
		{Name: "Alice", Balance: 1000.0},
		{Name: "Bob", Balance: 500.0},
	}
	if err := db.Create(&seed).Error; err != nil {
		log.Fatal(err)
	}
}

func showBalances(db *gorm.DB, label string) {
	var accounts []CookbookAccount
	if err := db.Order("id").Find(&accounts).Error; err != nil {
		log.Fatal(err)
	}

	fmt.Printf("  Balances (%s): ", label)
	for i, a := range accounts {
		if i > 0 {
			fmt.Print(", ")
		}
		fmt.Printf("%s=$%.2f", a.Name, a.Balance)
	}
	fmt.Println()
}

func commitExample(db *gorm.DB) {
	fmt.Println("=== Commit Example ===")
	showBalances(db, "before")

	amount := 200.0
	err := db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Model(&CookbookAccount{}).Where("name = ?", "Alice").
			Update("balance", gorm.Expr("balance - ?", amount)).Error; err != nil {
			return err
		}
		if err := tx.Model(&CookbookAccount{}).Where("name = ?", "Bob").
			Update("balance", gorm.Expr("balance + ?", amount)).Error; err != nil {
			return err
		}
		return nil
	})
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("  ✓ Transferred $%.2f from Alice to Bob\n", amount)
	showBalances(db, "after commit")
}

func rollbackExample(db *gorm.DB) {
	fmt.Println("\n=== Rollback Example ===")
	showBalances(db, "before")

	err := db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Model(&CookbookAccount{}).Where("name = ?", "Alice").
			Update("balance", 0).Error; err != nil {
			return err
		}
		fmt.Println("  Made Alice's balance = 0 (within transaction)")
		return errors.New("simulated failure")
	})
	if err != nil {
		fmt.Println("  ✓ Transaction rolled back automatically on error")
	}

	showBalances(db, "after rollback")
}

func manualTransaction(db *gorm.DB) {
	fmt.Println("\n=== Manual Transaction ===")
	showBalances(db, "before")

	tx := db.Begin()
	if tx.Error != nil {
		log.Fatal(tx.Error)
	}

	if err := tx.Model(&CookbookAccount{}).Where("name = ?", "Alice").
		Update("balance", gorm.Expr("balance + 100")).Error; err != nil {
		tx.Rollback()
		log.Fatal(err)
	}
	if err := tx.Model(&CookbookAccount{}).Where("name = ?", "Bob").
		Update("balance", gorm.Expr("balance + 50")).Error; err != nil {
		tx.Rollback()
		log.Fatal(err)
	}

	if err := tx.Commit().Error; err != nil {
		tx.Rollback()
		log.Fatal(err)
	}

	fmt.Println("  Applied bonuses: Alice +$100, Bob +$50")
	showBalances(db, "after manual commit")
}

func cleanup(db *gorm.DB) {
	if err := db.Migrator().DropTable(&CookbookAccount{}); err != nil {
		log.Fatal(err)
	}
	fmt.Println("\n✓ Cleaned up table 'cookbook_accounts'")
}

func main() {
	db := openTxnDB()

	setup(db)
	commitExample(db)
	rollbackExample(db)
	manualTransaction(db)
	cleanup(db)
}
