//go:build ignore

// 01_connect.go — Connecting to CUBRID with GORM.
//
// Demonstrates:
// - Opening a GORM connection with the cubrid-go dialector
// - Configuring GORM logger output
// - Running raw SQL (SELECT 1 + 1)
// - Reading connection metadata (version, database, user)

package main

import (
	"fmt"
	"log"
	"os"
	"time"

	cubrid "github.com/cubrid-labs/cubrid-go/dialector"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

const dsn = "cubrid://dba:@localhost:33000/testdb"

func openDB() (*gorm.DB, error) {
	gormLogger := logger.New(
		log.New(os.Stdout, "[gorm] ", log.LstdFlags),
		logger.Config{
			SlowThreshold:             time.Second,
			LogLevel:                  logger.Info,
			IgnoreRecordNotFoundError: true,
			Colorful:                  false,
		},
	)

	return gorm.Open(cubrid.Open(dsn), &gorm.Config{Logger: gormLogger})
}

func basicConnection(db *gorm.DB) error {
	fmt.Println("=== Basic Connection ===")

	var result struct {
		Value int `gorm:"column:result"`
	}

	if err := db.Raw("SELECT 1 + 1 AS result").Scan(&result).Error; err != nil {
		return err
	}

	fmt.Printf("1 + 1 = %d\n", result.Value)
	return nil
}

func connectionInfo(db *gorm.DB) error {
	fmt.Println("\n=== Connection Info ===")

	var info struct {
		Version  string `gorm:"column:version"`
		Database string `gorm:"column:db"`
		User     string `gorm:"column:user_name"`
	}

	if err := db.Raw("SELECT version() AS version").Scan(&info).Error; err != nil {
		return err
	}
	if err := db.Raw("SELECT database() AS db").Scan(&info).Error; err != nil {
		return err
	}
	if err := db.Raw("SELECT user() AS user_name").Scan(&info).Error; err != nil {
		return err
	}

	fmt.Printf("CUBRID version: %s\n", info.Version)
	fmt.Printf("Database: %s\n", info.Database)
	fmt.Printf("User: %s\n", info.User)
	return nil
}

func main() {
	db, err := openDB()
	if err != nil {
		log.Fatal(err)
	}

	if err := basicConnection(db); err != nil {
		log.Fatal(err)
	}
	if err := connectionInfo(db); err != nil {
		log.Fatal(err)
	}
}
