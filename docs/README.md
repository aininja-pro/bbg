# BBG Rebate Processing Tool

## Overview

The BBG Rebate Processing Tool is an internal automation system designed to transform quarterly rebate Excel files into TradeNet-ready CSV files. What previously took 3 weeks of manual processing now takes under 2 minutes.

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
- **Frontend**: React, Vite, TailwindCSS
- **Backend**: Python, FastAPI
- **Database**: SQLite (members, suppliers, business rules)
- **Processing**: Python libraries (openpyxl, pandas)

## Documentation

- [Getting Started Guide](getting-started.md) - First-time setup and access
- [User Guide](user-guide.md) - Complete instructions for processing files
- [Lookup Management](lookup-management.md) - Managing member and supplier directories
- [Rules Engine](rules-engine.md) - Creating and managing business rules
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions

## Quick Start

1. Open the tool in your web browser (URL provided by IT)
2. Click or drag an Excel file to upload
3. Click **Process & Preview** to see the results
4. Review the preview data
5. Click **Download CSV** to get your file
6. Import the CSV into TradeNet

That's it! For detailed instructions, see the [User Guide](user-guide.md).

## Support

If you encounter issues or need help:
- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [FAQ](faq.md)
- Contact your IT administrator or the development team

---

*Builders Buying Group - Rebate Processing Automation*
