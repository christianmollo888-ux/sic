import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def analyze_linkage():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("--- Sample from CN_GLOSA (Headers) ---")
    cur.execute('SELECT "MES", "TIPO", "NUMERO", "FECHA", "COD_ASIENT" FROM "CN_GLOSA" LIMIT 5')
    for r in cur.fetchall():
        print(r)

    print("\n--- Sample from CN_TRANS (Details) ---")
    cur.execute('SELECT "MES", "TIPO", "NUMERO", "FECHA", "COD_ASIENT" FROM "CN_TRANS" LIMIT 5')
    for r in cur.fetchall():
        print(r)

    print("\n--- Correlation Check ---")
    # See if (MES, TIPO, NUMERO) is unique in CN_GLOSA
    cur.execute('SELECT COUNT(*), COUNT(DISTINCT ("MES", "TIPO", "NUMERO")) FROM "CN_GLOSA"')
    res = cur.fetchone()
    print(f"CN_GLOSA: Total={res[0]}, Unique(MES, TIPO, NUMERO)={res[1]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    analyze_linkage()
