import psycopg2
import json

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def analyze_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    tables = ['CN_PCTAS', 'CN_TRANS', 'CN_GLOSA', 'CN_LCYLV']
    
    for table in tables:
        print(f"\n{'='*20} {table} {'='*20}")
        cur.execute(f'SELECT * FROM "{table}" LIMIT 5;')
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        print(f"Columns: {', '.join(colnames)}")
        for i, row in enumerate(rows):
            # Print row mapped to column names for clarity
            data = dict(zip(colnames, row))
            print(f"Row {i+1}: {data}")
        
        cur.execute(f'SELECT COUNT(*) FROM "{table}";')
        print(f"Total Rows: {cur.fetchone()[0]}")

    # Specific relationship check
    print(f"\n{'='*20} Relationship Check {'='*20}")
    cur.execute('''
        SELECT T."COD_ASIENT", G."GLOSA", T."DEBE", T."HABER"
        FROM "CN_TRANS" T
        JOIN "CN_GLOSA" G ON T."COD_ASIENT" = G."COD_ASIENT"
        LIMIT 5;
    ''')
    print("Join TRANS and GLOSA on COD_ASIENT:")
    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()

if __name__ == "__main__":
    analyze_data()
