# Compass Troubleshooting Guide

## 🔥 Quick Fix for Database Errors

If you're seeing errors like "no such column: feedback.external_ids", the database schema is out of sync.

### Solution 1: Use the Fix Script (Recommended - Works on All Platforms)

```bash
cd compass/backend

# Stop backend if running (Ctrl+C)

# Run the fix script (works on Windows, Mac, Linux)
python fix_db.py

# Restart backend - it will create fresh database
python main.py
```

### Solution 2: Manual Fix

```bash
cd compass/backend

# Stop backend if running (Ctrl+C)

# Delete old database
rm -f compass.db           # Mac/Linux
# or
del compass.db             # Windows

# Pull latest code
git pull origin main

# Restart backend - it will create fresh database
python main.py
```

That's it! The backend automatically creates the database with correct schema on startup.

## 🧪 Validation Script

To check if your system is set up correctly, run:

```bash
cd compass/backend
python validate_system.py
```

This comprehensive script checks:
- All required files exist
- Database schema is correct
- Python dependencies are installed
- Cross-platform compatibility
- API endpoints are defined
- Frontend integration
- Mock data generation works

**Example output:**
```
[1/8] Validating File Structure...
  ✓ File: backend/main.py
  ✓ File: backend/models.py
  ...
[2/8] Checking Python Dependencies...
  ✓ Dependency: fastapi
  ...
VALIDATION SUMMARY
Tests Run: 45
Passed: 45
Failed: 0
✓ ALL CHECKS PASSED - System is ready!
```

---

## 🎯 Common Error Patterns & Solutions

### Database Schema Mismatch

**Error Messages:**
- `no such column: feedback.external_ids`
- `no such table: import_jobs`
- `no such table: linear_issues`

**Cause:** Database file was created with an old schema version.

**Solution:**
```bash
cd compass/backend
python fix_db.py
python main.py
```

### Import Errors

**Error Messages:**
- `ModuleNotFoundError: No module named 'fastapi'`
- `ImportError: cannot import name 'X' from 'Y'`

**Cause:** Missing Python dependencies.

**Solution:**
```bash
cd compass/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install --upgrade -r requirements-minimal.txt
```

### Path Errors (Windows-Specific)

**Error Messages:**
- `FileNotFoundError: [Errno 2] No such file or directory`
- Path separator issues

**Cause:** Windows uses different path separators.

**Solution:** All scripts now use `pathlib.Path` for cross-platform compatibility. If you see this error, make sure you're running the latest version:
```bash
git pull origin main
```

### Database Locked

**Error Messages:**
- `database is locked`
- `OperationalError: database is locked`

**Cause:** Another process is accessing the database, or previous process didn't close properly.

**Solution:**
```bash
# Kill any running backend processes
# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Delete lock files
cd compass/backend
rm -f compass.db-wal compass.db-shm
```

## Common Issues & Fixes

### 1. Backend Won't Start

**Error**: Import errors, module not found, etc.

```bash
cd ~/compass/backend

# Reinstall dependencies
source venv/bin/activate
pip install --upgrade -r requirements-minimal.txt

# If still issues, recreate venv
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

### 2. Frontend Shows Blank Page

**Check browser console** (F12 → Console tab) for errors.

**Common fixes:**

```bash
cd ~/compass/frontend

# Pull latest
git pull origin main

# Clear and reinstall
rm -rf node_modules package-lock.json
npm install

# Restart
npm run dev
```

### 3. Database Schema Errors

**Errors mentioning "no such column", "no such table", etc.**

```bash
cd ~/compass/backend

# Nuclear option - delete and recreate
rm -f compass.db
python main.py
```

### 4. Port Already in Use

```bash
# Kill backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Kill frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

### 5. WebSocket Connection Errors

Frontend can't connect to WebSocket?

1. Make sure backend is running on port 8000
2. Check browser console for connection errors
3. Backend logs should show WebSocket connection

### 6. Mock Data Not Generating

If clicking "Generate Mock Data" does nothing:

1. Check backend logs for errors
2. Try manual sync: `curl -X POST http://localhost:8000/api/sources/sync`
3. Check database: `sqlite3 compass.db "SELECT COUNT(*) FROM feedback"`

