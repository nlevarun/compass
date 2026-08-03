# Compass Setup Guide

Complete setup instructions for running Compass locally.

## Prerequisites

- **Python 3.12+** (check with `python3 --version`)
- **Node.js 18+** and npm (check with `node --version`)
- **Git** (for cloning and pushing)

## Quick Start (Automated)

```bash
# Navigate to project
cd /home/wsl-user/compass

# Run setup script
bash setup.sh
```

This will:
1. Install Python dependencies
2. Install frontend dependencies
3. Initialize database
4. Generate mock data
5. Start both backend and frontend servers

## Manual Setup

### Step 1: Backend Setup

```bash
cd compass/backend

# Install Python dependencies
pip3 install --user -r requirements.txt

# Or with virtual environment (if venv available):
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python database.py

# Start backend server
python main.py
# Or: uvicorn main:app --reload
```

Backend will run on: **http://localhost:8000**
API docs: **http://localhost:8000/docs**

### Step 2: Frontend Setup

```bash
cd compass/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on: **http://localhost:5173**

### Step 3: Initial Data Load

Open **http://localhost:5173** and follow the workflow:

1. Click **"Sync Feedback"** - Loads 500+ mock entries from 8 sources
2. Click **"Run Clustering"** - NLP groups similar feedback (takes ~30s)
3. Click **"Generate Roadmap"** - Creates prioritized roadmap

## Testing Backend Directly

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
curl http://localhost:8000/api/stats
```

## Troubleshooting

### Python Dependencies Fail to Install

**Problem**: No pip or venv available

**Solution 1** - Install pip:
```bash
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
export PATH="$HOME/.local/bin:$PATH"
```

**Solution 2** - Install python3-pip via package manager (requires sudo):
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

**Solution 3** - Use simplified mode (no NLP):
The backend has fallback implementations that work without heavy dependencies (sentence-transformers, sklearn). Clustering will use simpler keyword-based methods.

### npm Version Too Old

**Problem**: `npm create vite` fails with version errors

**Solution**: Frontend already created manually. Just run:
```bash
cd frontend
npm install
npm run dev
```

To update npm:
```bash
npm install -g npm@latest
```

### UNC Path Errors (Windows/WSL)

**Problem**: npm commands fail with "UNC paths are not supported"

**Solution**: Run all commands from within WSL, not Windows Command Prompt:
```bash
# From Windows CMD:
wsl

# Now you're in WSL, navigate to project:
cd /home/wsl-user/compass
```

### Database Locked Errors

**Problem**: `database is locked` when running multiple operations

**Solution**: SQLite WAL mode is enabled by default. If issues persist:
```bash
# Stop all backend processes
# Delete database and reinitialize
rm compass.db
python backend/database.py
```

### Port Already in Use

**Problem**: Port 8000 or 5173 already in use

**Solution**:
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different ports
# Backend:
uvicorn main:app --port 8001

# Frontend (edit vite.config.js):
# server: { port: 5174 }
```

### Clustering Takes Too Long

**Problem**: Clustering > 1 minute

**Optimization**:
1. Reduce feedback count in `mock_generators.py`
2. Use GPU if available (install `torch` with CUDA)
3. Use smaller model in `clustering.py`:
   ```python
   model_name = "all-MiniLM-L6-v2"  # Current (fast)
   # vs "all-mpnet-base-v2"  # Slower but more accurate
   ```

## Project Structure

```
compass/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # API endpoints
│   ├── models.py              # Database models
│   ├── database.py            # DB connection
│   ├── requirements.txt       # Python dependencies
│   ├── ingestion/
│   │   ├── sources.py         # 8 feedback sources
│   │   └── mock_generators.py # Mock data generation
│   ├── nlp/
│   │   ├── clustering.py      # DBSCAN + embeddings
│   │   └── sentiment.py       # VADER + TextBlob
│   └── priority/
│       └── calculator.py      # Revenue-weighted scoring
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API calls
│   │   ├── App.jsx            # Main app
│   │   └── main.jsx           # Entry point
│   └── package.json
└── compass.db                  # SQLite database (auto-created)
```

## Environment Variables

Create `.env` file in `backend/` for custom config:

```env
# Database
DATABASE_URL=sqlite:///compass.db
# For PostgreSQL: postgresql://user:pass@host:5432/compass

# API
API_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Slack Integration (optional)
SLACK_TOKEN=xoxb-your-token-here
SLACK_CHANNEL_IDS=C12345,C67890
```

## Next Steps

- **Slack Integration**: Set up OAuth for real Slack data
- **PostgreSQL Migration**: Scale beyond SQLite
- **Deploy**: Docker containerization for production
- **Ground Truth**: Validate clustering accuracy with labeled data

## Support

- GitHub Issues: https://github.com/nlevarun/compass/issues
- Documentation: See README.md
- API Docs: http://localhost:8000/docs (when running)
