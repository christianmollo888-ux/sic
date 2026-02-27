import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

# Add parent directory to sys.path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SQLALCHEMY_DATABASE_URL
from backend import models

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_level_and_parent(code: str):
    if code.endswith('000000000'): 
        return 1, None
    if code.endswith('00000000'): 
        return 2, code[:1] + '0' * 9
    if code.endswith('000000'): 
        return 3, code[:2] + '0' * 8
    if code.endswith('0000'): 
        return 4, code[:4] + '0' * 6
    return 5, code[:6] + '0' * 4

def sync():
    db = SessionLocal()
    try:
        print("Recreating normalized tables...")
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)

        print("Syncing Accounts from CN_PCTAS...")
        legacy_accounts = db.execute(text('SELECT "CODIGO", "NOMBRE", "CLV" FROM "CN_PCTAS"')).fetchall()
        
        account_map = {}
        for row in legacy_accounts:
            code = row.CODIGO.strip()
            level, parent = get_level_and_parent(code)
            
            db_account = models.Account(
                code=code,
                name=row.NOMBRE.strip(),
                parent_code=parent,
                level=level,
                clv=row.CLV.strip()
            )
            db.add(db_account)
            db.flush()
            account_map[code] = db_account.id
        
        db.commit()
        print(f"  Synced {len(account_map)} accounts.")

        print("Syncing Journal Entries from CN_GLOSA...")
        legacy_headers = db.execute(text('SELECT "MES", "COD_ASIENT", "TIPO", "NUMERO", "FECHA", "GLOSA" FROM "CN_GLOSA"')).fetchall()
        
        entry_map = {}
        for row in legacy_headers:
            # Generate a consistent key
            key = (row.TIPO, row.NUMERO, row.FECHA)
            
            db_entry = models.JournalEntry(
                entry_code=row.COD_ASIENT.strip() if row.COD_ASIENT else None,
                date=row.FECHA,
                description=row.GLOSA.strip() if row.GLOSA else "",
                entry_type=str(row.TIPO),
                entry_number=row.NUMERO
            )
            db.add(db_entry)
            db.flush()
            entry_map[key] = db_entry.id
        
        db.commit()
        print(f"  Synced {len(entry_map)} headers.")

        print("Syncing Entry Details from CN_TRANS...")
        # Note: Added NO_CORRE to help identify individual lines if needed
        legacy_details = db.execute(text('SELECT "TIPO", "NUMERO", "FECHA", "CODIGO", "DEBE", "HABER" FROM "CN_TRANS"')).fetchall()
        
        detail_count = 0
        missing_headers = 0
        for row in legacy_details:
            a_code = row.CODIGO.strip()
            key = (row.TIPO, row.NUMERO, row.FECHA)
            
            if key in entry_map and a_code in account_map:
                db_detail = models.EntryDetail(
                    entry_id=entry_map[key],
                    account_id=account_map[a_code],
                    debit=row.DEBE or Decimal('0.00'),
                    credit=row.HABER or Decimal('0.00')
                )
                db.add(db_detail)
                detail_count += 1
                if detail_count % 1000 == 0:
                    print(f"  Processed {detail_count} details...")
            else:
                missing_headers += 1
        
        db.commit()
        print(f"  Successfully synced {detail_count} details. (Skipped {missing_headers} unlinked records)")

        print("Migration completed successfully with 5-level hierarchy!")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync()
