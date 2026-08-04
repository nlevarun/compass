# 🍎 Start Compass on Mac - Dead Simple

## Step 1: Pull Latest Changes

Open Terminal on your Mac:

```bash
cd ~/compass
git pull origin main
```

You should see: "2 files changed, 359 insertions(+)"

---

## Step 2: First Time Setup (5 minutes)

Only do this once:

```bash
# Install backend dependencies
cd ~/compass/backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic python-multipart slack-sdk

# Install frontend dependencies
cd ~/compass/frontend
npm install

# Done!
cd ~/compass
```

---

## Step 3: Run Compass (Every Time)

```bash
cd ~/compass
python3 RUN_COMPASS.py
```

**That's it!** 🎉

Wait ~30 seconds for it to build, then open:
👉 **http://localhost:8000**

---

## What You'll See

```
🚀 Starting Compass - All-in-One Server
============================================================

📱 Step 1: Activating new UI...
   ✅ New UI activated!

🏗️  Step 2: Building frontend...
   ✅ Frontend built successfully!

🔧 Step 3: Checking backend...
   ✅ Database ready!

🚀 Step 4: Starting Compass server...

✨ Compass is starting up...

📍 Open in your browser:
   👉 http://localhost:8000

🛑 Press Ctrl+C to stop
```

---

## The New UI

You'll see a beautiful 3-tab interface:

### 📥 **Collect** - Import feedback from everywhere
- Slack, GitHub, Email, Support tickets
- Visual source cards
- One-click sync

### 🔍 **Analyze** - Discover themes with AI
- Automatic clustering
- Visual theme cards
- Keywords and examples

### 🗺️ **Prioritize** - Build what matters
- Revenue-weighted roadmap
- Priority scores
- Top customers

Plus an onboarding tour on first visit!

---

## Common Issues

### "Command not found: python3"
Try this instead:
```bash
python RUN_COMPASS.py
```

### "Command not found: npm"
Install Node.js:
```bash
brew install node
```

### "Port 8000 already in use"
```bash
lsof -ti:8000 | xargs kill -9
python3 RUN_COMPASS.py
```

### Still seeing old UI?
Force a clean rebuild:
```bash
cd ~/compass/frontend
rm -rf dist node_modules .vite
npm install
cd ~/compass
python3 RUN_COMPASS.py
```

---

## Stop Compass

Press **Ctrl+C** in the terminal where it's running

---

## Why One Command Now?

**Before:** You needed 2 terminals
- Terminal 1: `cd backend && python main.py` (port 8000)
- Terminal 2: `cd frontend && npm run dev` (port 5173)
- Confusing which port to use!

**Now:** One command, one terminal, one port
- `python3 RUN_COMPASS.py`
- Everything on http://localhost:8000
- Backend API + Frontend served together
- No confusion! 🎯

---

## Development Mode (Optional)

If you're coding and want hot reload:

**Terminal 1:**
```bash
cd ~/compass/backend
source venv/bin/activate
python3 main_simple.py
```

**Terminal 2:**
```bash
cd ~/compass/frontend
npm run dev
```

Then use:
- Frontend: http://localhost:5173 (hot reload)
- Backend: http://localhost:8000/docs (API)

But for normal use, stick with `RUN_COMPASS.py`!

---

## 🎯 Quick Reference

| Command | What It Does |
|---------|--------------|
| `python3 RUN_COMPASS.py` | Start everything |
| `Ctrl+C` | Stop everything |
| `git pull origin main` | Get latest updates |
| http://localhost:8000 | Open Compass |
| http://localhost:8000/docs | API documentation |

---

## Next Steps

1. ✅ `cd ~/compass`
2. ✅ `git pull origin main`
3. ✅ `python3 RUN_COMPASS.py`
4. 🌐 Open http://localhost:8000
5. 🎉 Enjoy Compass!

**No WSL needed. No port confusion. Just works on Mac.** 🍎✨
