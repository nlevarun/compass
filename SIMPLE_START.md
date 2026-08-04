# 🚀 Start Compass - Super Simple

## One Command to Rule Them All

```bash
cd compass
python3 RUN_COMPASS.py
```

That's it! 🎉

---

## What This Does

1. ✅ Activates the new UI automatically
2. ✅ Builds the frontend
3. ✅ Initializes the database
4. ✅ Starts backend + frontend on ONE port (8000)
5. ✅ Opens in your browser at http://localhost:8000

**No more 2 terminals. No more port confusion. Just works.**

---

## First Time Setup (Mac)

### 1. Clone the repo (if you haven't)
```bash
cd ~
git clone https://github.com/nlevarun/compass.git
cd compass
```

### 2. Install Python dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic python-multipart slack-sdk
cd ..
```

### 3. Install Node.js (if needed)
```bash
# Check if you have Node.js
node --version

# If not, install with Homebrew
brew install node
```

### 4. Install frontend dependencies
```bash
cd frontend
npm install
cd ..
```

### 5. Run Compass!
```bash
python3 RUN_COMPASS.py
```

---

## What You'll See

```
🚀 Starting Compass - All-in-One Server
============================================================

📱 Step 1: Activating new UI...
   ✓ Backing up old App.jsx...
   ✓ Activating redesigned UI...
   ✅ New UI activated!

🏗️  Step 2: Building frontend...
   🔨 Building production frontend...
   ✅ Frontend built successfully!

🔧 Step 3: Checking backend...
   🗄️  Initializing database...
   ✅ Database ready!

🚀 Step 4: Starting Compass server...
============================================================

✨ Compass is starting up...

📍 Open in your browser:
   👉 http://localhost:8000

🛑 Press Ctrl+C to stop
```

---

## Access Points

- **Main App:** http://localhost:8000 (beautiful 3-tab UI)
- **API Docs:** http://localhost:8000/docs (interactive API)
- **API Endpoints:** http://localhost:8000/api/* (JSON responses)

Everything on ONE port! 🎯

---

## Features You'll See

### 📥 Collect Tab
- Source management (Slack, GitHub, Email, etc.)
- Sync buttons
- Connection status

### 🔍 Analyze Tab
- AI theme discovery
- Cluster visualization
- Keyword analysis

### 🗺️ Prioritize Tab
- Priority roadmap
- Revenue metrics
- Top customers

Plus:
- ✨ Onboarding tour (first time)
- 🎨 Professional indigo design
- 📊 Real-time updates
- 💬 Toast notifications

---

## Troubleshooting

### "Command not found: python3"
Try `python` instead:
```bash
python RUN_COMPASS.py
```

### "Command not found: npm"
Install Node.js:
```bash
brew install node
```

### Port 8000 already in use
```bash
# Kill whatever's using port 8000
lsof -ti:8000 | xargs kill -9

# Then run again
python3 RUN_COMPASS.py
```

### Frontend not updating
```bash
# Force rebuild
cd frontend
rm -rf dist node_modules
npm install
cd ..
python3 RUN_COMPASS.py
```

---

## Stop Compass

Just press **Ctrl+C** in the terminal

---

## Development Mode (Hot Reload)

If you're actively developing and want hot reload:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python3 main_simple.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

But for normal use, just use `python3 RUN_COMPASS.py`! 🚀

---

## Next Steps

1. ✅ Run `python3 RUN_COMPASS.py`
2. 🌐 Open http://localhost:8000
3. 👀 See the beautiful new UI
4. 📚 Read the onboarding tour
5. 🎮 Play with Compass!

Done! 🎉
