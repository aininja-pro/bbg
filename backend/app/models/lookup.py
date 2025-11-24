"""Lookup table models for TradeNet Members, Suppliers, and Programs & Products."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class TradeNetMember(Base):
    """TradeNet Members lookup table."""

    __tablename__ = "lookup_members"

    id = Column(Integer, primary_key=True, index=True)
    tradenet_company_id = Column(String(100), nullable=False, index=True)
    bbg_member_id = Column(String(100), nullable=True, index=True)  # Can be empty in CSV
    member_name = Column(String(255), nullable=False, index=True)  # Used by data_enricher.py
    territory_manager = Column(String(255), nullable=True, index=True)  # Territory Manager name
    member_status = Column(String(50), nullable=True)  # Member Status (Tier 1, Tier 2, etc.)
    active_flag = Column(Integer, nullable=True)  # Company Active Flag: 0 or 1
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TradeNetMember(id={self.id}, name={self.member_name})>"


class Supplier(Base):
    """TradeNet Suppliers lookup table."""

    __tablename__ = "lookup_suppliers"

    id = Column(Integer, primary_key=True, index=True)
    tradenet_supplier_id = Column(String(100), nullable=False, index=True, unique=True)
    bbg_id = Column(String(100), nullable=True, index=True)  # Buying Group ID - can be empty in CSV
    supplier_name = Column(String(255), nullable=False, index=True)  # Used by data_enricher.py
    active_flag = Column(Integer, nullable=True)  # Company Active Flag: 0 or 1
    contact_info = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Supplier(id={self.id}, name={self.supplier_name})>"


class ProgramProduct(Base):
    """Programs & Products lookup table."""

    __tablename__ = "lookup_products"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(String(100), nullable=False, index=True)
    program_name = Column(String(255), nullable=False)
    product_id = Column(String(100), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    proof_point = Column(String(255), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProgramProduct(id={self.id}, product={self.product_name})>"
