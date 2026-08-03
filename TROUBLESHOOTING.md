# Compass Troubleshooting Guide

## 🔥 Quick Fix for Database Errors

If you're seeing errors like "no such column: feedback.external_ids", the database schema is out of sync.

### Solution: Fresh Start (Recommended)

```bash
cd ~/compass/backend

# Stop backend if running (Ctrl+C)

# Delete old database
rm -f compass.db

# Pull latest code
git pull origin main

# Restart backend - it will create fresh database
python main.py
```

That's it! The backend automatically creates the database with correct schema on startup.

---

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
