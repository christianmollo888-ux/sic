import httpx
import sys

def verify_er_report():
    print("Testing ER Report Endpoint...")
    try:
        response = httpx.get("http://localhost:8000/reports/er?end_date=2025-12-31", timeout=5.0)
        response.raise_for_status()
        data = response.json().get("data", {})
        
        print("--- INGRESOS ---")
        for i in data.get("ingresos", []):
            if i['level'] == 1:
                print(f"[{i['code']}] {i['name']}: {i['amount']}")
        print(f"TOTAL INGRESOS: {data.get('total_ingresos')}")
        
        print("\n--- EGRESOS ---")
        for e in data.get("egresos", []):
            if e['level'] == 1:
                print(f"[{e['code']}] {e['name']}: {e['amount']}")
        print(f"TOTAL EGRESOS: {data.get('total_egresos')}")
        
        print(f"\nRESULTADO DEL EJERCICIO: {data.get('resultado')}")
        
    except Exception as e:
        print(f"Error testing ER endpoint: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_er_report()
