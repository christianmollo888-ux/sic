import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def verify_live_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Codes from the user's screenshot
    codes = ['1102020001', '1102030000', '1102100000']
    
    print(f"Comparing codes from screenshot with database 'sicjac'...")
    cur.execute('SELECT code, name FROM accounts WHERE code IN %s ORDER BY code', (tuple(codes),))
    rows = cur.fetchall()
    
    for code, name in rows:
        print(f"DB -> Code: {code} | Name: {name}")
    
    # Verify the sum for 1102100000 specifically as shown in Mayor modal
    cur.execute('''
        SELECT SUM(d.debit), SUM(d.credit)
        FROM entry_details d
        JOIN accounts a ON d.account_id = a.id
        WHERE a.code = '1102100000'
    ''')
    debit, credit = cur.fetchone()
    print(f"\nLedger for 1102100000 (ANTICIPO A CUENTA UTILIDADES SOCIOS):")
    print(f"  Total Debe: {debit or 0}")
    print(f"  Total Haber: {credit or 0}")
    print(f"  Saldo: {(debit or 0) - (credit or 0)}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    verify_live_data()
