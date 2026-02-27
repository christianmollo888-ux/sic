from sqlalchemy.orm import Session
import models, schemas, models_forms
import datetime
from decimal import Decimal
from datetime import date

# Accounts
def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Account).offset(skip).limit(limit).all()

def get_account_by_code(db: Session, code: str):
    return db.query(models.Account).filter(models.Account.code == code).first()

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

# Journal Entries
def get_journal_entries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.JournalEntry).order_by(models.JournalEntry.date.desc(), models.JournalEntry.id.desc()).offset(skip).limit(limit).all()

def get_journal_entries_count(db: Session):
    return db.query(models.JournalEntry).count()

def get_journal_entry(db: Session, entry_id: int):
    return db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()

def create_journal_entry(db: Session, entry: schemas.JournalEntryCreate):
    # Validation: Sum(Debit) == Sum(Credit)
    total_debit = sum(d.debit for d in entry.details)
    total_credit = sum(d.credit for d in entry.details)
    
    if total_debit != total_credit:
         raise ValueError(f"Entry not balanced: Debit({total_debit}) != Credit({total_credit})")

    db_entry = models.JournalEntry(
        entry_code=entry.entry_code,
        date=entry.date,
        description=entry.description,
        entry_type=entry.entry_type,
        entry_number=entry.entry_number
    )
    db.add(db_entry)
    db.flush() # Get ID
    
    for detail in entry.details:
        db_detail = models.EntryDetail(**detail.dict(), entry_id=db_entry.id)
        db.add(db_detail)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

from sqlalchemy import func

def get_account_ledger(db: Session, account_id: int):
    # Get the target account
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        return None

    # Determine the prefix to identify descendant accounts
    # e.g., '1000000000' -> '1', '1102000000' -> '1102'
    # Special case for L1 (single digit)
    if account.code.endswith('000000000'):
        prefix = account.code[:1]
    elif account.code.endswith('00000000'):
        prefix = account.code[:2]
    elif account.code.endswith('000000'):
        prefix = account.code[:4]
    elif account.code.endswith('0000'):
        prefix = account.code[:6]
    else:
        prefix = account.code

    # Sum debits and credits for the account and ALL its descendants
    totals = db.query(
        func.sum(models.EntryDetail.debit).label("total_debit"),
        func.sum(models.EntryDetail.credit).label("total_credit")
    ).join(
        models.Account, 
        models.EntryDetail.account_id == models.Account.id
    ).filter(
        models.Account.code.like(f"{prefix}%")
    ).first()
    
    debit = totals.total_debit or Decimal('0.00')
    credit = totals.total_credit or Decimal('0.00')
    balance = debit - credit
    
    return {
        "account_id": account_id,
        "code": account.code,
        "name": account.name,
        "total_debit": debit,
        "total_credit": credit,
        "balance": balance
    }

def get_bss_report_data(db: Session, end_date: date):
    # Get all accounts
    accounts = db.query(models.Account).order_by(models.Account.code).all()
    
    # Get direct totals per account up to end_date
    direct_totals_query = db.query(
        models.EntryDetail.account_id,
        func.sum(models.EntryDetail.debit).label("debit"),
        func.sum(models.EntryDetail.credit).label("credit")
    ).join(
        models.JournalEntry, models.EntryDetail.entry_id == models.JournalEntry.id
    ).filter(
        models.JournalEntry.date <= end_date
    ).group_by(
        models.EntryDetail.account_id
    ).all()
    
    direct_totals = {row.account_id: (row.debit or Decimal('0.00'), row.credit or Decimal('0.00')) for row in direct_totals_query}
    
    report_data = []
    
    for acc in accounts:
        # Determine prefix for hierarchy summation
        if acc.code.endswith('000000000'):
            prefix = acc.code[:1]
        elif acc.code.endswith('00000000'):
            prefix = acc.code[:2]
        elif acc.code.endswith('000000'):
            prefix = acc.code[:4]
        elif acc.code.endswith('0000'):
            prefix = acc.code[:6]
        else:
            prefix = acc.code
            
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        # Aggregate recursively in memory
        for other_acc in accounts:
            if other_acc.code.startswith(prefix):
                d, c = direct_totals.get(other_acc.id, (Decimal('0.00'), Decimal('0.00')))
                total_debit += d
                total_credit += c
        
        # Calculate Debit/Credit and Deudor/Acreedor
        if total_debit > total_credit:
            deudor = total_debit - total_credit
            acreedor = Decimal('0.00')
        else:
            deudor = Decimal('0.00')
            acreedor = total_credit - total_debit
            
        report_data.append({
            "code": acc.code,
            "name": acc.name,
            "debit": total_debit,
            "credit": total_credit,
            "deudor": deudor,
            "acreedor": acreedor,
            "level": acc.level
        })
        
    return report_data

