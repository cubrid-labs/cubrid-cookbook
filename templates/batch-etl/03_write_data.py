from __future__ import annotations

import random
import sys
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"
SOURCE_TABLE = "cookbook_sales"
TARGET_TABLE = "cookbook_sales_write_demo"


def build_chunk_rows(start_id: int, rows: int = 40, seed: int = 7) -> pd.DataFrame:
    rng = random.Random(seed)
    products = ["Notebook Pro 14", "Office Chair", "Backpack", "Protein Bars"]
    categories = {
        "Notebook Pro 14": "Electronics",
        "Office Chair": "Furniture",
        "Backpack": "Accessories",
        "Protein Bars": "Grocery",
    }
    regions = ["North", "South", "East", "West", "Central"]
    start = date(2025, 7, 1)

    payload: list[dict[str, object]] = []
    for i in range(rows):
        product = rng.choice(products)
        payload.append(
            {
                "demo_id": start_id + i,
                "sale_date": start + timedelta(days=i % 31),
                "product": product,
                "category": categories[product],
                "region": rng.choice(regions),
                "quantity": rng.randint(1, 12),
            }
        )

    return pd.DataFrame(payload)


def main() -> int:
    engine = create_engine(DATABASE_URL)

    try:
        if not inspect(engine).has_table(SOURCE_TABLE):
            print(f"Missing required source table '{SOURCE_TABLE}'.")
            print("Run 00_seed_data.py first to create and populate sample data.")
            return 1

        source_df = pd.read_sql_query(
            text(
                """
                SELECT
                    sale_id AS demo_id,
                    sale_date,
                    product,
                    category,
                    region,
                    quantity
                FROM cookbook_sales
                ORDER BY sale_id
                """
            ),
            engine,
        )
        base_df = source_df.head(25).copy()

        print("=== Initial DataFrame to write (replace) ===")
        print(base_df.head(10).to_string(index=False))

        base_df.to_sql(TARGET_TABLE, engine, if_exists="replace", index=False)
        print(f"Wrote {len(base_df)} rows to '{TARGET_TABLE}' with if_exists='replace'.")

        append_df = source_df.iloc[25:35].copy()
        append_df.to_sql(TARGET_TABLE, engine, if_exists="append", index=False)
        print(f"Appended {len(append_df)} rows with if_exists='append'.")

        chunk_df = build_chunk_rows(start_id=10_000, rows=50)
        chunk_df.to_sql(TARGET_TABLE, engine, if_exists="append", index=False, chunksize=10)
        print(f"Appended {len(chunk_df)} rows using chunked to_sql(chunksize=10).")

        total_df = pd.read_sql_query(
            text(f"SELECT COUNT(*) AS row_count FROM {TARGET_TABLE}"),
            engine,
        )
        preview_df = pd.read_sql_query(
            text(
                f"""
                SELECT demo_id, sale_date, product, category, region, quantity
                FROM {TARGET_TABLE}
                ORDER BY demo_id
                """
            ),
            engine,
        )

        print("\n=== Final row count in target table ===")
        print(total_df.to_string(index=False))

        print("\n=== Preview of target data ===")
        print(preview_df.head(15).to_string(index=False))

        return 0
    except SQLAlchemyError as exc:
        print(f"Database write/read failed: {exc}")
        return 1
    except Exception as exc:
        print(f"Unexpected error in write demo: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
