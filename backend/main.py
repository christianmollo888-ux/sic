from fastapi import FastAPI, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy.orm import Session
import models, schemas, crud, reports, models_forms
from database import engine, Base, get_db
from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIC4BUS Accounting API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to SIC4BUS Accounting API", "status": "online"}

# Accounts
@app.get("/accounts/", response_model=List[schemas.Account])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    accounts = crud.get_accounts(db, skip=skip, limit=limit)
    return accounts

@app.post("/accounts/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = crud.get_account_by_code(db, code=account.code)
    if db_account:
        raise HTTPException(status_code=400, detail="Account code already registered")
    return crud.create_account(db=db, account=account)

# Journal Entries
@app.get("/entries/", response_model=schemas.PaginatedJournalEntries)
def read_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entries = crud.get_journal_entries(db, skip=skip, limit=limit)
    total = crud.get_journal_entries_count(db)
    return {"items": entries, "total": total}

@app.post("/entries/", response_model=schemas.JournalEntry)
def create_entry(entry: schemas.JournalEntryCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_journal_entry(db=db, entry=entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/accounts/{account_id}/ledger/")
def read_account_ledger(account_id: int, db: Session = Depends(get_db)):
    return crud.get_account_ledger(db=db, account_id=account_id)

# System Diagnostics
@app.get("/system/tables")
def list_tables():
    return ["CN_PCTAS", "CN_GLOSA", "CN_TRANS", "CN_LCYLV", "accounts", "journal_entries", "entry_details"]

@app.get("/system/tables/{table_name}/data")
def get_table_data(table_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        data = crud.get_raw_table_data(db, table_name, skip, limit)
        return data
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/stats/capacity")
def get_capacity_stats(db: Session = Depends(get_db)):
    return crud.get_table_counts(db)

@app.get("/system/stats/totals")
def get_totals_comparison(db: Session = Depends(get_db)):
    return crud.get_financial_comparison(db)

@app.get("/system/schema")
def get_system_schema(db: Session = Depends(get_db)):
    return {
        "metadata": crud.get_schema_metadata(db),
        "relationships": crud.get_table_relationships()
    }

# Reports
@app.get("/reports/bss")
def get_bss_report(end_date: str, format: str = "pdf", db: Session = Depends(get_db)):
    try:
        from datetime import date
        dt = date.fromisoformat(end_date)
        data = crud.get_bss_report_data(db, dt)
        
        if format == "json":
             return {"data": data}
             
        pdf_bytes = reports.generate_bss_pdf(data, dt.strftime("%d/%m/%Y"))
        
        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=BSS_{end_date}.pdf"
            }
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
@app.get("/reports/comprobante/{entry_id}")
def get_comprobante_report(entry_id: int, db: Session = Depends(get_db)):
    try:
        entry = crud.get_journal_entry(db, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Comprobante not found")
        
        pdf_bytes = reports.generate_comprobante_pdf(entry)
        
        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Comprobante_{entry_id}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/er")
def get_er_report(end_date: str, db: Session = Depends(get_db)):
    try:
        from datetime import date
        dt = date.fromisoformat(end_date)
        data = crud.get_er_report_data(db, dt)
        return {"data": data}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/balance-general")
def get_balance_general_report(start_date: str, end_date: str, format: str = "pdf", db: Session = Depends(get_db)):
    try:
        from datetime import date
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)
        data = crud.get_balance_general_data(db, start_dt, end_dt)

        if format == "json":
            # Convert Decimals to floats for JSON serialization
            def to_float_rows(rows):
                return [{ **r, "balance": float(r["balance"]) } for r in rows]
            return {
                "data": {
                    "activo": to_float_rows(data["activo"]),
                    "pasivo_patrimonio": to_float_rows(data["pasivo_patrimonio"]),
                    "total_activo": float(data["total_activo"]),
                    "total_pasivo_patrimonio": float(data["total_pasivo_patrimonio"]),
                }
            }

        # Build date strings like the PDF model: "1 de Enero de 2025"
        months_es = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        start_str = f"{start_dt.day} de {months_es[start_dt.month-1]} de {start_dt.year}"
        end_str = f"{end_dt.day} de {months_es[end_dt.month-1]} de {end_dt.year}"

        pdf_bytes = reports.generate_balance_general_pdf(data, start_str, end_str)

        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Balance_General_{start_date}_{end_date}.pdf"
            }
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/diario")
def get_diario_report(start_date: str, end_date: str, format: str = "pdf", db: Session = Depends(get_db)):
    try:
        from datetime import date
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)
        
        entries = crud.get_libro_diario_data(db, start_dt, end_dt)
        
        if format == "json":
             # Serialize entries to dict for JSON response
             data = []
             for entry in entries:
                 entry_dict = {
                     "id": entry.id,
                     "date": entry.date.isoformat(),
                     "description": entry.description,
                     "entry_type": entry.entry_type,
                     "entry_number": entry.entry_number,
                     "details": []
                 }
                 for detail in entry.details:
                     entry_dict["details"].append({
                         "account": {
                             "code": detail.account.code,
                             "name": detail.account.name
                         },
                         "debit": float(detail.debit),
                         "credit": float(detail.credit)
                     })
                 data.append(entry_dict)
             return {"data": data}
             
        pdf_bytes = reports.generate_libro_diario_pdf(
            entries, 
            start_dt.strftime("%d/%m/%Y"), 
            end_dt.strftime("%d/%m/%Y")
        )
        
        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Libro_Diario_{start_date}_to_{end_date}.pdf"
            }
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/reports/diario_excel")
def get_diario_excel_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        from datetime import date
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)
        
        entries = crud.get_libro_diario_data(db, start_dt, end_dt)
        
        excel_bytes = reports.generate_libro_diario_excel(
            entries, 
            start_dt.strftime("%d/%m/%Y"), 
            end_dt.strftime("%d/%m/%Y")
        )
        
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=Libro_Diario_{start_date}_to_{end_date}.xlsx"
            }
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def parse_pdf_date(date_str):
    if not date_str:
        return None
    try:
        # Format often: dd/mm/yyyy hh:mm:ss
        return datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
    except:
        try:
             # Try variant without leading zeros or other separators if needed
             return datetime.datetime.strptime(date_str, "%d/%m/%y %H:%M:%S")
        except:
            return None

