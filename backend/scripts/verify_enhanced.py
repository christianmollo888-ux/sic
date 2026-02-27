from backend.utils_pdf import extract_form_200_data
from backend.database import SessionLocal
from backend import models_forms, schemas, crud
import json
import os
import datetime

def verify_enhanced_flow():
    pdf_path = r"c:\sicjac\formularios\F-200 12-2025.pdf"
    print(f"Verifying ENHANCED Flow for: {pdf_path}")
    
    # 1. Test Extraction
    raw_data = extract_form_200_data(pdf_path)
    print("Extracted Header Metadata:")
    print(json.dumps(raw_data['header'], indent=2))
    
    if not raw_data['header'].get('presentation_date'):
        print("FAIL: Could not extract presentation_date")
    
    db = SessionLocal()
    try:
        # Prepare payload
        values = []
        for rubro in [raw_data['rubro1'], raw_data['rubro2'], raw_data['rubro3']]:
            for k, v in rubro.items():
                values.append(schemas.DeclarationValueBase(field_code=k, value=v))
        
        # Helper to parse str to datetime
        def parse_iso(dstr):
            if not dstr: return None
            # The frontend does the parsing, but here we simulate it
            try:
                parts = dstr.split(' ') # "08/01/2026 11:42:41"
                d, m, y = parts[0].split('/')
                return datetime.datetime(int(y), int(m), int(d), *map(int, parts[1].split(':')))
            except:
                return None

        declaration_in = schemas.DeclarationCreate(
            taxpayer_nit=raw_data['header']['nit'],
            taxpayer_name=raw_data['header']['business_name'],
            form_code="200",
            version_number=raw_data['header'].get('version', '6'),
            month=int(raw_data['header']['month']),
            year=int(raw_data['header']['year']),
            values=values,
            presentation_date=parse_iso(raw_data['header']['presentation_date']),
            print_date=parse_iso(raw_data['header']['print_date']),
            pdf_user=raw_data['header']['pdf_user']
        )
        
        # 2. Test saving (Cleanup first to avoid duplicate error if we want a fresh test)
        # Actually, let's test the duplicate error!
        try:
            db_decl = crud.create_declaration(db, declaration_in)
            print(f"SUCCESS: Declaration saved with ID {db_decl.id}")
        except ValueError as e:
            print(f"EXPECTED ERROR (Duplicate): {e}")

        # 3. Test Temporal Validation
        future_decl = declaration_in.copy()
        future_decl.month = 12
        future_decl.year = 2026 # Future
        try:
            crud.create_declaration(db, future_decl)
            print("FAIL: Future declaration was saved unexpectedly")
        except ValueError as e:
            print(f"EXPECTED ERROR (Temporal): {e}")

        # 4. Verify detail retrieval (Labels/Rubrics)
        # Assuming ID 3 exists from previous run or we get the new ID
        last_decl = db.query(models_forms.Declaration).order_by(models_forms.Declaration.id.desc()).first()
        if last_decl:
             print(f"Retrieving details for ID {last_decl.id}...")
             # Simulate the API logic
             details = crud.get_declaration_details(db, last_decl.id)
             if details:
                 for v in details.values[:3]: # Just first 3
                     print(f"Field {v.field_definition.field_code}: {v.field_definition.label} ({v.field_definition.rubric}) = {v.value}")

    except Exception as e:
        print(f"Verification Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_enhanced_flow()
