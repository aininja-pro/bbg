"""Seed script to populate database with sample data for testing."""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, init_db
from app.models.lookup import TradeNetMember, Supplier, ProgramProduct


async def seed_data():
    """Populate database with sample lookup data."""
    print("🌱 Seeding database with sample data...")

    # Initialize database tables
    await init_db()

    async with AsyncSessionLocal() as db:
        try:
            # Sample TradeNet Members
            members = [
                TradeNetMember(
                    tradenet_company_id="TN001",
                    bbg_member_id="BBG001",
                    member_name="ABC Construction Co.",
                    last_updated=datetime.utcnow()
                ),
                TradeNetMember(
                    tradenet_company_id="TN002",
                    bbg_member_id="BBG002",
                    member_name="XYZ Builders LLC",
                    last_updated=datetime.utcnow()
                ),
                TradeNetMember(
                    tradenet_company_id="TN003",
                    bbg_member_id="BBG003",
                    member_name="Quality Homes Inc.",
                    last_updated=datetime.utcnow()
                ),
                TradeNetMember(
                    tradenet_company_id="TN004",
                    bbg_member_id="BBG004",
                    member_name="Premium Builders Group",
                    last_updated=datetime.utcnow()
                ),
                TradeNetMember(
                    tradenet_company_id="TN005",
                    bbg_member_id="BBG005",
                    member_name="Sunrise Development",
                    last_updated=datetime.utcnow()
                ),
            ]

            # Sample Suppliers
            suppliers = [
                Supplier(
                    tradenet_supplier_id="SUP001",
                    supplier_name="Home Depot",
                    contact_info="contact@homedepot.com",
                    last_updated=datetime.utcnow()
                ),
                Supplier(
                    tradenet_supplier_id="SUP002",
                    supplier_name="Lowe's",
                    contact_info="info@lowes.com",
                    last_updated=datetime.utcnow()
                ),
                Supplier(
                    tradenet_supplier_id="SUP003",
                    supplier_name="84 Lumber",
                    contact_info="sales@84lumber.com",
                    last_updated=datetime.utcnow()
                ),
                Supplier(
                    tradenet_supplier_id="SUP004",
                    supplier_name="Ferguson Enterprises",
                    contact_info="support@ferguson.com",
                    last_updated=datetime.utcnow()
                ),
                Supplier(
                    tradenet_supplier_id="SUP005",
                    supplier_name="ABC Supply",
                    contact_info="info@abcsupply.com",
                    last_updated=datetime.utcnow()
                ),
            ]

            # Sample Programs & Products
            products = [
                ProgramProduct(
                    program_id="PRG001",
                    program_name="Q1 2025 Rebate Program",
                    product_id="PROD001",
                    product_name="2x4x8 Lumber",
                    proof_point="Receipt Required",
                    last_updated=datetime.utcnow()
                ),
                ProgramProduct(
                    program_id="PRG001",
                    program_name="Q1 2025 Rebate Program",
                    product_id="PROD002",
                    product_name="Roofing Shingles",
                    proof_point="Invoice Required",
                    last_updated=datetime.utcnow()
                ),
                ProgramProduct(
                    program_id="PRG001",
                    program_name="Q1 2025 Rebate Program",
                    product_id="PROD003",
                    product_name="Drywall 4x8",
                    proof_point="Receipt Required",
                    last_updated=datetime.utcnow()
                ),
                ProgramProduct(
                    program_id="PRG002",
                    program_name="Winter Special Program",
                    product_id="PROD004",
                    product_name="Insulation Roll",
                    proof_point="Invoice Required",
                    last_updated=datetime.utcnow()
                ),
                ProgramProduct(
                    program_id="PRG002",
                    program_name="Winter Special Program",
                    product_id="PROD005",
                    product_name="Windows - Double Pane",
                    proof_point="Receipt + Job Number",
                    last_updated=datetime.utcnow()
                ),
                ProgramProduct(
                    program_id="PRG003",
                    program_name="Spring Renovation Program",
                    product_id="PROD006",
                    product_name="Paint - Exterior Grade",
                    proof_point="Receipt Required",
                    last_updated=datetime.utcnow()
                ),
                ProgramProduct(
                    program_id="PRG003",
                    program_name="Spring Renovation Program",
                    product_id="PROD007",
                    product_name="Concrete Mix",
                    proof_point="Invoice Required",
                    last_updated=datetime.utcnow()
                ),
            ]

            # Add all data to session
            db.add_all(members)
            db.add_all(suppliers)
            db.add_all(products)

            # Commit transaction
            await db.commit()

            print(f"✅ Successfully seeded:")
            print(f"   - {len(members)} TradeNet Members")
            print(f"   - {len(suppliers)} Suppliers")
            print(f"   - {len(products)} Programs & Products")
            print("\n🎉 Database seeding complete!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
