# Historical Data Import Guide

Compass supports importing years of historical feedback from support tools and CSV files. This guide covers all import methods and best practices.

## Supported Import Sources

### 1. Zendesk (Support Tickets)
Import all historical support tickets, including:
- Ticket descriptions and subjects
- Comments (public and private)
- Customer information
- Tags and metadata
- Status and priority

### 2. Intercom (Customer Conversations)
Import historical conversations, including:
- Conversation messages
- Customer data
- Tags and labels
- Conversation ratings
- State information

### 3. CSV Files (Generic)
Import from any CSV file with:
- Auto-detection of column mapping
- Customizable field mapping
- Validation and preview
- Batch processing

---

## Quick Start

### Zendesk Import

```bash
# 1. Get your Zendesk credentials
# - Subdomain: yourcompany (from yourcompany.zendesk.com)
# - Email: admin@yourcompany.com
# - API Token: Generate from Admin > Channels > API

# 2. Start import via API
POST /api/import/zendesk
{
  "subdomain": "yourcompany",
  "email": "admin@yourcompany.com",
  "api_token": "your_api_token_here",
  "start_date": "2019-01-01T00:00:00",
  "end_date": "2026-12-31T23:59:59",
  "status_filter": ["closed", "solved"],
  "fetch_comments": true,
  "fetch_users": true
}

# 3. Monitor progress
GET /api/import/status/{job_id}

# 4. View imported data
GET /api/feedback?source_id=<zendesk_source_id>
```

### Intercom Import

```bash
# 1. Get your Intercom API token
# - Go to Intercom Settings > Developers > Developer Hub
# - Create new app or use existing
# - Copy Access Token

# 2. Start import via API
POST /api/import/intercom
{
  "access_token": "your_intercom_token_here",
  "start_date": "2019-01-01T00:00:00",
  "end_date": "2026-12-31T23:59:59",
  "state_filter": "closed",
  "fetch_parts": true,
  "fetch_users": true
}

# 3. Monitor progress
GET /api/import/status/{job_id}
```

### CSV Import

```bash
# 1. Upload CSV file
POST /api/import/csv
Content-Type: multipart/form-data
file: your_feedback.csv

# Response includes:
# - Column preview
# - Suggested mapping
# - File path for next step

# 2. Review and start import
POST /api/import/csv/start
{
  "file_path": "/tmp/compass_uploads/...",
  "column_mapping": {
    "text": "feedback_text",
    "title": "subject",
    "customer_name": "customer",
    "customer_revenue": "arr",
    "submitted_at": "date_submitted",
    "sentiment_score": "rating"
  },
  "skip_invalid": true
}

# 3. Monitor progress
GET /api/import/status/{job_id}
```

---

## Detailed Configuration

### Zendesk Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subdomain` | string | Yes | Zendesk subdomain (e.g., "yourcompany") |
| `email` | string | Yes | Admin email for authentication |
| `api_token` | string | Yes | API token (not password!) |
| `start_date` | string | No | ISO 8601 date (default: 5 years ago) |
| `end_date` | string | No | ISO 8601 date (default: now) |
| `status_filter` | array | No | Filter by status (e.g., ["closed", "solved"]) |
| `fetch_comments` | boolean | No | Include ticket comments (default: true) |
| `fetch_users` | boolean | No | Fetch customer data (default: true) |

**Rate Limits:**
- Zendesk allows 700 requests/minute
- Importer automatically handles rate limiting
- Large imports (10,000+ tickets) may take hours

**Best Practices:**
- Start with a small date range to test
- Import closed/solved tickets first
- Use `fetch_users: true` for revenue data
- Run during off-peak hours for large imports

### Intercom Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `access_token` | string | Yes | Intercom API access token |
| `start_date` | string | No | ISO 8601 date (default: 5 years ago) |
| `end_date` | string | No | ISO 8601 date (default: now) |
| `state_filter` | string | No | Filter by state ("open", "closed", "snoozed") |
| `fetch_parts` | boolean | No | Include conversation messages (default: true) |
| `fetch_users` | boolean | No | Fetch contact data (default: true) |

**Rate Limits:**
- Intercom has dynamic rate limits
- Importer automatically handles throttling
- Typical import speed: 100-200 conversations/minute

**Best Practices:**
- Import closed conversations first
- Enable `fetch_users` for customer revenue data
- Use custom attributes for revenue (if configured in Intercom)

### CSV Configuration

