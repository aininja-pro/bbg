# Project Requirements Document (PRD)

## 1. Project Overview

Builders Buying Group (BBG) processes over 600 quarterly rebate submission Excel files (.xlsm) by hand, spending up to three weeks per quarter on error-prone data entry. This project delivers a web-based pipeline that automatically ingests each rebate file, unpivots and enriches its data, applies business-rule transformations, then exports clean CSVs ready for direct import into BBG’s Financial Management System (FMS). A built-in, no-code rules engine lets non-technical staff adjust logic—like supplier name mappings or state-specific product codes—without developer involvement.

We’re building this tool to slash manual effort from weeks to under two minutes per file, eliminate human data-entry errors, and give staff full control over evolving rebate rules. Success will be measured by:

*   Processing time <2 minutes per file
*   Self-service rule and lookup management (no developer calls)
*   Batch handling (50+ files → one merged CSV or a ZIP of individual files)
*   Zero FMS import failures

## 2. In-Scope vs. Out-of-Scope

### In-Scope (Version 1)

*   Excel ingestion & structure validation (.xlsm, hidden “reformatter” sheet, metadata cells B6/B7, header detection)
*   Transformation pipeline (unpivot wide→long, extract core fields, convert Excel dates to MM/DD/YYYY)
*   Data enrichment via three lookup tables (TradeNet Members, Suppliers, Programs & Products)
*   Template-based rules engine (search/replace, If/Then updates, filters, concatenation)
*   Preview interface with first 10 rows and warning highlights
*   In-browser real-time progress and warning banners (no email)
*   Export of results as one merged CSV or individual CSVs in a single ZIP (with manifest.txt)
*   Basic activity log of transformation runs (90-day retention)
*   Simple lookup backup (last 3 full CSV snapshots optional)

### Out-of-Scope (Later Phases)

*   User authentication or role-based access control
*   Email or Slack notifications by default (except real-time browser toasts)
*   Multi-tenant or public SaaS deployment
*   Full audit/version control of rules or lookups
*   Direct FMS API integration (import remains manual)
*   Advanced rule builder (AND/OR grouping)
*   Historical processing dashboards beyond 90-day log retention

## 3. User Flow

A BBG staff member opens the tool (hosted at a private URL) and drags one or more `.xlsm` files into the drop zone. As each file arrives, the REST API validates its structure (checks for the “reformatter” sheet, B6/B7 metadata, active product flags). A progress indicator shows validation, extraction, unpivot, rule application, and lookup enrichment in real time. If a critical error occurs (missing sheet or metadata), the process halts with a clear inline message.

When validation and transformation succeed, the first ten rows of output appear in a preview table. Rows with missing lookups or data-quality warnings are highlighted in amber. The user may switch to the **Rules** tab to tweak or reorder transformation rules, or the **Lookups** tab to refresh reference tables. Once satisfied, they return to the preview and choose **Download Merged CSV** or **Download ZIP of Individual Files**. A manifest within the ZIP summarizes run details and warnings.

## 4. Core Features

*   **Excel Ingestion & Validation**\
    • Accept `.xlsm` (macros enabled)\
    • Locate hidden “reformatter” sheet\
    • Extract B6 (bbg_member_id) & B7 (member_name)\
    • Auto-detect header row via keywords (“Date”, “Job Code”, etc.)\
    • Identify active product columns (Row 2=1) & product IDs (Row 7)\
    • Fail fast on missing elements with descriptive errors
*   **Transformation Pipeline**\
    • Unpivot wide → long format for each active product\
    • Extract fields: confirmed_occupancy, job_code, address1, city, state, zip_postal, address_type\
    • Convert Excel serial dates → MM/DD/YYYY\
    • Enrich each row via lookup tables (tradenet_company_id, tradenet_supplier_id, proof_point)
*   **Rules Engine**\
    • Types: Search & Replace | If/Then Update | If/Then Set Value | Row Filter | Concatenate\
    • Priority ordering, enable/disable toggles, conflict detection\
    • Applied sequentially after unpivot & before enrichment
