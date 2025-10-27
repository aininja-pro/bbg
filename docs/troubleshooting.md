# Troubleshooting Guide

Common errors, solutions, and how to resolve issues with the BBG Rebate Processing Tool.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Upload Errors](#upload-errors)
- [Processing Errors](#processing-errors)
- [Data Quality Issues](#data-quality-issues)
- [Lookup Table Errors](#lookup-table-errors)
- [Rules Engine Issues](#rules-engine-issues)
- [Download Problems](#download-problems)
- [Browser Issues](#browser-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

---

## Quick Diagnostics

Before diving into specific errors, try these quick checks:

### Basic Checks

✅ **Is the tool loading?** Refresh the page
✅ **Are you using a supported browser?** Chrome, Edge, or Firefox
✅ **Is your internet connection stable?** Check network
✅ **Is the file format correct?** Must be .xlsm or .xlsx
✅ **Is the file size reasonable?** Under 50MB

### Common Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Page won't load | Refresh browser (Ctrl+R or Cmd+R) |
| Upload area frozen | Refresh page and try again |
| Download didn't start | Check downloads folder, try again |
| Preview looks wrong | Scroll left/right in the table |
| Button not working | Wait a few seconds, don't click multiple times |

---

## Upload Errors

### Error: "File format not supported"

**Message:**
```
File format not supported. Please upload .xlsm or .xlsx files only.
```

**Cause:**
- File is not an Excel file
- File has wrong extension (.xls, .csv, .pdf, etc.)

**Solutions:**
1. Check the file extension - must be `.xlsm` or `.xlsx`
2. If file is old format (.xls), open in Excel and save as .xlsm
3. Make sure you're not uploading a PDF or CSV by mistake

---

### Error: "File size too large"

**Message:**
```
File size exceeds maximum limit of 50MB
```

**Cause:**
- File is larger than 50MB
- File contains embedded images or excess formatting

**Solutions:**
1. Check actual file size in file properties
2. Open file in Excel and remove unused sheets
3. Remove embedded images or charts
4. Save as a new file to reduce size
5. Contact IT if file legitimately needs to be larger

---

### Error: "Failed to upload file"

**Message:**
```
Failed to upload file. Please try again.
```

**Cause:**
- Network connection interrupted
- Server temporarily unavailable
- Browser blocked the upload

**Solutions:**
1. Check your internet connection
2. Refresh the page and try again
3. Try a different browser
4. Clear browser cache and cookies
5. Contact IT if problem persists

---

### Error: "Batch size exceeds limit"

**Message:**
```
Maximum batch size is 50 files. You selected 75 files. Please reduce the number of files.
```

**Cause:**
- Selected more than 50 files in batch mode

**Solutions:**
1. Select 50 or fewer files
2. Process files in multiple batches
3. Prioritize most important files first

---

## Processing Errors

### Error: "Required sheet missing: Usage-Reporting"

**Message:**
```
Required sheet 'Usage-Reporting' not found in the uploaded file
```

**Cause:**
- Excel file doesn't have a "Usage-Reporting" sheet
- Sheet is named differently (typo, extra spaces)

**Solutions:**
1. Open file in Excel
2. Check sheet names at the bottom
3. Verify "Usage-Reporting" sheet exists
4. Check for typos or extra spaces in sheet name
5. If named differently, rename sheet to exactly "Usage-Reporting"

---

### Error: "Required sheet missing: Programs-Products"

**Message:**
```
Required sheet 'Programs-Products' not found in the uploaded file
```

**Cause:**
- Excel file doesn't have a "Programs-Products" sheet
- Sheet is named differently

**Solutions:**
1. Open file in Excel
2. Check sheet names at the bottom
3. Verify "Programs-Products" sheet exists
4. Check for typos in sheet name
5. If named differently, rename sheet to exactly "Programs-Products"

---

### Error: "Member not found"

**Message:**
```
Member 'ABC Builders' not found in Members directory
```

**Cause:**
- OLD format file where member name in B7 isn't in the Members lookup table
- Member name has typo or different spelling

**Solutions:**
1. Check spelling of member name in cell B7
2. Go to Lookup Tables → Members
3. Search for the member
4. If missing, add the member with correct BBG Member ID
5. Try processing again

**Related:** See [Lookup Management Guide](lookup-management.md) for adding members.

---

### Error: "Invalid file structure"

**Message:**
```
File structure does not match expected format
```

**Cause:**
- File is not the standard BBG rebate template
- Template has been modified significantly
- Critical cells are missing or in wrong locations

**Solutions:**
1. Compare file to a known-good template
2. Check that B6 and B7 contain expected data (member info)
3. Verify Usage-Reporting sheet has data starting at Row 9
4. Check Programs-Products sheet has the correct structure
5. Contact the member to resubmit using the correct template

---

### Error: "No active products found"

**Message:**
```
No active products found in Programs-Products sheet
```

**Cause:**
- Row 2 in Programs-Products has no "1" flags
- All products are marked inactive
- Row 2 is blank or missing

**Solutions:**
1. Open file in Excel
2. Go to Programs-Products sheet
3. Check Row 2 - should have "1" for active products
4. Verify at least one product is marked active
5. If all are blank, contact the member for clarification

---

### Error: "Processing failed"

**Message:**
```
Processing failed. Please try again or contact support.
```

**Cause:**
- Generic error during processing
- Data format issue
- Server error

**Solutions:**
1. Refresh the page and try again
2. Check file for unusual data (special characters, formulas, etc.)
3. Try a different file to see if issue is file-specific
4. Check browser console for detailed error (F12 → Console tab)
5. Contact IT with the error details and file name

---

## Data Quality Issues

### Issue: Member ID is wrong

**Problem:**
Preview shows incorrect BBG Member ID

**Causes:**
- OLD format file, member name lookup found wrong match
- Member name has slight spelling difference in lookup table
- Multiple members with similar names

**Solutions:**
1. Check cell B7 in Excel for exact member name
2. Go to Lookup Tables → Members
3. Search for the member
4. Verify spelling matches exactly
5. Update member name in lookup table if needed
6. For NEW format, check cell B6 has correct ID

---

### Issue: Supplier names are wrong

**Problem:**
Supplier names in preview don't match expected values

**Causes:**
- Supplier not in lookup table
- Business rule not configured
- Business rule disabled
- Rule priority issue

**Solutions:**
1. Check what supplier name is in the Excel file (Programs-Products sheet)
2. Go to Lookup Tables → Suppliers and verify supplier exists
3. Go to Rules Engine and check if a rule should apply
4. Verify the rule is Enabled (green toggle)
5. Check rule priority order
6. Test by enabling/disabling rules to see effect

**Related:** See [Rules Engine Guide](rules-engine.md) for rule management.

---

### Issue: Missing supplier IDs

**Problem:**
tradenet_supplier_id column is blank or says "Not Found"

**Causes:**
- Supplier name doesn't match any entry in Suppliers lookup table
- Supplier was misspelled in Programs-Products sheet
- Supplier not yet added to lookup table

**Solutions:**
1. Note which supplier is missing
2. Go to Lookup Tables → Suppliers
3. Search for the supplier name (exact match required)
4. If not found, add the supplier with correct TradeNet Supplier ID
5. Process file again

**Temporary Workaround:**
- Download the CSV anyway
- Manually add supplier IDs in Excel before importing to TradeNet

---

### Issue: Dates formatted incorrectly

**Problem:**
confirmed_occupancy dates look wrong

**Expected Format:** `7/2/25` (M/D/YY)

**Solutions:**
This should be automatic. If dates are wrong:
1. Check the Excel file - dates should be in Excel date format
2. Make sure cells in confirmed_occupancy column are formatted as dates
3. If showing as numbers (like 45678), convert to date in Excel first
4. Contact IT if dates still wrong after processing

---

### Issue: Quantities have decimals

**Problem:**
quantity column shows decimal points (10.0, 5.0)

**Expected:** Whole numbers only (10, 5)

**Solutions:**
This should be automatic. If decimals remain:
1. The tool should strip decimals automatically
2. If you see decimals in the preview, it may be a display issue
3. Download the CSV and check - decimals should be removed
4. Contact IT if decimals persist in downloaded CSV

---

### Issue: Rows are missing

**Problem:**
Preview shows fewer rows than expected

**Causes:**
- Empty rows in Excel (skipped automatically)
- Rows with "HideRow" in quantity (filtered out)
- Data doesn't meet criteria

**Solutions:**
1. Check the Excel file - how many non-empty data rows exist?
2. Look for rows with "HideRow" in quantity column (these are excluded)
3. Verify confirmed_occupancy dates are present (empty dates may be skipped)
4. Check total_rows count in preview matches your expectations
5. If still wrong, contact IT with file for investigation

---

## Lookup Table Errors

### Error: "Failed to upload CSV"

**Message:**
```
Failed to upload lookup table CSV. Please check file format.
```

**Causes:**
- CSV file has wrong columns
- CSV file has incorrect headers
- File is not actually a CSV (wrong format)

**Solutions:**

**For Members CSV:**
1. Verify first row is exactly: `member_name,bbg_member_id`
2. Check no extra columns exist
3. Verify file is saved as CSV, not Excel
4. Open in Notepad/TextEdit to confirm it's plain text

**For Suppliers CSV:**
1. Verify first row is exactly: `supplier_name,tradenet_supplier_id`
2. Check no extra columns exist
3. Verify file is CSV format
4. Open in Notepad/TextEdit to confirm it's plain text

---

### Error: "Failed to add member/supplier"

**Message:**
```
Failed to add member. Please check required fields.
```

**Causes:**
- Required field is empty
- Field has invalid characters
- Duplicate entry already exists

**Solutions:**
1. Fill in all required fields
2. Remove special characters from names
3. Check if member/supplier already exists (search first)
4. Try again with valid data

---

### Error: "Duplicate entry"

**Message:**
```
A member with this name or ID already exists
```

**Causes:**
- Trying to add member/supplier that already exists
- Name or ID conflicts with existing record

**Solutions:**
1. Search for the member/supplier in the table
2. If found, edit the existing record instead
3. If not found but error persists, the ID might conflict
4. Use a unique ID or name

---

## Rules Engine Issues

### Issue: Rule not applying

**Problem:**
Created a rule but data isn't changing

**Causes:**
- Rule is disabled
- Condition doesn't match data exactly
- Another rule is overriding it

**Solutions:**
1. Check rule toggle is green (Enabled)
2. Verify condition matches data exactly:
   - Check for typos
   - Check for extra spaces
   - Check capitalization
3. Process a file and check preview carefully
4. Temporarily disable other rules to test
5. Check rule priority - higher priority rules override lower ones

---

### Issue: Rule applying incorrectly

**Problem:**
Rule is changing data it shouldn't

**Causes:**
- Condition is too broad
- Using "contains" instead of "equals"
- Multiple rules conflicting

**Solutions:**
1. Make condition more specific
2. Use "equals" for exact matches
3. Add additional AND conditions
4. Check other rules that might also match
5. Adjust rule priority

---

### Issue: Cannot create rule

**Problem:**
Save button doesn't work or form shows error

**Causes:**
- Required fields missing
- Invalid values
- Duplicate priority

**Solutions:**
1. Fill in all required fields (name, priority, condition, action)
2. Check priority number is valid (positive integer)
3. Verify condition values are not empty
4. Verify action field and value are selected
5. Try a different priority number

---

## Download Problems

### Issue: Download didn't start

**Problem:**
Clicked Download CSV but nothing happened

**Causes:**
- Browser blocked the download
- Popup blocker active
- Network interruption

**Solutions:**
1. Check your Downloads folder - it may have downloaded
2. Check browser's download bar (usually at bottom)
3. Look for popup blocker notification
4. Try clicking Download CSV again
5. Try a different browser
6. Check browser settings allow downloads

---

### Issue: Downloaded file is corrupt

**Problem:**
CSV file won't open or shows errors

**Causes:**
- Download interrupted
- File corruption during transfer
- Wrong program trying to open it

**Solutions:**
1. Try opening in a different program:
   - Excel
   - Google Sheets
   - Notepad/TextEdit
2. Re-download the file
3. Process the original file again
4. Check file size - should not be 0 bytes

---

### Issue: ZIP file won't extract

**Problem:**
Cannot extract batch ZIP file

**Causes:**
- ZIP file corrupted
- Extraction software issue
- Insufficient disk space

**Solutions:**
1. Re-download the ZIP file
2. Try different extraction method:
   - Windows: Right-click → Extract All
   - Mac: Double-click
   - Use 7-Zip or WinRAR
3. Check available disk space
4. Try extracting to a different folder

---

## Browser Issues

### Issue: Page won't load

**Problem:**
Blank page or loading spinner forever

**Causes:**
- Server offline
- Network issue
- Browser cache problem

**Solutions:**
1. Check URL is correct
2. Refresh page (Ctrl+R or Cmd+R)
3. Try different browser
4. Clear browser cache:
   - Chrome: Ctrl+Shift+Delete
   - Settings → Privacy → Clear browsing data
5. Contact IT if problem persists

---

### Issue: Buttons not responding

**Problem:**
Clicking buttons does nothing

**Causes:**
- JavaScript error
- Browser compatibility
- Page not fully loaded

**Solutions:**
1. Wait a few seconds - page may still be loading
2. Refresh the page
3. Open browser console (F12) and check for errors
4. Try a different browser (Chrome recommended)
5. Disable browser extensions that might interfere

---

### Issue: Preview table not displaying correctly

**Problem:**
Data table looks broken or garbled

**Causes:**
- Browser zoom level
- CSS not loading
- Screen resolution issue

**Solutions:**
1. Reset browser zoom to 100% (Ctrl+0 or Cmd+0)
2. Refresh the page
3. Try maximizing browser window
4. Scroll horizontally and vertically in the table
5. Try a different browser

---

## Performance Issues

### Issue: Processing is very slow

**Problem:**
File taking much longer than expected to process

**Typical Processing Times:**
- Small files (< 100 rows): 5-10 seconds
- Medium files (100-500 rows): 10-20 seconds
- Large files (500+ rows): 20-30 seconds
- Batch (10 files): 30-60 seconds

**If slower than above:**

**Solutions:**
1. Check internet connection speed
2. Close other programs using bandwidth
3. Process files in smaller batches
4. Try during off-peak hours
5. Contact IT if consistently slow

---

### Issue: Browser freezing

**Problem:**
Browser becomes unresponsive during processing

**Causes:**
- Very large file
- Too many files in batch
- Browser running out of memory

**Solutions:**
1. Wait - large files take time
2. Don't click repeatedly
3. Close other browser tabs
4. Restart browser
5. Process files in smaller batches
6. Try a different computer if available

---

## Getting Help

### Before Contacting Support

Gather this information:
1. **Error message** (exact text)
2. **File name** you were processing
3. **What you were trying to do**
4. **Browser and version** (e.g., Chrome 120)
5. **Screenshot** of the error if possible

### How to Take Screenshot

**Windows:**
- Press `Windows + Shift + S`
- Select area to capture

**Mac:**
- Press `Cmd + Shift + 4`
- Select area to capture

### Check Browser Console

Detailed error information is in the browser console:

1. Press **F12** (or Ctrl+Shift+I / Cmd+Option+I)
2. Click **Console** tab
3. Look for red error messages
4. Take screenshot or copy text
5. Send to IT with your support request

[Screenshot: Browser console showing errors]

### Support Checklist

When contacting support, include:

✅ Description of the problem
✅ What you were doing when it happened
✅ Error message text
✅ File name (if relevant)
✅ Screenshot
✅ Browser console errors (if available)
✅ Steps you've already tried

### Escalation Path

1. **First:** Check this troubleshooting guide
2. **Second:** Check the [FAQ](faq.md)
3. **Third:** Contact your team lead or administrator
4. **Fourth:** Contact IT support
5. **Fifth:** Contact the development team

---

## Error Code Reference

| Error Code | Meaning | Quick Fix |
|------------|---------|-----------|
| 400 | Bad request - file format issue | Check file format and structure |
| 404 | File or resource not found | Refresh page, try again |
| 413 | File too large | Reduce file size or split batch |
| 422 | Validation error | Check file contains required data |
| 500 | Server error | Retry, contact IT if persists |
| 503 | Service unavailable | Server may be down, contact IT |

---

## Common User Mistakes

### Mistake 1: Not waiting for processing to complete

**Issue:** Clicking buttons multiple times or closing page too soon

**Solution:** Wait for the processing indicator to complete. Don't click multiple times.

### Mistake 2: Wrong file format

**Issue:** Uploading .xls, .csv, or .pdf files

**Solution:** Convert to .xlsm or .xlsx first

### Mistake 3: Modified template

**Issue:** Member heavily modified the Excel template

**Solution:** Request resubmission using standard template

### Mistake 4: Disabled rules

**Issue:** Wondering why data isn't changing when rules are disabled

**Solution:** Check Rules Engine - make sure rules are enabled (green)

### Mistake 5: Not updating lookup tables

**Issue:** Processing fails for new members/suppliers not yet added

**Solution:** Keep lookup tables current, add new entries when needed

---

## Preventive Maintenance

To avoid issues:

✅ **Weekly:** Check that lookup tables are current
✅ **Monthly:** Review and test business rules
✅ **Quarterly:** Update lookup tables from TradeNet
✅ **Quarterly:** Test with sample files to ensure everything works
✅ **Before batch:** Test one file first before processing 50

---

## Still Need Help?

If this guide didn't solve your problem:

1. Check the [FAQ](faq.md) for additional questions
2. Review the [User Guide](user-guide.md) for feature instructions
3. Contact your IT administrator with error details
4. Email the development team with screenshots and description

**Remember:** Include as much detail as possible when reporting issues!

---

*Builders Buying Group - Rebate Processing Tool Support*
