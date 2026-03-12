# Streamlit CUBRID Dashboard Example

This example shows how to build an interactive Streamlit dashboard backed by CUBRID using SQLAlchemy.

## Files

- `app.py`: single-file Streamlit dashboard with sidebar navigation
- `database.py`: cached SQLAlchemy engine helper (`@st.cache_resource`)
- `seed_data.py`: creates and seeds `cookbook_orders` with 240 sample rows
- `requirements.txt`: Python dependencies

## Dashboard Sections

- **Overview**: KPI cards for total sales, average unit price, and order count (`st.metric`)
- **Data Explorer**: search, category/region filters, and column selection over order data
- **Analytics**: built-in Streamlit charts (`st.bar_chart`, `st.line_chart`)
- **Raw SQL**: execute custom `SELECT` statements from a text area

## Prerequisites

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

## Screenshot Guide (what you should see)

- **Overview screen**: three KPI metric cards across the top and a short caption
- **Data Explorer screen**: sidebar filters, search box, column picker, and interactive data grid
- **Analytics screen**: category sales bar chart and daily trend line chart side by side
- **Raw SQL screen**: SQL text area, Run Query button, and tabular query result output
