# Export Converter (Phase 2)

## Overview

The Export Converter is Phase 2 of the BBG Rebate Processing Tool. It takes the merged CSV files generated from Phase 1 (Import Converter) and splits them into distributable Excel reports organized by supplier or territory manager.

## What It Does

The Export Converter processes merged rebate CSV files and generates:

- **Mode 1 - Supplier Reports**: One Excel file per supplier (~49 files) with product tabs
- **Mode 2 - Territory Manager Reports**: One Excel file per territory manager (~20 files) with supplier tabs
- All files are packaged into a single ZIP file for easy download

## Accessing the Export Converter

1. Open the BBG Rebate Processing Tool
2. Click on the **"Export Converter"** tab at the top
3. Click on the **"Reports"** sub-tab

## Mode 1: Supplier Reports

### What It Creates

For each unique supplier in your data, Mode 1 generates a single Excel file containing:

**AllData Tab**: All transactions for that supplier across all products
**Product Tabs**: Individual tabs for each product ID (e.g., "5268", "5532", "5611")

### Excel Structure

- **Tabs**: 1 "AllData" tab + 1 tab per product
- **Columns** (16 total):
  - supplier_name, address_type, address, closing_date
  - product_id, product, quantity, total_rebates
  - member_name, pp_dist_subcontractor, pp_prod_purchase
  - year, quarter, state
  - Plus 2 empty columns

### Data Sorting

Within each tab, data is sorted by:
1. Member Name (alphabetical)
2. State
3. City
4. ZIP code

### Tab Ordering

Product tabs appear in ascending numeric order (5268, 5467, 5532, etc.)

### Use Case

Use Mode 1 to distribute reports to suppliers showing all their rebate activity organized by product.

---

## Mode 2: Territory Manager Reports

### What It Creates

For each territory manager, Mode 2 generates a single Excel file containing:

**All Data Tab**: All transactions for that TM across all suppliers
**Supplier Tabs**: Individual tabs for each supplier (e.g., "Air Vent", "BeaconQXO", "Boise")

### Excel Structure

- **Tabs**: 1 "All Data" tab + 1 tab per supplier
- **Columns** (16 total):
  - supplier_name, address_type, address, closing_date, category
  - product_id, product, quantity, bbg_member_id, member_name, tm
  - pp_dist_subcontractor, pp_prod_purchase, year, quarter, state

### Data Sorting

Within each tab, data is sorted by:
1. Member Name (alphabetical)
2. State
3. City
4. ZIP code

### Tab Ordering

Supplier tabs appear in alphabetical order (A-Z)

### Unassigned Members

Members without a territory manager assignment are grouped into a special "TM_Unassigned.xlsx" file.

### Use Case

Use Mode 2 to distribute reports to territory managers showing all activity for their assigned members.

---

## Step-by-Step Instructions

### Step 1: Upload Your Merged CSV

1. Navigate to **Export Converter → Reports**
2. Click or drag & drop your merged CSV file(s) from Phase 1
3. The file upload area supports:
   - Click to browse
   - Drag and drop
   - Multiple files at once

**Supported File Format**: CSV files only

### Step 2: Select Report Mode

Choose one of the two distribution modes:

**Supplier Reports**
- One Excel per supplier with product tabs
- Best for distributor/supplier distribution

**Territory Manager Reports**
- One Excel per TM with supplier tabs
- Best for internal team review

### Step 3: Generate Reports

1. Click the **"Generate Reports"** button
2. Watch the progress bar showing:
   - "Saving uploaded files..." (0%)
   - "Merging CSV files..." (5%)
   - "Analyzing data... (X rows)" (10%)
   - "Starting report generation..." (15%)
   - "X of Y suppliers/TMs" (15-100%)

**Processing Time**: 15-30 seconds for ~80,000 rows

### Step 4: Download ZIP File

1. When processing completes, a green "Reports Ready!" message appears
2. Review the summary:
   - Total rows processed
   - ZIP file size
3. Click **"Download ZIP"** button
4. Wait 5-7 seconds for download to prepare (button shows "Downloading...")
5. Browser will download the ZIP file automatically

### Step 5: Extract and Distribute

1. Extract the ZIP file on your computer
2. You'll find 40-50 Excel files (depending on mode)
3. Distribute the files to suppliers or territory managers

---

## Excel File Features

All generated Excel files include:

### Professional Formatting
- **Frozen header row** - Headers stay visible when scrolling
- **Bold, centered headers** - Easy to identify columns
- **Auto-sized columns** - Columns automatically fit content
- **Proper number formatting** - No Excel warning triangles

