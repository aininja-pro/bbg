"""Test script for processing actual BBG rebate file."""
import asyncio
from app.services.excel_processor import ExcelProcessor
from app.services.data_transformer import DataTransformer
from app.database import AsyncSessionLocal
from app.services.data_enricher import DataEnricher

async def test_real_file():
    """Test processing with real file."""
    file_path = "/Users/richardrierson/Downloads/Reviewed & Approved New Tradition Homes Q3 25 Usage Reporting Sheet - Jen (1).xlsm"

    print("=" * 60)
    print("Testing BBG Rebate File Processing")
    print("=" * 60)

    # Test Excel Processor
    print("\n1. Opening file and extracting metadata...")
    processor = ExcelProcessor(file_path)
    processor.open_file()
    processor.find_usage_reporting_sheet()

    metadata = processor.extract_metadata()
    print(f"   BBG Member ID: {metadata['bbg_member_id']}")
    print(f"   Member Name: {metadata['member_name']}")

    # Detect header
    print("\n2. Detecting header row...")
    header_row = processor.detect_header_row()
    print(f"   Header found at row: {header_row}")

    # Identify products
    print("\n3. Identifying active products...")
    active_products = processor.identify_active_products(header_row)
    print(f"   Found {len(active_products)} active products:")
    for col_idx, product_id in list(active_products.items())[:5]:
        col_letter = processor.get_column_letter(col_idx)
        print(f"      Column {col_letter} (index {col_idx}): Product {product_id}")

    # Transform data
    print("\n4. Transforming data (unpivoting)...")
    transformer = DataTransformer()
    df = transformer.transform(
        processor.reformatter_sheet,
        header_row,
        active_products,
        metadata
    )
    print(f"   Transformed to {len(df)} rows")
    print(f"   Columns: {list(df.columns)[:10]}...")

    # Show sample
    print("\n5. Sample transformed data (first 3 rows):")
    for idx, row in df.head(3).iterrows():
        print(f"\n   Row {idx + 1}:")
        print(f"      Member: {row['member_name']} (ID: {row['bbg_member_id']})")
        print(f"      Date: {row['date']}")
        print(f"      Job: {row.get('job_code', 'N/A')}")
        print(f"      Address: {row.get('address1', 'N/A')}, {row.get('city', 'N/A')}")
        print(f"      Product ID: {row['product_id']}")
        print(f"      Quantity: {row['quantity']}")

    # Test enrichment
    print("\n6. Testing data enrichment...")
    async with AsyncSessionLocal() as db:
        enricher = DataEnricher(db)
        df_enriched = await enricher.enrich_all(df)

        print(f"   Enriched {len(df_enriched)} rows")
        print(f"\n   Sample enriched data (first row):")
        first_row = df_enriched.iloc[0]
        print(f"      TradeNet Company ID: {first_row.get('tradenet_company_id', 'N/A')}")
        print(f"      Product Name: {first_row.get('product_name', 'N/A')}")
        print(f"      Proof Point: {first_row.get('proof_point', 'N/A')}")

        # Check warnings
        warnings = enricher.identify_warnings(df_enriched)
        print(f"\n   Data Quality Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"      - {warning['message']}")

    processor.close()

    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_real_file())
