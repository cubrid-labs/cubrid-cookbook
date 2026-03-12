"""06_lob.py — Large Object (BLOB/CLOB) handling with pycubrid.

Demonstrates:
- Creating CLOB columns and inserting text data
- Creating BLOB columns and inserting binary data
- Reading LOB data back
- Working with large text documents
"""

from __future__ import annotations

import pycubrid

DB_CONFIG = {
    "host": "localhost",
    "port": 33000,
    "database": "testdb",
    "user": "dba",
    "password": "",
}


def get_connection() -> pycubrid.Connection:
    return pycubrid.connect(**DB_CONFIG)


def setup(conn: pycubrid.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS cookbook_documents")
    cursor.execute("""
        CREATE TABLE cookbook_documents (
            id      INT AUTO_INCREMENT PRIMARY KEY,
            title   VARCHAR(200) NOT NULL,
            content CLOB
        )
    """)
    cursor.execute("DROP TABLE IF EXISTS cookbook_files")
    cursor.execute("""
        CREATE TABLE cookbook_files (
            id       INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(200) NOT NULL,
            data     BLOB
        )
    """)
    conn.commit()
    cursor.close()


def clob_example(conn: pycubrid.Connection) -> None:
    """Store and retrieve text data using CLOB."""
    print("=== CLOB (Character Large Object) ===")
    cursor = conn.cursor()

    # Insert text documents
    documents = [
        ("README", "# CUBRID Cookbook\n\nA collection of examples for CUBRID database."),
        ("License", "Apache License 2.0\n\nCopyright 2026 cubrid-labs"),
        (
            "Long Text",
            "Lorem ipsum dolor sit amet. " * 100,  # ~3KB of text
        ),
    ]

    for title, content in documents:
        # Create a CLOB object
        lob = conn.create_lob("CLOB", content)
        cursor.execute(
            "INSERT INTO cookbook_documents (title, content) VALUES (?, ?)",
            (title, lob),
        )
    conn.commit()
    print(f"  ✓ Inserted {len(documents)} documents with CLOB data")

    # Read back
    cursor.execute("SELECT title, content FROM cookbook_documents ORDER BY id")
    for row in cursor.fetchall():
        title = row[0]
        clob_data = row[1]
        # CLOB data may come as string or Lob object depending on size
        text = str(clob_data) if clob_data else ""
        preview = text[:60] + "..." if len(text) > 60 else text
        print(f"  {title:15s} ({len(text):,d} chars): {preview}")

    cursor.close()


def blob_example(conn: pycubrid.Connection) -> None:
    """Store and retrieve binary data using BLOB."""
    print("\n=== BLOB (Binary Large Object) ===")
    cursor = conn.cursor()

    # Create some binary data
    files = [
        ("icon.bin", bytes(range(256))),  # 256 bytes
        ("data.bin", b"\x00\x01\x02" * 1000),  # 3KB
        ("empty.bin", b""),  # Empty BLOB
    ]

    for filename, data in files:
        if data:
            lob = conn.create_lob("BLOB", data)
            cursor.execute(
                "INSERT INTO cookbook_files (filename, data) VALUES (?, ?)",
                (filename, lob),
            )
        else:
            cursor.execute(
                "INSERT INTO cookbook_files (filename, data) VALUES (?, NULL)",
                (filename,),
            )
    conn.commit()
    print(f"  ✓ Inserted {len(files)} files with BLOB data")

    # Read back
    cursor.execute("SELECT filename, data FROM cookbook_files ORDER BY id")
    for row in cursor.fetchall():
        filename = row[0]
        blob_data = row[1]
        if blob_data is not None:
            data = bytes(blob_data) if not isinstance(blob_data, bytes) else blob_data
            print(f"  {filename:15s} ({len(data):,d} bytes)")
        else:
            print(f"  {filename:15s} (NULL)")

    cursor.close()


def cleanup(conn: pycubrid.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS cookbook_documents")
    cursor.execute("DROP TABLE IF EXISTS cookbook_files")
    conn.commit()
    cursor.close()
    print("\n✓ Cleaned up")


if __name__ == "__main__":
    conn = get_connection()

    try:
        setup(conn)
        clob_example(conn)
        blob_example(conn)
    finally:
        cleanup(conn)
        conn.close()
