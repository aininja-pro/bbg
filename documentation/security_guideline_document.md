# BBG Rebate Processing Automation Tool

This step-by-step implementation guide covers all deliverables: architecture overview, database schema, API specifications, React frontend structure, data transformation logic, rules-engine execution, error handling, testing, and deployment.

---

## 1. Architecture Overview

### 1.1 Components

- Backend (FastAPI + Python)
- Database (PostgreSQL or SQLite)
- Frontend (React + TailwindCSS + shadcn/ui)
- File storage (in-memory or temp directory)
- ZIP generation service

### 1.2 Data Flow

1. User uploads one or more `.xlsm` files via React Dropzone.
2. Frontend sends files to FastAPI endpoint.
3. Backend validates structure, reads hidden “reformatter” tab.
4. Pandas/Openpyxl unpivots and enriches data via lookups.
5. Rules engine applies configured transformations.
6. Backend produces CSV(s) or ZIP archive with manifest.txt.
7. Frontend downloads result, displays warnings in preview.

### 1.3 Security Considerations

- All endpoints served over HTTPS.
- File uploads limited to 50 MB; reject larger payloads.
- Validate Excel structure rigorously; reject malformed files.
- Sanitize filenames and paths; use UUIDs for temp files.
- Rate limiting on upload endpoints.
- CORS restricted to trusted origins.
- Secure headers: HSTS, X-Content-Type-Options, CSP.

---

## 2. Database Schema

### 2.1 Tables

1. **rules**
   - id (UUID, PK)
   - rule_type (ENUM)
   - priority (INT)
   - enabled (BOOLEAN)
   - config (JSONB)
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

2. **lookup_members**
   - id (UUID, PK)
   - bbg_member_id (TEXT)
   - member_name (TEXT)
   - tradenet_company_id (TEXT)

3. **lookup_suppliers**
   - id (UUID, PK)
   - supplier_name (TEXT)
   - tradenet_supplier_id (TEXT)

4. **lookup_products**
   - id (UUID, PK)
   - product_id (TEXT)
   - product_name (TEXT)
   - pp_dist_subcontractor (BOOLEAN)

5. **activity_logs**
   - id (UUID, PK)
   - run_id (UUID)
   - user_id (nullable)
   - action (TEXT)
   - details (JSONB)
   - created_at (TIMESTAMP)

### 2.2 Relationships

- rules: standalone; executed in priority order.
- lookups: no foreign keys; matched in code.

---

## 3. API Endpoint Specifications

### 3.1 File Upload & Processing

- **POST** `/api/v1/upload`  
  - Accepts multipart/form-data: `files: List[UploadFile]`, `export_mode: string` (`merged` or `batch`), `include_warnings: bool`.
  - Responses:
    - `200 OK`: streaming ZIP or CSV binary with proper `Content-Disposition`.
    - `400 Bad Request`: validation errors.
    - `413 Payload Too Large`: file >50 MB.

### 3.2 Rules Management

- **GET** `/api/v1/rules`  — list all rules (ordered by priority).
- **POST** `/api/v1/rules` — create a new rule.
- **PUT** `/api/v1/rules/{id}` — update rule.
- **DELETE** `/api/v1/rules/{id}` — delete rule.
- **PATCH** `/api/v1/rules/reorder` — bulk update priorities.

### 3.3 Lookup Management

- **GET** `/api/v1/lookups/{type}`  — retrieve members/suppliers/products.
- **POST** `/api/v1/lookups/{type}/bulk`  — replace via CSV upload.
- **POST** `/api/v1/lookups/{type}`  — add single record.
- **PUT** `/api/v1/lookups/{type}/{id}`  — update record.
- **DELETE** `/api/v1/lookups/{type}/{id}`  — delete record.

### 3.4 Activity Logs

- **GET** `/api/v1/logs` — list recent runs (90-day retention).

---

## 4. React Component Architecture

### 4.1 Pages & Routes

- `/` Dashboard – upload zone, preview table, export buttons.
- `/rules` Rules Management – list, add/edit modals, drag-drop reorder.
- `/lookups/{members|suppliers|products}` Lookup tables with CSV bulk upload.
- `/logs` Recent activities.

### 4.2 Key Components

1. **FileUploader**
   - Uses React Dropzone.
   - Shows drag area, file list, size validations.
2. **PreviewTable**
   - TanStack Table.
   - Columns: data fields + validation_status + warnings.
3. **ExportControls**
   - Toggle merged/batch, include/exclude warnings.
   - Triggers API call.
4. **RulesList**
   - shadcn/ui Table with drag-and-drop reorder.
   - Modal forms for create/edit (component: RuleForm).
5. **LookupTable**
   - Table + CSV upload input + individual edit modal.
6. **LogList**
   - Simple table with timestamp, action, summary.

### 4.3 State Management

- Use React Query (TanStack Query) for data fetching/caching.
- Local state for upload files and preview data.
- Context for global settings (e.g., API base URL).

