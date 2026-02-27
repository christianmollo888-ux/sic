import psycopg2
from decimal import Decimal

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def verify_totals():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("--- Verifying Financial Totals ---")
    
    # Legacy totals
    cur.execute('SELECT SUM("DEBE"), SUM("HABER") FROM "CN_TRANS"')
    legacy_debit, legacy_credit = cur.fetchone()
    legacy_debit = Decimal(str(legacy_debit or 0))
    legacy_credit = Decimal(str(legacy_credit or 0))
    
    # Modern totals
    cur.execute('SELECT SUM(debit), SUM(credit) FROM entry_details')
    modern_debit, modern_credit = cur.fetchone()
    modern_debit = Decimal(str(modern_debit or 0))
    modern_credit = Decimal(str(modern_credit or 0))
    
    print(f"Legacy - Debit: {legacy_debit}, Credit: {legacy_credit}")
    print(f"Modern - Debit: {modern_debit}, Credit: {modern_credit}")
    
    diff_debit = modern_debit - legacy_debit
    diff_credit = modern_credit - legacy_credit
    
    print(f"Difference - Debit: {diff_debit}, Credit: {diff_credit}")
    
    if diff_debit == 0 and diff_credit == 0:
        print("\nSUCCESS: Totals match perfectly!")
    else:
        print("\nWARNING: Totals do not match.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    verify_totals()
