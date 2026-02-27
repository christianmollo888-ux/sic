import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def get_db_info():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    tables = ['CN_PCTAS', 'CN_GLOSA', 'CN_TRANS', 'CN_LCYLV']
    
    for table in tables:
        print(f"\n--- Columns in {table} ---")
        cur.execute(f'SELECT * FROM "{table}" LIMIT 0')
        cols = [d[0] for d in cur.description]
        print(cols)
        
    print("\n--- CLV values in CN_PCTAS ---")
    cur.execute('SELECT "CLV", COUNT(*) FROM "CN_PCTAS" GROUP BY "CLV" ORDER BY "CLV"')
    for row in cur.fetchall():
        print(f"CLV: {row[0]} | count: {row[1]}")

    print("\n--- Sample Hierarchy Data ---")
    cur.execute('SELECT "CODIGO", "NOMBRE", "CLV" FROM "CN_PCTAS" ORDER BY "CODIGO" LIMIT 20')
    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()

if __name__ == "__main__":
    get_db_info()
