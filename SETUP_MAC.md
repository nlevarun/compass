# Compass Setup Guide for Mac

## Quick Start

### 1. Pull Latest Changes
```bash
cd ~/compass
git pull origin main
```

### 2. Backend Setup
```bash
cd ~/compass/backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements-minimal.txt

# Start backend server
python main.py
```

Backend will run on: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

### 3. Frontend Setup (In New Terminal)
```bash
cd ~/compass/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will run on: **http://localhost:5173**

## What's Fixed

✅ **Backend Issues:**
- Fixed `import` reserved keyword conflict (renamed to `importers/`)
- Fixed missing imports: `Dict`, `Any`, `BackgroundTasks`, `UploadFile`, `File`
- Fixed `websockets.py` module name conflict (renamed to `ws_manager.py`)

✅ **Frontend Integration:**
- Integrated WebSocket real-time updates
- Added OfflineBanner, InstallPrompt, Toast components
- Added PriorityAnalysis tab
- Connection status indicator in header
- Real-time notifications system

## New Features Available

### Real-Time Updates
- Live feedback synchronization
- Cluster updates as they happen
- Progress tracking for imports
- WebSocket connection status

### Progressive Web App (PWA)
- Installable on mobile/desktop
- Offline support with service worker
- Responsive mobile-first design
- Home screen install prompt

### Advanced Priority Analysis
- Impact prediction with confidence intervals
- Custom scoring formula builder
- At-risk customer detection
- Priority breakdowns and explanations

### Historical Data Import
- Import from Zendesk (API)
- Import from Intercom (API)
- Import from CSV (bulk upload)
- Background job processing with progress

### Integrations
- Bidirectional Jira sync
- Bidirectional Linear sync
- GitHub commit/PR auto-linking
- 8+ feedback sources (Slack, GitHub, Discord, Reddit, etc.)

## Troubleshooting

### Backend won't start
```bash
# Make sure you're in the right directory
cd ~/compass/backend

# Activate venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements-minimal.txt
```

### Frontend won't start
```bash
# Make sure you're in the right directory
cd ~/compass/frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Try again
npm run dev
```

### "npm: command not found"
```bash
# Install Node.js on Mac
brew install node
```

### Port already in use
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

## Next Steps

1. ✅ Backend running on port 8000
2. ✅ Frontend running on port 5173
3. 🔄 Open http://localhost:5173 in browser
4. 🎯 Test features:
   - Click "Generate Mock Data" on Dashboard
   - Run clustering
   - Generate roadmap
   - Check real-time updates
   - Try Priority Analysis tab

## Resume Metrics Progress

✅ 8+ feedback sources integrated
✅ 500+ feedback entries capability
⏳ 85%+ NLP clustering accuracy (test with ground truth)
⏳ <30s roadmap generation (run performance test)
✅ Real-time updates implemented
✅ Historical data import
✅ Developer platform (SDKs, webhooks, docs)
