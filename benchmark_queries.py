import time, psycopg2, mysql.connector, sqlite3
from statistics import mean

QUERIES = {
    'SELECT': "SELECT * FROM orders WHERE total_amt > 1000 LIMIT 100;",
    'INSERT': "INSERT INTO products(name,price,category) VALUES ('x',1.0,'A'); DELETE FROM products WHERE name='x';",
    'UPDATE': "UPDATE orders SET total_amt = total_amt + 1 WHERE order_id = 1; UPDATE orders SET total_amt = total_amt - 1 WHERE order_id = 1;",
    'DELETE': "DELETE FROM products WHERE name='x';",  
    'JOIN': "SELECT o.order_id, c.name FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.total_amt > 500 LIMIT 100;"
}

def run_benchmark(conn, execute_fn, runs=20):
    results = {}
    for name,q in QUERIES.items():
        times = []
        for _ in range(runs):
            t0 = time.time()
            execute_fn(conn,q)
            t1 = time.time()
            times.append((t1-t0)*1000) 
        results[name] = mean(times)
    return results

def pg_exec(conn,q):
    cur = conn.cursor()
    cur.execute(q)
    try:
        cur.fetchall()
    except:
        pass
    conn.commit()

def mysql_exec(conn,q):
    cur = conn.cursor()
    cur.execute(q)
    try: cur.fetchall()
    except: pass
    conn.commit()

def sqlite_exec(conn,q):
    cur = conn.cursor()
    cur.executescript(q) 
    try: cur.fetchall()
    except: pass
    conn.commit()

if __name__ == "__main__":
    pg_conn = psycopg2.connect(host='localhost',port=5432,user='pguser',password='pgpass',dbname='pgdb')
    my_conn = mysql.connector.connect(host='localhost',user='mysqluser',password='mysqlpass',database='mysqldb')
    sqlite_conn = sqlite3.connect('test.db')
    print("Postgres benchmarks:", run_benchmark(pg_conn, pg_exec))
    print("MySQL benchmarks:", run_benchmark(my_conn, mysql_exec))
    print("SQLite benchmarks:", run_benchmark(sqlite_conn, sqlite_exec))