# Compass Validation & Testing Scripts

This directory contains several scripts to validate, test, and fix your Compass installation.

## 🧪 Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `validate_system.py` | Comprehensive system validation | Before starting development, after updates |
| `test_startup.py` | Quick startup test | Before deploying, in CI/CD |
| `fix_db.py` | Database cleanup and reset | Database schema errors, "no such column" errors |
| `database.py` | Initialize database manually | First-time setup, schema inspection |
| `test_imports.py` | Test module imports | After adding new integrations |

## 📋 Detailed Guide

### 1. validate_system.py - Comprehensive Validation

**What it does:**
- Validates complete file structure (all required files exist)
- Checks Python dependencies (critical and optional)
- Validates database schema (all tables and columns correct)
- Checks model integrity (SQLAlchemy models properly defined)
- Validates cross-platform compatibility (no hardcoded paths)
- Tests API endpoints (all critical endpoints defined)
- Checks frontend integration (API client matches backend)
- Tests mock data generation (data can be generated)

**Usage:**
```bash
cd compass/backend
python validate_system.py
```

**Example Output:**
```
======================================================================
COMPASS SYSTEM VALIDATION
======================================================================

[1/8] Validating File Structure...
  ✓ File: backend/main.py
  ✓ File: backend/models.py
  ✓ File: backend/database.py
  ...

[2/8] Checking Python Dependencies...
  ✓ Dependency: fastapi
  ✓ Dependency: uvicorn
  ⚠ Optional: torch (Optional dependency not installed)
  ...

[3/8] Validating Database Schema...
  ✓ Table: sources (9 columns)
  ✓ Table: feedback (14 columns)
  ✓ Column: feedback.external_ids
  ...

[8/8] Testing Mock Data Generation...
  ✓ Mock data generation (Generated 1 feedback items successfully)

======================================================================
VALIDATION SUMMARY
======================================================================
Tests Run: 45
Passed: 43
Failed: 0
Warnings: 2

✓ All critical checks passed (with warnings)
```

**Exit Codes:**
- `0` - All tests passed
- `1` - Some tests failed

**Best Practices:**
- Run after pulling new code
- Run before starting a new development session
- Run after installing dependencies
- Include in CI/CD pipeline

---

### 2. test_startup.py - Quick Startup Test

**What it does:**
- Tests all imports work
- Tests database can be initialized
- Tests mock sources can be created
- Tests mock data generation works
- Tests FastAPI app can be created

**Usage:**
```bash
cd compass/backend
python test_startup.py
```

**Example Output:**
```
======================================================================
COMPASS BACKEND STARTUP TEST
======================================================================

[1/5] Testing imports...
  ✓ Core dependencies imported
  ✓ Database models imported
  ✓ Database utilities imported
  ✓ Application components imported

[2/5] Testing database initialization...
  ✓ Database initialized
  ✓ All 10 tables created

[3/5] Testing mock source creation...
  ✓ Created 8 mock sources

[4/5] Testing mock data generation...
  ✓ Generated 5 valid feedback items

[5/5] Testing API app creation...
  ✓ FastAPI app created
  ✓ Found 45 API routes

======================================================================
TEST SUMMARY
======================================================================
✓ PASS     Imports
✓ PASS     Database Init
✓ PASS     Mock Sources
✓ PASS     Mock Data
✓ PASS     API App

======================================================================
✓ ALL TESTS PASSED (5/5)

✅ Backend is ready to start!

Next step: python main.py
```

**When to Use:**
- Quick pre-flight check before starting backend
- In CI/CD pipelines (faster than full validation)
- After making changes to core modules
- To verify backend will start without actually starting server

