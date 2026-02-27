import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def debug_ledger_query():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    prefix = '1'
    print(f"Checking details for prefix '{prefix}%'...")
    
    cur.execute("""
        SELECT COUNT(d.id), SUM(d.debit), SUM(d.credit)
        FROM entry_details d
        JOIN accounts a ON d.account_id = a.id
        WHERE a.code LIKE %s
    """, (prefix + '%',))
    
    count, debit, credit = cur.fetchone()
    print(f"  Count: {count}")
    print(f"  Debit: {debit}")
    print(f"  Credit: {credit}")
    
    print("\nSample accounts matching prefix:")
    cur.execute("SELECT code, name FROM accounts WHERE code LIKE %s LIMIT 5", (prefix + '%',))
    for row in cur.fetchall():
        print(f"  {row}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    debug_ledger_query()
