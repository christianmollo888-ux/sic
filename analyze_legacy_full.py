import psycopg2
import json

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def analyze_legacy_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("--- CN_PCTAS Sample (Hierarchy Check) ---")
    cur.execute('SELECT "CODIGOZ", "CODIGO", "CUENTA", "SUB", "NOMBRE", "CLV" FROM "CN_PCTAS" ORDER BY "CODIGO" LIMIT 20')
    cols = [d[0] for d in cur.description]
    for row in cur.fetchall():
        print(dict(zip(cols, row)))
        
    print("\n--- CN_GLOSA Sample ---")
    cur.execute('SELECT * FROM "CN_GLOSA" LIMIT 5')
    cols = [d[0] for d in cur.description]
    for row in cur.fetchall():
        print(dict(zip(cols, row)))

    print("\n--- CN_TRANS Sample ---")
    cur.execute('SELECT "MES", "TIPO", "NUMERO", "FECHA", "CODIGO", "DEBE", "HABER" FROM "CN_TRANS" LIMIT 5')
    cols = [d[0] for d in cur.description]
    for row in cur.fetchall():
        print(dict(zip(cols, row)))
        
    print("\n--- CN_LCYLV Sample (The 4th Table) ---")
    cur.execute('SELECT * FROM "CN_LCYLV" LIMIT 5')
    cols = [d[0] for d in cur.description]
    for row in cur.fetchall():
        print(dict(zip(cols, row)))

    cur.close()
    conn.close()

if __name__ == "__main__":
    analyze_legacy_data()
