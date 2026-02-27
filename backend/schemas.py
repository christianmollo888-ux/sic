from pydantic import BaseModel
import datetime
from datetime import date
from typing import List, Optional
from decimal import Decimal

# Detail Schemas
class EntryDetailBase(BaseModel):
    account_id: int
    debit: Decimal = Decimal('0.00')
    credit: Decimal = Decimal('0.00')

class EntryDetailCreate(EntryDetailBase):
    pass

class EntryDetail(EntryDetailBase):
    id: int
    entry_id: int

    class Config:
        from_attributes = True

# Account Schemas
class AccountBase(BaseModel):
    code: str
    name: str
    parent_code: Optional[str] = None
    level: Optional[int] = None
    clv: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    
    class Config:
        from_attributes = True

# Journal Entry Schemas
class JournalEntryBase(BaseModel):
    entry_code: Optional[str] = None
    date: date
    description: Optional[str] = None
    entry_type: Optional[str] = None
    entry_number: Optional[int] = None

class JournalEntryCreate(JournalEntryBase):
    details: List[EntryDetailCreate]

class JournalEntry(JournalEntryBase):
    id: int
    details: List[EntryDetail]

    class Config:
        from_attributes = True

class PaginatedJournalEntries(BaseModel):
    items: List[JournalEntry]
    total: int
# Form Schemas
class TaxpayerBase(BaseModel):
    nit: str
    business_name: str

class TaxpayerCreate(TaxpayerBase):
    pass

class Taxpayer(TaxpayerBase):
    id: int
    
    class Config:
        from_attributes = True

class FormVersionBase(BaseModel):
    form_code: str
    version_number: str
    effective_from: date
    is_active: bool = True

class FormVersion(FormVersionBase):
    id: int

    class Config:
        from_attributes = True

class DeclarationValueBase(BaseModel):
    field_code: str # Auxiliary for input
    value: Decimal

class DeclarationValue(BaseModel):
    id: int
    declaration_id: int
    field_definition_id: int
    value: Decimal

    class Config:
        from_attributes = True

class DeclarationBase(BaseModel):
    taxpayer_nit: str # Auxiliary for creation
    taxpayer_name: Optional[str] = None # Auxiliary for creation
    form_code: str # Auxiliary for creation
    version_number: str # Auxiliary for creation
    month: int
    year: int
    status: str = "Procesado"
    transaction_number: Optional[str] = None
    
    # Audit fields
    presentation_date: Optional[datetime.datetime] = None
    print_date: Optional[datetime.datetime] = None
    pdf_user: Optional[str] = None

class DeclarationCreate(DeclarationBase):
    values: List[DeclarationValueBase]

class Declaration(BaseModel):
    id: int
    taxpayer_id: int
    version_id: int
    month: int
    year: int
    submission_date: datetime.datetime
    status: str
    transaction_number: Optional[str] = None
    presentation_date: Optional[datetime.datetime] = None
    print_date: Optional[datetime.datetime] = None
    pdf_user: Optional[str] = None

    class Config:
        from_attributes = True

class DeclarationSummary(BaseModel):
    id: int
    taxpayer_name: str
    taxpayer_nit: str
    form_code: str
    version_number: str
    month: int
    year: int
    submission_date: datetime.datetime
    status: str
    transaction_number: Optional[str] = None
    presentation_date: Optional[datetime.datetime] = None
    pdf_user: Optional[str] = None

    class Config:
        from_attributes = True

class PaginatedDeclarations(BaseModel):
    items: List[DeclarationSummary]
    total: int

class TaxAuditReportRow(BaseModel):
    field_code: str
    label: str
    rubric: str
    months: List[Optional[Decimal]] # 12 values
    total: Decimal

class TaxAuditReport(BaseModel):
    taxpayer_nit: str
    taxpayer_name: str
    year: int
    rows: List[TaxAuditReportRow]
    presentation_dates: List[Optional[datetime.datetime]] # 12 values
    transaction_numbers: List[Optional[str]] # 12 values
