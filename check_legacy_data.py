import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def check_legacy_details():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    code = '1102100000'
    print(f"Checking records in legacy table CN_TRANS for code {code}...")
    
    cur.execute('SELECT COUNT(*) FROM "CN_TRANS" WHERE "CODIGO" = %s', (code,))
    count = cur.fetchone()[0]
    print(f"  Total records in CN_TRANS: {count}")
    
    if count == 0:
        print("  Looking for a code that HAS data...")
        cur.execute('SELECT "CODIGO", COUNT(*) FROM "CN_TRANS" GROUP BY "CODIGO" HAVING COUNT(*) > 5 LIMIT 5')
        other_codes = cur.fetchall()
        for oc in other_codes:
            print(f"  Try code: {oc[0]} (has {oc[1]} records)")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_legacy_details()
