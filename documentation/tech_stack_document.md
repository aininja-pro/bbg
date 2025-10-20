# Tech Stack Document for BBG Rebate Processing Automation Tool

This document explains the technology choices behind the BBG Rebate Processing Automation Tool in everyday language. It shows how each part fits together to make a fast, reliable, and easy-to-use web app for converting rebate Excel files into clean, validated CSVs.

---

## 1. Frontend Technologies

We chose modern web tools to give users a smooth, responsive experience:

- **React 18+**
  • A popular JavaScript library for building fast single-page apps.  
  • Lets us update parts of the screen quickly without reloading the page.

- **Tailwind CSS**
  • A utility-first CSS framework.  
  • Makes it easy to style buttons, tables, and forms in a consistent way without writing custom CSS from scratch.

- **shadcn/ui components**
  • A set of pre-built, accessible UI elements (modals, tabs, buttons) that work well with Tailwind.  
  • Speeds up development and keeps the interface look-and-feel unified.

- **React Dropzone**
  • A small library that handles drag-and-drop file uploads.  
  • Provides a clean upload area where users can drop one or many Excel files.

- **TanStack Table or AG Grid**
  • Advanced table libraries for previewing data.  
  • Offer sorting, filtering, and custom cell rendering so users can review the first 10–20 rows before export.

How they enhance user experience:
- Instant feedback on uploads and processing progress  
- Clean, mobile-responsive layout  
- Accessible components (keyboard navigation, screen-reader friendly)  
- Easy previews and inline editing for rules and lookup tables

---

## 2. Backend Technologies

The server side handles file reading, data transformation, rule application, lookups, and CSV generation:

- **Python 3.11+**
  • A modern, high-performance version of Python.

- **FastAPI**
  • A lightweight, high-speed web framework.  
  • Automatically generates API docs and validates request/response data.

- **Pandas**
  • A powerful data-processing library.  
  • Handles the unpivot logic, filtering, concatenation, and batch transformations efficiently.

- **openpyxl**
  • Reads and writes Excel files, including macro-enabled `.xlsm` sheets.  
  • Lets us extract hidden tabs, specific cells (B6, B7), and detect header rows.

- **Pydantic**
  • Validates incoming data structures (file metadata, API payloads).  
  • Catches structural errors (missing tabs, invalid cells) early.

- **PostgreSQL (or SQLite for small installs)**
  • Stores user-managed rules and lookup tables for members, suppliers, and products.  
  • Provides fast lookups during transformation.

- **Python’s built-in zipfile library**
  • Packages individual CSVs into a single ZIP for batch downloads.

How these work together:
1. User uploads `.xlsm` files via FastAPI endpoints.  
2. openpyxl reads the hidden “reformatter” sheet and extracts metadata.  
3. Pandas unpivots and applies business-logic rules (search/replace, if/then, filters, concatenations).  
4. The DB provides lookup data to enrich each row.  
5. Final rows are formatted into a 15-column DataFrame and exported as CSV(s).  
6. zipfile bundles individual files into a ZIP when needed.

---

## 3. Infrastructure and Deployment

Our goal is a smooth developer workflow and rock-solid production environment:

- **Version Control: Git & GitHub**
  • All code lives in a GitHub repo.  
  • Branch protection and pull-request reviews maintain quality.

- **CI/CD Pipelines (GitHub Actions)**
  • On every push to `main`, run tests and lint checks.  
  • Automatically deploy the backend to Render and the frontend to Vercel when tests pass.

- **Backend Hosting: Render**
  • Hosts the FastAPI service and PostgreSQL database.  
  • Provides automatic HTTPS, health checks, and autoscaling options.

- **Frontend Hosting: Vercel**
  • Hosts the React app with edge caching for fast global delivery.  
  • Automatically rebuilds on new commits.

Why this matters:
- **Reliability**: Automatic health monitoring and quick rollbacks.  
- **Scalability**: Handle multiple users and batch jobs without manual intervention.  
- **Developer Velocity**: One command from commit to live site, consistent environments.

---

## 4. Third-Party Integrations

In Phase 1, the app is self-contained and uses open-source libraries. No external payment or analytics services are integrated yet. Key integrated tools include:

- **Node.js & npm packages** for React, Tailwind, shadcn/ui, Dropzone, and table libraries.  
- **Python pip libraries** for FastAPI, Pandas, openpyxl, Pydantic.  
- **Render & Vercel APIs** for deployment hooks.

Future phases may add:
- **SendGrid or Mailgun** for email notifications  
- **Slack Webhooks** for team alerts  
- **Sentry or Logtail** for error tracking  

---

## 5. Security and Performance Considerations

We designed the stack with safe defaults and room to grow:

Security Measures:
- **Input Validation**: Pydantic models check file structure, cell presence, and data types before processing.  
- **File Type & Size Checks**: Only `.xlsm` files up to 50 MB are accepted to prevent abuse.  
- **HTTPS Everywhere**: All traffic is encrypted.  
- **Environment Variables**: Secrets (DB URLs, API keys) are never committed to code.  
- **No Public Access**: Phase 1 is an internal tool behind a private URL.

Performance Optimizations:
- **Pandas Vectorized Operations**: Unpivot and rule application happen in memory at C speed.  
- **Asynchronous Endpoints**: FastAPI handles concurrent uploads without blocking.  
- **Server Timeouts**: Configured to 5 minutes per request to handle large batches.  
- **Stateless Processing**: No server-side sessions—each request is isolated for easier scaling.

---

## 6. Conclusion and Overall Tech Stack Summary

Everything is chosen to meet these goals:
- **Speed**: Process one file in under 2 minutes, batch dozens of files in parallel.  
- **Flexibility**: Business users manage rules and lookups—no code changes needed.  
- **Reliability**: Clear validation, real-time feedback, and warning flags ensure zero surprises in FMS imports.  
- **Maintainability**: Popular frameworks and libraries reduce technical debt.  
- **Scalability**: CI/CD pipelines and cloud hosting let us grow from 3 users to many more.

Unique strengths of our stack:
- A **template-based rules engine** built on JSON and database storage, enabling non-technical updates.  
- A **self-service lookup management** UI for members, suppliers, and products.  
- A **clean separation** between a stateless FastAPI backend and a responsive React frontend.

With this foundation, the BBG team can quickly transform rebate Excel files into error-free CSVs, adapt to changing business rules, and focus on their core work—helping members save time and reduce mistakes.