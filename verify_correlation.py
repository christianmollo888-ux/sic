import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def verify():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute('SELECT COUNT(*), COUNT(DISTINCT ("TIPO", "NUMERO", "FECHA")) FROM "CN_GLOSA"')
    res = cur.fetchone()
    print(f"CN_GLOSA: Total={res[0]}, Unique(TIPO, NUMERO, FECHA)={res[1]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    verify()
