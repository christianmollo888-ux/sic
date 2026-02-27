import requests

def verify_multiple_ledgers():
    BASE_URL = "http://localhost:8000"
    
    print("Fetching accounts...")
    r = requests.get(f"{BASE_URL}/accounts/?limit=1000")
    accounts = r.json()
    
    # Target codes that we know have data from previous check
    targets = ['1102050001', '1101020001', '2101200001']
    
    found_targets = [a for a in accounts if a['code'] in targets]
    
    print("\nVerifying Ledgers for Active Accounts:")
    for acc in found_targets:
        lr = requests.get(f"{BASE_URL}/accounts/{acc['id']}/ledger/")
        ledger = lr.json()
        print(f"  Account: {acc['code']} | {acc['name']}")
        print(f"    Total Debe:  {ledger['total_debit']}")
        print(f"    Total Haber: {ledger['total_credit']}")
        print(f"    Saldo:       {ledger['balance']}")
        print("-" * 30)

if __name__ == "__main__":
    verify_multiple_ledgers()
