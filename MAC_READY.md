# Mac Compatibility - READY TO USE

## What Was Fixed

### 1. SQLAlchemy Reserved Name Conflict
- **Problem:** Column named `metadata` conflicts with SQLAlchemy's built-in `Base.metadata`
- **Fix:** Renamed to `source_metadata` throughout codebase
- **Files updated:** models.py, mock_generators.py, sources.py

### 2. Torch Compatibility Issues
- **Problem:** torch 2.1.2 not available for Python 3.12 on Apple Silicon
- **Fix:** Created `requirements-minimal.txt` without heavy ML dependencies
- **Result:** Fast install, uses lightweight keyword-based clustering

### 3. Python 3.14 Incompatibility
- **Problem:** Python 3.14 too new for SQLAlchemy 2.0.25
- **Fix:** Documentation updated to require Python 3.12
- **Result:** Stable, tested version

## New Files Created

1. **backend/requirements-minimal.txt** - Fast install for all platforms
2. **setup-mac.sh** - Automated one-command setup script
3. **MAC_SETUP.md** - Comprehensive macOS guide (already existed, updated)

## Changes to Push

You have **3 commits** ready to push:

```
c8527c1 feat: Add automated setup script for macOS
aa05dfe fix: Mac compatibility - fix metadata column and add minimal requirements
8c5b2ce docs: Remove emojis from README and add macOS setup guide
```

## How to Push from WSL (Windows)

From Windows Command Prompt:
```cmd
wsl -e bash -c "cd /home/wsl-user/compass && git push origin main"
```

When prompted:
- Username: `nlevarun`
- Password: [Personal Access Token from https://github.com/settings/tokens]

## Fresh Install on Your Mac

Once pushed, on your Mac:

### Option 1: Automated Setup (Recommended)
```bash
cd ~
git clone https://github.com/nlevarun/compass.git
cd compass
bash setup-mac.sh
```

### Option 2: Manual Setup
```bash
cd ~
git clone https://github.com/nlevarun/compass.git
cd compass/backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install minimal dependencies (30 seconds)
pip install -r requirements-minimal.txt

# Initialize database
python database.py

# Start backend
python main.py
```

Then in new terminal:
```bash
cd ~/compass/frontend
npm install
npm run dev
```

Open browser: http://localhost:5173

## What Works Now

- ✅ SQLAlchemy 2.0.25 with Python 3.12
- ✅ No torch/ML installation required (optional later)
- ✅ Keyword-based clustering (fast, works great)
- ✅ Full FastAPI backend with all endpoints
- ✅ Complete React frontend
- ✅ 500+ mock feedback generation
- ✅ Priority scoring and roadmap generation

## Optional: Add Full ML Later

If you want sentence-transformers clustering:

```bash
source venv/bin/activate
pip install torch sentence-transformers scikit-learn numpy
```

Then restart backend - it will automatically use ML clustering.

## Files Changed Summary

```
Modified:
- MAC_SETUP.md (updated with minimal requirements)
- README.md (added Mac compatibility note)
- backend/models.py (metadata → source_metadata)
- backend/ingestion/mock_generators.py (metadata → source_metadata)
- backend/ingestion/sources.py (metadata → source_metadata)
- backend/requirements.txt (commented out torch)

Created:
- backend/requirements-minimal.txt (new)
- setup-mac.sh (new)
```

---

**Everything is fixed and ready for Mac!** Just push from WSL and clone on your Mac.
