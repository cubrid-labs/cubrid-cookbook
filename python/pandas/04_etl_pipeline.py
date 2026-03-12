from __future__ import annotations

import logging
import sys
from typing import cast

import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"
SOURCE_TABLE = "cookbook_sales"
CLEAN_TABLE = "cookbook_sales_cleaned"
SUMMARY_TABLE = "cookbook_sales_summary"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def extract(engine) -> pd.DataFrame | None:
    if not inspect(engine).has_table(SOURCE_TABLE):
        logging.error("Missing required source table '%s'.", SOURCE_TABLE)
        logging.error("Run seed_data.py first to create and populate sample data.")
        return None

    df = pd.read_sql(SOURCE_TABLE, engine)
    if df.empty:
        logging.error("Source table '%s' is empty.", SOURCE_TABLE)
        return None

    logging.info("Extracted %d rows from %s.", len(df), SOURCE_TABLE)
    return df


def transform(df: pd.DataFrame):
    cleaned = cast(pd.DataFrame, df.copy())

    sale_dates = pd.to_datetime(cleaned["sale_date"], errors="coerce")
    cleaned["sale_date"] = sale_dates
    cleaned["product"] = cleaned["product"].astype(str).str.strip()
    cleaned["category"] = cleaned["category"].astype(str).str.strip()
    cleaned["region"] = cleaned["region"].astype(str).str.strip()

    cleaned = cast(
        pd.DataFrame,
        cleaned.dropna(
            subset=["sale_date", "product", "category", "region", "quantity", "unit_price"]
        ),
    )
    cleaned = cast(
        pd.DataFrame,
        cleaned[(cleaned["quantity"] > 0) & (cleaned["unit_price"] > 0)].copy(),
    )

    cleaned["revenue"] = cleaned["quantity"] * cleaned["unit_price"]
    cleaned["year_month"] = pd.to_datetime(cleaned["sale_date"], errors="coerce").map(
        lambda x: x.strftime("%Y-%m") if pd.notna(x) else None
    )

    summary = cast(
        pd.DataFrame,
        cleaned.groupby(["year_month", "category", "region"], as_index=False).agg(
            total_orders=("sale_id", "count"),
            total_quantity=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
            avg_unit_price=("unit_price", "mean"),
        ),
    )
    summary = summary.assign(avg_order_quantity=summary["total_quantity"] / summary["total_orders"])

    logging.info("Transformed data: %d cleaned rows, %d summary rows.", len(cleaned), len(summary))
    return cast(pd.DataFrame, cleaned), cast(pd.DataFrame, summary)


def load(engine, cleaned: pd.DataFrame, summary: pd.DataFrame) -> None:
    cleaned.to_sql(CLEAN_TABLE, engine, if_exists="replace", index=False)
    summary.to_sql(SUMMARY_TABLE, engine, if_exists="replace", index=False)
    logging.info("Loaded cleaned table '%s' and summary table '%s'.", CLEAN_TABLE, SUMMARY_TABLE)


def main() -> int:
    configure_logging()
    engine = create_engine(DATABASE_URL)

    try:
        extracted = extract(engine)
        if extracted is None:
            return 1

        cleaned, summary = transform(extracted)
        load(engine, cleaned, summary)

        print("=== ETL Completed: Cleaned Data Preview ===")
        print(cleaned.head(12).to_string(index=False))

        print("\n=== ETL Completed: Summary Preview ===")
        print(summary.head(20).to_string(index=False))

        return 0
    except SQLAlchemyError as exc:
        logging.error("ETL failed due to database error: %s", exc)
        return 1
    except Exception as exc:
        logging.error("ETL failed due to unexpected error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
