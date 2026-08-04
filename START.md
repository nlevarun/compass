# 🚀 Quick Start - One Command!

## Single Terminal (Recommended)

```bash
cd compass/backend
python serve_all.py
```

That's it! Opens at **http://localhost:8000**

The script will:
1. Build frontend automatically (first time only)
2. Start backend API
3. Serve frontend from same port
4. Everything works from ONE terminal

## Two Terminals (Development Mode)

If you want hot-reload for frontend development:

**Terminal 1 - Backend:**
```bash
cd compass/backend
source venv/bin/activate  # Mac/Linux
# or venv\Scripts\activate  # Windows
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd compass/frontend
npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## First Time Setup

```bash
# Clone
git clone https://github.com/nlevarun/compass.git
cd compass

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or venv\Scripts\activate  # Windows
pip install -r requirements-minimal.txt

# Frontend setup
cd ../frontend
npm install

# Start everything (from backend folder)
cd ../backend
python serve_all.py
```

## Troubleshooting

### Database errors?
```bash
cd compass/backend
python fix_db.py
python serve_all.py
```

### Blank page?
```bash
cd compass/frontend
rm -rf dist node_modules
npm install
npm run build
cd ../backend
python serve_all.py
```

### Port 8000 in use?
```bash
# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## What Works

✅ 8+ feedback sources
✅ NLP clustering
✅ Priority calculation
✅ Real-time WebSocket updates
✅ Historical data import
✅ Jira/Linear sync
✅ PWA (installable)
✅ Mobile responsive

## Next Steps

1. Open http://localhost:8000
2. Click "Generate Mock Data"
3. Click "Run Clustering"
4. Click "Generate Roadmap"
5. Explore Priority Analysis tab

Done! 🎉
