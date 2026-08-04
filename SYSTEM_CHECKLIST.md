# Compass System Checklist

Quick reference checklist for validating and starting Compass.

## 🚦 Pre-Flight Checklist

Before starting Compass, verify these items:

### Environment
- [ ] Python 3.12+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed and up to date
- [ ] In correct directory (`compass/backend` or `compass/frontend`)

### Backend Setup
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list | grep fastapi`)
- [ ] Database file exists OR ready to create
- [ ] Port 8000 available (`lsof -ti:8000` returns nothing)

### Frontend Setup
- [ ] node_modules installed (`ls node_modules`)
- [ ] Port 5173 available (`lsof -ti:5173` returns nothing)

---

## ✅ Validation Checklist

### Run These Commands

```bash
cd compass/backend

# 1. ✓ Comprehensive validation
python validate_system.py
# Expected output: "✓ ALL CHECKS PASSED - System is ready!"

# 2. ✓ Quick startup test
python test_startup.py
# Expected output: "✓ ALL TESTS PASSED (5/5)"
```

### What Each Test Checks

**validate_system.py:**
- [ ] All required files exist (45 files)
- [ ] Python dependencies installed (13 packages)
- [ ] Database schema correct (10 tables)
- [ ] Models properly defined (9 models)
- [ ] Cross-platform compatible (no hardcoded paths)
- [ ] API endpoints registered (45+ routes)
- [ ] Frontend API matches backend
- [ ] Mock data generation works

**test_startup.py:**
- [ ] All imports work
- [ ] Database can initialize
- [ ] Mock sources can be created
- [ ] Mock data can be generated
- [ ] FastAPI app can be created

---

## 🐛 Troubleshooting Checklist

If something doesn't work, check these in order:

### Common Issue 1: Database Errors
```
Error: "no such column: feedback.external_ids"
Error: "no such table: import_jobs"
```

**Fix:**
- [ ] Stop backend (Ctrl+C)
- [ ] Run: `python fix_db.py`
- [ ] Verify: Check for success message
- [ ] Restart: `python main.py`

### Common Issue 2: Import Errors
```
Error: "ModuleNotFoundError: No module named 'fastapi'"
Error: "ImportError: cannot import name 'X'"
```

**Fix:**
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Update pip: `pip install --upgrade pip`
- [ ] Install deps: `pip install -r requirements-minimal.txt`
- [ ] Verify: `pip list | grep fastapi`

### Common Issue 3: Port In Use
```
Error: "Address already in use"
Error: "[Errno 48] Address already in use"
```

**Fix (Mac/Linux):**
- [ ] Find process: `lsof -ti:8000`
- [ ] Kill process: `lsof -ti:8000 | xargs kill -9`
- [ ] Verify: `lsof -ti:8000` (should be empty)

**Fix (Windows):**
- [ ] Find process: `netstat -ano | findstr :8000`
- [ ] Kill process: `taskkill /PID <PID> /F`
- [ ] Verify: Port is free

### Common Issue 4: Database Locked
```
Error: "database is locked"
Error: "OperationalError: database is locked"
```

**Fix:**
- [ ] Kill backend: `lsof -ti:8000 | xargs kill -9`
- [ ] Remove locks: `rm -f compass.db-wal compass.db-shm`
- [ ] Restart: `python main.py`

---

## 🚀 Startup Checklist

### First Time Setup

**Backend:**
```bash
cd compass/backend

# 1. Create virtual environment
[ ] python3 -m venv venv

# 2. Activate virtual environment
[ ] source venv/bin/activate  # Mac/Linux
[ ] venv\Scripts\activate     # Windows

# 3. Install dependencies
[ ] pip install -r requirements-minimal.txt

# 4. Run validation
[ ] python validate_system.py

# 5. Start backend
[ ] python main.py
```

**Frontend:**
```bash
cd compass/frontend

# 1. Install dependencies
[ ] npm install

# 2. Start frontend
[ ] npm run dev
```

**Verify:**
- [ ] Backend running: http://localhost:8000/docs
- [ ] Frontend running: http://localhost:5173
- [ ] WebSocket connected: Green indicator in UI

---

### Daily Startup

**Terminal 1 - Backend:**
```bash
cd compass/backend
[ ] source venv/bin/activate
[ ] python test_startup.py
[ ] python main.py
```

**Terminal 2 - Frontend:**
```bash
cd compass/frontend
[ ] npm run dev
```

**Verify:**
- [ ] Backend logs show: "Uvicorn running on http://0.0.0.0:8000"
- [ ] Frontend logs show: "Local: http://localhost:5173/"
- [ ] Browser shows: Compass dashboard
- [ ] WebSocket: Green dot in top-right

---

### After Git Pull

```bash
cd compass/backend

# 1. Pull latest code
[ ] git pull origin main

# 2. Update dependencies (if requirements changed)
[ ] pip install -r requirements-minimal.txt

# 3. Fix database (if schema changed)
[ ] python fix_db.py

# 4. Validate system
[ ] python validate_system.py

