# Streamlit CUBRID Dashboard Example

An interactive Streamlit dashboard backed by CUBRID using SQLAlchemy — featuring KPI metrics, data exploration, analytics charts, and a raw SQL runner.

## Architecture

```mermaid
flowchart TD
    ST[Streamlit]
    ST --> UI[Sidebar + Page Content]
    UI --> DB[database.py\nSQLAlchemy engine + run_query()\n@st.cache_resource]
    DB --> C[(CUBRID\nlocalhost:33000\ncookbook_orders)]
```

## Files

| File | Role |
|------|------|
| `app.py` | Single-file Streamlit dashboard with sidebar navigation |
| `database.py` | Cached SQLAlchemy engine helper (`@st.cache_resource`) |
| `seed_data.py` | Creates and seeds `cookbook_orders` with 240 sample rows |
| `requirements.txt` | Python dependencies |

## Dashboard Sections

### Overview
- Three KPI metric cards: **Total Sales**, **Average Unit Price**, **Order Count**
- Uses `st.metric()` for clean presentation
- Metrics aggregated from `cookbook_orders` via `SUM()`, `AVG()`, `COUNT()`

### Data Explorer
- Full-text product search with `st.text_input()`
- Multi-select filters for **category** and **region**
- Column picker — choose which fields to display
- Interactive data grid with `st.dataframe()`

### Analytics
- **Sales by Category** — horizontal bar chart (`st.bar_chart`)
- **Daily Sales Trend** — line chart with sales amount and quantity (`st.line_chart`)
- Recent daily data table at the bottom

### Raw SQL
- Text area for custom `SELECT` statements
- "Run Query" button with result display
- Only `SELECT` queries allowed (safety check)

## Sample Data

`seed_data.py` generates 240 realistic order rows across:

| Dimension | Values |
|-----------|--------|
| **Categories** | Electronics, Home, Office, Lifestyle |
| **Products** | 16 products (Laptop, Tablet, Coffee Maker, Desk Chair, ...) |
| **Regions** | North, South, East, West, Central |
| **Date Range** | Jan 2024 – Feb 2025 (~14 months) |
| **Quantities** | 1–12 units per order |
| **Prices** | Realistic ranges per product (e.g., Laptop: $780–$1650) |

## Prerequisites

- Python 3.10+
- CUBRID running locally with database `testdb`
- Connection URL:

```text
cubrid+pycubrid://dba@localhost:33000/testdb
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Seed Sample Data

```bash
python seed_data.py
```

This creates table `cookbook_orders` and inserts 240 realistic order rows.

## Run the Dashboard

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Code Highlights

### Cached Engine (database.py)

```python
@st.cache_resource
def get_engine():
    return create_engine("cubrid+pycubrid://dba@localhost:33000/testdb")

def run_query(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn)
```

### KPI Metrics (app.py)

```python
kpi_df = run_query("""
    SELECT
        COALESCE(SUM(quantity * unit_price), 0) AS total_sales,
        COALESCE(AVG(unit_price), 0) AS avg_price,
        COUNT(*) AS order_count
    FROM cookbook_orders
""")
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,.2f}")
```

## Screenshot Guide (what you should see)

- **Overview screen**: Three KPI metric cards across the top and a short caption
- **Data Explorer screen**: Sidebar filters, search box, column picker, and interactive data grid
- **Analytics screen**: Category sales bar chart and daily trend line chart side by side
- **Raw SQL screen**: SQL text area, Run Query button, and tabular query result output

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: streamlit` | Install dependencies: `pip install -r requirements.txt` |
| Empty dashboard | Run `python seed_data.py` first to populate data |
| `OperationalError: connect failed` | Ensure CUBRID is running: `make up` from repo root |
| Charts not rendering | Check that `cookbook_orders` has data — re-run seed if needed |
