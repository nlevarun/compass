# Compass Setup Guide - macOS

Complete installation and setup instructions for running Compass on macOS.

## Prerequisites

Check if you have the required tools:

```bash
# Check Python version (need 3.12+)
python3 --version

# Check Node.js (need 18+)
node --version

# Check npm
npm --version

# Check git
git --version
```

If missing any:

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Install Node.js
brew install node

# Git usually comes with macOS Xcode Command Line Tools
xcode-select --install
```

## Installation

### Step 1: Clone Repository

```bash
cd ~
git clone https://github.com/nlevarun/compass.git
cd compass
```

### Step 2: Install Backend Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database.py
```

Expected output:
```
Initializing Compass database...

✓ Created tables: sources, feedback, clusters, roadmap_items
```

### Step 3: Install Frontend Dependencies

Open a new terminal tab (Cmd + T), then:

```bash
cd ~/compass/frontend

# Install dependencies
npm install
```

## Running Compass

### Terminal 1: Backend API

```bash
cd ~/compass/backend
source venv/bin/activate  # If using virtual environment
python main.py
```

Expected output:
```
🚀 Starting Compass API...
✓ Database initialized at sqlite:///compass.db
✓ Created 8 sources
✓ Compass API ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Backend runs on: **http://localhost:8000**

### Terminal 2: Frontend Dev Server

```bash
cd ~/compass/frontend
npm run dev
```

Expected output:
```
VITE v5.x.x ready in xxx ms

➜  Local:   http://localhost:5173/
```

Frontend runs on: **http://localhost:5173**

### Step 4: Open in Browser

Open Safari/Chrome and navigate to:
```
http://localhost:5173
```

## First Time Usage

Follow the workflow in the dashboard:

1. **Sync Feedback** - Click button to load 500+ mock entries from 8 sources
2. **Run Clustering** - NLP groups similar feedback (takes ~20-30 seconds)
3. **Generate Roadmap** - Creates prioritized roadmap based on clustering

Then explore:
- **Feedback Inbox** - Browse all feedback with filters
- **Clusters** - View NLP-grouped themes
- **Roadmap** - See data-driven prioritization

## Testing Backend API

You can test the API directly with curl:

```bash
# Health check
curl http://localhost:8000/

# Sync feedback
curl -X POST http://localhost:8000/api/sources/sync

# Run clustering
curl -X POST http://localhost:8000/api/clustering/run

# Generate roadmap
curl -X POST http://localhost:8000/api/roadmap/generate

# Get stats
curl http://localhost:8000/api/stats | jq

# API documentation (open in browser)
open http://localhost:8000/docs
```

## Troubleshooting

### Python Version Issues

If you have multiple Python versions:

```bash
# Use specific version
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 or 5173 is taken:

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or run on different port
uvicorn main:app --port 8001

# For frontend, edit vite.config.js to change port
```

### Permission Denied

If you get permission errors:

```bash
# Don't use sudo! Instead, use user install:
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Slow Clustering

On first run, sentence-transformers downloads ML models (~400MB). This happens once.

If clustering is still slow:
- Reduce feedback count in `backend/ingestion/mock_generators.py`
- Or use smaller batch size in `backend/nlp/clustering.py`

### Database Locked

If you get "database is locked":

```bash
# Stop all running backends
# Delete and reinitialize database
rm compass.db compass.db-wal compass.db-shm
python backend/database.py
```

## Production Tips

### Using PostgreSQL Instead of SQLite

1. Install PostgreSQL:
```bash
brew install postgresql@15
brew services start postgresql@15
```

2. Create database:
```bash
createdb compass
```

3. Update connection in `backend/database.py`:
```python
DATABASE_URL = "postgresql://localhost/compass"
```

### Running in Background

Use tmux or screen to keep servers running:

```bash
# Install tmux
brew install tmux

# Start tmux session
tmux new -s compass

# Split window: Ctrl+B then "
# Switch panes: Ctrl+B then arrow keys
# Detach: Ctrl+B then D
# Reattach: tmux attach -t compass
```

### Environment Variables

Create `.env` file in `backend/`:

```bash
# Database
DATABASE_URL=sqlite:///compass.db

# API
API_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Slack (optional)
SLACK_TOKEN=xoxb-your-token
SLACK_CHANNEL_IDS=C12345,C67890
```

## Development Workflow

```bash
# Backend changes (with auto-reload)
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Frontend changes (with hot reload)
cd frontend
npm run dev

# Run tests
python backend/database.py
python backend/nlp/clustering.py
python backend/priority/calculator.py

# Build frontend for production
cd frontend
npm run build
npm run preview
```

## Updating Code

```bash
cd ~/compass

# Pull latest changes
git pull origin main

# Update backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend dependencies
cd ../frontend
npm install

# Restart both servers
```

## Keyboard Shortcuts

### Terminal
- **Cmd + T**: New tab
- **Cmd + W**: Close tab
- **Cmd + K**: Clear screen
- **Ctrl + C**: Stop server

### Browser
- **Cmd + R**: Refresh page
- **Cmd + Shift + R**: Hard refresh
- **Cmd + Option + I**: Open DevTools

## Project Structure

```
~/compass/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # API endpoints
│   ├── models.py              # Database models
│   ├── database.py            # DB connection
│   ├── requirements.txt       # Python dependencies
│   ├── compass.db             # SQLite database (auto-created)
│   ├── ingestion/
│   │   ├── sources.py         # 8 feedback sources
│   │   └── mock_generators.py # Mock data generation
│   ├── nlp/
│   │   ├── clustering.py      # DBSCAN + embeddings
│   │   └── sentiment.py       # Sentiment analysis
│   └── priority/
│       └── calculator.py      # Priority scoring
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API client
│   │   └── App.jsx            # Main app
│   ├── package.json
│   └── node_modules/          # npm dependencies
└── README.md
```

## Quick Reference

```bash
# Start backend
cd ~/compass/backend && source venv/bin/activate && python main.py

# Start frontend
cd ~/compass/frontend && npm run dev

# View logs
tail -f backend/logs/app.log  # If logging enabled

# Check processes
lsof -i:8000  # Backend
lsof -i:5173  # Frontend

# Stop everything
Ctrl + C in each terminal
```

## Next Steps

- Integrate real Slack data (see README.md Slack Integration section)
- Deploy with Docker
- Migrate to PostgreSQL for production
- Add authentication
- Set up CI/CD with GitHub Actions

## Support

- GitHub: https://github.com/nlevarun/compass
- Issues: https://github.com/nlevarun/compass/issues
- API Docs: http://localhost:8000/docs
