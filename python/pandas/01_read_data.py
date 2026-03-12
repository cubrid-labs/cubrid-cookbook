from __future__ import annotations

import sys

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"
SALES_TABLE_NAME = "cookbook_sales"


def ensure_sales_table_exists(engine) -> bool:
    try:
        has_table = inspect(engine).has_table(SALES_TABLE_NAME)
    except SQLAlchemyError as exc:
        print(f"Failed to inspect database schema: {exc}")
        return False

    if not has_table:
        print(f"Missing required table '{SALES_TABLE_NAME}'.")
        print("Run seed_data.py first to create and populate sample data.")
        return False

    return True


def main() -> int:
    engine = create_engine(DATABASE_URL)

    if not ensure_sales_table_exists(engine):
        return 1

    try:
        print("=== pd.read_sql_query() with raw SQL ===")
        query = text(
            """
            SELECT
                sale_date,
                product,
                category,
                quantity,
                unit_price,
                region,
                quantity * unit_price AS revenue
            FROM cookbook_sales
            WHERE sale_date >= :start_date
            ORDER BY sale_date, sale_id
            """
        )
        df_query = pd.read_sql_query(query, engine, params={"start_date": "2025-03-01"})
        print(df_query.head(12).to_string(index=False))
        print(f"Rows returned: {len(df_query)}")

        print("\n=== pd.read_sql() with table name ===")
        df_read_sql = pd.read_sql(SALES_TABLE_NAME, engine)
        print(df_read_sql.head(8).to_string(index=False))
        print(f"Rows in {SALES_TABLE_NAME}: {len(df_read_sql)}")

        print("\n=== pd.read_sql_table() selecting columns ===")
        df_table = pd.read_sql_table(
            SALES_TABLE_NAME,
            engine,
            columns=["sale_date", "product", "region", "quantity", "unit_price"],
        )
        print(df_table.head(8).to_string(index=False))

        print("\n=== Quick metric: Revenue by region (from read_sql_table data) ===")
        df_table["revenue"] = df_table["quantity"] * df_table["unit_price"]
        revenue_by_region = df_table.groupby("region", as_index=False)["revenue"].sum()
        descending_idx = revenue_by_region["revenue"].argsort()[::-1]
        revenue_by_region = revenue_by_region.iloc[descending_idx]
        print(revenue_by_region.to_string(index=False))

        return 0
    except SQLAlchemyError as exc:
        print(f"Database query failed: {exc}")
        return 1
    except Exception as exc:
        print(f"Unexpected error while reading data: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
