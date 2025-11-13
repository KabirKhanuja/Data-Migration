def time_postgres(pg_conn_info, csv_dir):
    import psycopg2
    import os
    import time

    start = time.time()
    conn = psycopg2.connect(**pg_conn_info)
    cur = conn.cursor()

    schema_sql = open("schema.sql").read()
    for stmt in schema_sql.split(";"):
        if stmt.strip():
            try:
                cur.execute(stmt + ";")
            except Exception as e:
                if "already exists" in str(e):
                    pass
                else:
                    raise

    conn.commit()

    try:
        with open(os.path.join(csv_dir, "customers.csv"), "r") as f:
            cur.copy_expert(
                "COPY customers(customer_id,name,email,city,age) FROM STDIN CSV HEADER;",
                f
            )

        with open(os.path.join(csv_dir, "products.csv"), "r") as f:
            cur.copy_expert(
                "COPY products(product_id,name,price,category) FROM STDIN CSV HEADER;",
                f
            )

        with open(os.path.join(csv_dir, "orders.csv"), "r") as f:
            cur.copy_expert(
                "COPY orders(order_id,customer_id,order_date,total_amt) FROM STDIN CSV HEADER;",
                f
            )

        with open(os.path.join(csv_dir, "order_items.csv"), "r") as f:
            cur.copy_expert(
                "COPY order_items(order_item_id,order_id,product_id,qty,price) FROM STDIN CSV HEADER;",
                f
            )

        conn.commit()
    except Exception as e:
        print("COPY error:", e)
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return time.time() - start
