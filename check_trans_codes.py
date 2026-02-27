import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def check_trans():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("Checking COD_ASIENT in CN_TRANS...")
    cur.execute('''
        SELECT "COD_ASIENT", COUNT(*) 
        FROM "CN_TRANS" 
        GROUP BY "COD_ASIENT" 
        ORDER BY COUNT(*) DESC 
        LIMIT 10
    ''')
    rows = cur.fetchall()
    for r in rows:
        print(f"Code: '{r[0]}' - Count: {r[1]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_trans()
