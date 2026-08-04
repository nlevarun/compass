# 🚀 Start Compass - The Easy Way

## 🍎 On Your Mac

### First Time Setup (5 minutes - only once)

```bash
# 1. Go to compass directory
cd ~/compass

# 2. Pull latest code
git pull origin main

# 3. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic python-multipart slack-sdk

# 4. Setup frontend
cd ../frontend
npm install

# Done!
cd ..
```

### Start Compass (every time)

```bash
cd ~/compass
./start.sh
```

**That's it!** The script will:
1. ✅ Activate the new UI automatically
2. ✅ Initialize the database
3. ✅ Start backend on port 8000
4. ✅ Start frontend on port 5173
5. ✅ Connect them together

**Open in browser:** 👉 http://localhost:5173

---

## What You'll See

```
🚀 Starting Compass...

🍎 Detected macOS

📱 Step 1: Checking UI...
   Activating new UI...
   ✅ New UI activated!

🔧 Step 2: Checking backend...
   Initializing database...
   ✅ Database ready!

📦 Step 3: Checking frontend...
   ✅ Frontend dependencies ready

🚀 Step 4: Starting servers...
==================================================

Starting backend on http://localhost:8000...
Starting frontend on http://localhost:5173...

==================================================
✅ Compass is running!

📍 Access points:
   🌐 Main App:     http://localhost:5173
   📚 API Docs:     http://localhost:8000/docs
   🔌 Backend API:  http://localhost:8000/api

💡 The frontend (5173) will connect to backend (8000) automatically

🛑 Press Ctrl+C to stop everything
==================================================
```

---

## Two Ports Explained

**Why two ports?**
- **Port 5173** = React dev server (frontend with hot reload)
- **Port 8000** = Python FastAPI server (backend API)

The frontend at http://localhost:5173 automatically connects to the backend at http://localhost:8000.

**Which one to open?**
👉 **Open http://localhost:5173** - that's the main app!

The backend is just for API calls - you don't need to open it directly.

---

## The New UI

When you open http://localhost:5173, you'll see:

### 🎨 Beautiful 3-Tab Interface

**📥 Collect Tab**
- Import feedback from Slack, GitHub, Email, etc.
- Visual source cards showing connection status
- One-click sync button

**🔍 Analyze Tab**
- AI discovers themes automatically
- Visual cluster cards with examples
- Keywords and sentiment analysis

**🗺️ Prioritize Tab**
- Priority roadmap ranked by revenue
- Shows customer impact and request counts
- Top customer badges

**Plus:**
- ✨ Onboarding tour (first time only)
- 🎨 Professional indigo design (like Productboard)
- 📊 Real-time updates
- 💬 Toast notifications

---

## Stop Compass

Just press **Ctrl+C** in the terminal

It will automatically stop both backend and frontend.

---

## Troubleshooting

### "Permission denied: ./start.sh"
```bash
chmod +x start.sh
./start.sh
```

### "Virtual environment not found"
You need to do the first-time setup:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic python-multipart slack-sdk
```

### "Node modules not found"
```bash
cd frontend
npm install
```

### Port already in use
```bash
# Kill port 8000
lsof -ti:8000 | xargs kill -9

# Kill port 5173
lsof -ti:5173 | xargs kill -9

# Try again
./start.sh
```

### Still seeing old UI?
```bash
cd frontend/src
rm App.jsx App.old.jsx
cp App.redesigned.jsx App.jsx
cd ../..
./start.sh
```

---

## Quick Commands

| Command | Description |
|---------|-------------|
| `./start.sh` | Start everything |
| `Ctrl+C` | Stop everything |
| `git pull origin main` | Get latest updates |
| http://localhost:5173 | Main app (open this!) |
| http://localhost:8000/docs | API documentation |

---

## Next Steps

1. ✅ Do first-time setup (if you haven't)
2. ✅ Run `./start.sh`
3. 🌐 Open http://localhost:5173
4. 👀 See the beautiful new 3-tab UI
5. 📚 Complete the onboarding tour
6. 🎮 Try syncing some feedback!

**Enjoy Compass!** 🎉