### Tab Organization
- **AllData/All Data tab**: Complete dataset
- **Individual tabs**: Filtered subsets by product or supplier
- **31-character limit**: Tab names auto-truncated if needed
- **Invalid characters removed**: Safe tab names (no \/*?[]:)

---

## Prerequisites

### Territory Manager Data Required (Mode 2 Only)

Before using Mode 2, ensure you've uploaded the **Tradenet - Members.csv** file with Territory Manager assignments:

1. Go to **Import Converter → Lookup Tables → Members**
2. Click **"Bulk Upload CSV"**
3. Upload your Tradenet - Members.csv file
4. Verify the "Territory Manager" column is populated

**CSV Must Include**:
- "Buying Group ID" (joins to bbg_member_id in rebate data)
- "Territory Manager" (column 10)

### Input CSV Format

Your input CSV should be the **merged rebate data** from Phase 1 containing:

**Required Columns**:
- supplier_name
- product_id
- member_name
- bbg_member_id (for Mode 2 TM lookup)
- address, city, state, zip_postal (for sorting)
- All other transaction fields

---

## Tips and Best Practices

### File Naming

ZIP files are automatically named:
- Mode 1: `mode1_distribution_{job_id}.zip`
- Mode 2: `mode2_distribution_{job_id}.zip`

### Caching

Generated reports are cached for **24 hours**:
- You can re-download the same ZIP without re-processing
- After 24 hours, the cache expires and you'll need to regenerate

### Multiple Files

You can upload multiple CSV files at once:
- The tool will merge them before processing
- Use this for combining data from different batches or time periods

### Reset Button

Click **"Reset"** to:
- Clear uploaded files
- Start fresh with a new job
- Upload different files

---

## Troubleshooting

### "No Territory Manager data" Error

**Problem**: Mode 2 shows all transactions as "Unassigned"

**Solution**: Upload Tradenet - Members.csv with Territory Manager column in the Lookup Tables section first.

### "DataFrame must have 'supplier_name' column" Error

**Problem**: You uploaded the wrong file type

**Solution**: Upload the merged CSV from Phase 1, not a lookup table CSV.

### Download Takes 5-7 Seconds

**Normal Behavior**: Large ZIP files (10-15 MB) require time to:
- Decode from database storage
- Transfer over network
- Prepare browser download

The "Downloading..." indicator shows the system is working.

### Processing Takes 15-30 Seconds

**Normal Behavior**: The tool is:
- Merging CSV files
- Analyzing 80,000+ rows
- Generating 40-50 Excel files with formatting
- Packaging into ZIP

Progress updates keep you informed throughout.

---

## Technical Details

### Data Volume

Typical processing metrics:
- **Input**: 80,000-100,000 transaction rows
- **Output**: 40-50 Excel files
- **ZIP Size**: 10-15 MB
- **Processing Time**: 15-30 seconds

### Excel Limits

- Max rows per sheet: 1,048,576
- Max sheet name length: 31 characters
- Max columns: 16,384 (we use 16)

If a supplier or TM exceeds limits, the system logs a warning.

---

## API Endpoints (For Developers)

### POST /api/distribution/process
Submit CSV files for distribution processing

**Parameters**:
- `files`: List of CSV files
- `mode`: "mode1" or "mode2"

**Returns**: `{ job_id, status: "processing" }`

### GET /api/distribution/status/{job_id}
Check processing progress

**Returns**: `{ status, progress, progress_message, total_rows, file_size_bytes }`

### GET /api/download/{job_id}
Download generated ZIP file

**Returns**: ZIP file (application/zip)

---

## Comparison: Mode 1 vs Mode 2

| Feature | Mode 1: Supplier Reports | Mode 2: TM Reports |
|---------|-------------------------|-------------------|
| **Files Generated** | ~49 (one per supplier) | ~20 (one per TM) |
| **Excel Tabs** | AllData + Product tabs | All Data + Supplier tabs |
| **Columns** | 16 (includes total_rebates) | 16 (includes tm, bbg_member_id, category) |
| **Tab Ordering** | Products in numeric order | Suppliers alphabetical (A-Z) |
| **Data Sorting** | Member → State → City → ZIP | Member → State → City → ZIP |
| **Use Case** | Supplier distribution | Internal TM review |
| **Prerequisites** | None | TM data in lookup tables |

---

## Support

For questions or issues:
- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [FAQ](faq.md)
- Contact your IT administrator

---

*Last Updated: November 2025 - Phase 2 Launch*
