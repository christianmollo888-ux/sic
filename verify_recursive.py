import requests

def verify_recursive_ledger():
    BASE_URL = "http://localhost:8000"
    
    # 1000000000 = ACTIVO (Level 1)
    # 1100000000 = ACTIVO CORRIENTE (Level 2)
    # 1101000000 = DISPONIBLE (Level 3)
    codes = ['1000000000', '1100000000', '1101000000']
    
    r = requests.get(f"{BASE_URL}/accounts/?limit=1000")
    accounts = r.json()
    
    for code in codes:
        target = next((a for a in accounts if a['code'] == code), None)
        if target:
            lr = requests.get(f"{BASE_URL}/accounts/{target['id']}/ledger/")
            ledger = lr.json()
            print(f"Account: {code} | {target['name']}")
            print(f"  Total Debe:  {ledger['total_debit']}")
            print(f"  Total Haber: {ledger['total_credit']}")
            print(f"  Saldo:       {ledger['balance']}")
            print("-" * 30)
        else:
            print(f"Account {code} not found.")

if __name__ == "__main__":
    verify_recursive_ledger()