def get_balance_general_data(db: Session, start_date: date, end_date: date):
    """
    Genera los datos del Balance General siguiendo la estructura del reporte oficial:
    - CUENTAS DE ACTIVO (prefijo 1): saldo = débito - crédito
    - CUENTAS DE PASIVO Y PATRIMONIO (prefijo 2 y 3): saldo = crédito - débito
    Solo muestra cuentas con saldo != 0.
    """
    # Get all accounts for activo, pasivo, patrimonio
    accounts = db.query(models.Account).filter(
        models.Account.code.startswith('1') |
        models.Account.code.startswith('2') |
        models.Account.code.startswith('3')
    ).order_by(models.Account.code).all()

    # Get direct totals per account up to end_date
    direct_totals_query = db.query(
        models.EntryDetail.account_id,
        func.sum(models.EntryDetail.debit).label("debit"),
        func.sum(models.EntryDetail.credit).label("credit")
    ).join(
        models.JournalEntry, models.EntryDetail.entry_id == models.JournalEntry.id
    ).filter(
        models.JournalEntry.date <= end_date
    ).group_by(
        models.EntryDetail.account_id
    ).all()

    direct_totals = {row.account_id: (row.debit or Decimal('0.00'), row.credit or Decimal('0.00')) for row in direct_totals_query}

    def get_prefix(acc):
        code = acc.code
        if code.endswith('000000000'):
            return code[:1]
        elif code.endswith('00000000'):
            return code[:2]
        elif code.endswith('000000'):
            return code[:4]
        elif code.endswith('0000'):
            return code[:6]
        else:
            return code

    activo_rows = []
    pasivo_patrimonio_rows = []
    total_activo = Decimal('0.00')
    total_pasivo_patrimonio = Decimal('0.00')

    for acc in accounts:
        prefix = get_prefix(acc)

        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')

        for other_acc in accounts:
            if other_acc.code.startswith(prefix):
                d, c = direct_totals.get(other_acc.id, (Decimal('0.00'), Decimal('0.00')))
                total_debit += d
                total_credit += c

        if acc.code.startswith('1'):
            # Activo: saldo deudor = debit - credit
            balance = total_debit - total_credit
            row = {
                "code": acc.code,
                "name": acc.name,
                "balance": balance,
                "level": acc.level
            }
            activo_rows.append(row)
            if acc.level == 1:
                total_activo = balance
        else:
            # Pasivo y Patrimonio: saldo acreedor = credit - debit
            balance = total_credit - total_debit
            row = {
                "code": acc.code,
                "name": acc.name,
                "balance": balance,
                "level": acc.level
            }
            pasivo_patrimonio_rows.append(row)
            if acc.code.startswith('2') and acc.level == 1:
                total_pasivo_patrimonio += balance
            elif acc.code.startswith('3') and acc.level == 1:
                total_pasivo_patrimonio += balance

    # In a proper balance sheet, ACTIVO = PASIVO + PATRIMONIO.
    # Due to timing differences in year-end closing entries in the DB,
    # we use total_activo as the authoritative combined total for Pasivo+Patrimonio.
    return {
        "activo": activo_rows,
        "pasivo_patrimonio": pasivo_patrimonio_rows,
        "total_activo": total_activo,
        "total_pasivo_patrimonio": total_activo,  # Must equal total_activo (A = P + Pat)
    }

