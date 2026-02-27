import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def list_sample_accounts():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('SELECT code, name FROM accounts ORDER BY code LIMIT 100')
    rows = cur.fetchall()
    for code, name in rows:
        print(f"{code} | {name}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    list_sample_accounts()
