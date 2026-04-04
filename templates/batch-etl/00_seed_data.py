from __future__ import annotations

import random
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import cast

import pandas as pd
from sqlalchemy import (
    Column,
    Date,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    create_engine,
    insert,
)
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"
SALES_TABLE_NAME = "cookbook_sales"


def build_sales_rows(total_rows: int = 180, seed: int = 42) -> list[dict[str, object]]:
    rng = random.Random(seed)

    product_catalog: list[tuple[str, str, Decimal]] = [
        ("Notebook Pro 14", "Electronics", Decimal("1299.00")),
        ("Noise-Cancel Headphones", "Electronics", Decimal("249.00")),
        ("Office Chair", "Furniture", Decimal("189.00")),
        ("Standing Desk", "Furniture", Decimal("499.00")),
        ("Water Bottle", "Accessories", Decimal("24.00")),
        ("Backpack", "Accessories", Decimal("79.00")),
        ("Espresso Beans", "Grocery", Decimal("18.50")),
        ("Protein Bars", "Grocery", Decimal("32.00")),
    ]
    regions = ["North", "South", "East", "West", "Central"]
    channels = ["Online", "Retail", "Distributor"]

    start_date = date(2025, 1, 1)
    rows: list[dict[str, object]] = []

    for sale_id in range(1, total_rows + 1):
        product, category, base_price = rng.choice(product_catalog)
        price_factor = Decimal(str(rng.uniform(0.90, 1.15))).quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_UP,
        )
        unit_price = (base_price * price_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        rows.append(
            {
                "sale_id": sale_id,
                "sale_date": start_date + timedelta(days=rng.randint(0, 179)),
                "product": product,
                "category": category,
                "quantity": rng.randint(1, 20),
                "unit_price": unit_price,
                "region": rng.choice(regions),
                "sales_channel": rng.choice(channels),
                "is_promo": rng.randint(0, 1),
            }
        )

    return rows


def main() -> int:
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()

    sales_table = Table(
        SALES_TABLE_NAME,
        metadata,
        Column("sale_id", Integer, primary_key=True),
        Column("sale_date", Date, nullable=False),
        Column("product", String(100), nullable=False),
        Column("category", String(40), nullable=False),
        Column("quantity", Integer, nullable=False),
        Column("unit_price", Numeric(10, 2), nullable=False),
        Column("region", String(30), nullable=False),
        Column("sales_channel", String(30), nullable=False),
        Column("is_promo", Integer, nullable=False),
    )

    rows = build_sales_rows(total_rows=180)

    try:
        with engine.begin() as conn:
            metadata.drop_all(conn, tables=[sales_table], checkfirst=True)
            metadata.create_all(conn, tables=[sales_table])
            conn.execute(insert(sales_table), rows)
    except SQLAlchemyError as exc:
        print(f"Failed to seed data in table '{SALES_TABLE_NAME}': {exc}")
        print("Check CUBRID connection and credentials in DATABASE_URL.")
        return 1

    seeded_df = pd.DataFrame(rows)
    seeded_df["revenue"] = seeded_df["quantity"] * seeded_df["unit_price"]

    print(f"Seeded {len(rows)} rows into table '{SALES_TABLE_NAME}'.")
    print("\nPreview (first 10 rows):")
    print(seeded_df.head(10).to_string(index=False))

    print("\nSales by category:")
    grouped = (
        seeded_df.groupby("category")
        .agg(total_qty=("quantity", "sum"), total_revenue=("revenue", "sum"))
        .reset_index()
    )
    category_summary = cast(pd.DataFrame, grouped).sort_values(
        by="total_revenue",
        ascending=False,
    )
    print(category_summary.to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
