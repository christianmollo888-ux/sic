import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def check_schema():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    table_name = 'cn_glosa'
    print(f"Checking columns for {table_name}...")
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
    """)
    for row in cur.fetchall():
        print(f" - '{row[0]}': {row[1]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_schema()
