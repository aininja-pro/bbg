# Development Environment Setup

Complete guide to setting up your development environment for the BBG Rebate Processing Tool.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Download |
|----------|---------|----------|
| **Python** | 3.12+ | https://www.python.org/downloads/ |
| **Node.js** | 20+ (LTS) | https://nodejs.org/ |
| **Git** | Latest | https://git-scm.com/downloads |
| **Code Editor** | Any | VS Code recommended |

### Verify Installations

```bash
# Check Python
python3 --version
# Should show: Python 3.12.x

# Check Node.js
node --version
# Should show: v20.x.x or higher

# Check npm
npm --version
# Should show: 10.x.x or higher

# Check Git
git --version
# Should show: git version 2.x.x
```

### Operating System

This guide covers:
- **macOS** (primary)
- **Windows** (with notes for differences)
- **Linux** (similar to macOS)

---

## Initial Setup

### 1. Clone the Repository

```bash
# Navigate to your projects folder
cd ~/Desktop/Projects  # or wherever you keep projects

# Clone the repository
git clone https://github.com/aininja-pro/bbg.git

# Enter the project directory
cd bbg
```

### 2. Verify Project Structure

```bash
# Check that you have these folders
ls -la

# Should see:
# backend/
# frontend/
# docs/
# README.md
# PROJECT_STATUS.md
# mkdocs.yml
```

---

## Backend Setup

### 1. Navigate to Backend Folder

```bash
cd backend
```

### 2. Create Python Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
```

**Windows:**
```bash
python -m venv venv
```

This creates an isolated Python environment in the `venv/` folder.

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**You'll know it worked when you see `(venv)` at the start of your terminal prompt.**

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- openpyxl
- pandas
- And all other dependencies

**Installation takes 2-5 minutes.**

### 5. Verify Backend Installation

```bash
python3 -c "import fastapi; import uvicorn; print('Backend dependencies installed successfully!')"
```

Should print: `Backend dependencies installed successfully!`

---

## Frontend Setup

### 1. Navigate to Frontend Folder

```bash
cd ../frontend  # From backend folder
# Or from project root: cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

This installs:
- React
- Vite
- TailwindCSS
- And all other dependencies

**Installation takes 1-3 minutes.**

### 3. Verify Frontend Installation

```bash
npm list react vite tailwindcss --depth=0
```

Should show versions of react, vite, and tailwindcss.

---

## Database Setup

### 1. Navigate to Backend Folder

```bash
cd ../backend  # From frontend folder
```

### 2. Activate Virtual Environment

If not already activated:
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 3. Seed the Database

The database will be created automatically when you run the seed scripts.

#### Load Members and Suppliers

You need the lookup CSV files. If you have them:

```bash
# Make sure the CSV files are available
# Members: TradeNet - Members (1).csv
# Suppliers: TradeNet Supplier Directory (1).csv

python3 seed_real_data.py
```

**Output should show:**
```
Seeded 911 members
Seeded 91 suppliers
Database seeded successfully!
```

#### Load Business Rules

```bash
python3 seed_rules.py
```

**Output should show:**
```
Seeded 8 business rules
Rules seeded successfully!
```

### 4. Verify Database Created

```bash
ls -la bbg_rebates.db
```

Should see a file sized ~500KB or larger.

**If Database Needs Reset:**
```bash
rm bbg_rebates.db
python3 seed_real_data.py
python3 seed_rules.py
```

---

## Running the Application

You'll need **THREE terminal windows** (or tabs).

### Terminal 1: Backend Server

```bash
# Navigate to backend folder
cd /path/to/bbg/backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start backend server
uvicorn app.main:app --reload --port 8001
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/bbg/backend']
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend is now running at:** http://localhost:8001

**Leave this terminal running. Don't close it.**

### Terminal 2: Frontend Server

```bash
# Navigate to frontend folder
cd /path/to/bbg/frontend

# Start frontend dev server
npm run dev -- --port 5174
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5174/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Frontend is now running at:** http://localhost:5174

**Leave this terminal running. Don't close it.**

### Terminal 3: Documentation (Optional)

```bash
# Navigate to project root
cd /path/to/bbg

# Start MkDocs server
python3 -m mkdocs serve
```

**Expected Output:**
```
INFO    -  Building documentation...
INFO    -  Cleaning site directory
INFO    -  Documentation built in 0.23 seconds
INFO    -  [timestamp] Serving on http://127.0.0.1:8000/
```

**Documentation is now at:** http://localhost:8000

---

## Verification

### 1. Check Backend API

Open your browser and go to:
```
http://localhost:8001/docs
```

You should see the **FastAPI interactive API documentation** (Swagger UI).

**Try:**
- Click on `GET /health`
- Click "Try it out"
- Click "Execute"
- Should return: `{"status": "healthy", ...}`

### 2. Check Frontend

Open your browser and go to:
```
http://localhost:5174
```

You should see the **BBG Rebate Processing Tool** interface with three tabs:
- Upload & Process
- Rules Engine
- Lookup Tables

### 3. Test Full Workflow

**Upload a Test File:**

1. Go to http://localhost:5174
2. Click or drag an Excel file (.xlsm) to the upload area
3. Click **Process & Preview**
4. Wait for processing (should take 5-30 seconds)
5. See preview with data
6. Click **Download CSV**
7. Open downloaded CSV in Excel to verify

**If this works, your setup is complete! 🎉**

