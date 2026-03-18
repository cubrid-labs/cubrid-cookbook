//go:build ignore

// 04_relationships.go — Relationships with GORM + CUBRID.
//
// Demonstrates:
// - AutoMigrate for one-to-many models
// - Creating related rows through explicit foreign keys
// - Eager loading with Preload()
// - JOIN queries across cookbook_authors and cookbook_books
// - Cleanup by dropping both tables

package main

import (
	"fmt"
	"log"

	cubrid "github.com/cubrid-labs/cubrid-go/dialector"
	"gorm.io/gorm"
)

const relDSN = "cubrid://dba:@localhost:33000/testdb"

type CookbookAuthor struct {
	ID    uint           `gorm:"primaryKey;autoIncrement"`
	Name  string         `gorm:"size:100;not null"`
	Books []CookbookBook `gorm:"foreignKey:CookbookAuthorID"`
}

func (CookbookAuthor) TableName() string {
	return "cookbook_authors"
}

type CookbookBook struct {
	ID               uint           `gorm:"primaryKey;autoIncrement"`
	Title            string         `gorm:"size:200;not null"`
	CookbookAuthorID uint           `gorm:"not null;index"`
	Author           CookbookAuthor `gorm:"foreignKey:CookbookAuthorID;references:ID"`
}

func (CookbookBook) TableName() string {
	return "cookbook_books"
}

func openRelDB() *gorm.DB {
	db, err := gorm.Open(cubrid.Open(relDSN), &gorm.Config{})
	if err != nil {
		log.Fatal(err)
	}
	return db
}

func setup(db *gorm.DB) {
	// Drop in FK-safe order: books first (has FK to authors).
	db.Exec("DROP TABLE IF EXISTS cookbook_books")
	db.Exec("DROP TABLE IF EXISTS cookbook_authors")
	if err := db.AutoMigrate(&CookbookAuthor{}, &CookbookBook{}); err != nil {
		log.Fatal(err)
	}
	fmt.Println("✓ Created tables 'cookbook_authors' and 'cookbook_books'")
}

func createWithAssociations(db *gorm.DB) {
	fmt.Println("\n=== Create Data ===")

	authors := []CookbookAuthor{{Name: "Alice Writer"}, {Name: "Bob Novelist"}}
	if err := db.Create(&authors).Error; err != nil {
		log.Fatal(err)
	}

	books := []CookbookBook{
		{Title: "CUBRID Basics", CookbookAuthorID: authors[0].ID},
		{Title: "Advanced GORM", CookbookAuthorID: authors[0].ID},
		{Title: "Transactions by Example", CookbookAuthorID: authors[1].ID},
	}
	if err := db.Create(&books).Error; err != nil {
		log.Fatal(err)
	}

	fmt.Printf("✓ Inserted %d authors and %d books\n", len(authors), len(books))
}

func preloadExample(db *gorm.DB) {
	fmt.Println("\n=== Preload Example ===")

	var authors []CookbookAuthor
	if err := db.Preload("Books").Order("id").Find(&authors).Error; err != nil {
		log.Fatal(err)
	}

	for _, author := range authors {
		fmt.Printf("%s (%d books)\n", author.Name, len(author.Books))
		for _, book := range author.Books {
			fmt.Printf("  - %s\n", book.Title)
		}
	}
}

func joinExample(db *gorm.DB) {
	fmt.Println("\n=== Join Example ===")

	var rows []struct {
		Title      string `gorm:"column:title"`
		AuthorName string `gorm:"column:author_name"`
	}

	err := db.Table("cookbook_books AS b").
		Select("b.title AS title, a.name AS author_name").
		Joins("JOIN cookbook_authors AS a ON a.id = b.cookbook_author_id").
		Order("b.id").
		Find(&rows).Error
	if err != nil {
		log.Fatal(err)
	}

	for _, row := range rows {
		fmt.Printf("%-28s by %s\n", row.Title, row.AuthorName)
	}
}

func cleanup(db *gorm.DB) {
	// Must drop books first (has FK to authors).
	db.Exec("DROP TABLE IF EXISTS cookbook_books")
	db.Exec("DROP TABLE IF EXISTS cookbook_authors")
	fmt.Println("\n\u2713 Cleaned up tables")
}

func main() {
	db := openRelDB()

	setup(db)
	createWithAssociations(db)
	preloadExample(db)
	joinExample(db)
	cleanup(db)
}
