"""API endpoints for lookup table management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import csv
import io
from datetime import datetime

from app.database import get_db
from app.models.rule import Rule
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
    BulkUploadResponse,
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


# Bulk Upload Endpoints
@router.post("/members/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_members(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk upload TradeNet members from CSV file.
    This will DELETE all existing members and replace with the uploaded data.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )

    try:
        # Read CSV file
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))

        # Collect all members from CSV
        members = []
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Map CSV columns to simple schema
                # Use "Company Name" if available, otherwise "Full Company Name"
                member_name = row.get('Company Name', '').strip() or row.get('Full Company Name', '').strip()

                # Get Territory Manager from CSV (column 10)
                territory_manager = row.get('Territory Manager', '').strip() or None

                # Get Member Status from CSV (column 7)
                member_status = row.get('Member Status', '').strip() or None

                # Get Company Active Flag from CSV (column 11)
                active_flag_str = row.get('Company Active Flag', '').strip()
                active_flag = int(active_flag_str) if active_flag_str else None

                member_data = TradeNetMemberCreate(
                    tradenet_company_id=row.get('TradeNet Company ID', '').strip(),
                    bbg_member_id=row.get('Buying Group ID', '').strip() or None,
                    member_name=member_name,
                    territory_manager=territory_manager,
                    member_status=member_status,
                    active_flag=active_flag,
                )
                members.append(member_data)
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV parsing errors: {'; '.join(errors[:5])}"
            )

        # Delete all existing members
        await TradeNetMemberRepository.delete_all(db)

        # Create new members
        created_count = 0
        for member in members:
            await TradeNetMemberRepository.create(db, member)
            created_count += 1

        return BulkUploadResponse(
            created_count=created_count,
            message=f"Successfully uploaded {created_count} members (full replace)",
            errors=[]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )


@router.post("/suppliers/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_suppliers(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk upload suppliers from CSV file.
    This will DELETE all existing suppliers and replace with the uploaded data.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )

    try:
        # Read CSV file
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))

        # Collect all suppliers from CSV
        suppliers = []
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Map CSV columns to simple schema
                # Use "Company Name" if available, otherwise "Full Company Name"
                supplier_name = row.get('Company Name', '').strip() or row.get('Full Company Name', '').strip()

                # Parse active_flag as integer (0 or 1)
                active_flag_str = row.get('Company Active Flag', '').strip()
                active_flag = int(active_flag_str) if active_flag_str else None

                supplier_data = SupplierCreate(
                    tradenet_supplier_id=row.get('TradeNet Company ID', '').strip(),
                    bbg_id=row.get('Buying Group ID', '').strip() or None,
                    supplier_name=supplier_name,
                    active_flag=active_flag,
                    contact_info=row.get('Website', '').strip() or None,  # Store website in contact_info
                )
                suppliers.append(supplier_data)
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV parsing errors: {'; '.join(errors[:5])}"
            )

        # Delete all existing suppliers
        await SupplierRepository.delete_all(db)

        # Create new suppliers
        created_count = 0
        for supplier in suppliers:
            await SupplierRepository.create(db, supplier)
            created_count += 1

        return BulkUploadResponse(
            created_count=created_count,
            message=f"Successfully uploaded {created_count} suppliers (full replace)",
            errors=[]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )


@router.post("/seed-rules")
async def seed_default_rules(db: AsyncSession = Depends(get_db)):
    """Seed the default production rules. Only seeds if rules table is empty."""
    try:
        # Check if rules already exist
        result = await db.execute(select(Rule))
        existing_rules = result.scalars().all()

        if existing_rules:
            return {"message": f"Rules already exist ({len(existing_rules)} rules) - skipping seed"}

        # Production rules
        rules = [
            Rule(name="Day & Night is Carrier", rule_type="supplier_override", priority=1, enabled=True,
                 config={"condition": {"supplier_name_equals": "Day & Night Heating & Cooling"}, "set_supplier": "Carrier"},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Rule(name="Product 5534 → Air Vent", rule_type="supplier_override", priority=2, enabled=True,
                 config={"condition": {"product_id_contains": "5534"}, "set_supplier": "Air Vent"},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Rule(name="Product 5531 → CertainTeed", rule_type="supplier_override", priority=3, enabled=True,
                 config={"condition": {"product_id_contains": "5531"}, "set_supplier": "CertainTeed"},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Rule(name="Product 5406 → Air Vent", rule_type="supplier_override", priority=4, enabled=True,
                 config={"condition": {"product_id_contains": "5406"}, "set_supplier": "Air Vent"},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Rule(name="Product 5407 → CertainTeed", rule_type="supplier_override", priority=5, enabled=True,
                 config={"condition": {"product_id_contains": "5407"}, "set_supplier": "CertainTeed"},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Rule(name="Product 5255 → Heatilator", rule_type="supplier_override", priority=6, enabled=True,
                 config={"condition": {"product_id_contains": "5255"}, "set_supplier": "Heatilator (Hearth & Home)"},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Rule(name="Product 5270 → Leading Edge", rule_type="supplier_override", priority=7, enabled=True,
                 config={"condition": {"product_id_contains": "5270"}, "set_supplier": "Leading Edge"},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Rule(name="Product 5350 → Leading Edge", rule_type="supplier_override", priority=8, enabled=True,
                 config={"condition": {"product_id_contains": "5350"}, "set_supplier": "Leading Edge"},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Rule(name="Quadplex Rule", rule_type="if_then_else", priority=9, enabled=True,
                 config={"condition": {"logic": "AND", "rules": [{"field": "address_type", "operator": "contains", "value": "QuadPlex"}]},
                        "then_action": {"field": "address_type", "value": "MULTI_UNIT"}},
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        ]

        db.add_all(rules)
        await db.commit()

        return {"message": f"Successfully seeded {len(rules)} default rules"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
