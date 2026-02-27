import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def analyze_data_linking():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("Checking database population...")
    
    cur.execute("SELECT COUNT(*) FROM accounts")
    print(f"Accounts: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM journal_entries")
    print(f"Journal Entries (Headers): {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM entry_details")
    print(f"Entry Details: {cur.fetchone()[0]}")
    
    print("\nTop 10 accounts with transactions:")
    cur.execute("""
        SELECT a.code, a.name, COUNT(d.id) as detail_count
        FROM accounts a
        JOIN entry_details d ON a.id = d.account_id
        GROUP BY a.code, a.name
        ORDER BY detail_count DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    for row in rows:
        print(f"  Code: {row[0]} | Name: {row[1]} | Details: {row[2]}")
        
    print("\nChecking for details not linked to accounts:")
    cur.execute("SELECT COUNT(*) FROM entry_details WHERE account_id IS NULL")
    print(f"  Details without account_id: {cur.fetchone()[0]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    analyze_data_linking()
