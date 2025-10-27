# Lookup Management

This guide explains how to manage the lookup tables that power the BBG Rebate Processing Tool.

## Table of Contents

- [What Are Lookup Tables?](#what-are-lookup-tables)
- [Accessing Lookup Tables](#accessing-lookup-tables)
- [Members Directory](#members-directory)
- [Suppliers Directory](#suppliers-directory)
- [Uploading New Directories](#uploading-new-directories)
- [Adding Individual Records](#adding-individual-records)
- [Editing Records](#editing-records)
- [Deleting Records](#deleting-records)
- [Best Practices](#best-practices)

---

## What Are Lookup Tables?

Lookup tables are reference directories that contain critical information used during file processing:

### Members Directory
**Contains:** BBG member companies and their TradeNet IDs
**Used for:**
- Looking up Member IDs when processing OLD format files
- Validating member information
- Enriching output data with correct TradeNet IDs

**Current size:** ~911 members

### Suppliers Directory
**Contains:** Supplier companies and their TradeNet IDs
**Used for:**
- Mapping supplier names to TradeNet Supplier IDs
- Validating supplier information
- Ensuring correct supplier attribution in output

**Current size:** ~91 suppliers

### Why They Matter

Without accurate lookup tables:
- OLD format files won't process (can't find Member ID)
- Supplier IDs will be missing or incorrect
- TradeNet imports will fail

**Keep these tables up to date!**

---

## Accessing Lookup Tables

### Step 1: Navigate to Lookup Tables Tab
Click the **Lookup Tables** tab at the top of the page.

[Screenshot: Lookup Tables tab in main navigation]

### Step 2: Choose Members or Suppliers
You'll see two sub-tabs:
- **Members** - View and manage the Members directory
- **Suppliers** - View and manage the Suppliers directory

[Screenshot: Members and Suppliers sub-tabs]

---

## Members Directory

### Viewing Members

The Members table displays:
- **Member Name**: Company name (e.g., "Bosgraaf Homes")
- **BBG Member ID**: TradeNet member ID (e.g., "1003")
- **Actions**: Edit and Delete buttons

[Screenshot: Members table with sample data]

### Table Features

**Search:** Type in the search box to filter by name or ID
**Sort:** Click column headers to sort
**Pagination:** Navigate through pages if you have many records

### Members Data Format

Each member record contains:
- `member_name`: Full company name
- `bbg_member_id`: TradeNet member ID (usually 4 digits)

**Example:**
```
member_name: "Bosgraaf Homes"
bbg_member_id: "1003"
```

### When to Update Members

Update the Members directory when:
- A new member joins BBG
- A member's name changes
- A member's TradeNet ID changes
- TradeNet provides an updated member list

---

## Suppliers Directory

### Viewing Suppliers

The Suppliers table displays:
- **Supplier Name**: Company name (e.g., "Carrier")
- **TradeNet Supplier ID**: TradeNet ID (e.g., "5001")
- **Actions**: Edit and Delete buttons

[Screenshot: Suppliers table with sample data]

### Table Features

**Search:** Type in the search box to filter by name or ID
**Sort:** Click column headers to sort
**Pagination:** Navigate through pages if you have many records

### Suppliers Data Format

Each supplier record contains:
- `supplier_name`: Full company name as it appears in TradeNet
- `tradenet_supplier_id`: TradeNet supplier ID

**Example:**
```
supplier_name: "Carrier"
tradenet_supplier_id: "5001"
```

### When to Update Suppliers

Update the Suppliers directory when:
- A new supplier is added to TradeNet
- A supplier's name changes
- A supplier's TradeNet ID changes
- TradeNet provides an updated supplier directory

---

## Uploading New Directories

The fastest way to update lookup tables is to upload a complete CSV file from TradeNet.

### Uploading Members CSV

#### Step 1: Prepare Your CSV
Get the latest Members directory from TradeNet as a CSV file.

**Required CSV format:**
```csv
member_name,bbg_member_id
Bosgraaf Homes,1003
New Tradition Homes,1564
Example Builders,1234
```

**Requirements:**
- First row must be headers: `member_name,bbg_member_id`
- Each subsequent row is one member
- No extra columns (will be ignored)

#### Step 2: Upload
1. Go to **Lookup Tables** → **Members** tab
2. Click the **Upload CSV** button
3. Select your members CSV file
4. Click "Open"

[Screenshot: Upload CSV button]

#### Step 3: Confirm Replace
You'll see a confirmation dialog:

"This will replace all existing members with the contents of this file. Are you sure?"

- Click **Confirm** to proceed
- Click **Cancel** to abort

#### Step 4: Verification
After upload:
- You'll see a success message
- The table will refresh with the new data
- Verify a few records to ensure data loaded correctly

[Screenshot: Success message after upload]

### Uploading Suppliers CSV

Same process as Members, but for suppliers:

**Required CSV format:**
```csv
supplier_name,tradenet_supplier_id
Carrier,5001
CertainTeed,5002
Air Vent,5003
```

**Requirements:**
- First row must be headers: `supplier_name,tradenet_supplier_id`
- Each subsequent row is one supplier

### Upload Safety

**Important Notes:**
- Uploading a CSV **replaces all existing records**
- There is no undo - make sure you have a backup
- Test with a small file first if unsure
- Keep a copy of the current data before replacing

---

## Adding Individual Records

Add a single member or supplier without uploading a full CSV.

### Adding a Member

#### Step 1: Open Add Form
1. Go to **Lookup Tables** → **Members**
2. Click the **Add Member** button

[Screenshot: Add Member button]

#### Step 2: Fill in the Form
Enter the required information:
- **Member Name**: Full company name
- **BBG Member ID**: TradeNet member ID (4-5 digits usually)

[Screenshot: Add Member form]

#### Step 3: Save
1. Click **Save**
2. The new member appears in the table
3. Success message confirms the addition

### Adding a Supplier

Same process as adding a member:

#### Step 1: Open Add Form
1. Go to **Lookup Tables** → **Suppliers**
2. Click the **Add Supplier** button

#### Step 2: Fill in the Form
Enter:
- **Supplier Name**: Full company name as it appears in TradeNet
- **TradeNet Supplier ID**: Supplier ID from TradeNet

#### Step 3: Save
Click **Save** to add the supplier.

### Validation

The form validates:
- Required fields must be filled
- IDs must be valid format
- Names cannot be duplicates (warning shown)

---

## Editing Records

Update an existing member or supplier record.

### Editing a Member

#### Step 1: Find the Record
1. Go to **Lookup Tables** → **Members**
2. Use search or scroll to find the member
3. Click the **Edit** button in that row

[Screenshot: Edit button in member row]

#### Step 2: Update the Form
The edit form appears with current values filled in:
- Modify **Member Name** and/or **BBG Member ID**
- Make your changes

[Screenshot: Edit Member form with existing values]

#### Step 3: Save Changes
1. Click **Save**
2. The table updates with new values
3. Success message confirms the update

### Editing a Supplier

Same process:
1. Go to **Lookup Tables** → **Suppliers**
2. Find the supplier
3. Click **Edit**
4. Update values
5. Click **Save**

### When to Edit

Edit records when:
- A company name changes (merger, rebranding)
- An ID changes in TradeNet
- You discover a typo or error
- TradeNet notifies you of changes

---

## Deleting Records

Remove a member or supplier from the directory.

### Deleting a Member

#### Step 1: Find the Record
1. Go to **Lookup Tables** → **Members**
2. Find the member to delete
3. Click the **Delete** button in that row

[Screenshot: Delete button in member row]

#### Step 2: Confirm Deletion
A confirmation dialog appears:

"Are you sure you want to delete this member?"

- Click **Confirm** to delete
- Click **Cancel** to abort

#### Step 3: Verification
- The record is removed from the table
- Success message confirms deletion

### Deleting a Supplier

Same process:
1. Go to **Lookup Tables** → **Suppliers**
2. Find the supplier
3. Click **Delete**
4. Confirm

### When to Delete

Delete records when:
- A member leaves BBG
- A supplier is no longer used
- Duplicate records exist
- Records are obsolete

**Warning:** Deleting a member may cause OLD format files from that member to fail processing.

---

## Best Practices

### Regular Maintenance

✅ **Update quarterly**: Check for updates from TradeNet each quarter
✅ **Before batch processing**: Ensure directories are current
✅ **After TradeNet changes**: Update immediately if TradeNet notifies you of changes

### Backup Strategy

✅ **Export current data**: Before uploading new CSVs, export the current tables
✅ **Keep TradeNet originals**: Save the original CSV files from TradeNet
✅ **Document changes**: Keep a log of manual edits

### Data Quality

✅ **Consistent naming**: Use exact company names as they appear in TradeNet
✅ **Verify IDs**: Double-check IDs match TradeNet exactly
✅ **Test after changes**: Process a sample file after major updates
✅ **No duplicates**: Check for duplicate entries regularly

### Troubleshooting Lookup Issues

**Problem:** File fails with "Member not found"
**Solution:** Add the member to the Members directory

**Problem:** Supplier ID missing in output
**Solution:** Check if supplier exists in Suppliers directory, add if missing

**Problem:** Wrong supplier ID in output
**Solution:** Edit the supplier record or check business rules

### Access Control

**Who should update lookup tables?**
- Designated staff member(s) with TradeNet access
- Someone who receives TradeNet directory updates
- Authorized by management

**Coordination:**
- Notify team when you update directories
- Keep a change log for reference
- Don't let multiple people update simultaneously

---

## CSV Import Format Reference

### Members CSV Template

```csv
member_name,bbg_member_id
Bosgraaf Homes,1003
New Tradition Homes,1564
ABC Builders,1100
XYZ Construction,1200
```

**Rules:**
- Header row required
- Two columns exactly
- No blank rows
- No extra columns (ignored if present)
- UTF-8 encoding recommended

### Suppliers CSV Template

```csv
supplier_name,tradenet_supplier_id
Carrier,5001
CertainTeed,5002
Air Vent,5003
Heatilator,5004
Leading Edge,5005
```

**Rules:**
- Header row required
- Two columns exactly
- No blank rows
- No extra columns (ignored if present)
- UTF-8 encoding recommended

---

## Quick Reference

### Update Workflow

**Full Directory Update:**
1. Get latest CSV from TradeNet
2. Go to Lookup Tables → [Members/Suppliers]
3. Click **Upload CSV**
4. Select file
5. Confirm replace
6. Verify data loaded

**Single Record Update:**
1. Go to Lookup Tables → [Members/Suppliers]
2. Click **Add** or **Edit**
3. Fill in form
4. Click **Save**
5. Verify in table

### Common Tasks

| Task | Navigation | Action |
|------|------------|--------|
| View members | Lookup Tables → Members | Browse table |
| Add member | Lookup Tables → Members | Click "Add Member" |
| Edit member | Lookup Tables → Members | Click "Edit" button |
| Delete member | Lookup Tables → Members | Click "Delete" button |
| Replace all members | Lookup Tables → Members | Click "Upload CSV" |
| View suppliers | Lookup Tables → Suppliers | Browse table |
| Add supplier | Lookup Tables → Suppliers | Click "Add Supplier" |
| Edit supplier | Lookup Tables → Suppliers | Click "Edit" button |
| Delete supplier | Lookup Tables → Suppliers | Click "Delete" button |
| Replace all suppliers | Lookup Tables → Suppliers | Click "Upload CSV" |

---

## Next Steps

- Learn about the [Rules Engine](rules-engine.md) to understand how business rules interact with lookup tables
- Review the [User Guide](user-guide.md) to see how lookup tables are used during processing
- Check [Troubleshooting](troubleshooting.md) for lookup-related errors

---

**Questions?** Contact your IT administrator or the development team.
