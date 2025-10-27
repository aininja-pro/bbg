# Frequently Asked Questions (FAQ)

Common questions about the BBG Rebate Processing Tool.

## Table of Contents

- [General Questions](#general-questions)
- [File Processing](#file-processing)
- [Data and Output](#data-and-output)
- [Lookup Tables](#lookup-tables)
- [Business Rules](#business-rules)
- [Technical Questions](#technical-questions)
- [TradeNet Import](#tradenet-import)

---

## General Questions

### What is the BBG Rebate Processing Tool?

The BBG Rebate Processing Tool is an internal automation system that converts quarterly rebate Excel files from BBG members into TradeNet-ready CSV files. It reduces processing time from 3 weeks to under 2 minutes.

### Who can use this tool?

This tool is for BBG internal staff (3-4 team members) who process quarterly rebate submissions. No technical knowledge is required.

### Do I need to install anything?

No. The tool runs in your web browser. Just open the URL provided by your IT administrator.

### What browsers are supported?

- Google Chrome (recommended)
- Microsoft Edge
- Firefox

Safari may work but is not officially tested.

### Is my data secure?

Yes. Files are processed on the BBG server and are not stored permanently. After processing and download, cached files are automatically cleaned up.

### Can I use this tool remotely?

If you have access to the tool's URL and are on the BBG network (or VPN), yes. Check with your IT administrator about remote access.

---

## File Processing

### What file formats are supported?

The tool accepts:
- `.xlsm` (Excel Macro-Enabled Workbook) - recommended
- `.xlsx` (Excel Workbook)

Old `.xls` format is not supported. Convert to .xlsm first.

### What is the maximum file size?

50MB per file. Most rebate files are well under this limit (typically 5-10MB).

### How many files can I process at once?

In batch mode, you can process up to 50 files at once.

### How long does processing take?

- **Single file**: 5-30 seconds depending on size
- **Batch (10 files)**: 30-60 seconds
- **Batch (50 files)**: 2-5 minutes

### What's the difference between OLD and NEW format files?

**NEW Format:**
- Cell B6 contains the BBG Member ID
- Most recent member submissions use this format

**OLD Format:**
- Cell B6 is blank
- Member ID is looked up by member name in cell B7
- Legacy files use this format

The tool detects and handles both automatically. You don't need to do anything different.

### Can I process multiple files from different members at once?

Yes! In batch mode, you can upload files from different members. The tool processes each file according to its member information.

### What happens if a file has errors?

The tool will show an error message explaining what's wrong. Common issues:
- Missing required sheets
- Member not found in directory
- Invalid file structure

Fix the issue and try again, or check the [Troubleshooting Guide](troubleshooting.md).

---

## Data and Output

### What output format does the tool produce?

The tool generates CSV (Comma-Separated Values) files with exactly 15 columns formatted for TradeNet import:

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

### How many rows will be in my output?

It depends on the input file. Typical outputs:
- Small members: 100-300 rows
- Large members: 500-1500 rows per file

The tool "unpivots" the wide Excel format into one row per product per job, so the output has many more rows than the input.

### What does "unpivot" mean?

Excel files have products across columns (wide format). TradeNet needs one row per product (long format). The tool converts from wide to long automatically.

**Example:**
- Excel: 1 row with 5 products = 1 row
- CSV: 1 row with 5 products = 5 rows (one per product)

### Why are some supplier IDs missing?

If tradenet_supplier_id shows "Not Found" or is blank:
- The supplier isn't in the Suppliers lookup table
- Add the supplier, then re-process the file

See [Lookup Management](lookup-management.md) for details.

### Can I edit the CSV after downloading?

Yes. You can open the CSV in Excel and make manual edits if needed before importing to TradeNet. However, it's better to fix issues at the source (update lookup tables or rules).

### What is the preview for?

The preview lets you verify the data before downloading:
- Check member name and ID are correct
- Scan through the data for obvious errors
- Verify row count makes sense
- Confirm supplier mappings look right

### Are all rows shown in the preview?

**Single file mode:** Yes, all rows are shown (scrollable table)
**Batch merged mode:** First 200 rows shown; total count is accurate

All data is in the download regardless of preview limitations.

---

## Lookup Tables

### What are lookup tables?

Lookup tables are reference directories:
- **Members Directory**: BBG member names and their TradeNet IDs (~911 members)
- **Suppliers Directory**: Supplier names and their TradeNet IDs (~91 suppliers)

These are used to enrich the data during processing.

### How often should I update lookup tables?

Update lookup tables:
- **Quarterly**: When TradeNet provides updated directories
- **As needed**: When new members join or supplier info changes
- **Before batch processing**: Ensure tables are current

### Can I update just one member or supplier?

Yes. Use the "Add" or "Edit" buttons to update individual records without replacing the entire directory.

### What happens if I upload a new CSV?

Uploading a CSV **replaces all existing records** in that table. Make sure you have a backup of the current data first.

### Where do I get the lookup CSVs?

TradeNet provides updated member and supplier directories periodically. Your administrator should receive these. Keep the most recent versions.

---

## Business Rules

### What are business rules?

Business rules are IF-THEN logic statements that automatically modify data during processing. Example:

```
IF supplier_name equals "Day & Night Heating & Cooling"
THEN set supplier_name to "Carrier"
```

### Why do we need business rules?

Sometimes the supplier name in member files doesn't match what TradeNet expects. Rules automatically fix these discrepancies without manual editing.

### How many rules can I create?

No hard limit, but keep it manageable (typically 10-20 rules). Too many rules become hard to maintain.

### What happens if I disable a rule?

Disabling a rule means it won't be applied during processing, but it's still saved. You can re-enable it later without recreating it.

### What's the difference between disabling and deleting a rule?

- **Disable**: Rule is saved but not applied; can be re-enabled later
- **Delete**: Rule is permanently removed; must be recreated if needed

Disabling is safer if you're unsure whether you'll need the rule again.

### Can rules conflict with each other?

Yes. If two rules both match the same data, the higher priority rule (lower number) wins. Arrange priorities carefully to avoid conflicts.

### How do I test a rule?

1. Create the rule
2. Enable it
3. Process a test file that should trigger the rule
4. Check the preview to see if the rule applied correctly
5. Adjust as needed

### Who should create or edit rules?

Someone familiar with:
- BBG member data
- TradeNet supplier requirements
- Common data quality issues

Typically a designated team member with management approval.

---

## Technical Questions

### Can I process files offline?

No. The tool requires an internet connection to access the server where processing happens.

### Where are files stored?

Files are temporarily stored on the BBG server during processing. After download, cached files are automatically cleaned up. Original files are not permanently stored.

### What if the server goes down?

Contact your IT administrator. They can restart the server or troubleshoot the issue.

### Can I access the tool from home?

Check with your IT administrator about remote access policies. You may need VPN access to reach the tool.

### Is there an API or command-line version?

The tool has a backend API, but it's designed for internal use by the web interface. Contact the development team if you have specific integration needs.

### Can the tool handle other file types besides rebate files?

No. It's specifically designed for BBG quarterly rebate Excel files using the standard template. Other file types will not process correctly.

---

## TradeNet Import

### Is the output really ready for TradeNet?

Yes. The CSV format matches TradeNet's import specification exactly (15 columns in the correct order with proper formatting).

### Do I need to edit the CSV before importing?

Usually no. However, you may want to:
- Review for data quality
- Add any missing supplier IDs manually
- Fix any member-specific issues

### What if TradeNet rejects my import?

Check the TradeNet error message. Common issues:
- Missing supplier IDs (add to lookup table, reprocess)
- Invalid member IDs (update lookup table)
- Date formatting (shouldn't happen, contact IT if it does)

### Can I merge multiple CSVs for one TradeNet import?

Yes. Use batch mode with "Merged CSV" output option. The tool combines all files into one CSV with all rows from all members.

### How do I import the CSV to TradeNet?

Follow your normal TradeNet import procedures. The tool generates the file; TradeNet import is a separate process handled by your team's workflow.

### What if a member resubmits a corrected file?

Simply process the new file. The tool doesn't track file history, so each processing is independent. Use the new output for your TradeNet import.

---

## Batch Processing

### When should I use batch mode?

Use batch mode when you have multiple files to process:
- End of quarter with many member submissions
- Catching up on backlog
- Processing files for the entire quarter at once

### What's the difference between Merged CSV and ZIP output?

**Merged CSV:**
- All files combined into one large CSV
- One import to TradeNet with all data
- Faster import process

**ZIP Archive:**
- Individual CSVs for each file
- Separate imports to TradeNet
- Keeps member data separate

### Can I preview before downloading in ZIP mode?

No. ZIP mode downloads immediately after processing. Use Merged CSV mode if you want to preview before downloading.

### What if one file fails in a batch?

Currently, if any file fails, the entire batch fails. Process files individually to identify and fix problematic files, then reprocess the batch.

### Can I cancel batch processing mid-way?

Refresh the page to cancel, but you'll lose the processing progress. It's better to wait for completion or reduce batch size next time.

---

## Common Scenarios

### Scenario: New member joins BBG

**What to do:**
1. Get member's name and TradeNet ID
2. Go to Lookup Tables → Members
3. Click "Add Member"
4. Fill in name and ID
5. Save

Now you can process files from this member.

### Scenario: Supplier name changes

**What to do:**
1. Update the Suppliers lookup table with new name
2. OR create a business rule to map old name to new name
3. Reprocess any affected files

### Scenario: TradeNet updates their member directory

**What to do:**
1. Get the new CSV from TradeNet
2. Go to Lookup Tables → Members
3. Click "Upload CSV"
4. Select the new file
5. Confirm replace

### Scenario: Need to process 200 files

**What to do:**
Process in batches of 50:
1. Enable Batch Mode
2. Select 50 files
3. Choose output format (Merged or ZIP)
4. Process and download
5. Repeat for next 50 files

### Scenario: Member used wrong template

**What to do:**
1. Try processing - it may still work
2. If it fails, contact the member
3. Request resubmission using correct BBG template
4. Provide them with the standard template if needed

---

## Best Practices

### For Daily Use

✅ Process test file first before batch processing
✅ Review preview before downloading
✅ Keep lookup tables up to date
✅ Verify member files use correct template

### For Maintenance

✅ Update lookup tables quarterly
✅ Review business rules monthly
✅ Test with sample files after making changes
✅ Keep TradeNet CSV backups

### For Troubleshooting

✅ Check error message first
✅ Consult troubleshooting guide
✅ Test with different file to isolate issue
✅ Document unusual cases for team reference

---

## Getting More Help

### Documentation Resources

- [User Guide](user-guide.md) - Complete usage instructions
- [Getting Started](getting-started.md) - First-time setup
- [Lookup Management](lookup-management.md) - Managing directories
- [Rules Engine](rules-engine.md) - Business rules documentation
- [Troubleshooting](troubleshooting.md) - Error solutions

### Still Have Questions?

1. Check if your question is in this FAQ
2. Review the relevant documentation guide
3. Check the troubleshooting guide for errors
4. Contact your team lead or administrator
5. Contact IT support with detailed information

---

## Feature Requests

### Can I request a new feature?

Yes! Contact your administrator or the development team with:
- What feature you need
- Why it would be helpful
- How often you'd use it
- Any examples or details

### Will the tool get updates?

The tool is actively maintained. Updates may include:
- Bug fixes
- New features
- Performance improvements
- Enhanced error handling

Your administrator will notify you of any major updates.

---

## Quick Reference

### Processing Workflow

**Single File:**
1. Upload file → 2. Process & Preview → 3. Review → 4. Download CSV

**Batch Merged:**
1. Enable Batch Mode → 2. Select Merged CSV → 3. Upload files → 4. Process & Preview → 5. Download CSV

**Batch ZIP:**
1. Enable Batch Mode → 2. Select ZIP Archive → 3. Upload files → 4. Process & Download

### When to Update Lookup Tables

| When | Action |
|------|--------|
| New member joins | Add to Members table |
| Member name changes | Edit Members table |
| New supplier added | Add to Suppliers table |
| Quarterly TradeNet update | Upload new CSVs |

### When to Use Business Rules

| Scenario | Rule Type |
|----------|-----------|
| Supplier name doesn't match TradeNet | Supplier name equals rule |
| Specific product always one supplier | Product ID contains rule |
| Special member-specific mapping | Complex rule with AND/OR |

---

**Still have questions?** Contact your IT administrator or check the other documentation guides.

---

*Builders Buying Group - Rebate Processing Tool*
