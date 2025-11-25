# BBG Rebate Processing Tool

## Overview

The BBG Rebate Processing Tool is a two-phase internal automation system:

**Phase 1 - Import Converter**: Transform quarterly rebate Excel files into TradeNet-ready CSV files
**Phase 2 - Export Converter**: Split merged CSV data into distributable Excel reports by supplier or territory manager

## What It Does

This tool processes Excel rebate files (.xlsm format) from BBG members and:

- **Validates and extracts** rebate data from quarterly usage reporting sheets
- **Enriches the data** with TradeNet member and supplier information
- **Applies business rules** to map supplier names correctly
- **Generates clean CSV files** formatted exactly to TradeNet's import specifications

## Key Features

### Dual Format Support
The tool automatically detects and processes both OLD and NEW Excel formats:
- **NEW Format**: Member ID is present in cell B6
- **OLD Format**: Member ID is blank in B6, looked up by member name

### Fast Processing
- Single files process in seconds
- Batch mode can process up to 50 files at once
- Outputs either merged CSV or ZIP archive of individual files

### Smart Data Enrichment
- Automatically looks up BBG Member IDs from the TradeNet Members directory
- Maps supplier names to TradeNet Supplier IDs
- Applies configurable business rules for special supplier mappings

### Flexible Output Options
- **Single File Mode**: Process one file, get one CSV
- **Batch Mode - Merged**: Process multiple files, get one combined CSV
- **Batch Mode - ZIP**: Process multiple files, get individual CSVs in a ZIP archive

### Business Rules Engine
Create and manage custom rules to handle special cases:
- Map specific supplier names to correct TradeNet suppliers
- Override supplier mappings based on product IDs
- Enable/disable rules without deleting them
- Rules are applied in priority order

### Lookup Management
Maintain the reference data that powers the tool:
- **Members Directory**: 900+ BBG member companies with their TradeNet IDs
- **Suppliers Directory**: 90+ suppliers with their TradeNet IDs
- Upload new CSV files to replace directories
- Add or edit individual records through the interface

## Who Is This For?

This tool is designed for the **BBG internal team** (3-4 staff members) who process quarterly rebate submissions from member companies. It requires no technical knowledge to use—just upload files and download the results.

## Output Format

The tool generates CSV files with exactly 15 columns matching TradeNet's import specification:

1. member_name
2. bbg_member_id
3. confirmed_occupancy
4. job_code
5. address1
6. city
7. state
8. zip_postal
9. address_type
10. quantity
11. product_id
12. supplier_name
13. tradenet_supplier_id
14. pp_dist_subcontractor
15. tradenet_company_id

## Technology Stack

**For Technical Users:**
- **Frontend**: React, Vite, TailwindCSS (deployed on Render Static Site)
- **Backend**: Python, FastAPI (deployed on Render Web Service)
- **Database**: PostgreSQL on Render (SQLite for local development)
- **Processing**: Python libraries (openpyxl, pandas)

## Documentation

### Phase 1 - Import Converter
- [Getting Started Guide](getting-started.md) - First-time setup and access
- [User Guide](user-guide.md) - Complete instructions for processing files
- [Lookup Management](lookup-management.md) - Managing member and supplier directories
- [Rules Engine](rules-engine.md) - Creating and managing business rules

### Phase 2 - Export Converter
- [Export Converter Guide](export-converter.md) - Generate supplier and TM distribution reports

### General
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions

## Quick Start

### Phase 1 - Import Converter (Process Rebates)
1. Open the tool and go to **Import Converter** tab
2. Click or drag Excel rebate file(s) to upload
3. Click **Process & Preview** to see the results
4. Review the preview data
5. Click **Download CSV** to get your merged file

### Phase 2 - Export Converter (Generate Reports)
1. Go to **Export Converter → Reports** tab
2. Upload the merged CSV from Phase 1
3. Select **Supplier Reports** or **Territory Manager Reports**
4. Click **Generate Reports** and watch progress
5. Click **Download ZIP** when ready
6. Extract and distribute Excel files

For detailed instructions, see the [User Guide](user-guide.md) and [Export Converter Guide](export-converter.md).

## Support

If you encounter issues or need help:
- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [FAQ](faq.md)
- Contact your IT administrator or the development team

---

*Builders Buying Group - Rebate Processing Automation*
