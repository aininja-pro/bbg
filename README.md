# BBG Rebate Processing Automation Tool

A web-based pipeline that automatically processes quarterly rebate submission Excel files (.xlsm) for Builders Buying Group, transforming manual data entry from weeks to minutes.

## Project Overview

BBG processes over 600 quarterly rebate submission Excel files by hand, spending up to three weeks per quarter on error-prone data entry. This tool automates the entire pipeline:

- **Excel Ingestion**: Validates and processes .xlsm files
- **Data Transformation**: Unpivots wide format to long format, enriches data via lookup tables
- **Rules Engine**: No-code business logic management for staff
- **Export**: Clean CSVs ready for direct FMS import

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- Pandas & openpyxl
- PostgreSQL
- Hosted on Render.com

### Frontend
- React 18+
- TailwindCSS + shadcn/ui
- React Dropzone
- TanStack Table
- Hosted on Vercel

## Project Structure

```
BBG/
├── backend/           # FastAPI backend service
├── frontend/          # React frontend application
└── documentation/     # Project requirements and specs
```

## Development

See individual README files in `backend/` and `frontend/` directories for setup instructions.

## Documentation

Complete project documentation is available in the `documentation/` folder:
- Project Requirements Document (PRD)
- Technical Stack Document
- API & Database Schema
- App Flow & User Journey
- Security Guidelines

## Goals

- Process files in <2 minutes each
- Zero FMS import failures
- Self-service rule management
- Batch processing support (50+ files)
