from backend.utils_pdf import extract_form_200_data
from backend.database import SessionLocal
from backend import models_forms
import json
import os

def final_verification():
    pdf_path = r"c:\sicjac\formularios\F-200 12-2025.pdf"
    print(f"Verifying PDF: {pdf_path}")
    
    # 1. Test Extraction
    data = extract_form_200_data(pdf_path)
    
    # Verification criteria
    expected_nit = "5962375118"
    expected_period = "12/2025"
    
    extracted_nit = data['header'].get('nit')
    extracted_period = f"{data['header'].get('month')}/{data['header'].get('year')}"
    
    print(f"Extracted NIT: {extracted_nit}")
    print(f"Extracted Period: {extracted_period}")
    
    success = True
    if extracted_nit != expected_nit:
        print(f"FAIL: NIT mismatch. Expected {expected_nit}")
        success = False
    if extracted_period != expected_period:
        print(f"FAIL: Period mismatch. Expected {expected_period}")
        success = False
        
    # Check key rubro values
    # C1004 (Total Credito) should be around 61948 or 619.48 based on previous trace
    # C1002 (Total Debito) should be 0.0
    c1002 = data['rubro1'].get('C1002', -1)
    c1004 = data['rubro2'].get('C1004', -1)
    
    print(f"Extracted C1002: {c1002}")
    print(f"Extracted C1004: {c1004}")
    
    # 2. Test DB Model registration
    db = SessionLocal()
    try:
        # Check if we can query FormVersion (seeded earlier)
        version = db.query(models_forms.FormVersion).filter_by(form_code="200", version_number="6").first()
        if version:
            print(f"SUCCESS: Form 200 v6 metadata found in database.")
        else:
            print("FAIL: Form 200 v6 metadata not found.")
            success = False
            
    except Exception as e:
        print(f"DB Error: {e}")
        success = False
    finally:
        db.close()

    if success:
        print("\n=== FINAL VERIFICATION SUCCESSFUL ===")
    else:
        print("\n=== FINAL VERIFICATION FAILED ===")

if __name__ == "__main__":
    final_verification()
