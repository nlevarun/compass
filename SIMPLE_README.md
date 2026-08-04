# Compass - Customer Feedback Intelligence Platform

**Simple. Reliable. Revenue-Focused.**

Compass helps you make better product decisions by automatically analyzing customer feedback and prioritizing features based on revenue impact.

---

## What Does Compass Do?

### The Problem
Your customers are telling you what they want across Slack, email, support tickets, and surveys. But that feedback is scattered, unorganized, and hard to prioritize.

### The Solution
Compass:
1. **Collects** feedback from all your sources (Slack, email, support, etc.)
2. **Clusters** similar feedback using AI (e.g., "All mobile app performance complaints")
3. **Prioritizes** features based on customer revenue + sentiment + frequency
4. **Generates** a roadmap of what to build next

---

## Quick Start (3 Steps)

### 1. Setup Everything
```bash
cd /home/wsl-user/compass/backend
python3 fix_all.py
```

This will:
- Create virtual environment
- Install dependencies
- Initialize database
- Create sample data

### 2. Start the Server
```bash
cd /home/wsl-user/compass/backend
./venv/bin/python main_simple.py
```

Server starts at: http://localhost:8000

### 3. Test It Works
```bash
cd /home/wsl-user/compass
bash TEST_BASIC.sh
```

---

## How to Use Compass

### Step 1: Import Feedback
```bash
curl -X POST http://localhost:8000/api/sources/sync
```

This syncs feedback from all your configured sources. For MVP, it generates realistic sample data.

**Result:** 20+ new feedback items from customers like "Acme Corp", "Global Systems", etc.

### Step 2: Run Clustering
```bash
curl -X POST http://localhost:8000/api/clustering/run
```

AI analyzes all feedback and groups similar requests together.

**Result:** Clusters like:
- "Mobile App Issues" (15 requests, $2.5M revenue)
- "Performance Problems" (23 requests, $3.8M revenue)
- "Export & Reporting" (8 requests, $1.2M revenue)

### Step 3: Generate Roadmap
```bash
curl -X POST http://localhost:8000/api/roadmap/generate
```

Creates a prioritized list of features to build, ranked by revenue impact.

**Result:** Ranked roadmap:
1. Fix: Performance Problems ($3.8M impacted)
2. Fix: Mobile App Issues ($2.5M impacted)
3. Fix: Export & Reporting ($1.2M impacted)

### Step 4: View Results
```bash
# Dashboard stats
curl http://localhost:8000/api/stats

# All feedback
curl http://localhost:8000/api/feedback

# Clusters
curl http://localhost:8000/api/clusters

# Prioritized roadmap
curl http://localhost:8000/api/roadmap
```

---

## API Documentation

Once the server is running, visit:

**http://localhost:8000/docs**

Interactive Swagger UI with all endpoints documented.

---

## Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Dashboard statistics |
| `/api/sources` | GET | List all feedback sources |
| `/api/sources/sync` | POST | Sync feedback from sources |
| `/api/feedback` | GET | Get all feedback |
| `/api/clustering/run` | POST | Run AI clustering |
| `/api/clusters` | GET | Get all clusters |
| `/api/roadmap/generate` | POST | Generate prioritized roadmap |
| `/api/roadmap` | GET | Get current roadmap |

---

## Architecture (MVP)

```
┌─────────────────────────────────────────────┐
│  Feedback Sources                            │
│  • Slack                                     │
│  • Email                                     │
│  • Support Tickets                           │
│  • GitHub Issues                             │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  Compass Backend (FastAPI)                   │
│  • Ingestion Engine                          │
│  • NLP Clustering (keyword-based)            │
│  • Priority Calculator                       │
│  • Roadmap Generator                         │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  SQLite Database                             │
│  • Sources                                   │
│  • Feedback                                  │
│  • Clusters                                  │
│  • Roadmap Items                             │
└─────────────────────────────────────────────┘
```

---

## Priority Calculation

Compass calculates priority score as:

```
Priority Score = (Revenue Weight × Total Revenue / 10,000)
               + (Sentiment Weight × Avg Sentiment × 10)
               + (Frequency Weight × Request Count × 2)
```

