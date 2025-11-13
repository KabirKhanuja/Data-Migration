import os, psycopg2, mysql.connector, sqlite3, hashlib

def postgres_size(conn):
    cur = conn.cursor()
    cur.execute("SELECT pg_database_size(current_database());")
    return cur.fetchone()[0] / (1024*1024) 

def mysql_db_size(conn):
    cur = conn.cursor()
    cur.execute("SELECT SUM(data_length+index_length) FROM information_schema.tables WHERE table_schema=DATABASE();")
    return cur.fetchone()[0] / (1024*1024)

def sqlite_size(dbfile):
    return os.path.getsize(dbfile)/(1024*1024)

def checksum_table(conn, table, fetch_all_fn):
    h = hashlib.md5()
    for row in fetch_all_fn(conn, table):
        h.update(str(row).encode())
    return h.hexdigest()

def pg_fetch(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} ORDER BY 1;")
    return cur.fetchall()

def my_fetch(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} ORDER BY 1;")
    return cur.fetchall()

def sqlite_fetch(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} ORDER BY 1;")
    return cur.fetchall()

if __name__ == "__main__":
    pg_conn = psycopg2.connect(host='localhost',port=5432,user='pguser',password='pgpass',dbname='pgdb')
    print("Postgres DB size (MB):", postgres_size(pg_conn))
    print("Postgres customers checksum:", checksum_table(pg_conn,'customers', pg_fetch))