**Advantages:**
- Faster than full validation (~10 seconds vs ~30 seconds)
- Tests actual startup sequence
- No external dependencies (doesn't test frontend)
- Safe to run multiple times (uses test database)

---

### 3. fix_db.py - Database Fix Script

**What it does:**
- Finds all database files (compass.db, *.db)
- Verifies models.py loads correctly
- Checks all required models exist
- Deletes old database files
- Provides clear next steps

**Usage:**
```bash
cd compass/backend
python fix_db.py
```

**Example Output:**
```
🔧 Compass Database Fix Script
==================================================
Working directory: /home/user/compass/backend

Verifying database models...
✅ models.py loaded successfully
  ✓ Source model found
  ✓ Feedback model found
  ✓ Cluster model found
  ✓ RoadmapItem model found
  ✓ ImportJob model found
  ✓ JiraIssue model found
  ✓ LinearIssue model found

Cleaning up old database files...
✅ Deleted old database: compass.db

✅ Database cleanup complete!

📋 Next steps:
   1. Start backend: python main.py
   2. Fresh database will be created automatically with correct schema
   3. Visit http://localhost:8000/docs to verify API is running
```

**When to Use:**
- "no such column" errors
- "no such table" errors
- Database schema mismatch errors
- After pulling code with schema changes
- When starting completely fresh

**What it Does NOT Do:**
- Does NOT backup your data (deletes old database)
- Does NOT migrate data (complete reset)
- Does NOT start the backend (you must start it)

**Cross-Platform:**
- Uses `pathlib.Path` for Windows/Mac/Linux compatibility
- Handles different path separators automatically
- Works with virtual environments on all platforms

---

### 4. database.py - Manual Database Initialization

**What it does:**
- Creates database with correct schema
- Shows all tables created
- Displays column details for each table

**Usage:**
```bash
cd compass/backend
python database.py
```

**Example Output:**
```
Initializing Compass database...
✓ Database initialized at sqlite:///compass.db

✓ Created tables: sources, feedback, clusters, roadmap_items, import_jobs, jira_issues, linear_issues, releases, feature_builds, feature_release_mapping

Database schema:

sources:
  - id: INTEGER
  - name: VARCHAR(100)
  - source_type: VARCHAR(50)
  - is_active: BOOLEAN
  - config: JSON
  - created_at: DATETIME
  - last_synced_at: DATETIME

feedback:
  - id: INTEGER
  - source_id: INTEGER
  - text: TEXT
  - title: VARCHAR(500)
  - customer_name: VARCHAR(200)
  - customer_revenue: FLOAT
  - sentiment_score: FLOAT
  - submitted_at: DATETIME
  - ingested_at: DATETIME
  - cluster_id: INTEGER
  - embedding: JSON
  - source_metadata: JSON
  - external_ids: JSON
  ...
```

**When to Use:**
- First-time database setup
- Inspecting database schema
- Verifying table structure
- Educational purposes (learning schema)

---

### 5. test_imports.py - Integration Module Test

**What it does:**
- Tests new model imports (ImportJob, JiraIssue, LinearIssue)
- Tests importer module imports
- Tests integration module imports
- Tests database schema includes new tables
- Tests FastAPI imports for new features

**Usage:**
```bash
cd compass/backend
python test_imports.py
```

**When to Use:**
- After adding new integration modules
- After schema changes
- Verifying new features are properly integrated

---

## 🎯 Recommended Workflow

### Fresh Installation
```bash
cd compass/backend

# 1. Install dependencies
pip install -r requirements-minimal.txt

# 2. Run full validation
python validate_system.py

# 3. If validation passes, start backend
python main.py
```

### Daily Development
```bash
cd compass/backend

# Quick startup test
python test_startup.py

# If passes, start backend
python main.py
```

### After Pulling Code
```bash
cd compass/backend

# Pull latest
git pull origin main

# Fix database if schema changed
python fix_db.py

# Validate system
python validate_system.py

# Start backend
python main.py
```

### Troubleshooting Issues
```bash
cd compass/backend

# 1. Run validation to identify issues
python validate_system.py

# 2. If database errors, reset database
python fix_db.py

# 3. If dependency errors, reinstall
pip install --upgrade -r requirements-minimal.txt

# 4. Run startup test
python test_startup.py

# 5. If all passes, start backend
python main.py
```

---

## 🐛 Common Error Patterns

### "No Such Column: feedback.external_ids"
**Fix:**
```bash
python fix_db.py
python main.py
```

### "ImportError: cannot import name 'X'"
**Fix:**
```bash
pip install --upgrade -r requirements-minimal.txt
python test_imports.py
```

### "Database is locked"
**Fix:**
```bash
# Kill backend process
lsof -ti:8000 | xargs kill -9  # Mac/Linux
# or on Windows: taskkill /PID <PID> /F

# Remove lock files
rm -f compass.db-wal compass.db-shm

# Restart
python main.py
```

### "Module not found: main"
**Fix:**
```bash
# Make sure you're in the backend directory
cd compass/backend
python validate_system.py
```

---

## 📊 Script Comparison

| Feature | validate_system.py | test_startup.py | fix_db.py |
|---------|-------------------|-----------------|-----------|
| **Speed** | ~30 seconds | ~10 seconds | ~2 seconds |
| **Coverage** | Complete system | Backend only | Database only |
| **File checks** | ✅ Yes | ❌ No | ⚠️ Models only |
| **Dependency checks** | ✅ Yes | ⚠️ Import test | ❌ No |
| **Database validation** | ✅ Full | ⚠️ Basic | ✅ Reset |
| **Frontend checks** | ✅ Yes | ❌ No | ❌ No |
| **API validation** | ✅ Yes | ✅ Yes | ❌ No |
| **Exit code** | 0/1 | 0/1 | N/A |
| **Best for** | Pre-deployment | Quick check | DB errors |

---

## 🔧 Integration with CI/CD

### GitHub Actions Example
```yaml
name: Validate Compass

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-minimal.txt
      - name: Run validation
        run: |
          cd backend
          python validate_system.py
      - name: Run startup test
        run: |
          cd backend
          python test_startup.py
```

---

## 💡 Tips & Best Practices

1. **Run validation before commits**
   - Catches issues early
   - Prevents broken builds

2. **Use test_startup.py for quick checks**
   - Faster than full validation
   - Good for iterative development

3. **Keep fix_db.py handy**
   - Quick fix for most database issues
   - Safe to run multiple times

4. **Check exit codes in scripts**
   - All test scripts return 0 (success) or 1 (failure)
   - Use in automation: `python validate_system.py && python main.py`

5. **Read the error messages**
   - Scripts provide detailed error messages
   - Often include fix suggestions

---

## 🆘 Getting Help

If validation fails and you can't figure out why:

1. Check TROUBLESHOOTING.md for common issues
2. Run `python validate_system.py` for detailed diagnostics
3. Check error messages for specific guidance
4. Try the nuclear option (complete reset) in TROUBLESHOOTING.md

---

## 📝 Contributing

When adding new features:

1. Update validation scripts if adding:
   - New required files
   - New database tables
   - New API endpoints
   - New dependencies

2. Test on all platforms:
   - Windows
   - macOS
   - Linux

3. Update this README with:
   - New error patterns
   - New validation checks
   - New workflow recommendations
