"""Repository layer for lookup table database operations."""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lookup import TradeNetMember, Supplier, ProgramProduct
from app.schemas.lookup import (
    TradeNetMemberCreate,
    TradeNetMemberUpdate,
    SupplierCreate,
    SupplierUpdate,
    ProgramProductCreate,
    ProgramProductUpdate,
)


class TradeNetMemberRepository:
    """Repository for TradeNet Member operations."""

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[TradeNetMember]:
        """Get all TradeNet members with pagination."""
        result = await db.execute(
            select(TradeNetMember).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, member_id: int) -> Optional[TradeNetMember]:
        """Get a TradeNet member by ID."""
        result = await db.execute(
            select(TradeNetMember).where(TradeNetMember.id == member_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_bbg_id(db: AsyncSession, bbg_id: str) -> Optional[TradeNetMember]:
        """Get a TradeNet member by BBG member ID."""
        result = await db.execute(
            select(TradeNetMember).where(TradeNetMember.bbg_member_id == bbg_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, member: TradeNetMemberCreate) -> TradeNetMember:
        """Create a new TradeNet member."""
        db_member = TradeNetMember(**member.model_dump())
        db.add(db_member)
        await db.flush()
        await db.refresh(db_member)
        return db_member

    @staticmethod
    async def update(
        db: AsyncSession, member_id: int, member: TradeNetMemberUpdate
    ) -> Optional[TradeNetMember]:
        """Update a TradeNet member."""
        db_member = await TradeNetMemberRepository.get_by_id(db, member_id)
        if not db_member:
            return None

        update_data = member.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_member, field, value)

        await db.flush()
        await db.refresh(db_member)
        return db_member

    @staticmethod
    async def delete(db: AsyncSession, member_id: int) -> bool:
        """Delete a TradeNet member."""
        result = await db.execute(
            delete(TradeNetMember).where(TradeNetMember.id == member_id)
        )
        return result.rowcount > 0

    @staticmethod
    async def delete_all(db: AsyncSession) -> int:
        """Delete all TradeNet members."""
        result = await db.execute(delete(TradeNetMember))
        return result.rowcount


class SupplierRepository:
    """Repository for Supplier operations."""

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get all suppliers with pagination."""
        result = await db.execute(
            select(Supplier).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, supplier_id: int) -> Optional[Supplier]:
        """Get a supplier by ID."""
        result = await db.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, supplier: SupplierCreate) -> Supplier:
        """Create a new supplier."""
        db_supplier = Supplier(**supplier.model_dump())
        db.add(db_supplier)
        await db.flush()
        await db.refresh(db_supplier)
        return db_supplier

    @staticmethod
    async def update(
        db: AsyncSession, supplier_id: int, supplier: SupplierUpdate
    ) -> Optional[Supplier]:
        """Update a supplier."""
        db_supplier = await SupplierRepository.get_by_id(db, supplier_id)
        if not db_supplier:
            return None

        update_data = supplier.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_supplier, field, value)

        await db.flush()
        await db.refresh(db_supplier)
        return db_supplier

    @staticmethod
    async def delete(db: AsyncSession, supplier_id: int) -> bool:
        """Delete a supplier."""
        result = await db.execute(
            delete(Supplier).where(Supplier.id == supplier_id)
        )
        return result.rowcount > 0

    @staticmethod
    async def delete_all(db: AsyncSession) -> int:
        """Delete all suppliers."""
        result = await db.execute(delete(Supplier))
        return result.rowcount


class ProgramProductRepository:
    """Repository for Program & Product operations."""

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ProgramProduct]:
        """Get all programs & products with pagination."""
        result = await db.execute(
            select(ProgramProduct).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, product_id: int) -> Optional[ProgramProduct]:
        """Get a program & product by ID."""
        result = await db.execute(
            select(ProgramProduct).where(ProgramProduct.id == product_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, product: ProgramProductCreate) -> ProgramProduct:
        """Create a new program & product."""
        db_product = ProgramProduct(**product.model_dump())
        db.add(db_product)
        await db.flush()
        await db.refresh(db_product)
        return db_product

    @staticmethod
    async def update(
        db: AsyncSession, product_id: int, product: ProgramProductUpdate
    ) -> Optional[ProgramProduct]:
        """Update a program & product."""
        db_product = await ProgramProductRepository.get_by_id(db, product_id)
        if not db_product:
            return None

        update_data = product.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)

        await db.flush()
        await db.refresh(db_product)
        return db_product

    @staticmethod
    async def delete(db: AsyncSession, product_id: int) -> bool:
        """Delete a program & product."""
        result = await db.execute(
            delete(ProgramProduct).where(ProgramProduct.id == product_id)
        )
        return result.rowcount > 0

    @staticmethod
    async def delete_all(db: AsyncSession) -> int:
        """Delete all programs & products."""
        result = await db.execute(delete(ProgramProduct))
        return result.rowcount
