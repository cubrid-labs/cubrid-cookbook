# Pandas + SQLAlchemy Batch ETL Template

## Overview

Production-style batch ETL template for CUBRID using pandas and SQLAlchemy.
It demonstrates a full data workflow: seed source data, read/query data, run analysis, write transformed datasets, and execute an end-to-end ETL pipeline.

The template uses `cookbook_` table names and includes defensive checks for missing tables and database errors.

## Quick Start

1. Move into this directory and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start CUBRID (for example from a repository-level compose file), then run scripts in order:

   ```bash
   python seed_data.py
   python 01_read_data.py
   python 02_analysis.py
   python 03_write_data.py
   python 04_etl_pipeline.py
   ```

3. Review terminal output and verify generated tables in CUBRID.

## Project Structure

```text
seed_data.py        # Creates and seeds cookbook_sales with realistic sample rows
01_read_data.py     # Demonstrates pd.read_sql_query, pd.read_sql, pd.read_sql_table
02_analysis.py      # Performs descriptive stats, groupby, pivot, and date-based analysis
03_write_data.py    # Demonstrates to_sql replace/append/chunked writes
04_etl_pipeline.py  # Runs extract-transform-load into cleaned and summary tables
requirements.txt    # pandas, SQLAlchemy, CUBRID driver/dialect, matplotlib
```

## Configuration

All scripts define database configuration in-module:

- `DATABASE_URL` (current default: `cubrid+pycubrid://dba@localhost:33000/testdb`)

Main table names used by the template:

- Source: `cookbook_sales`
- Write demo target: `cookbook_sales_write_demo`
- ETL cleaned output: `cookbook_sales_cleaned`
- ETL summary output: `cookbook_sales_summary`

If your environment differs, update `DATABASE_URL` values consistently across all files.

## What Each Script Produces

- `seed_data.py`: recreates and seeds `cookbook_sales`.
- `01_read_data.py`: prints SQL read examples and revenue-by-region summary.
- `02_analysis.py`: prints dataset overview and analytics summaries.
- `03_write_data.py`: writes demo outputs into `cookbook_sales_write_demo`.
- `04_etl_pipeline.py`: creates cleaned/aggregated ETL output tables for downstream reporting.
