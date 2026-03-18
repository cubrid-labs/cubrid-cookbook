"""03_orm.py — SQLAlchemy ORM with CUBRID.

Demonstrates:
- DeclarativeBase models
- mapped_column with type annotations
- Session — add, query, update, delete
- Filtering, ordering, pagination
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "cookbook_books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100))
    isbn: Mapped[str | None] = mapped_column(String(13), unique=True, default=None)
    price: Mapped[float] = mapped_column(default=0.0)
    pages: Mapped[int] = mapped_column(default=0)
    published: Mapped[date | None] = mapped_column(default=None)

    def __repr__(self) -> str:
        return f"Book(id={self.id}, title='{self.title}', author='{self.author}')"


def create_tables(engine) -> None:
    print("=== ORM — Create Tables ===")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("  ✓ Created 'cookbook_books' table")


def add_books(engine) -> None:
    """Create (INSERT) using ORM."""
    print("\n=== ORM — Add Books ===")

    with Session(engine) as session:
        books = [
            Book(
                title="Clean Code",
                author="Robert C. Martin",
                isbn="9780132350884",
                price=39.99,
                pages=464,
                published=date(2008, 8, 1),
            ),
            Book(
                title="Design Patterns",
                author="Gang of Four",
                isbn="9780201633610",
                price=49.99,
                pages=395,
                published=date(1994, 10, 31),
            ),
            Book(
                title="The Pragmatic Programmer",
                author="David Thomas",
                isbn="9780135957059",
                price=44.99,
                pages=352,
                published=date(2019, 9, 23),
            ),
            Book(
                title="Refactoring",
                author="Martin Fowler",
                isbn="9780134757599",
                price=47.99,
                pages=448,
                published=date(2018, 11, 20),
            ),
            Book(
                title="Clean Architecture",
                author="Robert C. Martin",
                isbn="9780134494166",
                price=34.99,
                pages=432,
                published=date(2017, 9, 20),
            ),
        ]

        session.add_all(books)
        session.commit()
        print(f"  ✓ Added {len(books)} books")

        for book in books:
            print(f"    {book}")


def query_books(engine) -> None:
    """Read (SELECT) using ORM."""
    print("\n=== ORM — Query Books ===")

    with Session(engine) as session:
        # All books
        stmt = select(Book).order_by(Book.id)
        books = session.scalars(stmt).all()
        print(f"  All books ({len(books)}):")
        for b in books:
            print(f"    {b.title:30s}  by {b.author:20s}  ${b.price:.2f}")

        # Filter by author
        stmt = select(Book).where(Book.author == "Robert C. Martin")
        uncle_bob = session.scalars(stmt).all()
        print(f"\n  Books by Robert C. Martin ({len(uncle_bob)}):")
        for b in uncle_bob:
            print(f"    {b.title}")

        # Price range
        stmt = select(Book).where(Book.price.between(40.0, 50.0)).order_by(Book.price)
        mid_range = session.scalars(stmt).all()
        print(f"\n  Books $40-$50 ({len(mid_range)}):")
        for b in mid_range:
            print(f"    {b.title:30s}  ${b.price:.2f}")


def query_advanced(engine) -> None:
    """Advanced ORM queries."""
    print("\n=== ORM — Advanced Queries ===")

    with Session(engine) as session:
        # Aggregation
        stmt = (
            select(
                Book.author,
                func.count(Book.id).label("count"),
                func.avg(Book.price).label("avg_price"),
            )
            .group_by(Book.author)
            .order_by(func.count(Book.id).desc())
        )

        result = session.execute(stmt).all()
        print("  Books by author:")
        for row in result:
            print(f"    {row.author:20s}  {row.count} books  avg ${row.avg_price:.2f}")

        # Pagination (LIMIT/OFFSET)
        page_size = 2
        for page in range(1, 4):
            stmt = select(Book).order_by(Book.id).limit(page_size).offset((page - 1) * page_size)
            books = session.scalars(stmt).all()
            if not books:
                break
            print(f"\n  Page {page}:")
            for b in books:
                print(f"    {b.title}")

        # Scalar query
        stmt = select(func.count(Book.id))
        total = session.scalar(stmt)
        print(f"\n  Total books: {total}")

        # Exists
        stmt = select(Book).where(Book.isbn == "9780132350884")
        book = session.scalar(stmt)
        print(f"  'Clean Code' exists: {book is not None}")


def update_books(engine) -> None:
    """Update using ORM."""
    print("\n=== ORM — Update Books ===")

    with Session(engine) as session:
        # Get and modify
        book = session.scalar(select(Book).where(Book.title == "Clean Code"))
        if book:
            old_price = book.price
            book.price = 42.99
            session.commit()
            print(f"  ✓ Updated 'Clean Code' price: ${old_price:.2f} → ${book.price:.2f}")

        # Bulk update
        stmt = select(Book).where(Book.pages > 400)
        big_books = session.scalars(stmt).all()
        for b in big_books:
            b.price = round(b.price * 0.9, 2)
        session.commit()
        print(f"  ✓ Applied 10% discount to {len(big_books)} books with 400+ pages")


def delete_books(engine) -> None:
    """Delete using ORM."""
    print("\n=== ORM — Delete Books ===")

    with Session(engine) as session:
        book = session.scalar(select(Book).where(Book.title == "Design Patterns"))
        if book:
            session.delete(book)
            session.commit()
            print(f"  ✓ Deleted '{book.title}'")

        remaining = session.scalar(select(func.count(Book.id)))
        print(f"  Remaining books: {remaining}")


def cleanup(engine) -> None:
    Base.metadata.drop_all(engine)
    print("\n✓ Cleaned up")


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)

    try:
        create_tables(engine)
        add_books(engine)
        query_books(engine)
        query_advanced(engine)
        update_books(engine)
        delete_books(engine)
    finally:
        cleanup(engine)
        engine.dispose()
