# Rules Engine

Complete guide to the Business Rules Engine for managing supplier mappings and data transformations.

## Table of Contents

- [What Are Business Rules?](#what-are-business-rules)
- [Why Rules Are Needed](#why-rules-are-needed)
- [How Rules Work](#how-rules-work)
- [Accessing the Rules Engine](#accessing-the-rules-engine)
- [Viewing Rules](#viewing-rules)
- [Rule Types](#rule-types)
- [Creating New Rules](#creating-new-rules)
- [Editing Rules](#editing-rules)
- [Enabling and Disabling Rules](#enabling-and-disabling-rules)
- [Deleting Rules](#deleting-rules)
- [Rule Priority](#rule-priority)
- [Common Rule Examples](#common-rule-examples)
- [Best Practices](#best-practices)

---

## What Are Business Rules?

Business rules are IF-THEN logic statements that automatically modify data during file processing. They allow you to:

- Override supplier names based on conditions
- Map specific products to correct suppliers
- Handle special cases without manual editing
- Apply consistent transformations across all files

**Example Rule:**
```
IF product_id contains "5534"
THEN set supplier_name to "Air Vent"
```

---

## Why Rules Are Needed

### The Problem

Sometimes the supplier name in the Excel file doesn't match what TradeNet expects:

- **File says**: "Day & Night Heating & Cooling"
- **TradeNet expects**: "Carrier"

Or a specific product always belongs to a particular supplier regardless of what the file says:

- **Product 5534 always belongs to**: "Air Vent"

### The Solution

Business rules automatically fix these issues during processing:
- No manual editing of files
- Consistent corrections every time
- Easy to update when rules change
- Maintains data integrity

---

## How Rules Work

### Processing Order

1. **File Upload**: Excel file is uploaded
2. **Data Extraction**: Data is extracted from the file
3. **Rule Application**: Rules are applied in priority order (1, 2, 3...)
4. **Lookup Enrichment**: Supplier IDs are looked up
5. **Output Generation**: Final CSV is created

### Rule Evaluation

Rules are evaluated **in priority order**:
- **Priority 1** runs first
- **Priority 2** runs second
- And so on...

**Important:** Higher priority rules can override lower priority rules!

### Rule Conditions

Rules check conditions like:
- Does supplier name equal "X"?
- Does product ID contain "Y"?
- Is field A equal to value B?
- Complex AND/OR logic

If the condition is TRUE, the rule's action is applied.

### Rule Actions

When a rule's condition matches, it can:
- **Set** a field to a specific value
- **Replace** a value with another
- **Override** data from the file

---

## Accessing the Rules Engine

### Step 1: Navigate to Rules Engine Tab
Click the **Rules Engine** tab at the top of the page.

[Screenshot: Rules Engine tab in main navigation]

### Step 2: View Rules List
You'll see all configured rules with:
- Priority number
- Rule name
- Condition summary
- Action summary
- Enable/Disable toggle
- Edit and Delete buttons

[Screenshot: Rules Engine main interface]

---

## Viewing Rules

### Rules List Display

Each rule card shows:

**Priority Badge**: Blue circle with number (1, 2, 3...)
**Rule Name**: Descriptive name (e.g., "Map Day & Night to Carrier")
**Condition**: What the rule checks for
**Action**: What happens when the condition is true
**Status Toggle**: Green (Enabled) or Gray (Disabled)
**Action Buttons**: Edit and Delete

[Screenshot: Example rule card with all elements labeled]

### Understanding Rule Display

**Example Rule Display:**
```
[1] Map Day & Night to Carrier
    supplier_name equals "Day & Night Heating & Cooling" → Carrier
    [Enabled ✓]  [Edit]  [Delete]
```

**Interpretation:**
- Priority 1 (runs first)
- Named "Map Day & Night to Carrier"
- Checks if supplier_name equals "Day & Night Heating & Cooling"
- If true, changes supplier_name to "Carrier"
- Currently enabled

### Rule Status Indicators

**Green toggle (Enabled)**: Rule is active and will be applied during processing
**Gray toggle (Disabled)**: Rule is saved but not applied during processing

---

## Rule Types

The Rules Engine supports flexible IF-THEN rules with multiple condition types.

### Type 1: Simple Supplier Name Match

**Format:**
```
IF supplier_name equals "[exact name]"
THEN set supplier_name to "[new name]"
```

**Example:**
```
IF supplier_name equals "Day & Night Heating & Cooling"
THEN set supplier_name to "Carrier"
```

**Use Case:** When a supplier name in files needs to be standardized to TradeNet's naming.

### Type 2: Product ID Match

**Format:**
```
IF product_id contains "[product code]"
THEN set supplier_name to "[supplier name]"
```

**Example:**
```
IF product_id contains "5534"
THEN set supplier_name to "Air Vent"
```

**Use Case:** When a specific product always belongs to a specific supplier.

### Type 3: Complex Conditions (AND/OR Logic)

**Format:**
```
IF ([field1] [operator] [value1]) AND/OR ([field2] [operator] [value2])
THEN set [field] to [value]
```

**Example:**
```
IF (product_id contains "5531") AND (quantity > 0)
THEN set supplier_name to "CertainTeed"
```

**Use Case:** Advanced rules with multiple conditions.

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| equals | Exact match | supplier_name equals "Carrier" |
| contains | Contains substring | product_id contains "5534" |
| starts_with | Starts with string | product_id starts_with "55" |
| ends_with | Ends with string | product_id ends_with "34" |
| > | Greater than | quantity > 10 |
| < | Less than | quantity < 100 |
| >= | Greater or equal | quantity >= 1 |
| <= | Less or equal | quantity <= 50 |

### Supported Fields

You can create rules on any field:
- supplier_name
- product_id
- quantity
- member_name
- city
- state
- Any other field in the data

---

## Creating New Rules

### Step 1: Open Add Rule Form
1. Go to **Rules Engine** tab
2. Click the **Add Rule** button (top right)

[Screenshot: Add Rule button]

### Step 2: Fill in Basic Information

**Rule Name** (required)
- Descriptive name for the rule
- Example: "Map Product 5534 to Air Vent"

**Priority** (required)
- Number indicating order of execution (1 = first)
- System suggests next available priority
- Lower numbers run first

**Enabled** (checkbox)
- Check to enable the rule immediately
- Uncheck to save but not apply the rule

[Screenshot: Rule basic information form]

### Step 3: Define Condition

Choose the condition type:

#### Option A: Simple Condition
1. Select **Simple Condition**
2. Choose the **Field** to check (e.g., supplier_name)
3. Choose the **Operator** (e.g., equals)
4. Enter the **Value** to compare (e.g., "Day & Night Heating & Cooling")

[Screenshot: Simple condition form]

#### Option B: Complex Condition (AND/OR)
1. Select **Complex Condition**
2. Choose **Logic Type**: AND or OR
3. Add multiple condition rules:
   - For each rule, select Field, Operator, Value
4. Click **Add Condition** to add more rules

[Screenshot: Complex condition form with AND/OR logic]

### Step 4: Define Action

Specify what happens when the condition is true:

**Action Type:** Set Field
**Field:** Choose which field to modify (e.g., supplier_name)
**Value:** Enter the new value (e.g., "Carrier")

[Screenshot: Action form]

### Step 5: Save Rule
1. Review all settings
2. Click **Save** to create the rule
3. The rule appears in the rules list

### Step 6: Test the Rule
1. Upload a test file that matches the rule's condition
2. Process and preview
3. Verify the rule applied correctly

---

## Editing Rules

### Step 1: Find the Rule
1. Go to **Rules Engine** tab
2. Locate the rule you want to edit

### Step 2: Open Edit Form
Click the **Edit** button for that rule.

[Screenshot: Edit button in rule card]

### Step 3: Modify Settings
The edit form appears with current values:
- Update name, priority, condition, or action
- Change enabled/disabled status

[Screenshot: Edit Rule form with existing values]

### Step 4: Save Changes
1. Click **Save**
2. The rule updates in the list
3. Success message confirms the change

### Step 5: Reorder Priority (if changed)
If you changed the priority:
1. Other rules may renumber automatically
2. Verify the new priority order
3. Test with a sample file

---

## Enabling and Disabling Rules

### Quick Toggle

You can enable/disable rules without editing:

1. Find the rule in the list
2. Click the **toggle switch** on the right
3. The rule status changes immediately:
   - **Green = Enabled** (rule will apply)
   - **Gray = Disabled** (rule won't apply)

[Screenshot: Toggle switch in enabled and disabled states]

### When to Disable

Disable a rule temporarily when:
- Testing how files process without the rule
- The rule is causing issues but you don't want to delete it
- A supplier mapping changes temporarily
- Troubleshooting data issues

### When to Enable

Enable a disabled rule when:
- You've finished testing
- The temporary issue is resolved
- You want to restore the rule's effect

**Tip:** Disabling is better than deleting if you might need the rule again.

---

## Deleting Rules

### Step 1: Find the Rule
Locate the rule you want to delete in the rules list.

### Step 2: Click Delete
Click the red **Delete** button for that rule.

[Screenshot: Delete button in rule card]

### Step 3: Confirm Deletion
A confirmation dialog appears:

"Are you sure you want to delete this rule?"

- Click **Confirm** to permanently delete
- Click **Cancel** to keep the rule

### Step 4: Verification
- The rule is removed from the list
- Success message confirms deletion
- Priority numbers of other rules may adjust

### When to Delete

Delete a rule when:
- The rule is permanently obsolete
- The business requirement changed
- The rule was created in error
- Consolidating with another rule

**Warning:** Deletion is permanent. Consider disabling instead if you're unsure.

---

## Rule Priority

### How Priority Works

Rules execute in **priority order** (lowest number first):

```
Priority 1 → runs first
Priority 2 → runs second
Priority 3 → runs third
...
```

### Why Priority Matters

**Scenario:**
- Rule 1: IF product_id contains "5534" THEN supplier = "Air Vent"
- Rule 2: IF supplier_name equals "Air Vent" THEN supplier = "Acme Corp"

**Result:** Product 5534 ends up as "Acme Corp" because Rule 2 runs after Rule 1.

**Solution:** Arrange priorities so rules don't conflict, or use more specific conditions.

### Reordering Rules

To change rule order:
1. Edit the rule
2. Change its priority number
3. Save
4. Other rules may auto-adjust their priorities

**Best Practice:** Leave gaps in priority (1, 5, 10, 15...) so you can insert rules between existing ones.

### Priority Strategy

**Higher Priority (1, 2, 3...):**
- Most specific rules (e.g., exact product matches)
- Override everything else

**Lower Priority (8, 9, 10...):**
- General rules (e.g., broad supplier name mappings)
- Apply only if no specific rule matched

---

## Common Rule Examples

### Example 1: Map Supplier Name

**Scenario:** Files contain "Day & Night Heating & Cooling" but TradeNet expects "Carrier"

**Rule:**
```
Name: Map Day & Night to Carrier
Priority: 1
Condition: supplier_name equals "Day & Night Heating & Cooling"
Action: Set supplier_name to "Carrier"
```

### Example 2: Product-Specific Supplier

**Scenario:** Product 5534 always belongs to Air Vent regardless of what the file says

**Rule:**
```
Name: Product 5534 → Air Vent
Priority: 2
Condition: product_id contains "5534"
Action: Set supplier_name to "Air Vent"
```

### Example 3: Multiple Products to One Supplier

**Scenario:** Products 5531, 5407 always belong to CertainTeed

**Create two rules:**

**Rule A:**
```
Name: Product 5531 → CertainTeed
Priority: 3
Condition: product_id contains "5531"
Action: Set supplier_name to "CertainTeed"
```

**Rule B:**
```
Name: Product 5407 → CertainTeed
Priority: 4
Condition: product_id contains "5407"
Action: Set supplier_name to "CertainTeed"
```

### Example 4: Conditional Override

**Scenario:** Only override supplier if quantity is greater than 0

**Rule:**
```
Name: Product 5255 → Heatilator (if quantity > 0)
Priority: 5
Condition: (product_id contains "5255") AND (quantity > 0)
Action: Set supplier_name to "Heatilator"
```

### Example 5: State-Based Rule

**Scenario:** For Texas members, use a different supplier

**Rule:**
```
Name: Texas → Local Supplier
Priority: 6
Condition: state equals "TX"
Action: Set supplier_name to "Texas Local Supply"
```

---

## Best Practices

### Rule Design

✅ **Be specific**: Use exact matches when possible to avoid unintended changes
✅ **Name clearly**: Use descriptive names that explain what the rule does
✅ **Document why**: Add comments or notes about why the rule exists
✅ **Test thoroughly**: Always test rules with sample files before batch processing

### Priority Management

✅ **Specific first**: Put specific rules (product matches) at higher priority than general rules (supplier names)
✅ **Leave gaps**: Use priorities 1, 5, 10, 15... so you can insert rules later
✅ **Review regularly**: Check that rule order still makes sense as you add new rules

### Maintenance

✅ **Disable don't delete**: If unsure, disable rather than delete
✅ **Regular review**: Quarterly review to remove obsolete rules
✅ **Version control**: Keep notes on when rules were added and why
✅ **Coordinate changes**: Let team members know when you change rules

### Testing

✅ **Test after creating**: Process a test file immediately after creating a rule
✅ **Test after editing**: Verify changes didn't break anything
✅ **Test edge cases**: Try files that match and don't match the condition
✅ **Compare outputs**: Check before/after to see rule effects

### Common Mistakes to Avoid

❌ **Too broad conditions**: e.g., "product_id contains '5'" matches 5, 50, 55, 500...
❌ **Conflicting rules**: Rules that undo each other
❌ **Wrong priority**: Specific rule at low priority, general rule at high priority
❌ **Typos in values**: "Carrier " (with space) won't match "Carrier"
❌ **Forgetting to enable**: Creating a rule but leaving it disabled

---

## Troubleshooting Rules

### Rule Not Applying

**Problem:** Created a rule but it's not changing the data

**Solutions:**
1. Check if the rule is **Enabled** (toggle should be green)
2. Verify the **condition** matches exactly (check for typos, spaces)
3. Check **priority** - a higher priority rule may be overriding it
4. Use exact quotes and capitalization from your data

### Rule Applying Too Much

**Problem:** Rule is changing data it shouldn't

**Solutions:**
1. Make the condition **more specific**
2. Add additional AND conditions to narrow the match
3. Increase the rule's priority so it runs before other rules
4. Test with "contains" vs "equals" operators

### Wrong Priority Order

**Problem:** Rules are running in the wrong order

**Solutions:**
1. Edit each rule's priority number
2. Put most specific rules first (lower numbers)
3. Put general catch-all rules last (higher numbers)
4. Leave gaps between priorities for future rules

### Rules Conflicting

**Problem:** Two rules are fighting each other

**Solutions:**
1. Review both rules' conditions and actions
2. Adjust priorities so they don't override each other
3. Make conditions mutually exclusive with AND/OR logic
4. Combine into one rule with complex conditions

---

## Quick Reference

### Rule Management Workflow

**Create Rule:**
1. Go to Rules Engine tab
2. Click **Add Rule**
3. Fill in name, priority, condition, action
4. Click **Save**
5. Test with sample file

**Edit Rule:**
1. Find rule in list
2. Click **Edit**
3. Modify settings
4. Click **Save**
5. Test changes

**Disable Rule:**
1. Find rule in list
2. Click toggle switch to gray
3. Rule saved but not applied

**Delete Rule:**
1. Find rule in list
2. Click **Delete**
3. Confirm deletion

### Current System Rules

The system currently has 8 standard rules:

1. Day & Night Heating & Cooling → Carrier
2. Product 5534 → Air Vent
3. Product 5531 → CertainTeed
4. Product 5406 → Air Vent
5. Product 5407 → CertainTeed
6. Product 5255 → Heatilator (Hearth & Home)
7. Product 5270 → Leading Edge
8. Product 5350 → Leading Edge

**Note:** Check with management before modifying these core rules.

---

## Advanced Topics

### Rule Testing Strategy

**Step 1: Create Test Set**
- Collect files that should trigger the rule
- Collect files that should NOT trigger the rule

**Step 2: Process with Rule Enabled**
- Upload test file
- Process and preview
- Verify rule applied correctly

**Step 3: Process with Rule Disabled**
- Disable the rule
- Process same file
- Compare output to see difference

**Step 4: Re-Enable**
- Enable rule again
- Confirm it still works

### Bulk Rule Updates

If you need to update many rules:
1. Disable all rules
2. Process a test file to see baseline output
3. Enable rules one by one
4. Test after each enable
5. Document which rules affect which data

### Rule Documentation

Keep a spreadsheet of rules:
- Priority
- Name
- Condition
- Action
- Date Created
- Created By
- Reason/Notes

This helps when onboarding new staff or troubleshooting.

---

## Next Steps

- Review the [User Guide](user-guide.md) to see how rules affect file processing
- Check [Lookup Management](lookup-management.md) to understand how rules interact with lookup tables
- Read [Troubleshooting](troubleshooting.md) for rule-related error solutions

---

**Questions about rules?** Contact your administrator or the development team.
