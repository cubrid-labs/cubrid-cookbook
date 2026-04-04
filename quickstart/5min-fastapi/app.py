from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pycubrid

app = FastAPI(title="CUBRID Quickstart API")


class ItemIn(BaseModel):
    val: str


class ItemOut(ItemIn):
    id: int


def get_conn() -> pycubrid.Connection:
    return pycubrid.connect(
        host="cubrid",
        port=33000,
        database="testdb",
        user="dba",
        password="",
    )


@app.on_event("startup")
def create_table() -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cookbook_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            val VARCHAR(255) NOT NULL
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


@app.get("/items", response_model=list[ItemOut])
def list_items() -> list[ItemOut]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, val FROM cookbook_items ORDER BY id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [ItemOut(id=row[0], val=row[1]) for row in rows]


@app.post("/items", response_model=ItemOut)
def create_item(item: ItemIn) -> ItemOut:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cookbook_items (val) VALUES (?)", (item.val,))
    conn.commit()
    item_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return ItemOut(id=item_id, val=item.val)


@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int) -> ItemOut:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, val FROM cookbook_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemOut(id=row[0], val=row[1])