---

## Starting Fresh (Clean Slate)

If everything is broken, start completely fresh:

```bash
# 1. Stop everything (Ctrl+C on both terminals)

# 2. Pull latest code
cd ~/compass
git pull origin main

# 3. Backend fresh start
cd ~/compass/backend
rm -f compass.db
source venv/bin/activate
pip install -r requirements-minimal.txt
python main.py

# 4. Frontend fresh start (new terminal)
cd ~/compass/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev

# 5. Open browser
# http://localhost:5173
```

---

## Verification Checklist

✅ Backend running on http://localhost:8000
- Visit http://localhost:8000/docs to see API docs
- Should see "Compass API" documentation page

✅ Frontend running on http://localhost:5173
- Should see Compass dashboard with header
- Connection indicator should be green (connected)

✅ WebSocket connected
- Green dot in top right of frontend
- Backend logs show "Client connected"

✅ Database created
- File `compass.db` exists in backend folder
- Run `sqlite3 compass.db ".tables"` - should see: sources, feedback, clusters, etc.

---

## Expected Backend Logs (Good State)

```
⚠️  NLP dependencies not installed. Using simplified clustering.
⚠️  Sentiment analysis dependencies not installed. Using simplified analysis.
INFO:websockets:WebSocket ConnectionManager initialized
INFO:events:EventEmitter initialized
Starting Compass API server...
🚀 Starting Compass API...
Database initialized at: compass.db
Creating mock sources...
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Expected Frontend Logs (Good State)

```
VITE v5.0.12  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## Environment Info

- **Python**: 3.12+
- **Node**: 18+
- **OS**: macOS
- **Database**: SQLite (compass.db)
- **Backend Port**: 8000
- **Frontend Port**: 5173

---

## Files to Check

If something is wrong, check these files exist:

```
backend/
  compass.db          ← Database file (auto-created)
  main.py             ← Backend entry point
  models.py           ← Database schema
  venv/               ← Python virtual environment

frontend/
  node_modules/       ← npm packages
  src/
    App.jsx           ← Main app component
    services/
      api.js          ← API client
      websocket.js    ← WebSocket client
```

---

## Need More Help?

1. Check backend terminal for error messages
2. Check frontend terminal for error messages
3. Check browser console (F12) for JavaScript errors
4. Take screenshot of error and describe what you were doing

---

## Tomorrow's Startup Commands

```bash
# Terminal 1 - Backend
cd ~/compass/backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd ~/compass/frontend
npm run dev

# Browser
# Open: http://localhost:5173
```

---

## What Should Work Right Now

✅ Dashboard loads with clean UI
✅ WebSocket connection indicator (top right)
✅ Navigation tabs (Overview, Feedback, Insights, Roadmap, Priority Analysis)
✅ Backend API docs at http://localhost:8000/docs
✅ Generate Mock Data button (creates 500+ feedback entries)
✅ Run Clustering (groups similar feedback)
✅ Generate Roadmap (prioritizes features)

---

## What's Implemented

- ✅ 8+ feedback sources (Slack, GitHub, Discord, Reddit, Zendesk, Intercom, Email, Support)
- ✅ NLP clustering with fallback
- ✅ Priority calculation with advanced scoring
- ✅ Real-time WebSocket updates
- ✅ Historical data import (Zendesk, Intercom, CSV)
- ✅ Jira/Linear bidirectional sync
- ✅ PWA (installable on mobile)
- ✅ Priority Analysis tab
- ✅ Python & TypeScript SDKs
- ✅ Comprehensive API docs

Sleep well! Everything will work tomorrow. 🚀

---

## 🛠️ Using the Database Fix Script

The `fix_db.py` script is a universal tool that works on all platforms (Windows, Mac, Linux).

### What it does:

1. Finds and deletes old database files (compass.db and any *.db files)
2. Verifies models.py can be loaded
3. Confirms all required models are defined
4. Provides clear next steps

### Usage:

```bash
cd compass/backend
python fix_db.py
```

### When to use it:

- Database schema errors
- "no such column" errors
- "no such table" errors
- After pulling new code that changes database schema
- When starting fresh

### What it checks:

