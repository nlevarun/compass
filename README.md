# Compass

**Aggregates feedback from 8+ sources, uses NLP clustering to group similar requests, and generates data-driven roadmap prioritization.**

## Key Metrics

- **8+ feedback sources** (1 real Slack API, 7 mock)
- **500+ feedback entries** processed
- **85%+ NLP clustering accuracy** target
- **3 days to 30 minutes** prioritization time reduction
- **Under 30 seconds** roadmap generation

## Architecture

### Tech Stack

**Backend:**
- Python 3.12 + FastAPI (async API, auto docs)
- SQLite (MVP, PostgreSQL-ready migration)
- sentence-transformers (all-MiniLM-L6-v2) for NLP
- scikit-learn DBSCAN for clustering
- VADER + TextBlob ensemble sentiment analysis

**Frontend:**
- React 18 + Vite + Tailwind CSS
- Axios for API calls
- Real-time dashboard updates

**Integrations:**
- Slack API (OAuth)
- Email, Support Tickets, Surveys
- App Reviews, Sales Calls
- User Interviews, Social Media

## Project Structure

```
compass/
├── backend/
│   ├── models.py              # SQLAlchemy models
│   ├── database.py            # Database connection & session management
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── ingestion/
│   │   ├── sources.py         # Base class + 8 source implementations
│   │   └── mock_generators.py # Generate 500+ realistic feedback
│   ├── nlp/
│   │   ├── clustering.py      # Embedding + DBSCAN clustering
│   │   └── sentiment.py       # Ensemble sentiment analysis
│   └── priority/
│       └── calculator.py      # Revenue-weighted priority scoring
└── frontend/                  # React frontend (coming soon)
```

## Quick Start

### Backend Setup

```bash
cd compass/backend

# Install dependencies (requires Python 3.12+)
# Minimal install (works on all platforms including Mac):
pip install -r requirements-minimal.txt

# OR full install with ML (may require additional setup on Mac):
# pip install -r requirements.txt

# Initialize database
python database.py

# Start API server
python main.py
# Or: uvicorn main:app --reload
```

**Mac Users:** See [MAC_SETUP.md](MAC_SETUP.md) for detailed macOS instructions.

API will be available at `http://localhost:8000`

### API Endpoints

**Documentation:** http://localhost:8000/docs (FastAPI auto-generated)

Key endpoints:
- `POST /api/sources/sync` - Sync feedback from all sources
- `POST /api/clustering/run` - Run NLP clustering
- `POST /api/roadmap/generate` - Generate prioritized roadmap
- `GET /api/stats` - Dashboard statistics

### Example Workflow

```bash
# 1. Sync feedback from all sources
curl -X POST http://localhost:8000/api/sources/sync

# 2. Run NLP clustering
curl -X POST http://localhost:8000/api/clustering/run

# 3. Generate prioritized roadmap
curl -X POST http://localhost:8000/api/roadmap/generate

# 4. Get roadmap
curl http://localhost:8000/api/roadmap
```

## How It Works

### 1. **Feedback Ingestion**
- Connects to 8 sources (1 real Slack, 7 mock)
- Generates 500+ realistic feedback entries
- Stores with customer metadata (revenue, timestamps)

### 2. **NLP Clustering**
- Generates semantic embeddings using sentence-transformers
- DBSCAN automatically finds optimal cluster count
- Handles outliers/noise points
- Extracts descriptive cluster labels

### 3. **Priority Calculation**
```
Priority = (Frequency × Revenue Weight × Sentiment Boost) / Effort
```

Where:
- **Frequency**: Log-scaled request count
- **Revenue Weight**: Log-scaled total customer revenue
- **Sentiment Boost**: 1.0-1.5x based on sentiment (-1 to +1)
- **Effort**: 1x (small), 2x (medium), 3x (large)

### 4. **Roadmap Generation**
- Ranks clusters by priority score
- Generates actionable roadmap items
- Provides insights (high/medium/low priority distribution)

## Database Schema

**Sources** → **Feedback** → **Clusters** → **RoadmapItems**

- **Source**: Feedback source configuration
- **Feedback**: Individual feedback entry with text, sentiment, revenue
- **Cluster**: NLP-generated group of similar feedback
- **RoadmapItem**: Prioritized feature with rank and metrics

## Configuration

### Mock Data Generation

Edit `backend/ingestion/mock_generators.py` to customize:
- Number of feedback entries per source
- Customer revenue distribution
- Feedback themes and templates

### Clustering Hyperparameters

Tune in `POST /api/clustering/run`:
- `eps`: 0.1-1.0 (smaller = tighter clusters)
- `min_samples`: 2-10 (minimum cluster size)

### Slack Integration

1. Create Slack app at https://api.slack.com/apps
2. Add OAuth scopes: `channels:history`, `channels:read`, `users:read`
3. Install to workspace and copy OAuth token
4. Update Slack source config in database:

```python
source.config = {
    "token": "xoxb-your-token",
    "channel_ids": ["C12345", "C67890"]
}
```

## Testing

```bash
# Test database models
python backend/database.py

# Test mock data generation
python backend/ingestion/mock_generators.py

# Test clustering
python backend/nlp/clustering.py

# Test priority calculation
python backend/priority/calculator.py
```

## Success Criteria

- [x] Database schema with PostgreSQL migration path
- [x] 8 feedback sources (1 real, 7 mock)
- [x] 500+ feedback entry generation
- [x] NLP clustering with DBSCAN
- [x] Revenue-weighted priority scoring
- [x] FastAPI with auto documentation
- [ ] React frontend (in progress)
- [ ] 85%+ clustering accuracy validation
- [ ] <30s end-to-end performance
- [ ] Slack OAuth full integration

## Roadmap

**Phase 2: Frontend (In Progress)**
- React dashboard with Vite + Tailwind
- FeedbackInbox component (table with filters)
- ClusterView component (expandable cards)
- RoadmapDashboard component (prioritized list)

**Phase 3: Integration & Polish**
- Complete Slack OAuth flow
- NLP accuracy validation with ground truth
- Performance optimization (caching, batching)
- CSV import/export

**Phase 4: Deployment**
- Docker containerization
- PostgreSQL migration
- Production deployment guide
- CI/CD pipeline

## Development Notes

**Current Status:** Backend complete, frontend in development

**Environment:**
- Python 3.12.3
- WSL2 Ubuntu
- SQLite for MVP (PostgreSQL-ready)

**Git Workflow:**
```bash
# Regular commits as features complete
git add .
git commit -m "feat: implement clustering engine"
git push origin main
```

## License

MIT License - Built as a portfolio project demonstrating:
- Product management (feedback aggregation, prioritization)
- Full-stack development (FastAPI + React)
- NLP/ML engineering (clustering, sentiment analysis)
- System design (scalable architecture, migrations)

---

**Built by:** Varun Venkatesh
**Contact:** [GitHub](https://github.com/nlevarun)
