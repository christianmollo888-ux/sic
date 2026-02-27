from backend.database import SessionLocal
from backend import models_forms

def verify_seeding():
    db = SessionLocal()
    try:
        versions = db.query(models_forms.FormVersion).all()
        print(f"Form Versions: {len(versions)}")
        for v in versions:
            print(f" - {v.form_code} v{v.version_number}")
            
        fields = db.query(models_forms.FormFieldDefinition).all()
        print(f"Form Fields: {len(fields)}")
        
        # Check specific field
        field_13 = db.query(models_forms.FormFieldDefinition).filter_by(field_code="13").first()
        if field_13:
            print(f"Field 13 Label: {field_13.label}")
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_seeding()
