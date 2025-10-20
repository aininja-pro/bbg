# Backend Structure Document for BBG Rebate Processing Automation Tool

This document outlines the backend setup for the BBG Rebate Processing Automation Tool. It explains how the system is built, where it runs, and how different parts fit together. You don’t need a deep technical background to understand it.

## 1. Backend Architecture

Overall, the backend is a RESTful API built in Python. Here’s how it’s organized:

- **Framework & Patterns**
  - FastAPI handles HTTP requests and routing.
  - Pydantic models define and validate data structures.
  - A service layer separates business logic (file processing, rules engine) from API routes.
  - A repository or data-access layer manages database reads/writes.

- **Scalability & Performance**
  - Stateless design: each request is independent, so you can run multiple server instances behind a load balancer.
  - Heavy data work (Excel parsing, unpivoting, rules application) leverages Pandas for speedy in-memory transformations.
  - File uploads use streaming and chunked reads to stay within the 50 MB limit.

- **Maintainability**
  - Clear separation of concerns: API routes, processing services, and data access are in different modules.
  - Rules engine is template-driven (JSON configs), so new rule types or changes don’t require code rewrites.
  - Pydantic ensures any invalid input is caught early with helpful error messages.

## 2. Database Management

We use a SQL database to store rules, lookup tables, and activity logs. You can choose between PostgreSQL (production) or SQLite (local development).

- **Type**: Relational (SQL)
- **Systems**:
  - PostgreSQL on Render (managed service)
  - SQLite (embedded, optional for testing or small deployments)

- **Data Storage & Access**:
  - Tables for rules, lookups (members, suppliers, products), and logs.
  - SQLAlchemy (or equivalent) to map tables to Python objects.
  - JSONB column for flexible rule configurations.

- **Practices**:
  - Back up lookup tables when they’re replaced by CSV uploads.
  - Retain activity logs for 90 days, purging older entries via a scheduled job.

## 3. Database Schema

### Human-readable Overview

- **rules**: stores each rule’s type, priority, enabled flag, configuration, and timestamps.
- **lookup_members**: TradeNet members, linking `tradenet_company_id` to BBG info.
- **lookup_suppliers**: supplier directory details.
- **lookup_products**: product and program information.
- **activity_logs**: records of each processing run, with status, warnings, and errors.

### SQL Schema (PostgreSQL)

```sql
-- Rules table
drop table if exists rules;
create table rules (
  id uuid primary key,
  rule_type text not null,
  priority integer not null,
  enabled boolean not null default true,
  config jsonb not null,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now()
);

-- Lookup: TradeNet Members
drop table if exists lookup_members;
create table lookup_members (
  id serial primary key,
  tradenet_company_id text not null,
  bbg_member_id text not null,
  member_name text not null,
  last_updated timestamp with time zone not null default now()
);

-- Lookup: TradeNet Suppliers
drop table if exists lookup_suppliers;
create table lookup_suppliers (
  id serial primary key,
  tradenet_supplier_id text not null,
  supplier_name text not null,
  last_updated timestamp with time zone not null default now()
);

-- Lookup: Programs & Products
drop table if exists lookup_products;
create table lookup_products (
  id serial primary key,
  program_id text not null,
  program_name text not null,
  product_id text not null,
  product_name text not null,
  last_updated timestamp with time zone not null default now()
);

-- Activity Logs
drop table if exists activity_logs;
create table activity_logs (
  id serial primary key,
  run_timestamp timestamp with time zone not null default now(),
  status text not null,
  warnings text[],
  errors text[],
  details jsonb
);
```  

## 4. API Design and Endpoints

The API uses REST conventions. All endpoints live under `/api`.

- **File Handling**
  - POST `/api/upload` – upload `.xlsm` file (multipart/form-data). Returns a file ID.
  - POST `/api/validate` – validate structure of an uploaded file. Returns success or error details.
  - POST `/api/preview` – run the unpivot + enrichment on first N rows. Returns preview data.
  - POST `/api/transform` – full transformation. Returns a job ID for download.
  - GET `/api/download/{job_id}` – download single CSV or ZIP archive.

- **Rules Management**
  - GET `/api/rules` – list all rules in priority order.
  - POST `/api/rules` – create a new rule.
  - PUT `/api/rules/{id}` – update a rule’s fields (type, config, enabled, priority).
  - DELETE `/api/rules/{id}` – remove a rule.
  - POST `/api/rules/reorder` – adjust multiple priorities at once.

- **Lookup Management**
  - GET `/api/lookups/members|suppliers|products` – list records.
  - POST `/api/lookups/{type}/upload` – replace table via CSV upload.
  - POST `/api/lookups/{type}` – add a single record.
  - PUT `/api/lookups/{type}/{id}` – update one record.
  - DELETE `/api/lookups/{type}/{id}` – delete one record.

- **Activity Logs**
  - GET `/api/logs` – retrieve recent logs (90-day window).

## 5. Hosting Solutions

- **Backend & Database**
  - Hosted on Render.com.  
  - Managed PostgreSQL database for production.  
  - Automatic HTTPS, health checks, container auto-scaling.

- **Why Render?**
  - Quick deployments from Git.  
  - Pay-as-you-go, with free tiers for small workloads.  
  - Built-in load balancing and vertical scaling options.

## 6. Infrastructure Components

- **Load Balancer**
  - Render’s built-in router spreads requests across active instances.

- **Temporary File Storage**
  - Each instance has ephemeral disk space for processing uploads.  
  - Cleanup job removes old files hourly.

- **CDN**
  - Not needed for the backend API itself. Static assets (if any) are handled by the frontend on Vercel.

- **Scheduled Jobs**
  - Nightly tasks to purge logs older than 90 days and vacuum the database.

## 7. Security Measures

- **Transport Security**
  - HTTPS for all endpoints (Render provides TLS automatically).

- **Input Validation & Limits**
  - Pydantic schemas ensure only the expected data types and fields are accepted.
  - File size capped at 50 MB; 5-minute processing timeout enforced.

- **Data Protection**
  - Database credentials stored securely in Render environment variables.
  - JSONB fields sanitized before use.

- **CORS & Headers**
  - Strict CORS policy allowing only the frontend domain.
  - HTTP headers to prevent common browser attacks (XSS, clickjacking).

## 8. Monitoring and Maintenance

- **Health Checks & Logs**
  - Render dashboard shows real-time CPU, memory, and response times.
  - Application logs (info, warning, error) streamed to Render logs console.

- **Error Tracking**
  - Optional integration with Sentry or similar for exception alerts.

- **Maintenance Routines**
  - Automated cleanup of old logs and temp files.
  - Database vacuum and backups scheduled daily.
  
## 9. Conclusion and Overall Backend Summary

The backend for the BBG Rebate Processing Automation Tool is a Python-based, RESTful service focused on file ingestion, data transformation, and rule-driven processing. It uses a managed PostgreSQL database for storing rules, lookups, and logs. Deployed on Render, it benefits from automatic scaling, secure HTTPS, and built-in load balancing. The design emphasizes maintainability (clear layers, Pydantic models), performance (Pandas for data crunching), and flexibility (template-based rules engine). Together, these components ensure the system can handle large quarterly rebate files, adapt to changing business logic, and provide reliable, auditable results to users.