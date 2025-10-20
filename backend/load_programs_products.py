"""Load Programs & Products from the Excel file into database."""
import asyncio
import openpyxl
from datetime import datetime

from app.database import AsyncSessionLocal, init_db
from app.models.lookup import ProgramProduct


async def load_programs_products():
    """Load Programs & Products from Excel file."""
    print("🌱 Loading Programs & Products from Excel file...")

    # Initialize database
    await init_db()

    file_path = "/Users/richardrierson/Downloads/Reviewed & Approved New Tradition Homes Q3 25 Usage Reporting Sheet - Jen (1).xlsm"
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb["Programs-Products"]

    products = []

    # Read from row 2 onwards (row 1 is headers)
    for row in sheet.iter_rows(min_row=2, values_only=True):
        program = row[0]  # Program name
        product_id = row[1]  # Product ID
        product_name = row[2]  # Product Name
        proof_point = row[3] if len(row) > 3 else None  # Proof Point

        # Skip empty rows
        if not product_id or not product_name:
            continue

        product = ProgramProduct(
            program_id=str(program) if program else "Unknown",
            program_name=str(program) if program else "Unknown",
            product_id=str(int(product_id)) if isinstance(product_id, (int, float)) else str(product_id),
            product_name=str(product_name),
            proof_point=str(proof_point) if proof_point else None,
            last_updated=datetime.utcnow()
        )
        products.append(product)

    wb.close()

    async with AsyncSessionLocal() as db:
        try:
            print(f"💾 Inserting {len(products)} products into database...")
            db.add_all(products)
            await db.commit()

            print(f"\n✅ Successfully loaded:")
            print(f"   - {len(products)} Programs & Products")
            print("\n🎉 Programs-Products loading complete!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error loading data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(load_programs_products())