#### Column Mapping

Required fields:
- `text` - Feedback text (required)

Optional fields:
- `title` - Feedback title/subject
- `customer_name` - Customer name
- `customer_revenue` - Annual revenue (numeric)
- `submitted_at` - Date submitted
- `sentiment_score` - Pre-calculated sentiment (-1 to 1)

#### Auto-Detection

The CSV importer attempts to auto-detect column mapping based on column names:

| Compass Field | Detected Patterns |
|---------------|-------------------|
| `text` | feedback, text, comment, description, body, message, content |
| `title` | title, subject, summary, heading |
| `customer_name` | customer, name, user, contact, client, account |
| `customer_revenue` | revenue, arr, mrr, value, contract |
| `submitted_at` | date, created, submitted, timestamp, time |
| `sentiment_score` | sentiment, score, rating |

#### Data Formats

**Dates:**
- ISO 8601: `2026-01-15T10:30:00Z`
- US format: `01/15/2026`
- European format: `15/01/2026`
- Relative: `2 days ago`, `yesterday`

**Revenue:**
- Numeric: `100000`
- With currency: `$100,000`
- With commas: `100,000.00`

**Sentiment:**
- Scale: -1.0 (negative) to 1.0 (positive)
- 0.0 is neutral

---

## Monitoring Import Jobs

### Check Job Status

```bash
GET /api/import/status/{job_id}
```

Response:
```json
{
  "job_id": "uuid-here",
  "type": "zendesk",
  "status": "running",
  "total_items": 10000,
  "processed_items": 3500,
  "failed_items": 12,
  "started_at": "2026-08-03T10:00:00Z",
  "completed_at": null,
  "result_summary": null,
  "error_log": null
}
```

### List All Jobs

```bash
GET /api/import/jobs?limit=50
```

---

## Post-Import Steps

### 1. Verify Data

```bash
# Check total feedback count
GET /api/stats

# View recent imported feedback
GET /api/feedback?limit=100

# Check data quality
GET /api/feedback?source_id={import_source_id}
```

### 2. Run Clustering

After importing, run clustering to group similar feedback:

```bash
POST /api/clustering/run
{
  "eps": 0.5,
  "min_samples": 3
}
```

### 3. Generate Roadmap

Create prioritized roadmap from clusters:

```bash
POST /api/roadmap/generate
```

---

## Troubleshooting

### Common Issues

#### "API token invalid"
- Verify token is correct
- Ensure token has admin permissions
- Check token hasn't expired

#### "Rate limit exceeded"
- Importer should handle automatically
- If persists, contact support tool provider
- Consider importing in smaller batches

#### "CSV column not found"
- Check column names match mapping exactly
- Use CSV preview to see actual column names
- Try auto-detection feature

#### "Import job stuck"
- Check job status for error log
- Large imports (50,000+) may take hours
- Restart import with smaller date range if needed

### Performance Tips

**For Large Imports (100,000+ items):**
1. Split by date ranges (e.g., by year)
2. Run during off-peak hours
3. Monitor database size
4. Consider PostgreSQL for production

**Memory Optimization:**
- CSV importer uses chunked reading
- Batch size: 500 items per commit
- Total memory usage: ~100MB per 10,000 items

---

## Data Privacy & Security

### Sensitive Data

**What to exclude:**
- Personal identifiable information (PII)
- Credit card numbers
- Passwords or API keys
- Medical information

**How to exclude:**
1. Use status filters to exclude sensitive tickets
2. Filter CSV before upload
3. Review imported data and delete if needed

### Data Retention

- Imported data stored in Compass database
- Use `DELETE /api/feedback/{id}` to remove entries
- Bulk delete: contact admin

---

## API Reference

### Import Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/import/zendesk` | POST | Start Zendesk import |
| `/api/import/intercom` | POST | Start Intercom import |
| `/api/import/csv` | POST | Upload CSV for preview |
| `/api/import/csv/start` | POST | Start CSV import |
| `/api/import/status/{job_id}` | GET | Get job status |
| `/api/import/jobs` | GET | List all jobs |

### Request/Response Examples

See code samples in Quick Start section above.

---

## Support

For issues or questions:
- Check troubleshooting section
- Review error logs in job status
- Contact support with job_id for debugging

---

## Changelog

- **2026-08-03**: Initial version
- Support for Zendesk, Intercom, CSV
- Background job processing
- Progress tracking
- Auto-detection for CSV
