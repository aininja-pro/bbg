# Database Schema

Database structure and schema documentation for the BBG Rebate Processing Tool.

## Database Overview

**Type:** PostgreSQL (Production on Render) / SQLite (Local Development)
**Production:** PostgreSQL on Render.com
**Local Development:** `backend/bbg_rebates.db` (SQLite)
**ORM:** SQLAlchemy 2.0+
**Size:** ~500KB (with seed data, SQLite) / Variable (PostgreSQL)

## Tables

### 1. lookup_members

TradeNet Members directory

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique member ID |
| tradenet_company_id | VARCHAR(100) | NOT NULL, INDEXED | TradeNet company ID |
| bbg_member_id | VARCHAR(100) | INDEXED | BBG member ID (can be empty) |
| member_name | VARCHAR(255) | NOT NULL, INDEXED | Company name |
| last_updated | DATETIME | DEFAULT NOW | Last update timestamp |

**Indexes:**
- `ix_lookup_members_tradenet_company_id`
- `ix_lookup_members_bbg_member_id`
- `ix_lookup_members_member_name`

**Typical Row Count:** ~911 members

---

### 2. lookup_suppliers

TradeNet Suppliers directory

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique supplier ID |
| tradenet_supplier_id | VARCHAR(100) | NOT NULL, UNIQUE, INDEXED | TradeNet supplier ID |
| bbg_id | VARCHAR(100) | INDEXED | Buying Group ID (optional) |
| supplier_name | VARCHAR(255) | NOT NULL, INDEXED | Supplier company name |
| active_flag | INTEGER | NULL | Active status (0 or 1) |
| contact_info | TEXT | NULL | Contact information |
| last_updated | DATETIME | DEFAULT NOW | Last update timestamp |

**Indexes:**
- `ix_lookup_suppliers_tradenet_supplier_id` (unique)
- `ix_lookup_suppliers_bbg_id`
- `ix_lookup_suppliers_supplier_name`

**Typical Row Count:** ~91 suppliers

---

### 3. lookup_products

Programs & Products (currently unused in processing)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique product ID |
| program_id | VARCHAR(100) | NOT NULL, INDEXED | Program identifier |
| program_name | VARCHAR(255) | NOT NULL | Program name |
| product_id | VARCHAR(100) | NOT NULL, INDEXED | Product identifier |
| product_name | VARCHAR(255) | NOT NULL | Product name |
| proof_point | VARCHAR(255) | NULL | Proof point description |
| last_updated | DATETIME | DEFAULT NOW | Last update timestamp |

**Note:** Products are currently extracted from uploaded files, not from this table.

---

### 4. rules

Business rules engine

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique rule ID |
| name | VARCHAR(255) | NOT NULL | Human-readable rule name |
| rule_type | VARCHAR(50) | NOT NULL | Type of rule (see types below) |
| priority | INTEGER | NOT NULL, DEFAULT 0, INDEXED | Execution order (lower = first) |
| enabled | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether rule is active |
| config | JSON | NOT NULL | Rule configuration (structure varies by type) |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW | Last update timestamp |

**Rule Types:**
- `search_replace` - Find and replace text
- `if_then_update` - Conditional field update
- `if_then_set` - Conditional value setting
- `row_filter` - Filter rows by condition
- `concatenate` - Combine multiple fields

**Config Examples:**

```json
// search_replace
{
  "column": "supplier_name",
  "find": "Day & Night Heating & Cooling",
  "replace": "Carrier"
}

// if_then_update (simple)
{
  "condition": {
    "supplier_name_equals": "Day & Night"
  },
  "set_supplier": "Carrier"
}

// if_then_update (complex)
{
  "condition": {
    "logic": "AND",
    "rules": [
      {"field": "product_id", "operator": "contains", "value": "5534"},
      {"field": "quantity", "operator": ">", "value": 0}
    ]
  },
  "then_action": {
    "field": "supplier_name",
    "value": "Air Vent"
  }
}
```

**Typical Row Count:** 8-20 rules

---

### 5. processed_files (Cached Files)

Temporarily cached processed files

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique cache ID |
| job_id | VARCHAR(36) | NOT NULL, UNIQUE, INDEXED | UUID for job |
| filename | VARCHAR(255) | NOT NULL | Original filename |
| file_data | BLOB | NOT NULL | Processed CSV/ZIP data |
| file_type | VARCHAR(10) | NOT NULL | "csv" or "zip" |
| row_count | INTEGER | NULL | Number of rows processed |
| file_count | INTEGER | NULL | Number of files (batch mode) |
| status | VARCHAR(20) | NOT NULL | "pending", "completed", "failed" |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Creation timestamp |
| expires_at | DATETIME | NOT NULL | Expiration timestamp |

