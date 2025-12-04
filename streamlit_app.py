import streamlit as st
import pandas as pd
import altair as alt
from stimulate_results import simulate_metrics, to_dataframe
import json
from io import StringIO

st.set_page_config(page_title="DB Migration Dashboard", layout="wide")

st.title("DB Migration Dashboard Overview")
st.markdown(
    "This app displays migration metrics (migration time, per-query latency, storage, consistency) "
    "for MySQL / PostgreSQL / SQLite."
)

with st.sidebar:
    st.header("Migration Parameters")
    jitter = st.slider("Environment variability (jitter)", min_value=0.00, max_value=0.5, value=0.12, step=0.01)
    st.markdown("Enter an optional threshold for consistency below which DBs will be flagged:")
    consistency_threshold = st.slider("Consistency threshold (%)", min_value=90.0, max_value=100.0, value=98.0, step=0.1)
    st.markdown("---")
    st.markdown("Paste your SQL queries below :")
    col_sel = st.selectbox("Select DB to paste queries", ["MySQL", "Postgres", "SQLite"])

    mysql_example = {
        "SELECT": "SELECT * FROM orders WHERE total_amt > 500 LIMIT 100;",
        "INSERT": "INSERT INTO products(name,price,category) VALUES ('X', 9.99, 'A');",
        "UPDATE": "UPDATE orders SET total_amt = total_amt + 1 WHERE order_id = 1;",
        "DELETE": "DELETE FROM products WHERE name='X';",
        "JOIN": "SELECT o.order_id, c.name FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.total_amt > 500;"
    }

    postgres_example = {
        "SELECT": "SELECT * FROM orders WHERE total_amt > 500 LIMIT 100;",
        "INSERT": "INSERT INTO products(name,price,category) VALUES ('X', 9.99, 'A');",
        "UPDATE": "UPDATE orders SET total_amt = total_amt + 1 WHERE order_id = 1;",
        "DELETE": "DELETE FROM products WHERE name='X';",
        "JOIN": "SELECT o.order_id, c.name FROM orders o INNER JOIN customers c ON o.customer_id = c.customer_id WHERE o.total_amt > 500;"
    }

    sqlite_example = {
        "SELECT": "SELECT * FROM orders WHERE total_amt > 500 LIMIT 100;",
        "INSERT": "INSERT INTO products(name,price,category) VALUES ('X', 9.99, 'A');",
        "UPDATE": "UPDATE orders SET total_amt = total_amt + 1 WHERE order_id = 1;",
        "DELETE": "DELETE FROM products WHERE name='X';",
        "JOIN": "SELECT o.order_id, c.name FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.total_amt > 500;"
    }

    if col_sel == "MySQL":
        example = mysql_example
    elif col_sel == "Postgres":
        example = postgres_example
    else:
        example = sqlite_example
    qry_text = st.text_area(f"{col_sel} queries (JSON-like or free text). Example shown below:",
                             value=json.dumps(example, indent=2), height=220)
    run_btn = st.button("Run Analysis")

st.write("### Input preview")
st.code(qry_text, language="json")

if run_btn:
    try:
        parsed = json.loads(qry_text)
    except Exception:
        parsed = {"SELECT": qry_text}

    sim = simulate_metrics(databases=["MySQL", "Postgres", "SQLite"], jitter=float(jitter))
    df = to_dataframe(sim)

    df['flag_low_consistency'] = df['consistency_pct'] < consistency_threshold

    st.success("Analysis complete.")
    st.dataframe(df.style.format({
        'migration_time_s': "{:.2f}",
        'consistency_pct': "{:.2f}",
        'data_mb': "{:.2f}",
        'index_mb': "{:.2f}",
        'total_mb': "{:.2f}",
    }), height=260)

    st.markdown("## Visualizations")
    c1, c2 = st.columns([1,1])
    with c1:
        st.subheader("Migration Time (s)")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('db', sort=None),
            y='migration_time_s'
        ).properties(height=250)
        st.altair_chart(chart, use_container_width=True)

    with c2:
        st.subheader("Average Query Latency (ms)")
        latency_cols = [c for c in df.columns if c.startswith('latency_')]
        df_lat = df.melt(id_vars=['db'], value_vars=latency_cols, var_name='query', value_name='latency_ms')
        df_lat['query'] = df_lat['query'].str.replace('latency_','').str.replace('_ms','').str.upper()
        line = alt.Chart(df_lat).mark_circle(size=60).encode(
            x='query',
            y='latency_ms',
            color='db',
            tooltip=['db','query','latency_ms']
        ).properties(height=250)
        st.altair_chart(line, use_container_width=True)

    st.markdown("### Storage footprint")
    st.table(df[['db','data_mb','index_mb','total_mb']].set_index('db'))

    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, file_name="migration_results.csv", mime="text/csv")
else:
    st.info("Set the controls in the sidebar and press 'Run Analysis' to generate results.")