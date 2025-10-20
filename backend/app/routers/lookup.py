"""API endpoints for lookup table management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.lookup import (
    TradeNetMemberRepository,
    SupplierRepository,
    ProgramProductRepository,
)
from app.schemas.lookup import (
    TradeNetMemberCreate,
    TradeNetMemberUpdate,
    TradeNetMemberResponse,
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    ProgramProductCreate,
    ProgramProductUpdate,
    ProgramProductResponse,
    BulkDeleteResponse,
)

router = APIRouter(prefix="/api/lookups", tags=["Lookups"])


# TradeNet Members Endpoints
@router.get("/members", response_model=List[TradeNetMemberResponse])
async def get_members(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all TradeNet members."""
    members = await TradeNetMemberRepository.get_all(db, skip, limit)
    return members


@router.get("/members/{member_id}", response_model=TradeNetMemberResponse)
async def get_member(
    member_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific TradeNet member by ID."""
    member = await TradeNetMemberRepository.get_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    return member


@router.post("/members", response_model=TradeNetMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    member: TradeNetMemberCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new TradeNet member."""
    new_member = await TradeNetMemberRepository.create(db, member)
    return new_member


@router.put("/members/{member_id}", response_model=TradeNetMemberResponse)
async def update_member(
    member_id: int,
    member: TradeNetMemberUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a TradeNet member."""
    updated_member = await TradeNetMemberRepository.update(db, member_id, member)
    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    return updated_member


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a TradeNet member."""
    deleted = await TradeNetMemberRepository.delete(db, member_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    return None


@router.delete("/members", response_model=BulkDeleteResponse)
async def delete_all_members(db: AsyncSession = Depends(get_db)):
    """Delete all TradeNet members."""
    count = await TradeNetMemberRepository.delete_all(db)
    return BulkDeleteResponse(
        deleted_count=count,
        message=f"Successfully deleted {count} members"
    )


# Suppliers Endpoints
@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all suppliers."""
    suppliers = await SupplierRepository.get_all(db, skip, limit)
    return suppliers


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific supplier by ID."""
    supplier = await SupplierRepository.get_by_id(db, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with ID {supplier_id} not found"
        )
    return supplier


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier: SupplierCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new supplier."""
    new_supplier = await SupplierRepository.create(db, supplier)
    return new_supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a supplier."""
    updated_supplier = await SupplierRepository.update(db, supplier_id, supplier)
    if not updated_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with ID {supplier_id} not found"
        )
    return updated_supplier


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a supplier."""
    deleted = await SupplierRepository.delete(db, supplier_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with ID {supplier_id} not found"
        )
    return None


@router.delete("/suppliers", response_model=BulkDeleteResponse)
async def delete_all_suppliers(db: AsyncSession = Depends(get_db)):
    """Delete all suppliers."""
    count = await SupplierRepository.delete_all(db)
    return BulkDeleteResponse(
        deleted_count=count,
        message=f"Successfully deleted {count} suppliers"
    )


# Programs & Products Endpoints
@router.get("/products", response_model=List[ProgramProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all programs & products."""
    products = await ProgramProductRepository.get_all(db, skip, limit)
    return products


@router.get("/products/{product_id}", response_model=ProgramProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific program & product by ID."""
    product = await ProgramProductRepository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product


@router.post("/products", response_model=ProgramProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProgramProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new program & product."""
    new_product = await ProgramProductRepository.create(db, product)
    return new_product


@router.put("/products/{product_id}", response_model=ProgramProductResponse)
async def update_product(
    product_id: int,
    product: ProgramProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a program & product."""
    updated_product = await ProgramProductRepository.update(db, product_id, product)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return updated_product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a program & product."""
    deleted = await ProgramProductRepository.delete(db, product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return None


@router.delete("/products", response_model=BulkDeleteResponse)
async def delete_all_products(db: AsyncSession = Depends(get_db)):
    """Delete all programs & products."""
    count = await ProgramProductRepository.delete_all(db)
    return BulkDeleteResponse(
        deleted_count=count,
        message=f"Successfully deleted {count} products"
    )
