"""Pydantic schemas for lookup table validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# TradeNet Members Schemas
class TradeNetMemberBase(BaseModel):
    """Base schema for TradeNet Member."""
    tradenet_company_id: str = Field(..., max_length=100)
    bbg_member_id: Optional[str] = Field(None, max_length=100)
    member_name: str = Field(..., max_length=255)
    territory_manager: Optional[str] = Field(None, max_length=255)


class TradeNetMemberCreate(TradeNetMemberBase):
    """Schema for creating a TradeNet Member."""
    pass


class TradeNetMemberUpdate(BaseModel):
    """Schema for updating a TradeNet Member."""
    tradenet_company_id: Optional[str] = Field(None, max_length=100)
    bbg_member_id: Optional[str] = Field(None, max_length=100)
    member_name: Optional[str] = Field(None, max_length=255)
    territory_manager: Optional[str] = Field(None, max_length=255)


class TradeNetMemberResponse(TradeNetMemberBase):
    """Schema for TradeNet Member response."""
    id: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


# Suppliers Schemas
class SupplierBase(BaseModel):
    """Base schema for Supplier."""
    tradenet_supplier_id: str = Field(..., max_length=100)
    bbg_id: Optional[str] = Field(None, max_length=100)
    supplier_name: str = Field(..., max_length=255)
    active_flag: Optional[int] = None
    contact_info: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Schema for creating a Supplier."""
    pass


class SupplierUpdate(BaseModel):
    """Schema for updating a Supplier."""
    tradenet_supplier_id: Optional[str] = Field(None, max_length=100)
    bbg_id: Optional[str] = Field(None, max_length=100)
    supplier_name: Optional[str] = Field(None, max_length=255)
    active_flag: Optional[int] = None
    contact_info: Optional[str] = None


class SupplierResponse(SupplierBase):
    """Schema for Supplier response."""
    id: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


# Programs & Products Schemas
class ProgramProductBase(BaseModel):
    """Base schema for Program & Product."""
    program_id: str = Field(..., max_length=100)
    program_name: str = Field(..., max_length=255)
    product_id: str = Field(..., max_length=100)
    product_name: str = Field(..., max_length=255)
    proof_point: Optional[str] = Field(None, max_length=255)


class ProgramProductCreate(ProgramProductBase):
    """Schema for creating a Program & Product."""
    pass


class ProgramProductUpdate(BaseModel):
    """Schema for updating a Program & Product."""
    program_id: Optional[str] = Field(None, max_length=100)
    program_name: Optional[str] = Field(None, max_length=255)
    product_id: Optional[str] = Field(None, max_length=100)
    product_name: Optional[str] = Field(None, max_length=255)
    proof_point: Optional[str] = Field(None, max_length=255)


class ProgramProductResponse(ProgramProductBase):
    """Schema for Program & Product response."""
    id: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


# Bulk operations
class BulkDeleteResponse(BaseModel):
    """Response for bulk delete operations."""
    deleted_count: int
    message: str


class BulkUploadResponse(BaseModel):
    """Response for bulk upload operations."""
    created_count: int
    message: str
    errors: list[str] = []
