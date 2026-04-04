from __future__ import annotations

import sys

import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"
SALES_TABLE_NAME = "cookbook_sales"


def load_sales_dataframe() -> pd.DataFrame | None:
    engine = create_engine(DATABASE_URL)

    try:
        if not inspect(engine).has_table(SALES_TABLE_NAME):
            print(f"Missing required table '{SALES_TABLE_NAME}'.")
            print("Run 00_seed_data.py first to create and populate sample data.")
            return None

        df = pd.read_sql(SALES_TABLE_NAME, engine)
        if df.empty:
            print(f"Table '{SALES_TABLE_NAME}' exists but has no rows.")
            return None

        return df
    except SQLAlchemyError as exc:
        print(f"Failed to load data from CUBRID: {exc}")
        return None


def main() -> int:
    df = load_sales_dataframe()
    if df is None:
        return 1

    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["revenue"] = df["quantity"] * df["unit_price"]

    print("=== Dataset Overview ===")
    print(df.head(10).to_string(index=False))

    print("\n=== Statistical Summary (describe) ===")
    print(df[["quantity", "unit_price", "revenue"]].describe().to_string())

    print("\n=== Product Frequency (value_counts) ===")
    print(df["product"].value_counts().to_string())

    print("\n=== GroupBy: Category and Region ===")
    grouped = df.groupby(["category", "region"], as_index=False).agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("revenue", "sum"),
        orders=("sale_id", "count"),
    )
    print(grouped.to_string(index=False))

    print("\n=== Pivot Table: Revenue by Category x Region ===")
    pivot = pd.pivot_table(
        df,
        index="category",
        columns="region",
        values="revenue",
        aggfunc="sum",
        fill_value=0,
    )
    print(pivot.to_string())

    print("\n=== Date-based Analysis: Monthly Sales ===")
    df["year_month"] = df["sale_date"].dt.to_period("M").astype(str)
    monthly = df.groupby("year_month", as_index=False).agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("revenue", "sum"),
        order_count=("sale_id", "count"),
    )
    print(monthly.to_string(index=False))

    print("\n=== Date-based Analysis: Day of Week Revenue ===")
    df["day_name"] = df["sale_date"].dt.day_name()
    weekday = df.groupby("day_name", as_index=False).agg(
        total_revenue=("revenue", "sum"), orders=("sale_id", "count")
    )
    print(weekday.to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
