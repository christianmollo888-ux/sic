import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def check_duplicates():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("Checking duplicates for COD_ASIENT in CN_GLOSA...")
    cur.execute('''
        SELECT "COD_ASIENT", COUNT(*) 
        FROM "CN_GLOSA" 
        GROUP BY "COD_ASIENT" 
        HAVING COUNT(*) > 1 
        ORDER BY COUNT(*) DESC
        LIMIT 10
    ''')
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"Code: {r[0]} - Count: {r[1]}")
    else:
        print("No duplicates found by GROUP BY.")

    # Also check what we actually have in the new table if it was partially filled
    cur.execute('SELECT COUNT(*) FROM "journal_entries"')
    print(f"Total entries currently in journal_entries: {cur.fetchone()[0]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_duplicates()
