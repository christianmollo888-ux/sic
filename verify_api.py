import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing API Health...")
    r = requests.get(f"{BASE_URL}/")
    print(f"Health: {r.json()}")

    print("\nTesting GET /accounts/...")
    r = requests.get(f"{BASE_URL}/accounts/?limit=5")
    accounts = r.json()
    print(f"Accounts received: {len(accounts)}")
    if accounts:
        print(f"Sample Account: {accounts[0]}")
        acc_id = accounts[0]['id']

        print(f"\nTesting GET /accounts/{acc_id}/ledger/...")
        r = requests.get(f"{BASE_URL}/accounts/{acc_id}/ledger/")
        print(f"Ledger: {r.json()}")

    print("\nTesting GET /entries/...")
    r = requests.get(f"{BASE_URL}/entries/?limit=2")
    entries = r.json()
    print(f"Entries received: {len(entries)}")
    if entries:
        print(f"Sample Entry: {entries[0]}")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"Error testing API: {e}")
