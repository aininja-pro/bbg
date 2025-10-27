# User Guide

Complete instructions for using the BBG Rebate Processing Tool.

## Table of Contents

- [Uploading Files](#uploading-files)
- [Processing Single Files](#processing-single-files)
- [Batch Processing](#batch-processing)
- [Understanding the Preview](#understanding-the-preview)
- [Downloading Results](#downloading-results)
- [File Formats](#file-formats)
- [Data Validation](#data-validation)
- [Warnings vs Errors](#warnings-vs-errors)

---

## Uploading Files

### Supported File Formats

The tool accepts Excel files in these formats:
- `.xlsm` (Excel Macro-Enabled Workbook) - **Recommended**
- `.xlsx` (Excel Workbook)

### File Requirements

Your Excel file must contain:
- A **Usage-Reporting** sheet (the main data tab)
- A **Programs-Products** sheet (product definitions)
- Standard BBG rebate template structure

### Two Upload Methods

#### Method 1: Drag and Drop
1. Locate your Excel file in Windows Explorer or Finder
2. Click and drag the file over the upload area
3. The upload area will highlight when you hover over it
4. Release your mouse to drop the file

[Screenshot: Drag and drop upload area]

#### Method 2: Click to Browse
1. Click anywhere in the upload area
2. A file browser window will open
3. Navigate to your file location
4. Select the file and click "Open"

[Screenshot: File browser dialog]

### Upload Limits

- **Single File Mode**: One file at a time
- **Batch Mode**: Up to 50 files at once
- **File Size**: Maximum 50MB per file

---

## Processing Single Files

### Step-by-Step Instructions

#### 1. Upload Your File
Use either drag-and-drop or click-to-browse to upload one Excel file.

Once uploaded, you'll see the filename displayed below the upload area.

[Screenshot: File selected, showing filename]

#### 2. Click Process & Preview
Click the blue **Process & Preview** button to start processing.

[Screenshot: Process & Preview button]

#### 3. Wait for Processing
You'll see a processing indicator with:
- A spinning animation
- "Processing..." message
- The filename being processed

This typically takes 5-15 seconds depending on file size.

[Screenshot: Processing indicator]

#### 4. Review the Preview
Once complete, you'll see:
- **Member Information**: Name and BBG Member ID
- **Row Count**: Total number of data rows processed
- **Data Table**: Scrollable preview of all rows
- **Download Button**: Ready to download the CSV

[Screenshot: Complete preview with data table]

#### 5. Download the CSV
Click the **Download CSV** button. The file will download with an auto-generated filename:

```
[original_filename]_processed.csv
```

For example:
```
Bosgraaf_Homes_Q4_24_processed.csv
```

#### 6. Success Message
After downloading, you'll see a green success message:

"Processing Complete! Your CSV file has been downloaded successfully. Ready for TradeNet import!"

[Screenshot: Success message]

#### 7. Process Another File
Click **Process Another File** to start over with a new file.

---

## Batch Processing

Process multiple files at once with two output options: Merged CSV or ZIP archive.

### Enabling Batch Mode

1. Check the **Batch Mode** checkbox at the top of the page
2. The interface will update to show batch options

[Screenshot: Batch Mode checkbox enabled]

### Choosing Output Format

When Batch Mode is enabled, you'll see two output options:

#### Option 1: Merged CSV
- **What it does**: Combines all files into one large CSV
- **Best for**: Importing all data at once into TradeNet
- **Preview**: Available before download
- **Output**: Single CSV file with all rows from all files

#### Option 2: ZIP Archive
- **What it does**: Creates individual CSVs, bundled in a ZIP file
- **Best for**: Keeping files separate for individual member processing
- **Preview**: Not available (downloads immediately)
- **Output**: One ZIP file containing multiple CSVs

[Screenshot: Output format radio buttons]

### Selecting Multiple Files

#### Using File Browser
1. Click the upload area
2. Hold **Ctrl** (Windows) or **Cmd** (Mac)
3. Click each file you want to process
4. Click "Open"

#### Using Drag and Drop
1. Select multiple files in Windows Explorer or Finder
2. Drag them all together to the upload area
3. Drop to upload

### File Selection Summary

After selecting files, you'll see:
- Total number of files selected
- List of filenames
- Total combined size

[Screenshot: Multiple files selected, showing list]

### Processing Batch - Merged CSV

1. Ensure **Merged CSV** is selected as the output format
2. Click **Process & Preview [X] Files**
3. Wait for processing (progress indicator shows)
4. Review the preview:
   - Shows combined data from all files
   - First 200 rows displayed
   - Total row count shown
5. Click **Download CSV** to get the merged file

**Merged Filename Format:**
```
Batch_Merged_[X]_files_[timestamp].csv
```

Example:
```
Batch_Merged_15_files_2025-10-27T14-30-45.csv
```

### Processing Batch - ZIP Archive

1. Select **ZIP Archive** as the output format
2. Click **Process & Download [X] Files**
3. Wait for processing
4. The ZIP file downloads automatically (no preview)

**ZIP Filename Format:**
```
Batch_Processed_[X]_files_[timestamp].zip
```

Example:
```
Batch_Processed_15_files_2025-10-27T14-30-45.zip
```

**ZIP Contents:**
Each Excel file becomes a separate CSV inside the ZIP:
```
member_name_1_processed.csv
member_name_2_processed.csv
member_name_3_processed.csv
...
```

### Batch Processing Limits

- **Maximum Files**: 50 files per batch
- If you try to select more, you'll see an error message
- **Tip**: Process large batches in groups of 50

---

## Understanding the Preview

After processing, the preview shows your data in a table format.

### Preview Header Information

At the top of the preview:
- **Member Name**: The BBG member company name
- **BBG Member ID**: The TradeNet member ID (e.g., 1003, 1564)
- **Total Rows**: Number of data rows in the output (e.g., 240, 1380)

[Screenshot: Preview header with member info]

### Data Table

The preview table shows all 15 columns:

| Column | Description |
|--------|-------------|
| member_name | BBG member company name |
| bbg_member_id | TradeNet member ID |
| confirmed_occupancy | Occupancy date (format: M/D/YY) |
| job_code | Job or project identifier |
| address1 | Street address |
| city | City name |
| state | Two-letter state code |
| zip_postal | Zip code (no decimals) |
| address_type | RESIDENTIAL or COMMERCIAL |
| quantity | Quantity of items (no decimals) |
| product_id | TradeNet product ID |
| supplier_name | Supplier company name |
| tradenet_supplier_id | TradeNet supplier ID |
| pp_dist_subcontractor | Subcontractor name |
| tradenet_company_id | TradeNet company ID |

### Scrolling the Preview

- The table is scrollable (up/down and left/right)
- Headers remain visible while scrolling
- All rows are shown (up to 200 rows for batch merged)

[Screenshot: Scrollable data table]

### Preview Limitations

**Single File Mode:**
- Shows all rows from the file

**Batch Merged Mode:**
- Shows first 200 rows only
- Total row count is accurate
- All data is included in the download

---

## Downloading Results

### Single File Download

1. Click **Download CSV** from the preview
2. The file downloads to your default downloads folder
3. Success message appears
4. Preview is cleared

### Batch Merged Download

1. Review the preview
2. Click **Download CSV**
3. Merged CSV file downloads
4. Success message appears

### Batch ZIP Download

- Downloads automatically after processing
- No preview step
- Success message appears

### Downloaded File Locations

Files download to your browser's default download folder:
- **Windows**: Usually `C:\Users\[YourName]\Downloads`
- **Mac**: Usually `/Users/[YourName]/Downloads`

### Opening Downloaded Files

**CSV Files:**
- Can be opened in Excel
- Can be opened in Notepad/TextEdit
- Ready for TradeNet import

**ZIP Files:**
- Right-click and select "Extract All" (Windows)
- Double-click to extract (Mac)
- Contains individual CSV files

---

## File Formats

### OLD Format vs NEW Format

The tool automatically detects which format your file uses:

#### NEW Format (Current)
- **Identifier**: Cell B6 contains the BBG Member ID
- **Processing**: Member ID is read directly from B6
- **Example**: `1564` in cell B6

#### OLD Format (Legacy)
- **Identifier**: Cell B6 is blank
- **Processing**: Member name is read from B7 and looked up in the Members directory
- **Example**: `Bosgraaf Homes` in B7, ID looked up as `1003`

**You don't need to do anything different** - the tool handles both formats automatically.

[Screenshot: Example of OLD vs NEW format detection]

### File Structure

Both formats require:

**Usage-Reporting Sheet:**
- Row 5: Subcontractor names (pp_dist_subcontractor)
- Row 6: Member ID (NEW format only) or blank (OLD format)
- Row 7: Member name
- Row 9: Column headers
- Row 10+: Data rows

**Programs-Products Sheet:**
- Row 2: Active product flags (1 = active)
- Row 7: Product IDs
- Row 8+: Product information including supplier names

---

## Data Validation

### Automatic Validation

The tool automatically validates:

✅ **Member ID or Name**: Must exist in the Members directory
✅ **Product IDs**: Must be present in the Programs-Products sheet
✅ **Supplier Names**: Mapped to TradeNet Supplier IDs
✅ **Dates**: Converted to M/D/YY format
✅ **Numbers**: Converted to integers (no decimals)
✅ **Address Types**: Defaults to RESIDENTIAL if blank

### Data Transformations

The tool applies these transformations:

| Field | Transformation |
|-------|----------------|
| confirmed_occupancy | Excel date → M/D/YY string (e.g., 7/2/25) |
| zip_postal | Remove decimals, keep as string |
| quantity | Convert to integer, remove decimals |
| address_type | Default to "RESIDENTIAL" if empty |
| supplier_name | Apply business rules for overrides |

### Empty Values

Some fields may be empty in your data:
- **allowed empty**: address_type (defaults to RESIDENTIAL)
- **should have values**: Most other fields

If critical fields are missing, you may see warnings in the output.

---

## Warnings vs Errors

### Errors (Red)

**Errors prevent processing and must be fixed:**

- File format not recognized
- Required sheets missing (Usage-Reporting or Programs-Products)
- Member not found in directory (OLD format)
- File corrupted or cannot be read
- Batch size exceeds 50 files

When you see an error:
1. Read the error message carefully
2. Check the [Troubleshooting Guide](troubleshooting.md)
3. Fix the issue and try again

[Screenshot: Error message example]

### Warnings (Yellow)

**Warnings indicate potential issues but don't stop processing:**

- Product ID not found in TradeNet Suppliers
- Supplier name not found (defaults to file's supplier name)
- Unusual data values
- Missing optional fields

When you see a warning:
1. Review the preview data
2. Check if the warning affects your data
3. If data looks correct, proceed with download
4. If data looks wrong, contact your administrator

[Screenshot: Warning message example]

### Success (Green)

**Success messages confirm everything worked:**

- "Processing Complete!"
- "Your CSV file has been downloaded successfully"
- "Ready for TradeNet import!"

[Screenshot: Success message]

---

## Best Practices

### Before Processing

✅ Ensure files are the standard BBG rebate template
✅ Check that files are .xlsm or .xlsx format
✅ Verify file size is under 50MB
✅ Make sure you have the correct quarter's files

### During Processing

✅ Wait for processing to complete (don't close the browser)
✅ Review the preview before downloading
✅ Check member name and ID are correct
✅ Scan through the data table for obvious issues

### After Processing

✅ Open the CSV in Excel to do a quick visual check
✅ Verify row count matches expectations
✅ Check a few rows for data accuracy
✅ Import into TradeNet following normal procedures

### Batch Processing Tips

✅ Group files by quarter for easier tracking
✅ Use Merged CSV when importing all at once
✅ Use ZIP when you need to keep files separate
✅ Process in groups of 50 or less
✅ Keep original Excel files as backups

---

## Quick Reference

### Single File Workflow
1. Upload file
2. Click **Process & Preview**
3. Review preview
4. Click **Download CSV**
5. Import to TradeNet

### Batch Merged Workflow
1. Enable **Batch Mode**
2. Select **Merged CSV**
3. Upload multiple files
4. Click **Process & Preview [X] Files**
5. Review preview
6. Click **Download CSV**
7. Import to TradeNet

### Batch ZIP Workflow
1. Enable **Batch Mode**
2. Select **ZIP Archive**
3. Upload multiple files
4. Click **Process & Download [X] Files**
5. Wait for automatic download
6. Extract ZIP
7. Import CSVs to TradeNet

---

## Next Steps

- Learn about [Lookup Management](lookup-management.md) to maintain member and supplier directories
- Understand the [Rules Engine](rules-engine.md) to manage supplier mapping rules
- Check [Troubleshooting](troubleshooting.md) if you encounter issues
- Review the [FAQ](faq.md) for common questions

---

**Need help?** Contact your IT administrator or check the [Troubleshooting Guide](troubleshooting.md).
