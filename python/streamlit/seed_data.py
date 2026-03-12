from __future__ import annotations

import importlib
import random
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import text

if __package__:
    from .database import TABLE_NAME as table_name, get_engine
else:
    database_module = importlib.import_module("database")
    table_name = database_module.TABLE_NAME
    get_engine = database_module.get_engine


def generate_orders(row_count: int = 240) -> list[dict[str, object]]:
    random.seed(42)
    start_date = date(2024, 1, 1)

    products_by_category: dict[str, list[tuple[str, float, float]]] = {
        "Electronics": [
            ("Laptop", 780.0, 1650.0),
            ("Tablet", 210.0, 680.0),
            ("Smartphone", 290.0, 1250.0),
            ("Headphones", 60.0, 310.0),
        ],
        "Home": [
            ("Coffee Maker", 45.0, 180.0),
            ("Blender", 35.0, 145.0),
            ("Vacuum Cleaner", 90.0, 360.0),
            ("Air Purifier", 110.0, 420.0),
        ],
        "Office": [
            ("Desk Chair", 85.0, 340.0),
            ("Standing Desk", 160.0, 780.0),
            ("Monitor", 120.0, 510.0),
            ("Docking Station", 70.0, 290.0),
        ],
        "Lifestyle": [
            ("Fitness Tracker", 55.0, 260.0),
            ("Smart Watch", 120.0, 470.0),
            ("Water Bottle", 8.0, 38.0),
            ("Backpack", 25.0, 130.0),
        ],
    }
    regions = ["North", "South", "East", "West", "Central"]

    rows: list[dict[str, object]] = []
    for _ in range(row_count):
        category = random.choice(list(products_by_category.keys()))
        product, low_price, high_price = random.choice(products_by_category[category])
        quantity = random.randint(1, 12)
        unit_price = round(random.uniform(low_price, high_price), 2)
        order_day = start_date + timedelta(days=random.randint(0, 420))
        region = random.choice(regions)

        rows.append(
            {
                "product": product,
                "category": category,
                "quantity": quantity,
                "unit_price": unit_price,
                "order_date": order_day,
                "region": region,
            }
        )

    return rows


def seed_orders() -> None:
    engine = get_engine()

    drop_table_sql = f"DROP TABLE {table_name}"
    create_table_sql = f"""
    CREATE TABLE {table_name} (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        product VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DOUBLE NOT NULL,
        order_date DATE NOT NULL,
        region VARCHAR(50) NOT NULL
    )
    """
    insert_sql = f"""
    INSERT INTO {table_name}
        (product, category, quantity, unit_price, order_date, region)
    VALUES
        (:product, :category, :quantity, :unit_price, :order_date, :region)
    """

    with engine.begin() as connection:
        exists_sql = "SELECT class_name FROM db_class WHERE class_name = :table_name"
        table_exists = not pd.read_sql_query(
            text(exists_sql), connection, params={"table_name": table_name}
        ).empty

        if table_exists:
            connection.execute(text(drop_table_sql))

        connection.execute(text(create_table_sql))
        connection.execute(text(insert_sql), generate_orders())

    print(f"Seeded {table_name} with 240 rows.")


if __name__ == "__main__":
    seed_orders()
