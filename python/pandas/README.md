# Pandas + CUBRID Data Analysis Cookbook

Comprehensive examples for reading, analyzing, writing, and running ETL pipelines with pandas and CUBRID via SQLAlchemy.

## Prerequisites

- Python 3.10+
- Running CUBRID instance at `localhost:33000`
- Database `testdb` accessible as user `dba`
- SQLAlchemy CUBRID dialect and pycubrid driver

All scripts use this SQLAlchemy URL:

`cubrid+pycubrid://dba@localhost:33000/testdb`

## Setup

```bash
cd /data/GitHub/cubrid-cookbook/python/pandas
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Files

- `seed_data.py`
  - Creates and populates `cookbook_sales` with 180 realistic sales rows.
- `01_read_data.py`
  - Demonstrates `pd.read_sql_query()`, `pd.read_sql()`, and `pd.read_sql_table()`.
- `02_analysis.py`
  - Runs groupby, aggregation, pivot tables, `describe()`, `value_counts()`, and date-based analysis.
- `03_write_data.py`
  - Demonstrates `DataFrame.to_sql()` with `if_exists="replace"`, `if_exists="append"`, and chunked writes.
- `04_etl_pipeline.py`
  - End-to-end ETL with logging: extract from CUBRID, transform, and load summary tables.

## Data Schema

`cookbook_sales` table columns:

- `sale_id` (INTEGER, primary key)
- `sale_date` (DATE)
- `product` (VARCHAR)
- `category` (VARCHAR)
- `quantity` (INTEGER)
- `unit_price` (NUMERIC(10,2))
- `region` (VARCHAR)
- `sales_channel` (VARCHAR)
- `is_promo` (INTEGER, 0/1)

Derived tables created by scripts:

- `cookbook_sales_write_demo`
- `cookbook_sales_cleaned`
- `cookbook_sales_summary`

## Run Order

```bash
python seed_data.py
python 01_read_data.py
python 02_analysis.py
python 03_write_data.py
python 04_etl_pipeline.py
```

Each script checks required source tables and prints clear errors when tables are missing.

## Example Console Output (truncated)

`seed_data.py`

```text
Seeded 180 rows into table 'cookbook_sales'.

Preview (first 10 rows):
 sale_id  sale_date               product    category  quantity  unit_price  region sales_channel  is_promo  revenue
       1 2025-01-07       Office Chair   Furniture         8      196.22   South        Retail         0  1569.76
       2 2025-01-27  Notebook Pro 14  Electronics         4     1210.45    West        Online         1  4841.80
```

`02_analysis.py`

```text
=== Statistical Summary (describe) ===
          quantity   unit_price      revenue
count   180.000000   180.000000   180.000000
mean      9.650000   286.121944  2728.594444
...
```

`04_etl_pipeline.py`

```text
2026-03-13 10:12:01 | INFO | Extracted 180 rows from cookbook_sales.
2026-03-13 10:12:01 | INFO | Transformed data: 180 cleaned rows, 48 summary rows.
2026-03-13 10:12:02 | INFO | Loaded cleaned table 'cookbook_sales_cleaned' and summary table 'cookbook_sales_summary'.
```
