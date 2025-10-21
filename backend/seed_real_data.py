"""Seed script to populate database with real TradeNet data."""
import asyncio
import csv
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, init_db
from app.models.lookup import TradeNetMember, Supplier


async def load_members(csv_path: str) -> list[TradeNetMember]:
    """Load TradeNet members from CSV file."""
    members = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            member = TradeNetMember(
                tradenet_company_id=row['TradeNet Company ID'],
                bbg_member_id=row['Buying Group ID'],
                member_name=row['Full Company Name'],
                last_updated=datetime.utcnow()
            )
            members.append(member)

    return members


async def load_suppliers(csv_path: str) -> list[Supplier]:
    """Load suppliers from CSV file."""
    suppliers = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip empty TradeNet Company IDs
            if not row['TradeNet Company ID']:
                continue

            supplier = Supplier(
                tradenet_supplier_id=row['TradeNet Company ID'],
                supplier_name=row['Company Name'],  # Use short name (Column D), not Full Company Name
                contact_info=row.get('Website', '') or None,
                last_updated=datetime.utcnow()
            )
            suppliers.append(supplier)

    return suppliers


async def seed_real_data():
    """Populate database with real TradeNet lookup data."""
    print("🌱 Seeding database with real TradeNet data...")

    # Initialize database tables
    await init_db()

    # CSV file paths
    members_csv = "/Users/richardrierson/Downloads/TradeNet - Members (1).csv"
    suppliers_csv = "/Users/richardrierson/Downloads/TradeNet Supplier Directory (1).csv"

    async with AsyncSessionLocal() as db:
        try:
            # Load data from CSV files
            print("📖 Reading CSV files...")
            members = await load_members(members_csv)
            suppliers = await load_suppliers(suppliers_csv)

            print(f"   Found {len(members)} members")
            print(f"   Found {len(suppliers)} suppliers")

            # Add all data to session
            print("💾 Inserting into database...")
            db.add_all(members)
            db.add_all(suppliers)

            # Commit transaction
            await db.commit()

            print(f"\n✅ Successfully seeded:")
            print(f"   - {len(members)} TradeNet Members")
            print(f"   - {len(suppliers)} Suppliers")
            print("\n🎉 Database seeding complete!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_real_data())
