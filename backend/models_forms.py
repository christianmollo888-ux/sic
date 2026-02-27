from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Taxpayer(Base):
    __tablename__ = "taxpayers"
    id = Column(Integer, primary_key=True, index=True)
    nit = Column(String, unique=True, index=True, nullable=False)
    business_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    declarations = relationship("Declaration", back_populates="taxpayer")
    types = relationship("TaxpayerType", secondary="taxpayer_type_links")

class TaxpayerType(Base):
    __tablename__ = "taxpayer_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False) # e.g., "Exportador", "GRACO"
    description = Column(Text)

class TaxpayerTypeLink(Base):
    __tablename__ = "taxpayer_type_links"
    taxpayer_id = Column(Integer, ForeignKey("taxpayers.id"), primary_key=True)
    taxpayer_type_id = Column(Integer, ForeignKey("taxpayer_types.id"), primary_key=True)

class FormVersion(Base):
    __tablename__ = "form_versions"
    id = Column(Integer, primary_key=True, index=True)
    form_code = Column(String, nullable=False) # "200"
    version_number = Column(String, nullable=False) # "6"
    effective_from = Column(Date)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    fields = relationship("FormFieldDefinition", back_populates="version")

class FormFieldDefinition(Base):
    __tablename__ = "form_field_definitions"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("form_versions.id"))
    rubric = Column(String) # "Rubro 1"
    field_code = Column(String) # "Casilla 13"
    label = Column(String)
    is_calculated = Column(Boolean, default=False)
    formula = Column(String, nullable=True) # e.g. "C13 * 0.13"

    version = relationship("FormVersion", back_populates="fields")

class Declaration(Base):
    __tablename__ = "declarations"
    id = Column(Integer, primary_key=True, index=True)
    taxpayer_id = Column(Integer, ForeignKey("taxpayers.id"))
    version_id = Column(Integer, ForeignKey("form_versions.id"))
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    submission_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String)
    transaction_number = Column(String)
    original_declaration_id = Column(Integer, ForeignKey("declarations.id"), nullable=True)
    
    # Audit fields
    presentation_date = Column(DateTime, nullable=True)
    print_date = Column(DateTime, nullable=True)
    pdf_user = Column(String, nullable=True)
    server_processed_at = Column(DateTime, default=datetime.datetime.utcnow)

    taxpayer = relationship("Taxpayer", back_populates="declarations")
    version = relationship("FormVersion")
    values = relationship("DeclarationValue", back_populates="declaration", cascade="all, delete-orphan")

class DeclarationValue(Base):
    __tablename__ = "declaration_values"
    id = Column(Integer, primary_key=True, index=True)
    declaration_id = Column(Integer, ForeignKey("declarations.id"))
    field_definition_id = Column(Integer, ForeignKey("form_field_definitions.id"))
    value = Column(Numeric(15, 2))

    declaration = relationship("Declaration", back_populates="values")
    field_definition = relationship("FormFieldDefinition")
