# BBG Backend TODO

## Pending Items

### 1. Supplier Mapping (Awaiting Client Clarification)

**Issue**: Need to map Program names to TradeNet Supplier IDs

**Example**:
- Product 5492: Program = "Day & Night Heating & Cooling"
- Product 5510: Program = "Carrier Corporation"
- **Both should map to**: supplier_name = "Carrier", tradenet_supplier_id = "376"

**Question for Client**: How do we map Program names (from Programs-Products tab) to TradeNet Supplier Directory entries?

**Possible Solutions**:
1. Manual mapping table in database
2. Fuzzy name matching
3. Additional column in Programs-Products Excel
4. Business rules/lookup

**Current Status**: These fields are currently blank in output
- `supplier_name`
- `tradenet_supplier_id`

---

### 2. Date Format

**Current**: 07/02/2025
**Desired**: 7/2/25

Minor formatting adjustment needed.

---

### 3. Extra Columns in Output

**Current**: 17 columns (includes product_name, proof_point)
**Desired**: 15 columns

Should we remove product_name and proof_point from final CSV?
