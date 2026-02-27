from backend.utils_pdf import extract_form_200_data
from backend.database import SessionLocal
from backend import models_forms, schemas, crud
import json
import os
import datetime

def verify_persistence_flow():
    pdf_path = r"c:\sicjac\formularios\F-200 12-2025.pdf"
    print(f"Verifying Persistence Flow for: {pdf_path}")
    
    db = SessionLocal()
    try:
        # 1. Extract Data
        raw_data = extract_form_200_data(pdf_path)
        
        # 2. Prepare payload for saving
        # Flatten values
        values = []
        for rubro in [raw_data['rubro1'], raw_data['rubro2'], raw_data['rubro3']]:
            for k, v in rubro.items():
                values.append(schemas.DeclarationValueBase(field_code=k, value=v))
        
        declaration_in = schemas.DeclarationCreate(
            taxpayer_nit=raw_data['header']['nit'],
            taxpayer_name=raw_data['header']['business_name'],
            form_code="200",
            version_number="6",
            month=int(raw_data['header']['month']),
            year=int(raw_data['header']['year']),
            values=values,
            transaction_number="SIM-123456"
        )
        
        # 3. Save via CRUD
        db_decl = crud.create_declaration(db, declaration_in)
        print(f"SUCCESS: Declaration saved with ID {db_decl.id}")
        
        # 4. Verify History Retrieval
        history = crud.get_declarations(db)
        found = any(d.id == db_decl.id for d in history)
        if found:
            print(f"SUCCESS: Declaration {db_decl.id} found in history list.")
        else:
            print(f"FAIL: Declaration {db_decl.id} NOT found in history list.")
            
        # 5. Verify Details Retrieval
        details = crud.get_declaration_details(db, db_decl.id)
        if details and len(details.values) > 0:
            print(f"SUCCESS: Retrieved {len(details.values)} values for declaration {db_decl.id}.")
            # Check 1004 (Total Credito) specifically
            c1004_val = next((v.value for v in details.values if v.field_definition.field_code == '1004'), None)
            print(f"Value for 1004 (Total Credito): {c1004_val}")
        else:
            print(f"FAIL: Could not retrieve details for declaration {db_decl.id}.")

    except Exception as e:
        print(f"Verification Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_persistence_flow()
