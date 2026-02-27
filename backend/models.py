from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False) # Legacy CODIGO
    name = Column(String, nullable=False) # Legacy NOMBRE
    parent_code = Column(String, index=True, nullable=True) # For hierarchy
    level = Column(Integer, nullable=True) # 1 to 5
    clv = Column(String, nullable=True) # 'S' or 'T'
    
    details = relationship("EntryDetail", back_populates="account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_code = Column(String, index=True, nullable=True) # Legacy COD_ASIENT (might be empty)
    date = Column(Date, nullable=False) # Legacy FECHA
    description = Column(Text, nullable=True) # Legacy GLOSA
    entry_type = Column(String, nullable=True) # Legacy TIPO
    entry_number = Column(Integer, nullable=True) # Legacy NUMERO
    
    details = relationship("EntryDetail", back_populates="entry", cascade="all, delete-orphan")

class EntryDetail(Base):
    __tablename__ = "entry_details"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    debit = Column(Numeric(15, 2), default=0) # Legacy DEBE
    credit = Column(Numeric(15, 2), default=0) # Legacy HABER
    
    entry = relationship("JournalEntry", back_populates="details")
    account = relationship("Account", back_populates="details")
