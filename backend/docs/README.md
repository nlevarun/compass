# Compass Backend Documentation

## Overview

Compass is a Customer Feedback Intelligence Platform that aggregates feedback from multiple sources, uses NLP to cluster similar requests, and generates data-driven product roadmaps.

## Documentation Index

### Getting Started
- [Installation & Setup](../README.md)
- [API Overview](API_OVERVIEW.md)
- [Database Schema](DATABASE_SCHEMA.md)

### Core Features
- [Feedback Sources & Ingestion](SOURCES.md)
- [NLP Clustering](CLUSTERING.md)
- [Priority Calculation](PRIORITY_CALCULATION.md)
- [Roadmap Generation](ROADMAP.md)

### Advanced Features
- **[Historical Data Import](IMPORTING_DATA.md)** ⭐ NEW
- **[Jira & Linear Integration](JIRA_INTEGRATION.md)** ⭐ NEW
- [WebSockets & Real-time Updates](WEBSOCKETS.md)
- [Custom Scoring Formulas](CUSTOM_SCORING.md)

### Integration Guides
- [Slack Integration](SLACK_INTEGRATION.md)
- [Email Integration](EMAIL_INTEGRATION.md)
- [Support Tool Integration](SUPPORT_INTEGRATION.md)
- [Zendesk Import](IMPORTING_DATA.md#zendesk-import)
- [Intercom Import](IMPORTING_DATA.md#intercom-import)
- [CSV Import](IMPORTING_DATA.md#csv-import)

### API Reference
- [REST API Endpoints](API_REFERENCE.md)
- [WebSocket Events](WEBSOCKET_EVENTS.md)
- [Webhooks](WEBHOOKS.md)

### Development
- [Architecture](ARCHITECTURE.md)
- [Testing](TESTING.md)
- [Deployment](DEPLOYMENT.md)
- [Contributing](CONTRIBUTING.md)

---

## Quick Links

### Historical Data Import
Import years of feedback from Zendesk, Intercom, or CSV:
- [Import Guide](IMPORTING_DATA.md)
- [API: POST /api/import/zendesk](IMPORTING_DATA.md#zendesk-import)
- [API: POST /api/import/intercom](IMPORTING_DATA.md#intercom-import)
- [API: POST /api/import/csv](IMPORTING_DATA.md#csv-import)

### Jira & Linear Sync
Bidirectional integration with project management tools:
- [Integration Guide](JIRA_INTEGRATION.md)
- [API: POST /api/integrations/jira/create-issue](JIRA_INTEGRATION.md#create-issues-from-clusters)
- [API: POST /api/integrations/linear/create-issue](JIRA_INTEGRATION.md#create-issues-from-clusters)
- [Bidirectional Sync](JIRA_INTEGRATION.md#bidirectional-status-sync)

---

## Competitive Advantages

### 1. Historical Data Import
Unlike competitors (Productboard, Aha!, UserVoice) which only handle new data, Compass can import **years** of historical feedback from:
- Zendesk (all tickets + comments + customer data)
- Intercom (all conversations + messages)
- Any CSV file (with auto-mapping)

**Why it matters:** Start with day-one insights, not waiting months for data.

### 2. Bidirectional Jira/Linear Sync
Most tools do one-way sync or sync poorly. Compass offers:
- **Compass → Jira/Linear:** Auto-create issues with customer context
- **Jira/Linear → Compass:** Sync status back to roadmap
- **Auto-priority updates** based on feedback changes
- **Customer feedback as comments** on issues

**Why it matters:** Keep engineering in sync with customer needs automatically.

### 3. NLP-Powered Clustering
Advanced semantic clustering (not just keyword matching):
- Uses sentence transformers for deep understanding
- Auto-generates cluster labels
- Links similar feedback across sources

### 4. Revenue-Weighted Prioritization
Not just vote counting:
- Customer revenue impact
- Sentiment analysis
- Churn risk scoring
- Custom priority formulas (ICE, RICE, WSJF)

---

## Architecture

```
/backend/
├── main.py                 # FastAPI application
├── models.py               # SQLAlchemy models
├── database.py             # Database connection
├── ingestion/              # Feedback ingestion
│   ├── sources.py          # Source connectors
│   └── mock_generators.py  # Mock data
├── import/                 # Historical data import ⭐ NEW
│   ├── zendesk_importer.py
│   ├── intercom_importer.py
│   └── csv_importer.py
├── integrations/           # External integrations ⭐ NEW
│   ├── jira_sync.py
│   └── linear_sync.py
├── nlp/                    # NLP & clustering
│   ├── clustering.py
│   └── sentiment.py
├── priority/               # Priority calculation
│   └── calculator.py
└── docs/                   # Documentation
    ├── IMPORTING_DATA.md   ⭐ NEW
    ├── JIRA_INTEGRATION.md ⭐ NEW
    └── ...
```

---

## API Endpoints Summary

### Core Endpoints (15)
- Sources: 2 endpoints
- Feedback: 2 endpoints
- Clustering: 2 endpoints
- Roadmap: 3 endpoints
- Stats: 1 endpoint
- WebSocket: 1 endpoint
- Events: 1 endpoint
- Priority: 3 endpoints

### Import Endpoints (5) ⭐ NEW
- POST /api/import/zendesk
- POST /api/import/intercom
- POST /api/import/csv
- GET /api/import/status/{job_id}
- GET /api/import/jobs

### Jira Integration (5) ⭐ NEW
- POST /api/integrations/jira/test
- POST /api/integrations/jira/create-issue
- POST /api/integrations/jira/link-issue
- GET /api/integrations/jira/status/{jira_key}
- POST /api/integrations/jira/sync

### Linear Integration (5) ⭐ NEW
- POST /api/integrations/linear/test
- POST /api/integrations/linear/create-issue
- POST /api/integrations/linear/link-issue
- GET /api/integrations/linear/status/{issue_id}
- POST /api/integrations/linear/sync

**Total: 30 endpoints**

---

## Database Schema

### Core Tables
- `sources` - Feedback sources (Slack, Email, etc.)
- `feedback` - Individual feedback entries
- `clusters` - NLP-generated clusters
- `roadmap_items` - Prioritized roadmap

### Import Tables ⭐ NEW
- `import_jobs` - Track import job status
  - Stores: job_type, status, progress, results, errors

### Integration Tables ⭐ NEW
- `jira_issues` - Linked Jira issues
  - Stores: jira_key, status, priority, sync status
- `linear_issues` - Linked Linear issues
  - Stores: linear_id, status, priority, sync status

---

## Tech Stack

- **Framework:** FastAPI 0.109
- **Database:** SQLite (MVP) → PostgreSQL (production)
- **NLP:** sentence-transformers, scikit-learn
- **Integrations:**
  - Jira: `jira-python` library
  - Linear: GraphQL API
  - Zendesk: REST API v2
  - Intercom: REST API v2.11
- **Real-time:** WebSockets
- **Data Processing:** pandas, numpy

---

## Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///compass.db

# Jira (optional)
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=email@company.com
JIRA_API_TOKEN=your_token

# Linear (optional)
LINEAR_API_KEY=lin_api_...

# Zendesk (for imports)
ZENDESK_SUBDOMAIN=yourcompany
ZENDESK_EMAIL=admin@company.com
ZENDESK_API_TOKEN=your_token

# Intercom (for imports)
INTERCOM_ACCESS_TOKEN=your_token
```

---

## Getting Started

### 1. Install Dependencies

```bash
cd /home/wsl-user/compass/backend
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python database.py
```

### 3. Start Server

```bash
python main.py
# or
uvicorn main:app --reload
```

### 4. Import Historical Data

See [IMPORTING_DATA.md](IMPORTING_DATA.md)

### 5. Set Up Jira/Linear

See [JIRA_INTEGRATION.md](JIRA_INTEGRATION.md)

---

## Support

- Documentation: This directory
- API Docs: http://localhost:8000/docs (Swagger UI)
- Issues: GitHub Issues
- Email: support@compass.example.com

---

## Changelog

### 2026-08-03
- ✅ Historical data import (Zendesk, Intercom, CSV)
- ✅ Jira bidirectional sync
- ✅ Linear integration
- ✅ Import job tracking
- ✅ Background job processing
- ✅ Documentation (IMPORTING_DATA.md, JIRA_INTEGRATION.md)

### Previous Releases
- Advanced priority calculation
- WebSocket real-time updates
- Custom scoring formulas
- At-risk customer detection
- NLP clustering engine
- Basic roadmap generation
