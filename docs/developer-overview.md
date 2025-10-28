# Developer Overview

Technical documentation for developers who need to maintain, modify, or take over the BBG Rebate Processing Tool.

## Table of Contents

- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [Key Components](#key-components)
- [Design Decisions](#design-decisions)
- [Development Workflow](#development-workflow)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  - Vite dev server (port 5174)                              │
│  - React components with TailwindCSS                         │
│  - Three main tabs: Upload, Rules, Lookups                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │ (fetch calls)
┌──────────────────────▼──────────────────────────────────────┐
│                     BACKEND (FastAPI)                        │
│  - Python 3.12 + FastAPI                                    │
│  - Uvicorn server (port 8001)                               │
│  - CORS enabled for localhost                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ SQLAlchemy ORM
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    DATABASE (SQLite)                         │
│  - bbg_rebates.db                                           │
│  - Tables: members, suppliers, rules, activity              │
└─────────────────────────────────────────────────────────────┘

                       │
                       │ File Processing
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  FILE PROCESSING PIPELINE                    │
│  1. Excel Reader (openpyxl)                                 │
│  2. Data Transformer (pandas)                               │
│  3. Data Enricher (lookups + rules)                         │
│  4. CSV Generator (pandas)                                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction

1. **User** uploads Excel file via React frontend
2. **Frontend** sends file to backend API via multipart/form-data
3. **Backend** processes file through pipeline:
   - Extract metadata (member info, products)
   - Transform data (unpivot, format)
   - Enrich with lookups and apply rules
   - Generate CSV
4. **Backend** returns preview data OR downloadable CSV
5. **Frontend** displays preview or triggers download

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI framework |
| Vite | 5.x | Build tool and dev server |
| TailwindCSS | 3.x | Styling |
| JavaScript (ES6+) | - | Language (not TypeScript) |

**Key Libraries:**
- `react-dropzone` - File upload drag-and-drop
- `@tanstack/react-table` - Data table display (if used)

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12 | Language |
| FastAPI | 0.115+ | Web framework |
| Uvicorn | 0.30+ | ASGI server |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.9+ | Data validation |
| openpyxl | 3.1+ | Excel file reading |
| pandas | 2.2+ | Data transformation |

### Database

- **Production:** PostgreSQL on Render.com
- **Local Development:** SQLite (file-based)
- Location (local): `backend/bbg_rebates.db`
- SQLite for easy local development, PostgreSQL for production scalability

### Development Tools

- **Git** - Version control
- **GitHub** - Repository hosting
- **MkDocs Material** - Documentation site generator

---

## Project Structure

```
BBG/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── App.jsx             # Main app with tab navigation
│   │   ├── main.jsx            # React entry point
│   │   ├── components/
│   │   │   ├── ui/             # Reusable UI components
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Card.jsx
│   │   │   │   └── Tabs.jsx
│   │   │   ├── upload/
│   │   │   │   └── FileUpload.jsx
│   │   │   ├── preview/
│   │   │   │   └── DataPreview.jsx
│   │   │   ├── rules/
│   │   │   │   ├── RulesManager.jsx
│   │   │   │   └── AddRuleModal.jsx
│   │   │   └── lookups/
│   │   │       ├── MembersTable.jsx
│   │   │       └── SuppliersTable.jsx
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx
│   │   │   └── LookupTablesPage.jsx
│   │   ├── services/
│   │   │   └── api.js          # Backend API calls
│   │   └── lib/
│   │       └── utils.js        # Utility functions
│   ├── public/                 # Static assets
│   ├── index.html              # HTML entry point
│   ├── package.json            # Node dependencies
│   ├── vite.config.js          # Vite configuration
│   └── tailwind.config.js      # Tailwind configuration
│
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Settings and configuration
│   │   ├── database.py         # Database connection
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── lookup.py       # Member, Supplier, Product models
│   │   │   ├── rule.py         # Rule model
│   │   │   └── activity.py     # Activity log model
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── lookup.py
│   │   │   ├── rule.py
│   │   │   └── upload.py
│   │   ├── repositories/       # Database CRUD operations
│   │   │   ├── lookup.py
│   │   │   ├── rule.py
│   │   │   └── activity.py
│   │   ├── routers/            # API endpoints
│   │   │   ├── lookup.py       # /api/lookups/*
│   │   │   ├── upload.py       # /api/upload, /api/process-and-download
│   │   │   └── rules.py        # /api/rules/*
│   │   ├── services/           # Business logic
│   │   │   ├── excel_processor.py     # Read Excel files
│   │   │   ├── data_transformer.py    # Unpivot & transform
│   │   │   ├── data_enricher.py       # Apply lookups & rules
│   │   │   └── pipeline.py            # Orchestrate processing
│   │   └── utils/
│   │       └── helpers.py
│   ├── bbg_rebates.db          # SQLite database
│   ├── requirements.txt        # Python dependencies
│   ├── seed_real_data.py       # Load members/suppliers
│   └── seed_rules.py           # Load business rules
│
├── docs/                        # Documentation (MkDocs)
│   ├── README.md
│   ├── getting-started.md
│   ├── user-guide.md
│   ├── lookup-management.md
│   ├── rules-engine.md
│   ├── troubleshooting.md
│   ├── faq.md
│   ├── developer-overview.md    # This file
│   └── images/
│
├── mkdocs.yml                   # MkDocs configuration
├── PROJECT_STATUS.md            # Project handoff document
└── README.md                    # Repository README
```

---

## Data Flow

### File Upload & Processing Flow

```
1. USER UPLOADS FILE
   ↓
2. FileUpload.jsx (Frontend)
   - Validates file type (.xlsm, .xlsx)
   - Sends to backend via FormData
   ↓
3. /api/upload (Backend Router)
   - Receives multipart/form-data
   - Saves file temporarily
   ↓
4. Pipeline.process_file() (Service Layer)
   ↓
5. ExcelProcessor.read_file()
   - Opens Excel file with openpyxl
   - Detects OLD vs NEW format (check cell B6)
   - Extracts metadata (member info from B6/B7)
   - Extracts Programs-Products sheet
   - Reads Usage-Reporting data (rows 9+)
   ↓
6. DataTransformer.transform()
   - Unpivots wide format → long format
   - Formats dates (Excel → M/D/YY)
   - Converts numbers (remove decimals)
   - Standardizes column names
   ↓
7. DataEnricher.enrich()
   - Lookup member ID (if OLD format)
   - Apply business rules (supplier overrides)
   - Lookup supplier IDs from directory
   - Add TradeNet company IDs
   ↓
8. Generate CSV
   - Sort by date, job code, column order
   - Create 15-column CSV format
   ↓
9. Return to Frontend
   - Preview: JSON with first N rows
   - Download: CSV file blob
   ↓
10. Display or Download
    - Preview: DataPreview.jsx renders table
    - Download: Browser downloads CSV
```

### Business Rules Processing

```
1. Rule Definition (Database)
   - Priority order (1, 2, 3...)
   - Condition (field, operator, value)
   - Action (set field to value)
   ↓
2. Rule Loading
   - Load all ENABLED rules from database
   - Sort by priority (ascending)
   ↓
3. Rule Application (for each data row)
   - Iterate through rules in priority order
   - Check if condition matches row data
   - If match: apply action (modify field)
   - Continue to next rule
   ↓
4. Result
   - Modified data with rules applied
   - Higher priority rules can override lower ones
```

---

## Key Components

### Backend Services

#### 1. ExcelProcessor (`app/services/excel_processor.py`)

**Purpose:** Read and parse Excel files

**Key Methods:**
- `read_file(file_path)` - Main entry point
- `_detect_format()` - Check if OLD or NEW format
- `_extract_metadata()` - Get member info from B6/B7
- `_extract_products()` - Read Programs-Products sheet
- `_read_data_rows()` - Read Usage-Reporting rows

**Important Logic:**
- **Format Detection:** If B6 is empty → OLD format
- **Product Identification:** Row 2 flags (1 = active), Row 7 IDs
- **Data Start:** Row 9 = headers, Row 10+ = data

#### 2. DataTransformer (`app/services/data_transformer.py`)

**Purpose:** Transform wide Excel format to long CSV format

**Key Methods:**
- `transform(raw_data, products)` - Main transformation
- `_unpivot()` - Convert wide → long format
- `_format_dates()` - Convert Excel dates
- `_format_numbers()` - Remove decimals
- `_standardize_columns()` - Ensure correct column names

**Important Logic:**
- **Unpivot:** Each product column becomes multiple rows
- **Date Format:** Excel serial → M/D/YY string
- **Numbers:** quantity and zip_postal as integers

#### 3. DataEnricher (`app/services/data_enricher.py`)

**Purpose:** Add lookup data and apply business rules

**Key Methods:**
- `enrich(data, lookups, rules)` - Main enrichment
- `_lookup_member_id()` - Find BBG member ID by name
- `_apply_rules()` - Execute business rules in order
- `_lookup_supplier_ids()` - Map supplier names to IDs

**Important Logic:**
- Rules applied in priority order (1 first)
- Each rule can override previous values
- Lookups match on exact string equality

#### 4. Pipeline (`app/services/pipeline.py`)

**Purpose:** Orchestrate the entire processing flow

**Key Method:**
- `process_file(file_path, db_session)` - End-to-end processing

**Flow:**
1. Read Excel file
2. Transform data
3. Load lookups and rules from database
4. Enrich data
5. Generate CSV
6. Return result

### Frontend Components

#### 1. UploadPage (`src/pages/UploadPage.jsx`)

**Purpose:** Main upload and processing page

**State Management:**
- `selectedFile` - Single file in normal mode
- `selectedFiles` - Multiple files in batch mode
- `batchMode` - Toggle between single/batch
- `outputMode` - Merged CSV or ZIP
- `previewData` - Result data for preview
- `jobId` - Cached processing ID for instant downloads

**Key Functions:**
- `handleProcess()` - Process single file
- `handleBatchProcess()` - Process multiple files
- `handleDownload()` - Download single CSV
- `handleBatchDownload()` - Download merged or ZIP

#### 2. RulesManager (`src/components/rules/RulesManager.jsx`)

**Purpose:** Manage business rules

**Features:**
- List all rules with priority
- Toggle enable/disable
- Edit existing rules
- Delete rules
- Add new rules (via AddRuleModal)

**API Calls:**
- `GET /api/rules` - Fetch all rules
- `PUT /api/rules/{id}` - Update rule
- `DELETE /api/rules/{id}` - Delete rule
- `POST /api/rules` - Create rule

#### 3. LookupTablesPage (`src/pages/LookupTablesPage.jsx`)

**Purpose:** Manage Members and Suppliers directories

**Features:**
- View members/suppliers tables
- Add individual records
- Edit records
- Delete records
- Upload CSV to replace entire table

---

## Design Decisions

### Why PostgreSQL in Production, SQLite in Development?

**Decision:** Use PostgreSQL on Render for production, SQLite for local development

**Reasoning:**
- ✅ **PostgreSQL (Production):**
  - Better concurrency support
  - Production-grade reliability
  - Managed by Render (automatic backups)
  - Scales with growing user base
  - Better performance under load
- ✅ **SQLite (Development):**
  - Simple local setup (no external DB server)
  - Single file database (easy to reset)
  - Faster development iteration
  - No configuration needed

**Current Status:** Deployed on Render with PostgreSQL database

### Why File-Based Product Extraction?

**Decision:** Extract products from each uploaded file instead of central database

**Reasoning:**
- Each member has different active products
- Product lists change per quarter
- Avoids stale data in database
- More dynamic and accurate

**Original Plan:** Load Programs-Products once into database
**Changed to:** Extract from each file during processing

### Why FastAPI?

**Decision:** FastAPI over Flask/Django

**Reasoning:**
- ✅ Built-in async support
- ✅ Automatic API documentation (OpenAPI)
- ✅ Fast performance
- ✅ Type hints with Pydantic
- ✅ Modern Python framework

### Why React (not Vue/Angular)?

**Decision:** React with functional components

**Reasoning:**
- ✅ Large ecosystem
- ✅ Easy to find developers
- ✅ Component reusability
- ✅ Hooks for state management (no Redux needed for this scale)

### Why Vite (not Create React App)?

**Decision:** Vite for build tooling

**Reasoning:**
- ✅ Much faster dev server
- ✅ Faster builds
- ✅ Modern ESM-based
- ✅ Better DX (developer experience)

### Why Material Theme for MkDocs?

**Decision:** MkDocs Material for documentation

**Reasoning:**
- ✅ Professional appearance
- ✅ Built-in search
- ✅ Dark/light mode
- ✅ Mobile responsive
- ✅ Easy deployment to GitHub Pages

---

## Development Workflow

### Starting Development

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend
npm run dev -- --port 5174

# Terminal 3 - Documentation (optional)
python3 -m mkdocs serve
```

**Access:**
- Frontend: http://localhost:5174
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs
- MkDocs: http://localhost:8000

### Making Changes

**Frontend Changes:**
1. Edit files in `frontend/src/`
2. Vite hot-reloads automatically
3. Check browser console for errors

**Backend Changes:**
1. Edit files in `backend/app/`
2. Uvicorn restarts automatically (--reload flag)
3. Test API at http://localhost:8001/docs

**Database Changes:**
1. Edit models in `backend/app/models/`
2. Delete `bbg_rebates.db`
3. Restart backend (recreates tables)
4. Re-seed data: `python3 seed_real_data.py`

### Testing Changes

**Manual Testing:**
1. Upload a test Excel file
2. Check preview data
3. Download CSV
4. Open CSV in Excel to verify

**Test Files:**
- NEW format: `New Tradition Homes Q3 25 Usage Reporting Sheet.xlsm`
- OLD format: `Bosgraaf Homes Q4 24 Usage Reporting Sheet.xlsm`

### Git Workflow

```bash
# Check status
git status

# Make changes
git add .
git commit -m "Description of changes"
git push
```

### Database Reset

If database gets corrupted or needs fresh start:

```bash
cd backend
source venv/bin/activate
rm bbg_rebates.db
python3 seed_real_data.py    # Load members & suppliers
python3 seed_rules.py         # Load business rules
```

---

## Common Development Tasks

### Add a New Business Rule

1. **Backend:** Already supports flexible rules via API
2. **Frontend:** Use the AddRuleModal component
3. **Test:** Process a file that matches the rule

### Add a New Lookup Table

1. **Backend:**
   - Add model in `app/models/lookup.py`
   - Add repository in `app/repositories/lookup.py`
   - Add router endpoints in `app/routers/lookup.py`
2. **Frontend:**
   - Create component in `src/components/lookups/`
   - Add sub-tab in `LookupTablesPage.jsx`
3. **Database:** Delete and re-seed to create new table

### Modify CSV Output Format

1. **Backend:**
   - Edit `data_transformer.py` to add/remove columns
   - Update `_standardize_columns()` method
   - Ensure column order matches TradeNet spec
2. **Frontend:** Preview table auto-adjusts to new columns

### Add New File Format Support

1. **Backend:**
   - Edit `excel_processor.py`
   - Add new format detection logic
   - Handle different cell locations/structures
2. **Test:** Ensure OLD and NEW formats still work

---

## Performance Considerations

### Current Performance

- **Single file:** 5-30 seconds (depends on size)
- **Batch 10 files:** 30-60 seconds
- **Batch 50 files:** 2-5 minutes

### Bottlenecks

1. **Excel Reading:** openpyxl is slower than pandas for large files
2. **Pandas Operations:** Unpivot and transformations are CPU-bound
3. **Sequential Processing:** Files processed one at a time

### Potential Optimizations

**If needed in future:**

1. **Parallel Processing:**
   - Use `multiprocessing` for batch mode
   - Process multiple files simultaneously
   - Requires careful database transaction handling

2. **Caching:**
   - Cache lookup tables in memory (currently loaded each request)
   - Use Redis for shared cache across processes

3. **Async Processing:**
   - Move file processing to background tasks (Celery, FastAPI BackgroundTasks)
   - Return job ID immediately
   - Poll for completion

4. **Faster Excel Reading:**
   - Try `xlrd` or `pandas.read_excel()` with engine='openpyxl'
   - Benchmark different libraries

---

## Security Considerations

### Current Security

- ✅ CORS restricted to localhost
- ✅ File type validation (.xlsm, .xlsx only)
- ✅ File size limits (50MB max)
- ✅ SQL injection protected (SQLAlchemy ORM)
- ✅ No authentication (internal tool only)

### Production Security Needs

**Before deploying to production:**

1. **Authentication:**
   - Add user login (OAuth, JWT, or simple auth)
   - Restrict access to authorized BBG staff
   - Track who uploaded which files

2. **HTTPS:**
   - Use SSL/TLS certificates
   - Enforce HTTPS only

3. **File Security:**
   - Scan uploaded files for malware
   - Sandbox file processing
   - Auto-delete uploaded files after processing

4. **Rate Limiting:**
   - Limit API requests per user
   - Prevent abuse

5. **Database Security:**
   - Move to PostgreSQL for production
   - Use database user with limited permissions
   - Regular backups

---

## Next Steps for New Developers

1. **Read the Documentation:**
   - [Setup Development Environment](setup-development.md)
   - [API Reference](api-reference.md)
   - [Database Schema](database-schema.md)

2. **Run the Application Locally:**
   - Follow setup instructions
   - Upload test files
   - Experiment with UI

3. **Understand the Code:**
   - Start with `backend/app/main.py`
   - Trace through a file upload request
   - Read the service layer code

4. **Make a Small Change:**
   - Fix a bug or add a minor feature
   - Test thoroughly
   - Commit to Git

5. **Review PROJECT_STATUS.md:**
   - Contains current state
   - Known issues
   - Future enhancements

---

## Getting Help

### Resources

- **PROJECT_STATUS.md** - Current project state and handoff info
- **API Docs** - http://localhost:8001/docs (when running)
- **GitHub Issues** - Report bugs or feature requests
- **Code Comments** - Many files have inline documentation

### Contact

- Original Developer: [Your contact info]
- Repository: https://github.com/aininja-pro/bbg

---

**Ready to dive deeper?** Check out the other developer guides:
- [Setup Development Environment](setup-development.md)
- [API Reference](api-reference.md)
- [Database Schema](database-schema.md)
- [Deployment Guide](deployment.md)