def get_er_report_data(db: Session, end_date: date):
    # Get income and expense accounts (starting with 4, 5, or 6)
    accounts = db.query(models.Account).filter(
        (models.Account.code.startswith('4')) |
        (models.Account.code.startswith('5')) |
        (models.Account.code.startswith('6'))
    ).order_by(models.Account.code).all()
    
    # Get direct totals per account up to end_date
    direct_totals_query = db.query(
        models.EntryDetail.account_id,
        func.sum(models.EntryDetail.debit).label("debit"),
        func.sum(models.EntryDetail.credit).label("credit")
    ).join(
        models.JournalEntry, models.EntryDetail.entry_id == models.JournalEntry.id
    ).filter(
        models.JournalEntry.date <= end_date
    ).group_by(
        models.EntryDetail.account_id
    ).all()
    
    direct_totals = {row.account_id: (row.debit or Decimal('0.00'), row.credit or Decimal('0.00')) for row in direct_totals_query}
    
    ingresos = []
    egresos = []
    total_ingresos = Decimal('0.00')
    total_egresos = Decimal('0.00')
    
    for acc in accounts:
        # Determine prefix for hierarchy summation
        if acc.code.endswith('000000000'):
            prefix = acc.code[:1]
        elif acc.code.endswith('00000000'):
            prefix = acc.code[:2]
        elif acc.code.endswith('000000'):
            prefix = acc.code[:4]
        elif acc.code.endswith('0000'):
            prefix = acc.code[:6]
        else:
            prefix = acc.code
            
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        # Aggregate recursively in memory
        for other_acc in accounts:
            if other_acc.code.startswith(prefix):
                d, c = direct_totals.get(other_acc.id, (Decimal('0.00'), Decimal('0.00')))
                total_debit += d
                total_credit += c
        
        # Logic for Balance formatting in ER
        # Income (4): Credit - Debit
        # Expenses (5, 6): Debit - Credit
        if acc.code.startswith('4'):
            balance = total_credit - total_debit
            if acc.level == 1:
                total_ingresos += direct_totals.get(acc.id, (Decimal('0'), Decimal('0')))[1] - direct_totals.get(acc.id, (Decimal('0'), Decimal('0')))[0]
                # Actually, for Level 1, we should accumulate only base level children, but the hierarchical recursive
                # above gives us the total for the entire tree directly when looking at acc.code '400000...'
                total_ingresos = balance
            
            ingresos.append({
                "code": acc.code,
                "name": acc.name,
                "amount": balance,
                "level": acc.level
            })
        else:
            balance = total_debit - total_credit
            if acc.level == 1:
                total_egresos += balance
                
            egresos.append({
                "code": acc.code,
                "name": acc.name,
                "amount": balance,
                "level": acc.level
            })
            
    # Remove rows with 0 amount to clean up report
    ingresos = [i for i in ingresos if i['amount'] != 0 or i['level'] == 1]
    egresos = [e for e in egresos if e['amount'] != 0 or e['level'] == 1]

    resultado_ejercicio = total_ingresos - total_egresos
    
    return {
        "ingresos": ingresos,
        "egresos": egresos,
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "resultado": resultado_ejercicio
    }

def get_libro_diario_data(db: Session, start_date: date, end_date: date):
    # Fetch all journal entries within the date range, ordered by date and id
    entries = db.query(models.JournalEntry).filter(
        models.JournalEntry.date >= start_date,
        models.JournalEntry.date <= end_date
    ).order_by(models.JournalEntry.date, models.JournalEntry.id).all()
    
    return entries

from sqlalchemy import text, func

def get_raw_table_data(db: Session, table_name: str, skip: int = 0, limit: int = 100):
    # Security check: ensure table_name is allowed
    allowed_tables = ['CN_PCTAS', 'CN_GLOSA', 'CN_TRANS', 'CN_LCYLV', 'accounts', 'journal_entries', 'entry_details']
    if table_name not in allowed_tables:
        raise ValueError("Unauthorized table access")
    
    # Use double quotes for legacy tables which are case-sensitive/uppercase in Postgres
    query_table = f'"{table_name}"' if table_name.startswith("CN_") else table_name
    
    query = text(f"SELECT * FROM {query_table} OFFSET :skip LIMIT :limit")
    result = db.execute(query, {"skip": skip, "limit": limit})
    
    # Convert to list of dicts
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result]

def get_table_counts(db: Session):
    tables = ['CN_PCTAS', 'CN_GLOSA', 'CN_TRANS', 'CN_LCYLV', 'accounts', 'journal_entries', 'entry_details']
    stats = {}
    for table in tables:
        query_table = f'"{table}"' if table.startswith("CN_") else table
        count = db.execute(text(f"SELECT COUNT(*) FROM {query_table}")).scalar()
        stats[table] = count
    return stats