# Form Processing
@app.post("/forms/process-pdf")
async def process_form_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    import tempfile
    import os
    from utils_pdf import extract_form_200_data
    
    try:
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extract data
        data = extract_form_200_data(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return data
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
@app.get("/forms/taxpayers")
async def get_taxpayers(db: Session = Depends(get_db)):
    taxpayers = db.query(models_forms.Taxpayer).all()
    return [{"nit": t.nit, "name": t.business_name} for t in taxpayers]

@app.post("/forms/declarations", response_model=schemas.Declaration)
async def create_form_declaration(declaration: schemas.DeclarationCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_declaration(db, declaration)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving declaration: {str(e)}")

@app.get("/forms/declarations", response_model=schemas.PaginatedDeclarations)
async def list_form_declarations(
    skip: int = 0, 
    limit: int = 100, 
    taxpayer_nit: Optional[str] = None,
    form_code: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    declarations, total = crud.get_declarations(
        db, skip=skip, limit=limit,
        taxpayer_nit=taxpayer_nit, form_code=form_code,
        month=month, year=year, status=status
    )
    # We need to map to DeclarationSummary which includes taxpayer info
    result = []
    for d in declarations:
        result.append({
            "id": d.id,
            "taxpayer_name": d.taxpayer.business_name,
            "taxpayer_nit": d.taxpayer.nit,
            "form_code": d.version.form_code if d.version else "N/A",
            "version_number": d.version.version_number if d.version else "N/A",
            "month": d.month,
            "year": d.year,
            "submission_date": d.submission_date,
            "status": d.status,
            "transaction_number": d.transaction_number,
            "presentation_date": d.presentation_date,
            "pdf_user": d.pdf_user
        })
    print("DEBUG list_form_declarations - total:", total, "items length:", len(result))
    return {"items": result, "total": total}

@app.delete("/forms/declarations/{declaration_id}")
async def delete_form_declaration(declaration_id: int, db: Session = Depends(get_db)):
    print(f"DEBUG: DELETE request received for declaration_id: {declaration_id}")
    success = crud.delete_declaration(db, declaration_id)
    if not success:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")
    return {"message": "Declaración eliminada correctamente"}

@app.get("/forms/declarations/{id}")
async def get_form_declaration(id: int, db: Session = Depends(get_db)):
    d = crud.get_declaration_details(db, id)
    if not d:
        raise HTTPException(status_code=404, detail="Declaration not found")
    
    # Format field values with labels and rubric
    result_values = []
    for v in d.values:
        result_values.append({
            "field_code": v.field_definition.field_code,
            "label": v.field_definition.label,
            "rubric": v.field_definition.rubric,
            "value": float(v.value)
        })
        
    return {
        "header": {
            "nit": d.taxpayer.nit,
            "business_name": d.taxpayer.business_name,
            "month": d.month,
            "year": d.year,
            "submission_date": d.submission_date.isoformat(),
            "transaction_number": d.transaction_number,
            "presentation_date": d.presentation_date.isoformat() if d.presentation_date else None,
            "print_date": d.print_date.isoformat() if d.print_date else None,
            "pdf_user": d.pdf_user,
            "server_processed_at": d.server_processed_at.isoformat() if d.server_processed_at else None
        },
        "values": result_values
    }

@app.get("/forms/reports/resumen-200/excel")
def get_resumen_200_excel(nit: str, year: int, db: Session = Depends(get_db)):
    report = crud.get_tax_audit_report_data(db, nit, year)
    if not report:
        raise HTTPException(status_code=404, detail="No se encontraron datos")
    
    import reports
    content = reports.generate_resumen_formulario_200_excel(report)
    
    filename = f"Resumen_Formulario_200_{nit}_{year}.xlsx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/forms/reports/tax-audit", response_model=schemas.TaxAuditReport)
def get_tax_audit_report(nit: str, year: int, db: Session = Depends(get_db)):
    report = crud.get_tax_audit_report_data(db, nit, year)
    if not report:
        raise HTTPException(status_code=404, detail="No se encontraron datos para el reporte")
    return report

@app.get("/forms/reports/tax-audit/excel")
def get_tax_audit_report_excel(nit: str, year: int, db: Session = Depends(get_db)):
    report = crud.get_tax_audit_report_data(db, nit, year)
    if not report:
        raise HTTPException(status_code=404, detail="No se encontraron datos")
    
    import reports
    content = reports.generate_tax_audit_excel(report)
    
    filename = f"Auditoria_Tributaria_{nit}_{year}.xlsx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/forms/reports/tax-audit/pdf")
def get_tax_audit_report_pdf(nit: str, year: int, db: Session = Depends(get_db)):
    report = crud.get_tax_audit_report_data(db, nit, year)
    if not report:
        raise HTTPException(status_code=404, detail="No se encontraron datos")
    
    import reports
    content = reports.generate_tax_audit_pdf(report)
    
    filename = f"Auditoria_Tributaria_{nit}_{year}.pdf"
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