---

## Troubleshooting

### Backend Issues

#### Issue: `ModuleNotFoundError: No module named 'fastapi'`

**Cause:** Virtual environment not activated or dependencies not installed.

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

---

#### Issue: `Port 8001 already in use`

**Cause:** Another process is using port 8001.

**Solution 1 - Use different port:**
```bash
uvicorn app.main:app --reload --port 8002
```

Then update frontend API URL in `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8002'
```

**Solution 2 - Kill the process:**

macOS/Linux:
```bash
lsof -ti:8001 | xargs kill -9
```

Windows:
```bash
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

---

#### Issue: `Database is locked`

**Cause:** SQLite database is being accessed by multiple processes.

**Solution:**
```bash
# Stop all backend processes
# Restart backend server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

---

### Frontend Issues

#### Issue: `npm: command not found`

**Cause:** Node.js not installed or not in PATH.

**Solution:**
1. Install Node.js from https://nodejs.org/
2. Restart terminal
3. Verify: `node --version`

---

#### Issue: `Port 5174 already in use`

**Cause:** Another Vite server is running.

**Solution 1 - Use different port:**
```bash
npm run dev -- --port 5175
```

**Solution 2 - Kill the process:**

macOS/Linux:
```bash
lsof -ti:5174 | xargs kill -9
```

Windows:
```bash
netstat -ano | findstr :5174
taskkill /PID <PID> /F
```

---

#### Issue: `Failed to fetch` errors in browser console

**Cause:** Backend not running or CORS issue.

**Solution:**
1. Check backend is running at http://localhost:8001
2. Check backend terminal for errors
3. Verify CORS settings in `backend/app/main.py`:
   ```python
   allow_origins=["http://localhost:5173", "http://localhost:5174"]
   ```

---

### Database Issues

#### Issue: No data in lookup tables

**Cause:** Database not seeded.

**Solution:**
```bash
cd backend
source venv/bin/activate
python3 seed_real_data.py
python3 seed_rules.py
```

---

#### Issue: `FileNotFoundError: TradeNet CSV not found`

**Cause:** Seed scripts can't find the CSV files.

**Solution:**
1. Download CSV files from TradeNet
2. Place in `~/Downloads/` or update paths in seed scripts
3. Or manually create database entries via API

---

### File Processing Issues

#### Issue: `Required sheet 'Usage-Reporting' not found`

**Cause:** Uploaded file is not the correct BBG template.

**Solution:**
- Use a test file from the correct template
- Verify Excel file has sheets: "Usage-Reporting" and "Programs-Products"

---

#### Issue: Processing takes too long (> 1 minute for small file)

**Cause:** Performance issue or blocking operation.

**Solution:**
- Check backend terminal for errors
- Check file size (should be < 50MB)
- Restart backend server

---

## Development Tools

### Recommended VS Code Extensions

- **Python** - Python language support
- **Pylance** - Python language server
- **ES7+ React/Redux/React-Native snippets** - React snippets
- **Tailwind CSS IntelliSense** - Tailwind autocomplete
- **ESLint** - JavaScript linting
- **Prettier** - Code formatting

### VS Code Settings

Create `.vscode/settings.json` in project root:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### Useful Commands

```bash
# Check all running servers
lsof -i :8001  # Backend
lsof -i :5174  # Frontend
lsof -i :8000  # MkDocs

# View backend logs in real-time
# (already visible in backend terminal)

# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Reset virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Clear MkDocs cache
rm -rf site/
```

---

## Environment Variables

### Backend Environment

Currently uses defaults in `backend/app/config.py`. No `.env` file needed for local development.

**Default values:**
- `API_HOST`: "0.0.0.0"
- `API_PORT`: 8001
- `DATABASE_URL`: "sqlite:///./bbg_rebates.db"
- `DEBUG`: True

**To customize:** Create `backend/.env`:
```env
API_HOST=127.0.0.1
API_PORT=8001
DEBUG=True
DATABASE_URL=sqlite:///./bbg_rebates.db
```

### Frontend Environment

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8001
```

**Note:** Changes to `.env` require restarting the dev server.

---

## Next Steps

Now that your environment is set up:

1. **Read the codebase:**
   - Start with `backend/app/main.py`
   - Look at `frontend/src/App.jsx`
   - Trace through a file upload request

2. **Make a test change:**
   - Edit a frontend component
   - See it hot-reload in the browser
   - Edit backend code
   - See uvicorn restart automatically

3. **Explore the APIs:**
   - Use FastAPI docs at http://localhost:8001/docs
   - Test endpoints directly
   - See request/response formats

4. **Read other dev docs:**
   - [Developer Overview](developer-overview.md)
   - [API Reference](api-reference.md)
   - [Database Schema](database-schema.md)

---

## Quick Reference

### Start Development Session

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend && npm run dev -- --port 5174

# Terminal 3 - Documentation (optional)
python3 -m mkdocs serve
```

### Stop Development Session

Press `Ctrl+C` in each terminal.

### Reset Everything

```bash
# Reset database
cd backend
source venv/bin/activate
rm bbg_rebates.db
python3 seed_real_data.py
python3 seed_rules.py

# Reset frontend
cd ../frontend
rm -rf node_modules
npm install

# Reset backend packages
cd ../backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

**Environment setup complete!** You're ready to start developing. Check out the [Developer Overview](developer-overview.md) for architecture details.