This ensures high-revenue customers' feedback is weighted appropriately.

---

## What's Included (MVP)

✅ **Source Management** - Configure feedback sources
✅ **Feedback Collection** - Sync from multiple channels
✅ **NLP Clustering** - Group similar feedback
✅ **Priority Scoring** - Revenue-weighted prioritization
✅ **Roadmap Generation** - Auto-generate feature roadmap
✅ **REST API** - Full API with documentation
✅ **SQLite Database** - Easy setup, no external DB needed

---

## What's NOT Included (Yet)

❌ Public feedback boards (like Canny)
❌ Real-time webhooks
❌ Advanced ML clustering (BERTopic, sentence transformers)
❌ Jira/Linear integration
❌ Session replay
❌ MCP protocol support
❌ PostgreSQL support

These features exist in the codebase but are **disabled** for stability.

---

## Troubleshooting

### "Module not found" errors
```bash
cd /home/wsl-user/compass/backend
python3 fix_all.py
```

### "Database not initialized"
```bash
cd /home/wsl-user/compass/backend
./venv/bin/python -c "from database import init_db; init_db()"
```

### "No feedback found"
```bash
curl -X POST http://localhost:8000/api/sources/sync
```

### Test everything
```bash
cd /home/wsl-user/compass
bash TEST_BASIC.sh
```

---

## Files You Need

### Core Files (Must Exist)
- `backend/main_simple.py` - Simplified working API
- `backend/models.py` - Database models
- `backend/database.py` - Database connection
- `backend/requirements.txt` - Dependencies

### Setup Files
- `backend/fix_all.py` - One-command setup
- `TEST_BASIC.sh` - Test script

### Original Files (Reference Only)
- `backend/main.py` - Full-featured version (may have broken imports)
- `backend/nlp/` - Advanced NLP features
- `backend/priority/` - Advanced priority algorithms
- `backend/integrations/` - Third-party integrations

**For MVP, only use `main_simple.py`**

---

## Development Workflow

### 1. Make Changes
Edit `backend/main_simple.py`

### 2. Restart Server
```bash
# Kill existing server (Ctrl+C)
./venv/bin/python main_simple.py
```

Or use auto-reload:
```bash
./venv/bin/uvicorn main_simple:app --reload --port 8000
```

### 3. Test Changes
```bash
curl http://localhost:8000/api/stats
```

---

## Database Schema

### Sources Table
- `id` - Unique source ID
- `name` - Source name ("Slack #feedback")
- `source_type` - "real" or "mock"
- `is_active` - Active status
- `config` - JSON configuration
- `last_synced_at` - Last sync timestamp

### Feedback Table
- `id` - Unique feedback ID
- `source_id` - Reference to source
- `text` - Feedback content
- `title` - Optional title
- `customer_name` - Customer who submitted
- `customer_revenue` - Annual revenue
- `sentiment_score` - -1.0 to 1.0
- `submitted_at` - When customer submitted
- `cluster_id` - Assigned cluster

### Clusters Table
- `id` - Unique cluster ID
- `label` - Cluster name ("Mobile App Issues")
- `description` - Description
- `size` - Number of feedback items
- `priority_score` - Calculated priority
- `total_revenue` - Sum of customer revenues
- `avg_sentiment` - Average sentiment

### Roadmap Items Table
- `id` - Unique item ID
- `cluster_id` - Reference to cluster
- `title` - Feature title
- `description` - Description
- `rank` - Priority rank (1 = highest)
- `priority_score` - Score
- `request_count` - Number of requests
- `impacted_revenue` - Total revenue impacted
- `status` - "proposed", "planned", "in_progress", "shipped"

---

## Contributing

This is MVP version focused on **reliability over features**.

### Guidelines
1. Keep `main_simple.py` simple and working
2. No external dependencies unless critical
3. All endpoints must handle errors gracefully
4. Test with `TEST_BASIC.sh` before committing

---

## License

MIT License - See LICENSE file

---

## Support

For issues or questions:
1. Run `bash TEST_BASIC.sh` to diagnose problems
2. Check logs in terminal
3. Visit http://localhost:8000/docs for API reference

---

**Remember: Simple, reliable, revenue-focused. That's what Compass is about.**