**Indexes:**
- `ix_processed_files_job_id` (unique)
- `ix_processed_files_status`
- `ix_processed_files_created_at`

**Typical Row Count:** 0-100 (auto-cleaned after expiration)

---

## Entity Relationships

```
┌──────────────────────┐
│  lookup_members      │
│  (911 records)       │
└──────────────────────┘
         │
         │ (Used by data enricher)
         │
         ▼
┌─────────────────────────────────────┐
│  File Processing Pipeline           │
│  (In-memory, no DB persistence)     │
└─────────────────────────────────────┘
         │
         │ (Applies rules)
         ▼
┌──────────────────────┐
│  rules               │
│  (8-20 records)      │
│  - priority ordered  │
└──────────────────────┘
         │
         │ (Looks up supplier IDs)
         ▼
┌──────────────────────┐
│  lookup_suppliers    │
│  (91 records)        │
└──────────────────────┘
         │
         │ (Optional caching)
         ▼
┌──────────────────────┐
│  processed_files     │
│  (temporary cache)   │
└──────────────────────┘
```

**Note:** No foreign key relationships. Tables are independent lookup directories.

---

## Database Initialization

### Automatic Creation

Tables are created automatically on first run via SQLAlchemy:

```python
# In backend/app/database.py
from app.models.lookup import TradeNetMember, Supplier, ProgramProduct
from app.models.rule import Rule
from app.models.processed_file import ProcessedFile

# Tables created when engine starts
Base.metadata.create_all(bind=engine)
```

### Manual Seeding

```bash
cd backend
source venv/bin/activate

# Seed lookup tables
python3 seed_real_data.py

# Seed rules
python3 seed_rules.py
```

---

## Database Queries

### Common Queries

**Get all enabled rules by priority:**
```sql
SELECT * FROM rules
WHERE enabled = 1
ORDER BY priority ASC;
```

**Find member by name:**
```sql
SELECT * FROM lookup_members
WHERE member_name = 'Bosgraaf Homes';
```

**Find supplier by name:**
```sql
SELECT * FROM lookup_suppliers
WHERE supplier_name = 'Carrier';
```

**Count records:**
```sql
SELECT COUNT(*) FROM lookup_members;
SELECT COUNT(*) FROM lookup_suppliers;
SELECT COUNT(*) FROM rules WHERE enabled = 1;
```

---

## Database Maintenance

### Backup

```bash
# Copy the database file
cp bbg_rebates.db bbg_rebates.db.backup

# Or use SQLite backup
sqlite3 bbg_rebates.db ".backup bbg_rebates.db.backup"
```

### Reset Database

```bash
cd backend
source venv/bin/activate
rm bbg_rebates.db
python3 seed_real_data.py
python3 seed_rules.py
```

### Inspect Database

```bash
sqlite3 bbg_rebates.db

# In SQLite shell:
.tables                          # List tables
.schema lookup_members           # Show table structure
SELECT * FROM rules LIMIT 5;    # Query data
.quit                            # Exit
```

---

## Performance Considerations

### Indexes

All frequently-queried columns are indexed:
- Member names (for OLD format lookups)
- Supplier names (for rule application)
- IDs (for joins and lookups)
- Rule priority (for ordered execution)

### Query Performance

- **Member lookup:** < 1ms (indexed search)
- **Supplier lookup:** < 1ms (indexed search)
- **Rules fetch:** < 5ms (small table, indexed priority)

### Current Production Setup

**PostgreSQL on Render:**
- ✅ Multiple concurrent connections
- ✅ Better write performance
- ✅ Automatic backups by Render
- ✅ Production-grade reliability

**Local Development (SQLite):**
- Multiple readers OK
- Only ONE writer at a time
- Write operations lock entire database
- Sufficient for solo development

**Note:** Production is already using PostgreSQL on Render for better concurrency and reliability.

---

## Schema Migration

### Adding a New Column

1. Update model in `backend/app/models/`
2. Delete database: `rm bbg_rebates.db`
3. Restart backend (recreates tables)
4. Re-seed data

**For production:** Use Alembic for migrations:
```bash
alembic revision --autogenerate -m "Add new column"
alembic upgrade head
```

### Adding a New Table

1. Create model class in `backend/app/models/`
2. Import in `backend/app/database.py`
3. Restart backend (auto-creates table)
4. Seed data if needed

---

## Data Integrity

### Constraints

- Primary keys ensure unique records
- Indexed foreign keys for lookups
- NOT NULL on critical fields
- UNIQUE on TradeNet IDs

### Validation

Pydantic schemas validate data before database insertion:
- See `backend/app/schemas/`
- Type checking, length limits, format validation

---

## Related Documentation

- [API Reference](api-reference.md) - CRUD operations on tables
- [Developer Overview](developer-overview.md) - How database fits in architecture
- [Setup Development](setup-development.md) - Database initialization steps