# 5. Start backend
[ ] python main.py
```

---

## 📊 Health Check Checklist

### Backend Health

**Check these endpoints:**
- [ ] http://localhost:8000 - Root endpoint
- [ ] http://localhost:8000/docs - API documentation
- [ ] http://localhost:8000/api/sources - List sources
- [ ] http://localhost:8000/api/stats - Dashboard stats

**Expected responses:**
- [ ] Status code: 200
- [ ] Content-Type: application/json
- [ ] No error messages

### Frontend Health

**Check browser console (F12):**
- [ ] No red errors in console
- [ ] WebSocket connected message
- [ ] API calls succeeding

**Check UI:**
- [ ] Dashboard loads
- [ ] Navigation works
- [ ] Connection indicator is green
- [ ] Stats display correctly

### Database Health

```bash
cd compass/backend

# Check database exists
[ ] ls -la compass.db

# Check tables exist
[ ] python database.py

# Check data exists
[ ] sqlite3 compass.db "SELECT COUNT(*) FROM sources;"
```

**Expected:**
- [ ] compass.db file exists (>0 bytes)
- [ ] 10 tables created
- [ ] At least 1 source exists

---

## 🔄 Reset Checklist (Nuclear Option)

If everything is broken:

```bash
# 1. Stop all processes
[ ] Ctrl+C in backend terminal
[ ] Ctrl+C in frontend terminal

# 2. Backend reset
cd compass/backend
[ ] rm -f compass.db *.db-wal *.db-shm
[ ] rm -rf venv
[ ] python3 -m venv venv
[ ] source venv/bin/activate
[ ] pip install -r requirements-minimal.txt
[ ] python validate_system.py

# 3. Frontend reset
cd compass/frontend
[ ] rm -rf node_modules package-lock.json
[ ] npm install

# 4. Start both
# Terminal 1:
[ ] cd compass/backend && source venv/bin/activate && python main.py

# Terminal 2:
[ ] cd compass/frontend && npm run dev

# 5. Verify
[ ] http://localhost:8000/docs loads
[ ] http://localhost:5173 loads
[ ] WebSocket connects (green)
```

---

## 📝 Documentation Checklist

Have you read:
- [ ] README.md - Project overview
- [ ] TROUBLESHOOTING.md - Common issues
- [ ] backend/VALIDATION_README.md - Validation scripts
- [ ] VALIDATION_SUMMARY.md - System validation report
- [ ] This file - Quick checklists

---

## 🎯 Success Criteria

### Backend Success
- ✅ `python validate_system.py` → All tests pass
- ✅ `python test_startup.py` → All tests pass
- ✅ `python main.py` → Starts without errors
- ✅ http://localhost:8000/docs → API docs load
- ✅ Logs show: "Uvicorn running on http://0.0.0.0:8000"

### Frontend Success
- ✅ `npm run dev` → Starts without errors
- ✅ http://localhost:5173 → Dashboard loads
- ✅ Console shows: No red errors
- ✅ WebSocket indicator: Green (connected)
- ✅ Navigation: All tabs work

### Database Success
- ✅ File exists: `compass.db`
- ✅ Tables: 10 tables created
- ✅ Data: Mock sources exist
- ✅ No errors: Schema matches models

### Integration Success
- ✅ Frontend → Backend: API calls work
- ✅ Backend → Frontend: WebSocket messages received
- ✅ Backend → Database: Queries execute
- ✅ Database → Backend: Data retrieved correctly

---

## 💡 Pro Tips

### Speed Up Development
- Use `python test_startup.py && python main.py` (chain commands)
- Keep validation terminal open for quick checks
- Use `git pull origin main && python fix_db.py` after pulls

### Prevent Issues
- Run validation before commits
- Reset database after schema changes
- Check both terminals for errors
- Monitor WebSocket connection status

### Debug Efficiently
1. Check backend terminal first (most errors here)
2. Check frontend console second (API errors)
3. Check browser network tab (request/response)
4. Check database last (data issues)

---

## 🔗 Quick Links

### Local URLs
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### Documentation
- Main README: `compass/README.md`
- Troubleshooting: `compass/TROUBLESHOOTING.md`
- Validation Guide: `compass/backend/VALIDATION_README.md`
- This Checklist: `compass/SYSTEM_CHECKLIST.md`

### Scripts
- Validate System: `python backend/validate_system.py`
- Test Startup: `python backend/test_startup.py`
- Fix Database: `python backend/fix_db.py`
- Init Database: `python backend/database.py`

---

## ✅ Final Checklist Before Starting Work

Before starting development, verify:

- [ ] Git is up to date (`git pull origin main`)
- [ ] Virtual environment activated
- [ ] Dependencies installed (run `pip list`)
- [ ] Validation passes (`python validate_system.py`)
- [ ] Backend starts (`python main.py`)
- [ ] Frontend starts (`npm run dev`)
- [ ] Both accessible in browser
- [ ] WebSocket connected (green indicator)
- [ ] API docs accessible
- [ ] No console errors

**If all checked: ✅ You're ready to develop!**

---

**Last Updated:** 2026-08-04
**Platform Support:** Windows, macOS, Linux
**Validation Tools:** 3 automated scripts
