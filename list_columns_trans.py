import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def list_columns():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM "CN_TRANS" LIMIT 1')
    colnames = [desc[0] for desc in cur.description]
    print(f"Columns in CN_TRANS: {colnames}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    list_columns()
