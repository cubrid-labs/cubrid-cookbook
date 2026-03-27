from __future__ import annotations

import importlib

import pandas as pd
from sqlalchemy import text

st = importlib.import_module("streamlit")

if __package__:
    from .database import TABLE_NAME as orders_table_name, get_engine, run_query
else:
    database_module = importlib.import_module("database")
    orders_table_name = database_module.TABLE_NAME
    get_engine = database_module.get_engine
    run_query = database_module.run_query


st.set_page_config(page_title="CUBRID Sales Dashboard", page_icon="📊", layout="wide")


def load_orders() -> pd.DataFrame:
    sql = f"""
    SELECT
        id,
        product,
        category,
        quantity,
        unit_price,
        order_date,
        region,
        quantity * unit_price AS total_amount
    FROM {orders_table_name}
    ORDER BY order_date, id
    """
    return run_query(sql)


def render_overview() -> None:
    st.subheader("Overview")
    with st.spinner("Loading KPI metrics..."):
        kpi_sql = f"""
        SELECT
            COALESCE(SUM(quantity * unit_price), 0) AS total_sales,
            COALESCE(AVG(unit_price), 0) AS avg_price,
            COUNT(*) AS order_count
        FROM {orders_table_name}
        """
        kpi_df = run_query(kpi_sql)

    total_sales = float(kpi_df.loc[0, "total_sales"])
    avg_price = float(kpi_df.loc[0, "avg_price"])
    order_count = int(kpi_df.loc[0, "order_count"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Average Unit Price", f"${avg_price:,.2f}")
    col3.metric("Order Count", f"{order_count:,}")

    st.caption("Metrics are calculated from `cookbook_orders`.")


def render_data_explorer() -> None:
    st.subheader("Data Explorer")
    with st.spinner("Loading orders for exploration..."):
        orders_df = load_orders()

    categories = sorted(orders_df["category"].dropna().unique().tolist())
    regions = sorted(orders_df["region"].dropna().unique().tolist())

    search_term = st.text_input("Search product", placeholder="Try: Laptop")
    selected_categories = st.multiselect("Category filter", categories, default=categories)
    selected_regions = st.multiselect("Region filter", regions, default=regions)

    all_columns = orders_df.columns.tolist()
    selected_columns = st.multiselect("Columns", all_columns, default=all_columns)

    filtered = orders_df[
        orders_df["category"].isin(selected_categories) & orders_df["region"].isin(selected_regions)
    ]
    filtered = pd.DataFrame(filtered)

    if search_term.strip():
        search_lower = search_term.strip().lower()
        product_values = filtered["product"].astype(str).tolist()
        search_mask = [search_lower in value.lower() for value in product_values]
        filtered = filtered.loc[search_mask]

    if selected_columns:
        st.dataframe(filtered[selected_columns], use_container_width=True, hide_index=True)
    else:
        st.warning("Select at least one column to display results.")

    st.caption(f"Showing {len(filtered):,} rows")


def render_analytics() -> None:
    st.subheader("Analytics")

    with st.spinner("Building analytics charts..."):
        sales_by_category_sql = f"""
        SELECT
            category,
            SUM(quantity * unit_price) AS total_sales
        FROM {orders_table_name}
        GROUP BY category
        ORDER BY total_sales DESC
        """
        sales_by_day_sql = f"""
        SELECT
            order_date,
            SUM(quantity * unit_price) AS total_sales,
            SUM(quantity) AS total_quantity
        FROM {orders_table_name}
        GROUP BY order_date
        ORDER BY order_date
        """
        category_df = run_query(sales_by_category_sql)
        daily_df = run_query(sales_by_day_sql)

    left, right = st.columns(2)
    with left:
        st.markdown("**Sales by Category**")
        category_chart_df = category_df.set_index("category")
        st.bar_chart(category_chart_df["total_sales"])

    with right:
        st.markdown("**Daily Sales Trend**")
        daily_chart_df = daily_df.copy()
        daily_chart_df["order_date"] = pd.to_datetime(daily_chart_df["order_date"])
        daily_chart_df = daily_chart_df.set_index("order_date")
        st.line_chart(daily_chart_df[["total_sales", "total_quantity"]])

    st.dataframe(daily_df.tail(20), use_container_width=True, hide_index=True)


def render_raw_sql() -> None:
    st.subheader("Raw SQL")
    st.caption("Run custom SELECT queries against `cookbook_orders`.")

    default_sql = f"SELECT * FROM {orders_table_name} ORDER BY id DESC LIMIT 20"
    sql_input = st.text_area("SQL query", value=default_sql, height=140)

    if st.button("Run Query", type="primary"):
        query = sql_input.strip()
        if not query:
            st.warning("Please enter SQL before running the query.")
            return

        if not query.lower().startswith("select"):
            st.error("Only SELECT statements are allowed in this dashboard.")
            return

        with st.spinner("Executing SQL query..."):
            try:
                engine = get_engine()
                with engine.connect() as connection:
                    result_df = pd.read_sql_query(text(query), connection)
            except Exception as exc:
                st.error(f"Query failed: {exc}")
                return

        st.success(f"Returned {len(result_df):,} rows")
        st.dataframe(result_df, use_container_width=True, hide_index=True)


def main() -> None:
    st.title("CUBRID Streamlit Dashboard")
    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Choose section",
        ["Overview", "Data Explorer", "Analytics", "Raw SQL"],
        index=0,
    )

    if page == "Overview":
        render_overview()
    elif page == "Data Explorer":
        render_data_explorer()
    elif page == "Analytics":
        render_analytics()
    else:
        render_raw_sql()


if __name__ == "__main__":
    main()
