from backend.database import SessionLocal
from backend import crud
import json

def verify_report_data():
    db = SessionLocal()
    nit = "5962375118"
    year = 2025
    print(f"Verifying Tax Audit Report for NIT: {nit}, Year: {year}")
    
    report = crud.get_tax_audit_report_data(db, nit, year)
    if not report:
        print("FAIL: No report data found")
        return

    print(f"Taxpayer: {report.taxpayer_name}")
    print(f"Year: {report.year}")
    
    # Check if we have rows
    print(f"Found {len(report.rows)} rows in the report matrix.")
    
    # Check for specific month values (Month 12 should have data from our verify_enhanced.py run)
    month_12_has_data = False
    for row in report.rows:
        if row.months[11] > 0:
            month_12_has_data = True
            print(f"Month 12 Data Found in Casilla {row.field_code}: {row.months[11]}")
            break
            
    if month_12_has_data:
        print("SUCCESS: Data aggregation working for December 2025.")
    else:
        print("WARNING: No data found for Dec 2025. Ensure you uploaded a form for this period.")

    db.close()

if __name__ == "__main__":
    verify_report_data()