---

## 5. Data Transformation Logic (Pseudocode)

```python
# 1. Load workbook and "reformatter" sheet
wb = load_workbook(file)
if "reformatter" not in wb.sheetnames:
    raise ValidationError
ws = wb["reformatter"]

# 2. Extract metadata
bbg_member_id = ws["B6"].value
member_name   = ws["B7"].value

# 3. Detect header row and product columns
header_row = find_header_row(ws)
flags = ws[2]  # row index=2
product_ids = ws[7]
active_cols = [col for col, flag in flags if flag.value == 1]

# 4. Load raw data (rows >= header_row)
df = pd.DataFrame(ws.values, header=header_row)
metadata_cols = df.columns[:7]
product_cols = [product_ids[c] for c in active_cols]

# 5. Unpivot
melted = df.melt(
    id_vars=metadata_cols,
    value_vars=active_cols,
    var_name="col_index",
    value_name="quantity"
)
# filter quantity >=1
melted = melted[melted["quantity"].fillna(0) >= 1]

# 6. Enrich
members = load_lookup("members")
suppliers = load_lookup("suppliers")
products = load_lookup("products")

melted["tradenet_company_id"] = melted["member_name"].map(members)
# similarly for supplier and product details

# 7. Date conversion
def excel_date_to_str(d):
    return (datetime(1899,12,30) + timedelta(days=d)).strftime("%m/%d/%Y")

melted["date_field"] = melted["date_serial"].apply(excel_date_to_str)

# 8. Apply rules (see Section 6)
for rule in get_enabled_rules():
    melted = apply_rule(melted, rule)

# 9. Final validation
assert melted[required_columns].notnull().all()

# 10. Export to CSV or ZIP
```

---

## 6. Rules Engine Execution Flow

1. **Fetch rules** sorted by `priority` where `enabled = true`.
2. For each rule:
   - Parse `config` JSON into parameters.
   - Dispatch to handler by `rule_type`:
     - `search_replace(df, config)`
     - `if_then_update(df, config)`
     - `if_then_set(df, config)`
     - `filter_rows(df, config)`
     - `concatenate(df, config)`
3. Each handler logs warnings or errors to `activity_logs`.
4. After all rules, return transformed DataFrame.

Handler pseudocode example:
```python
def search_replace(df, cfg):
    col = cfg["target_column"]
    df[col] = df[col].str.replace(cfg["find_text"], cfg["replace_text"])
    return df
```

---

## 7. Error Handling Strategy

### 7.1 Validation Errors (Critical)

- Missing sheet or cells → return HTTP 400 with error details.
- No active product columns → block processing.
- Zero data rows → block processing.

### 7.2 Warnings (Non-critical)

- Missing lookup matches → flag `validation_status = "warning"`.
- Data type mismatches → convert where possible; else warn.
- Rules failures → skip rule and log warning.

### 7.3 API Error Responses

- Standard JSON: `{ code: string, message: string, details?: any }`.
- No stack traces exposed.

---

## 8. Testing Requirements

### 8.1 Unit Tests

- Excel parser: valid & invalid sheet structures.
- Date conversion logic.
- Each rules handler with sample DataFrames.
- Lookup enrichment with missing and matching records.

### 8.2 Integration Tests

- End-to-end upload → CSV export for single file.
- Batch mode: multiple files + ZIP manifest.
- Error cases: oversized file, malformed workbook.

### 8.3 Frontend Tests

- Component snapshots (FileUploader, PreviewTable).
- React Query mocking for API.
- Form validation for rules and lookups.

### 8.4 Security/Performance

- Load test: 600+ rows, concurrent requests.
- Verify rate limiting, file size enforcement.
- Run dependency vulnerability scans (SCA).

---

## 9. Deployment Guide

### 9.1 Backend (Render)

1. Define `render.yaml`: web service (`fastapi`), worker (optional for ZIP offloading).
2. Environment variables:
   - `DATABASE_URL` (managed PostgreSQL)
   - `SECRET_KEY` (for future JWT)
3. TLS enforced by default.
4. Health checks on `/healthz`.

### 9.2 Frontend (Vercel)

1. Configure project with `vercel.json` for build command `npm run build`.
2. Set environment variable `NEXT_PUBLIC_API_BASE_URL`.
3. Enforce HTTPS redirect.

### 9.3 Database

- Use Render Postgres; apply migrations via Alembic.
- Enable SSL.
- Create read-only replica if needed.

### 9.4 CI/CD

- GitHub Actions pipeline:
  - Install dependencies, lint, run tests.
  - Build Docker image for backend.
  - Deploy to Render on successful tests.
  - Deploy frontend to Vercel.

### 9.5 Monitoring & Logging

- Use Render logs + external APM (e.g., Datadog).
- Alerts on error rates >1% or >5 failed uploads/min.

---

By following this guide, developers can build a secure, performant, and maintainable BBG Rebate Processing Automation Tool that meets all outlined requirements and edge cases.