def get_financial_comparison(db: Session):
    # Legacy totals from CN_TRANS
    legacy = db.execute(text('SELECT SUM("DEBE") as total_debit, SUM("HABER") as total_credit FROM "CN_TRANS"')).first()
    
    # Modern totals from entry_details
    modern = db.query(
        func.sum(models.EntryDetail.debit).label("total_debit"),
        func.sum(models.EntryDetail.credit).label("total_credit")
    ).first()
    
    return {
        "legacy": {
            "debit": legacy.total_debit or Decimal('0.00'),
            "credit": legacy.total_credit or Decimal('0.00'),
        },
        "modern": {
            "debit": modern.total_debit or Decimal('0.00'),
            "credit": modern.total_credit or Decimal('0.00'),
        },
        "difference": {
            "debit": (modern.total_debit or 0) - (legacy.total_debit or 0),
            "credit": (modern.total_credit or 0) - (legacy.total_credit or 0),
        }
    }
def get_schema_metadata(db: Session):
    tables = ['CN_PCTAS', 'CN_GLOSA', 'CN_TRANS', 'CN_LCYLV', 'accounts', 'journal_entries', 'entry_details']
    
    table_descriptions = {
        'CN_PCTAS': 'Plan de Cuentas (Legacy). Catálogo principal de cuentas contables del sistema original, estructurado por niveles. Define la jerarquía y tipología (ingreso, egreso, activo, pasivo).',
        'CN_GLOSA': 'Glosas de Asientos (Legacy). Almacena los encabezados de los comprobantes contables (fecha, descripción general, tipo de comprobante).',
        'CN_TRANS': 'Transacciones Contables (Legacy). Tabla de detalle donde se registran los movimientos individuales (débitos y créditos) asociados a un comprobante específico en CN_GLOSA.',
        'CN_LCYLV': 'Apoyo Libreta Cívica/Varios (Legacy). Tabla auxiliar de parámetros y clasificaciones utilizada en el sistema antiguo para referencias secundarias.',
        'accounts': 'Cuentas Contables (Nuevo). Catálogo modernizado del plan de cuentas. Incluye enlaces jerárquicos internos (parent_code) y soporte completo para el nuevo modelo SIC4BUS.',
        'journal_entries': 'Comprobantes/Asientos (Nuevo). Encabezados de los asientos contables registrados en el nuevo sistema SIC4BUS. Contiene la fecha, el código unificado y la justificación o glosa.',
        'entry_details': 'Detalle de Asientos (Nuevo). Líneas de movimiento individuales de cada asiento contable. Registra qué cuenta recibe el débito o el crédito y se enlaza al asiento principal.'
    }

    schema = {}
    for table in tables:
        # Resolve table name case
        search_table = table if not table.startswith("CN_") else table
        
        query = text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = :table
            ORDER BY ordinal_position
        """)
        result = db.execute(query, {"table": search_table})
        columns = [
            {"column": row.column_name, "type": row.data_type, "nullable": row.is_nullable == "YES"} 
            for row in result
        ]
        
        # If empty (due to case sensitivity in some Postgres setups), try uppercase
        if not columns and table.startswith("CN_"):
             result = db.execute(query, {"table": table.upper()})
             columns = [
                {"column": row.column_name, "type": row.data_type, "nullable": row.is_nullable == "YES"} 
                for row in result
            ]
             
        # Fetch sample data (up to 3 rows)
        sample_data = []
        try:
             query_table = f'"{table}"' if table.startswith("CN_") else table
             sample_query = text(f"SELECT * FROM {query_table} LIMIT 3")
             sample_result = db.execute(sample_query)
             col_names = sample_result.keys()
             
             for row in sample_result:
                 # Process row to handle unsupported formats like dates or decimals natively in JSON serialization later
                 row_dict = {}
                 for k, v in zip(col_names, row):
                     if v is not None:
                         # Cast common types to string for safe JSON serialization in sample data
                         if hasattr(v, 'isoformat'):
                             row_dict[k] = v.isoformat()
                         elif hasattr(v, 'quantize') or isinstance(v, float) or isinstance(v, Decimal):
                             row_dict[k] = str(v)
                         else:
                             row_dict[k] = v
                     else:
                         row_dict[k] = None
                 sample_data.append(row_dict)
        except Exception as e:
             # Failsafe if the table is totally empty or missing
             print(f"Could not fetch sample data for {table}: {e}")
             sample_data = []
             
        schema[table] = {
            "description": table_descriptions.get(table, "Sin descripción disponible."),
            "columns": columns,
            "sample_data": sample_data
        }
             
    return schema

def get_table_relationships():
    return [
        {
            "from": "entry_details.entry_id", 
            "to": "journal_entries.id", 
            "type": "Muchos-a-Uno (Foreign Key)",
            "description": "Cada línea de detalle (entry_details) pertenece obligatoriamente a un único asiento contable o comprobante (journal_entries). Garantiza que no existan movimientos huérfanos."
        },
        {
            "from": "entry_details.account_id", 
            "to": "accounts.id", 
            "type": "Muchos-a-Uno (Foreign Key)",
            "description": "Vincula el movimiento contable específico con la cuenta afectada en el Plan de Cuentas. Permite sumarizar los montos (débitos/créditos) para obtener el saldo de una cuenta."
        },
        {
            "from": "accounts.parent_code", 
            "to": "accounts.code", 
            "type": "Auto-Referencia (Jerarquía)",
            "description": "Estructura de árbol. Conecta una cuenta de nivel inferior (hija) con su cuenta sumadora inmediata (padre). Ejemplo: '1101' depende de '11'. Permite generar balances sumarizados por niveles."
        },
        {
            "from": "CN_TRANS.CODIGO", 
            "to": "CN_PCTAS.CODIGO", 
            "type": "Enlace Legacy (Implícito)",
            "description": "En el sistema antiguo, el código de la transacción se corresponde con el código del Plan de Cuentas legacy. Es una integridad referencial mantenida por la lógica de la aplicación antigua."
        },
        {
            "from": "CN_TRANS (MES/TIPO/NUMERO)", 
            "to": "CN_GLOSA (MES/TIPO/NUMERO)", 
            "type": "Enlace Encabezado-Detalle Legacy",
            "description": "Relación compuesta antigua. Un comprobante (CN_GLOSA) y sus líneas de detalle correspondientes (CN_TRANS) se agrupan utilizando la combinación única de Mes, Tipo de Comprobante y Número de Comprobante."
        },
        {
            "from": "CN_TRANS.COD_LCY", 
            "to": "CN_LCYLV.COD_LCY", 
            "type": "Enlace Soporte Auxiliar Legacy",
            "description": "Conexión a una tabla de catálogos secundarios (apéndices, proyectos, libretas, etc.) usada en registros sumamente específicos del sistema original."
        }
    ]
# Form Persistence
def get_taxpayer_by_nit(db: Session, nit: str):
    return db.query(models_forms.Taxpayer).filter(models_forms.Taxpayer.nit == nit).first()

def create_taxpayer(db: Session, taxpayer: schemas.TaxpayerCreate):
    db_taxpayer = models_forms.Taxpayer(**taxpayer.dict())
    db.add(db_taxpayer)
    db.commit()
    db.refresh(db_taxpayer)
    return db_taxpayer

def create_declaration(db: Session, declaration: schemas.DeclarationCreate):
    # 1. Get or create taxpayer
    taxpayer = get_taxpayer_by_nit(db, declaration.taxpayer_nit)
    if not taxpayer:
        taxpayer = models_forms.Taxpayer(
            nit=declaration.taxpayer_nit,
            business_name=declaration.taxpayer_name or "Contribuyente Nuevo"
        )
        db.add(taxpayer)
        db.flush()

    # 2. Validation: Duplicates
    from sqlalchemy import and_
    existing = db.query(models_forms.Declaration).filter(
        and_(
            models_forms.Declaration.taxpayer_id == taxpayer.id,
            models_forms.Declaration.month == declaration.month,
            models_forms.Declaration.year == declaration.year,
            models_forms.Declaration.version_id.is_not(None)
        )
    ).first()
    
    if existing:
        raise ValueError(f"Ya existe una declaración para el periodo {declaration.month}/{declaration.year} para este NIT.")

    # 3. Validation: Temporal Consistency (Gestión vigente)
    now = datetime.datetime.now()
    if declaration.year > now.year or (declaration.year == now.year and declaration.month >= now.month):
        # Strictly "month completed" means current month is not yet allowed if we are very strict
        # But usually, it means it can't be future. 
        # Let's say: cannot be current month or future if we want "completed months only"
        raise ValueError(f"El periodo {declaration.month}/{declaration.year} no ha concluido o es futuro.")

    # 4. Get form version
    version = db.query(models_forms.FormVersion).filter(
        models_forms.FormVersion.form_code == declaration.form_code,
        models_forms.FormVersion.version_number == declaration.version_number
    ).first()
    
    if not version:
        raise ValueError(f"Form version {declaration.form_code} v{declaration.version_number} not found")

    # 5. Create Declaration
    db_declaration = models_forms.Declaration(
        taxpayer_id=taxpayer.id,
        version_id=version.id,
        month=declaration.month,
        year=declaration.year,
        submission_date=datetime.datetime.utcnow(),
        status=declaration.status,
        transaction_number=declaration.transaction_number,
        presentation_date=declaration.presentation_date,
        print_date=declaration.print_date,
        pdf_user=declaration.pdf_user,
        server_processed_at=datetime.datetime.utcnow()
    )
    db.add(db_declaration)
    db.flush()

    # 6. Create Values
    # We need a mapping of field_code to field_definition_id
    fields = db.query(models_forms.FormFieldDefinition).filter(
        models_forms.FormFieldDefinition.version_id == version.id
    ).all()
    field_map = {f.field_code: f.id for f in fields}

    for val in declaration.values:
        # Try different formats: 'C13', '13', 'Casilla 13'
        clean_code = val.field_code.replace('C','').replace('Casilla ','').strip()
        def_id = field_map.get(val.field_code) or field_map.get(clean_code) or field_map.get(f"Casilla {clean_code}")
        
        if def_id:
            db_val = models_forms.DeclarationValue(
                declaration_id=db_declaration.id,
                field_definition_id=def_id,
                value=val.value
            )
            db.add(db_val)

    db.commit()
    db.refresh(db_declaration)
    return db_declaration

def get_declarations(db: Session, skip: int = 0, limit: int = 100, taxpayer_nit: str = None, form_code: str = None, month: int = None, year: int = None, status: str = None):
    query = db.query(models_forms.Declaration)
    
    if taxpayer_nit:
        query = query.join(models_forms.Taxpayer, models_forms.Declaration.taxpayer_id == models_forms.Taxpayer.id).filter(models_forms.Taxpayer.nit == taxpayer_nit)
    if form_code:
        query = query.join(models_forms.FormVersion, models_forms.Declaration.version_id == models_forms.FormVersion.id).filter(models_forms.FormVersion.form_code == form_code)
    if month is not None:
        query = query.filter(models_forms.Declaration.month == month)
    if year is not None:
        query = query.filter(models_forms.Declaration.year == year)
    if status:
        query = query.filter(models_forms.Declaration.status == status)
        
    total = query.count()
    items = query.order_by(models_forms.Declaration.submission_date.desc()).offset(skip).limit(limit).all()
    return items, total

def get_declaration_details(db: Session, declaration_id: int):
    return db.query(models_forms.Declaration).filter(models_forms.Declaration.id == declaration_id).first()

def delete_declaration(db: Session, declaration_id: int):
    db_declaration = db.query(models_forms.Declaration).filter(models_forms.Declaration.id == declaration_id).first()
    if db_declaration:
        db.delete(db_declaration)
        db.commit()
        return True
    return False

def get_tax_audit_report_data(db: Session, nit: str, year: int):
    # 1. Get taxpayer
    taxpayer = get_taxpayer_by_nit(db, nit)
    if not taxpayer:
        return None

    # 2. Get all declarations for this taxpayer and year
    declarations = db.query(models_forms.Declaration).filter(
        models_forms.Declaration.taxpayer_id == taxpayer.id,
        models_forms.Declaration.year == year
    ).all()

    # 3. Get field definitions
    # For the report we want a standard list based on v6
    v6 = db.query(models_forms.FormVersion).filter_by(form_code="200", version_number="6").first()
    if not v6:
        return None

    field_defs = db.query(models_forms.FormFieldDefinition).filter_by(
        version_id=v6.id
    ).order_by(models_forms.FormFieldDefinition.id).all()

    # 4. Initialize result structure
    report_rows = []
    pres_dates = [None] * 12
    trans_nums = [None] * 12

    # Map month -> declaration
    decl_map = {d.month: d for d in declarations}
    for m in range(1, 13):
        if m in decl_map:
            pres_dates[m-1] = decl_map[m].presentation_date
            trans_nums[m-1] = decl_map[m].transaction_number

    # Pre-fetch all values for efficiency and resilience
    decl_vals_map = {}
    for m in range(1, 13):
        if m in decl_map:
            vals = db.query(models_forms.DeclarationValue).filter(
                models_forms.DeclarationValue.declaration_id == decl_map[m].id
            ).all()
            decl_vals_map[m] = vals

    # 5. Populate rows
    for f_def in field_defs:
        months_values = [Decimal('0.00')] * 12
        total_year = Decimal('0.00')
        target_code = f_def.field_code.replace("C", "").replace("Casilla ", "").strip()
        
        for m in range(1, 13):
            if m in decl_map:
                val_obj = None
                for dv in decl_vals_map[m]:
                    dv_code = dv.field_definition.field_code.replace("C", "").replace("Casilla ", "").strip()
                    if dv_code == target_code:
                        val_obj = dv
                        break
                
                if val_obj:
                    months_values[m-1] = val_obj.value
                    total_year += val_obj.value
        
        report_rows.append(schemas.TaxAuditReportRow(
            field_code=f_def.field_code,
            label=f_def.label,
            rubric=f_def.rubric,
            months=months_values,
            total=total_year
        ))

    # 6. Recalculate mathematical dependencies for F-200 v6
    # Create a map for quick reference
    row_map = {r.field_code: r for r in report_rows}

    def get_val(code, col_index):
        if code not in row_map: return Decimal('0.00')
        if col_index == 12: return row_map[code].total
        return row_map[code].months[col_index]

    def set_val(code, col_index, val):
        if code in row_map:
            # Enforce 2 decimal places rounding
            rounded_val = val.quantize(Decimal('0.00'))
            if col_index == 12:
                row_map[code].total = rounded_val
            else:
                row_map[code].months[col_index] = rounded_val

    # Apply calculations for each month (0-11) and the total column (12)
    for col in range(13):
        # Débito
        c13 = get_val('13', col)
        c16 = get_val('16', col)
        c17 = get_val('17', col)
        c18 = get_val('18', col)
        set_val('39', col, (c13 + c16 + c17 + c18) * Decimal('0.13'))
        
        c39 = get_val('39', col)
        c55 = get_val('55', col)
        c19 = get_val('19', col)
        set_val('1002', col, c39 + c55 + c19)
        
        # Crédito
        c26 = get_val('26', col)
        c27 = get_val('27', col)
        c28 = get_val('28', col)
        set_val('114', col, (c26 + c27 + c28) * Decimal('0.13'))
        
        c114 = get_val('114', col)
        c30 = get_val('30', col)
        c1003 = get_val('1003', col)
        set_val('1004', col, c114 + c30 + c1003)
        
        # Saldos y diferencias
        c1002 = get_val('1002', col)
        c1004 = get_val('1004', col)
        
        d_contrib = c1004 - c1002
        d_fisco = c1002 - c1004
        set_val('693', col, max(Decimal('0.00'), d_contrib))
        set_val('909', col, max(Decimal('0.00'), d_fisco))
        
        c909 = get_val('909', col)
        c635 = get_val('635', col)
        set_val('1001', col, max(Decimal('0.00'), c909 - c635))
        
        c629 = get_val('629', col)
        c622 = get_val('622', col)
        c640 = get_val('640', col)
        set_val('468', col, max(Decimal('0.00'), c629 - c622 - c640))
        
        c468 = get_val('468', col)
        c465 = get_val('465', col)
        c466 = get_val('466', col)
        set_val('996', col, max(Decimal('0.00'), c468 - c465 - c466))

    return schemas.TaxAuditReport(
        taxpayer_nit=taxpayer.nit,
        taxpayer_name=taxpayer.business_name,
        year=year,
        rows=report_rows,
        presentation_dates=pres_dates,
        transaction_numbers=trans_nums
    )