*   **Lookup Management**\
    • Three tables: TradeNet Members, Suppliers, Programs & Products\
    • CSV upload (full replace) or inline add/edit/delete rows\
    • Search/filter, immediate persistence, last_updated timestamp\
    • Optional auto-backups of previous CSVs (retain last 3)
*   **Preview & Warning System**\
    • Show first 10 rows with data & lookup warnings highlighted\
    • Warning banner summarizing count by type\
    • Option to exclude warned rows from export
*   **Export Options**\
    • Merged CSV: `BBG_Rebates_Q{quarter}_{year}_{YYYYMMDD_HHMMSS}.csv`\
    • Individual CSVs: `{SanitizedMemberName}_{BBG_ID}_Q{quarter}_{year}.csv` bundled in a single ZIP with `manifest.txt`\
    • ZIP default for batch; merged CSV for bulk FMS import
*   **Activity Logging**\
    • Log each run: run_id, timestamp, input files, members processed, row counts, warnings, duration, status\
    • Retain logs for 90 days, auto-cleanup
*   **In-Browser Notifications**\
    • Real-time progress updates (upload, validate, transform)\
    • Success/error toasts; optional Browser Notification API if granted

## 5. Tech Stack & Tools

### Backend

*   Python 3.11+
*   FastAPI REST service
*   Pandas for transformations
*   openpyxl for Excel reading
*   Pydantic for input validation
*   PostgreSQL (or SQLite) for lookup & activity storage
*   Deployment: Render.com

### Frontend

*   React 18+ (SPA)
*   TailwindCSS + shadcn/ui components
*   React Dropzone for uploads
*   TanStack Table or AG Grid for data preview
*   In-browser Notification API for completion alerts
*   Deployment: Vercel

## 6. Non-Functional Requirements

*   **Performance**:\
    • Single file processed in <2 minutes (target 30–90 seconds)\
    • Batch of 50 files in <10 minutes
*   **Scalability**:\
    • Handle files up to 50 MB\
    • Concurrency for batch mode
*   **Reliability**:\
    • 99.5% uptime on Render/Vercel\
    • Automatic retries for transient errors
*   **Security**:\
    • Private network or VPN-restricted\
    • HTTPS everywhere\
    • No public authentication (Phase 1)
*   **Usability**:\
    • Accessible (WCAG 2.1 AA)\
    • Clear error/warning messaging\
    • Responsive layout for desktop browsers
*   **Maintainability**:\
    • Modular code (rules engine, pipeline, lookups)\
    • Configuration-driven rule definitions

## 7. Constraints & Assumptions

*   **Internal Tool**: No external users; deployed on private URL
*   **Date Handling**: Use raw Excel serials → MM/DD/YYYY; no time zones
*   **Lookup Freshness**: Users will manually refresh lookup tables as needed
*   **No Authentication**: Phase 1 assumes trusted, internal network
*   **File Retention**: Do not store uploaded or output files on server permanently

## 8. Known Issues & Potential Pitfalls

*   **Header Detection**: Variations in column labels require robust keyword matching\
    *Mitigation*: Fallback to regex search, configurable header identifiers
*   **Excel Serial Edge Cases**: Leap year bug in 1900 epoch\
    *Mitigation*: Use openpyxl’s built-in date conversion logic
*   **Large File Memory Use**: Pandas can spike memory for 50 MB files\
    *Mitigation*: Stream rows in chunks or limit max concurrency
*   **Rule Conflicts**: Overlapping rules may produce conflicting updates\
    *Mitigation*: On-save validation to detect duplicate targets or circular logic
*   **Lookup Gaps**: Missing reference data leads to empty fields\
    *Mitigation*: Flag warnings but continue processing; allow exclude-warned toggle
*   **Browser Download Limits**: Many individual files can trigger blocking\
    *Mitigation*: Default to a single ZIP download

*This document serves as the definitive, AI-readable specification for BBG’s Rebate Processing Automation Tool. Subsequent technical documents (database schema, API specs, frontend component architecture) will reference these clear, unambiguous requirements.*
