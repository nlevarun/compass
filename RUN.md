# 🚀 How to Run Compass

## Quick Start (Two Terminals)

### Terminal 1 - Backend
```bash
cd ~/compass/backend

# Fix database if needed
python fix_db.py

# Start backend
python main.py
```

Backend runs at: **http://localhost:8000**

### Terminal 2 - Frontend
```bash
cd ~/compass/frontend

# First time only: install dependencies
npm install

# Start frontend dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## Current Issue

You're on **Mac** but your terminal is trying to access **WSL (Windows)** paths!

**Solution:**

Make sure you've cloned the repo on your Mac:

```bash
# On your Mac terminal (not WSL)
cd ~
git clone https://github.com/nlevarun/compass.git
cd compass

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt

# Frontend setup
cd ../frontend
npm install
```

Then follow the two-terminal instructions above.

---

## Troubleshooting

### "Command not found: npm"
```bash
# Install Node.js on Mac
brew install node
```

### "Command not found: python3"
```bash
# Python should be pre-installed on Mac
# Check version
python3 --version

# If missing, install with Homebrew
brew install python@3.12
```

### "Database schema errors"
```bash
cd ~/compass/backend
python fix_db.py
```

### "Blank page in browser"
1. Make sure backend is running (Terminal 1)
2. Make sure frontend is running (Terminal 2)
3. Open **http://localhost:5173** (not 8000)
4. Check browser console (F12) for errors

---

## Production Build (Optional)

If you want to build frontend and serve from backend:

```bash
# Build frontend
cd ~/compass/frontend
npm run build

# This creates frontend/dist folder

# Serve everything from backend
cd ~/compass/backend
python main_with_static.py
```

Then open **http://localhost:8000**

---

## What You Should See

✅ **http://localhost:8000/docs** - API documentation (backend)
✅ **http://localhost:5173** - Compass UI (frontend)

The frontend at :5173 will:
- Connect to backend at :8000
- Show professional dashboard
- Have 5 tabs: Overview, Feedback, Insights, Roadmap, Priority Analysis
- Show connection status (green dot = connected)

---

## Next Steps

1. Click "Generate Mock Data" on Overview tab
2. Wait for 500+ feedback entries to be created
3. Click "Run Clustering"
4. Click "Generate Roadmap"
5. Explore Priority Analysis tab

Done! 🎉