```
✅ Deleted old database: compass.db
✅ models.py loaded successfully
  ✓ Source model found
  ✓ Feedback model found
  ✓ Cluster model found
  ✓ RoadmapItem model found
  ✓ ImportJob model found
  ✓ JiraIssue model found
  ✓ LinearIssue model found
```

---

## 🧪 Using the Validation Script

The `validate_system.py` script performs comprehensive system validation.

### What it checks:

1. **File Structure** - All required files exist
2. **Python Dependencies** - Critical and optional packages
3. **Database Schema** - All tables and columns are correct
4. **Model Integrity** - SQLAlchemy models are properly defined
5. **Cross-Platform Compatibility** - No hardcoded paths
6. **API Endpoints** - All critical endpoints are defined
7. **Frontend Integration** - API client matches backend
8. **Mock Data Generation** - Data generation works

### Usage:

```bash
cd compass/backend
python validate_system.py
```

### Sample Output:

```
======================================================================
COMPASS SYSTEM VALIDATION
======================================================================
Root directory: /home/user/compass
Backend directory: /home/user/compass/backend
Frontend directory: /home/user/compass/frontend

[1/8] Validating File Structure...
  ✓ File: backend/main.py
  ✓ File: backend/models.py
  ✓ File: backend/database.py
  ...

[2/8] Checking Python Dependencies...
  ✓ Dependency: fastapi
  ✓ Dependency: uvicorn
  ✓ Dependency: sqlalchemy
  ...

[3/8] Validating Database Schema...
  ✓ Table: sources (9 columns)
  ✓ Table: feedback (14 columns)
  ✓ Column: feedback.external_ids
  ...

[4/8] Checking Model Integrity...
  ✓ Model: Source (Table: sources)
  ✓ Model: Feedback (Table: feedback)
  ...

[5/8] Checking Cross-Platform Compatibility...
  ✓ Path compatibility (No hardcoded path separators found)
  ✓ Database path (Database path is relative)

[6/8] Validating API Endpoints...
  ✓ Endpoint: GET /api/sources
  ✓ Endpoint: POST /api/sources/sync
  ✓ Endpoint: GET /api/feedback
  ...

[7/8] Checking Frontend Integration...
  ✓ Frontend API: getSources
  ✓ Frontend API: syncSources
  ✓ Environment variables (Frontend uses environment variables for API URL)
  ...

[8/8] Testing Mock Data Generation...
  ✓ Mock data generation (Generated 1 feedback items successfully)

======================================================================
VALIDATION SUMMARY
======================================================================
Tests Run: 45
Passed: 45
Failed: 0
Warnings: 0

✓ ALL CHECKS PASSED - System is ready!
```

### When to use it:

- After fresh installation
- Before starting development
- After updating code
- When troubleshooting issues
- To verify cross-platform setup
- Before deploying to new environment

### Error Handling:

If validation fails, the script provides:
- Clear error messages
- Specific file/function that failed
- Recommended fixes
- Common troubleshooting steps

---

## 📋 Pre-Flight Checklist

Before starting Compass, run through this checklist:

### Backend Setup
```bash
cd compass/backend

# 1. Check Python version (needs 3.12+)
python --version

# 2. Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install/update dependencies
pip install -r requirements-minimal.txt

# 4. Run validation
python validate_system.py

# 5. If database issues, run fix script
python fix_db.py

# 6. Start backend
python main.py
```

### Frontend Setup
```bash
cd compass/frontend

# 1. Check Node version (needs 18+)
node --version

# 2. Install dependencies
npm install

# 3. Start frontend
npm run dev
```

### Verify Running
- Backend API docs: http://localhost:8000/docs
- Frontend app: http://localhost:5173
- WebSocket: Green indicator in top-right of UI

---

## 🚨 Emergency Reset (Nuclear Option)

If everything is completely broken and nothing works:

```bash
# 1. Stop all processes (Ctrl+C in both terminals)

# 2. Navigate to compass directory
cd ~/compass

# 3. Pull latest code
git pull origin main

# 4. Backend reset
cd backend
rm -f compass.db *.db-wal *.db-shm
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-minimal.txt
python validate_system.py
python main.py

# 5. Frontend reset (in new terminal)
cd compass/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

This completely resets everything to a clean state.
