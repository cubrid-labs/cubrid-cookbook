//go:build ignore

// 02_crud.go — CRUD operations with GORM + CUBRID.
//
// Demonstrates:
// - AutoMigrate table creation for cookbook_users
// - INSERT with db.Create()
// - SELECT with Find(), Where(), and First()
// - UPDATE with Model().Update()
// - DELETE with db.Delete()
// - Table cleanup with DropTable()

package main

import (
	"fmt"
	"log"

	cubrid "github.com/cubrid-labs/cubrid-go/dialector"
	"gorm.io/gorm"
)

const crudDSN = "cubrid://dba:@localhost:33000/testdb"

type CookbookUser struct {
	_     struct{} `gorm:"table:cookbook_users"`
	ID    uint   `gorm:"primaryKey;autoIncrement"`
	Name  string `gorm:"size:100;not null"`
	Email string `gorm:"size:200;uniqueIndex"`
	Age   int    `gorm:"default:0"`
}

func (CookbookUser) TableName() string {
	return "cookbook_users"
}

func openCRUDDB() *gorm.DB {
	db, err := gorm.Open(cubrid.Open(crudDSN), &gorm.Config{})
	if err != nil {
		log.Fatal(err)
	}
	return db
}

func setupTable(db *gorm.DB) {
	if err := db.Migrator().DropTable(&CookbookUser{}); err != nil {
		log.Fatal(err)
	}
	if err := db.AutoMigrate(&CookbookUser{}); err != nil {
		log.Fatal(err)
	}
	fmt.Println("✓ Created table 'cookbook_users' with AutoMigrate")
}

func createRecords(db *gorm.DB) {
	alice := CookbookUser{Name: "Alice", Email: "alice@example.com", Age: 30}
	if err := db.Create(&alice).Error; err != nil {
		log.Fatal(err)
	}

	users := []CookbookUser{
		{Name: "Bob", Email: "bob@example.com", Age: 25},
		{Name: "Charlie", Email: "charlie@example.com", Age: 35},
		{Name: "Diana", Email: "diana@example.com", Age: 28},
		{Name: "Eve", Email: "eve@example.com", Age: 32},
	}
	if err := db.Create(&users).Error; err != nil {
		log.Fatal(err)
	}

	fmt.Printf("✓ Inserted %d rows\n", 1+len(users))
}

func readRecords(db *gorm.DB) {
	var allUsers []CookbookUser
	if err := db.Order("id").Find(&allUsers).Error; err != nil {
		log.Fatal(err)
	}

	fmt.Printf("\nAll users (%d rows):\n", len(allUsers))
	fmt.Printf("  %3s  %-12s  %-25s  %3s\n", "ID", "Name", "Email", "Age")
	fmt.Printf("  %3s  %-12s  %-25s  %3s\n", "---", "----", "-----", "---")
	for _, u := range allUsers {
		fmt.Printf("  %3d  %-12s  %-25s  %3d\n", u.ID, u.Name, u.Email, u.Age)
	}

	var age30Plus []CookbookUser
	if err := db.Where("age >= ?", 30).Order("age").Find(&age30Plus).Error; err != nil {
		log.Fatal(err)
	}
	fmt.Printf("\nUsers age >= 30 (%d rows):\n", len(age30Plus))
	for _, u := range age30Plus {
		fmt.Printf("  %-12s  age=%d\n", u.Name, u.Age)
	}

	var first CookbookUser
	if err := db.Where("name = ?", "Alice").First(&first).Error; err != nil {
		log.Fatal(err)
	}
	fmt.Printf("\nFirst matching user: %s (%s)\n", first.Name, first.Email)
}

func updateRecords(db *gorm.DB) {
	if err := db.Model(&CookbookUser{}).Where("name = ?", "Alice").Update("age", 31).Error; err != nil {
		log.Fatal(err)
	}
	fmt.Println("\n✓ Updated Alice's age to 31")

	if err := db.Model(&CookbookUser{}).Where("age < ?", 30).Update("age", gorm.Expr("age + 1")).Error; err != nil {
		log.Fatal(err)
	}
	fmt.Println("✓ Incremented age for users younger than 30")
}

func deleteRecords(db *gorm.DB) {
	if err := db.Where("name = ?", "Eve").Delete(&CookbookUser{}).Error; err != nil {
		log.Fatal(err)
	}
	fmt.Println("\n✓ Deleted Eve")
}

func cleanup(db *gorm.DB) {
	if err := db.Migrator().DropTable(&CookbookUser{}); err != nil {
		log.Fatal(err)
	}
	fmt.Println("\n✓ Cleaned up table 'cookbook_users'")
}

func main() {
	db := openCRUDDB()

	setupTable(db)
	createRecords(db)
	readRecords(db)
	updateRecords(db)
	readRecords(db)
	deleteRecords(db)
	readRecords(db)
	cleanup(db)
}
