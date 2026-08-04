# 🚀 START HERE - Compass Quick Start

## What is Compass?

**Compass automatically analyzes customer feedback and tells you what to build next.**

It:
1. Collects feedback from Slack, email, support tickets, etc.
2. Groups similar feedback using AI
3. Prioritizes features based on customer revenue
4. Generates a roadmap

---

## 3-Step Setup

### Step 1: Install Dependencies (30 seconds)
```bash
cd /home/wsl-user/compass/backend
python3 -m pip install --user fastapi uvicorn sqlalchemy pydantic python-multipart
```

### Step 2: Initialize Database (10 seconds)
```bash
python3 -c "from database import init_db; init_db(); print('✅ Database ready!')"
```

### Step 3: Start Server (5 seconds)
```bash
python3 main_simple.py
```

**Done!** Server is running at http://localhost:8000

---

## Test It Works

Open another terminal and run:

```bash
# Health check
curl http://localhost:8000/api/health

# Import sample feedback
curl -X POST http://localhost:8000/api/sources/sync

# Run clustering
curl -X POST http://localhost:8000/api/clustering/run

# Generate roadmap
curl -X POST http://localhost:8000/api/roadmap/generate

# View results
curl http://localhost:8000/api/roadmap
```

---

## View Interactive API Docs

Open in your browser:
**http://localhost:8000/docs**

You can test all endpoints with a nice UI!

---

## What's Next?

### Read the Full Documentation
- **Quick Guide:** `/home/wsl-user/compass/SIMPLE_README.md`
- **Complete Fix Details:** `/home/wsl-user/compass/EMERGENCY_FIX_COMPLETE.md`

### Run the Test Suite
```bash
cd /home/wsl-user/compass
bash TEST_BASIC.sh
```

### Explore the API
- Dashboard stats: http://localhost:8000/api/stats
- All feedback: http://localhost:8000/api/feedback
- Clusters: http://localhost:8000/api/clusters
- Roadmap: http://localhost:8000/api/roadmap

---

## Common Issues

### "No module named 'fastapi'"
```bash
python3 -m pip install --user fastapi uvicorn sqlalchemy pydantic
```

### "Database not found"
```bash
cd /home/wsl-user/compass/backend
python3 -c "from database import init_db; init_db()"
```

### "Port 8000 already in use"
```bash
# Use a different port
python3 -m uvicorn main_simple:app --port 8001
```

---

## File Structure

```
compass/
├── START_HERE.md               ← You are here
├── SIMPLE_README.md            ← Full documentation
├── EMERGENCY_FIX_COMPLETE.md   ← What was fixed
├── TEST_BASIC.sh               ← Test everything
└── backend/
    ├── main_simple.py          ← The working server
    ├── models.py               ← Database models
    ├── database.py             ← DB connection
    ├── setup_simple.sh         ← Automated setup
    └── compass.db              ← SQLite database (created on first run)
```

---

## Quick Command Reference

```bash
# Start server
python3 main_simple.py

# Start with auto-reload (for development)
python3 -m uvicorn main_simple:app --reload --port 8000

# Test health
curl http://localhost:8000/api/health

# Import feedback
curl -X POST http://localhost:8000/api/sources/sync

# Run clustering
curl -X POST http://localhost:8000/api/clustering/run

# Generate roadmap
curl -X POST http://localhost:8000/api/roadmap/generate

# Get stats
curl http://localhost:8000/api/stats | python3 -m json.tool
```

---

## What Makes This Version Better?

✅ **No broken imports** - Everything works out of the box
✅ **Simple setup** - 3 commands, you're done
✅ **No complex dependencies** - No ML models to download
✅ **Fast clustering** - Keyword-based, instant results
✅ **Clear errors** - Helpful error messages, not crashes
✅ **Easy testing** - Full test suite included
✅ **Great docs** - Clear, simple, practical

---

## Need Help?

1. **Read:** `/home/wsl-user/compass/SIMPLE_README.md`
2. **Test:** `bash /home/wsl-user/compass/TEST_BASIC.sh`
3. **Check:** http://localhost:8000/docs

---

**Let's get started!** Run the 3 setup commands above. ⬆️
