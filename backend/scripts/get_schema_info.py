import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def get_schema():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    tables = ['CN_PCTAS', 'CN_GLOSA', 'CN_TRANS', 'CN_LCYLV', 'accounts', 'journal_entries', 'entry_details']
    
    schema = {}
    for table in tables:
        # For legacy tables, they are stored uppercase in Postgres if created with quotes
        # Information schema uses actual case
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table if not table.startswith('CN_') else table,))
        
        rows = cur.fetchall()
        if not rows and table.startswith('CN_'):
             # Try uppercase just in case
             cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = %s
            """, (table.upper(),))
             rows = cur.fetchall()
             
        schema[table] = [{"column": r[0], "type": r[1], "nullable": r[2]} for r in rows]
        
    for table, cols in schema.items():
        print(f"\n--- {table} ---")
        for c in cols:
            print(f"  {c['column']} ({c['type']}) {'NULL' if c['nullable'] == 'YES' else 'NOT NULL'}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    get_schema()
