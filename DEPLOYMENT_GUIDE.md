# Compass API Platform - Deployment Guide

Complete guide for deploying the enhanced Compass API with SDKs and webhooks to production.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Migration](#database-migration)
4. [API Deployment](#api-deployment)
5. [SDK Publishing](#sdk-publishing)
6. [Documentation Hosting](#documentation-hosting)
7. [Monitoring & Logging](#monitoring--logging)
8. [Post-Deployment](#post-deployment)

---

## Prerequisites

### Required
- Python 3.8+
- PostgreSQL 13+ (production database)
- Node.js 16+ (for TypeScript SDK build)
- SSL certificate for HTTPS
- Domain name (e.g., api.compass.example.com)

### Recommended
- Redis (for rate limiting and caching)
- Load balancer (AWS ALB, nginx)
- CDN for documentation (CloudFlare, AWS CloudFront)
- Monitoring tools (Datadog, New Relic, Prometheus)
- Log aggregation (ELK stack, Papertrail, CloudWatch)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/compass.git
cd compass
```

### 2. Set Up Python Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/compass

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://app.compass.example.com,https://dashboard.compass.example.com

# Security
API_KEY_SECRET=your-secret-key-here  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
WEBHOOK_SECRET_KEY=your-webhook-secret  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Rate Limiting
RATE_LIMIT_STORAGE=redis://localhost:6379/0  # Optional, uses memory if not set

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn  # Optional

# Email (for notifications)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=notifications@compass.example.com
SMTP_PASSWORD=your-smtp-password
```

### 4. Update Configuration

Edit `backend/main_v1.py` for production:

```python
# BEFORE (Development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AFTER (Production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.compass.example.com",
        "https://dashboard.compass.example.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Database Migration

### 1. Create Production Database

```bash
# PostgreSQL
createdb compass_production

# Or via psql
psql -U postgres
CREATE DATABASE compass_production;
CREATE USER compass_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE compass_production TO compass_user;
```

### 2. Update Database Connection

In `backend/database.py`:

```python
import os
from sqlalchemy import create_engine

# Use environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://compass_user:password@localhost:5432/compass_production"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=20,        # Connection pool size
    max_overflow=40      # Max connections beyond pool_size
)
```

### 3. Run Migrations

```bash
# Initialize database
python -c "from database import init_db; init_db()"

# Or use Alembic for versioned migrations
alembic upgrade head
```

### 4. Create Initial API Key

```bash
python -c "
from database import get_db
from models import APIKey
import hashlib
import secrets

api_key = f'compass_{secrets.token_urlsafe(32)}'
key_hash = hashlib.sha256(api_key.encode()).hexdigest()

with get_db() as db:
    db_key = APIKey(
        name='Production Master Key',
        key_hash=key_hash,
        key_prefix=api_key[:12],
        is_active=True
    )
    db.add(db_key)
    db.commit()
    print(f'API Key: {api_key}')
"
```

**⚠️ IMPORTANT:** Save this master key securely!

---

## API Deployment

### Option 1: Docker (Recommended)

#### 1. Create Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main_v1:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://compass_user:password@db:5432/compass
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: compass
      POSTGRES_USER: compass_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 3. Deploy

```bash
docker-compose up -d
```

### Option 2: Cloud Platform (AWS, GCP, Azure)

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 compass-api

# Create environment
eb create compass-prod

# Deploy
eb deploy
```

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/compass-api

# Deploy
gcloud run deploy compass-api \
  --image gcr.io/PROJECT_ID/compass-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure App Service

```bash
# Create resource group
az group create --name compass-rg --location eastus

# Create app service plan
az appservice plan create \
  --name compass-plan \
  --resource-group compass-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group compass-rg \
  --plan compass-plan \
  --name compass-api \
  --runtime "PYTHON|3.11"

# Deploy
az webapp up --name compass-api
```

### Option 3: Traditional Server (Ubuntu)

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql nginx

# Set up application
cd /var/www/compass
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/compass.service
```

```ini
[Unit]
Description=Compass API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/compass/backend
Environment="PATH=/var/www/compass/venv/bin"
ExecStart=/var/www/compass/venv/bin/uvicorn main_v1:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl enable compass
sudo systemctl start compass
```

#### Configure nginx

```nginx
# /etc/nginx/sites-available/compass
server {
    listen 80;
    server_name api.compass.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/compass /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Set up SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.compass.example.com
```

---

## SDK Publishing

### Python SDK (PyPI)

#### 1. Prepare Package

```bash
cd backend/sdk/python

# Update version in setup.py
# Edit setup.py and increment version number

# Build package
python setup.py sdist bdist_wheel
```

#### 2. Test on Test PyPI

```bash
# Install twine
pip install twine

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ compass-sdk
```

#### 3. Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify
pip install compass-sdk
```

### TypeScript SDK (NPM)

#### 1. Prepare Package

```bash
cd frontend/sdk/typescript

# Update version in package.json
npm version patch  # or minor, or major

# Build package
npm run build
```

#### 2. Test Locally

```bash
# Pack for local testing
npm pack

# Install in test project
cd /path/to/test-project
npm install /path/to/compass-sdk/compass-sdk-1.0.0.tgz
```

#### 3. Publish to NPM

```bash
# Login to NPM
npm login

# Publish
npm publish

# Verify
npm info compass-sdk
```

---

## Documentation Hosting

### Option 1: GitHub Pages

```bash
# Create docs branch
git checkout -b gh-pages

# Copy documentation
mkdir -p docs
cp docs/*.md docs/

# Create index.html
cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Compass API Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/docsify/themes/vue.css">
</head>
<body>
    <div id="app"></div>
    <script>
        window.$docsify = {
            name: 'Compass API',
            repo: 'https://github.com/your-org/compass',
            loadSidebar: true,
            subMaxLevel: 3
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/docsify/lib/docsify.min.js"></script>
</body>
</html>
EOF

# Push to GitHub
git add .
git commit -m "Add documentation"
git push origin gh-pages

# Enable GitHub Pages in repository settings
```

Visit: https://your-org.github.io/compass

### Option 2: ReadTheDocs

1. Sign up at https://readthedocs.org
2. Connect your GitHub repository
3. Configure build settings
4. Documentation auto-builds on push

### Option 3: Custom Domain

```bash
# Use static site generator (MkDocs, Docusaurus, etc.)
pip install mkdocs mkdocs-material

# Create mkdocs.yml
cat > mkdocs.yml << 'EOF'
site_name: Compass API Documentation
theme:
  name: material
nav:
  - Home: index.md
  - API Reference: API.md
  - Developer Guide: DEVELOPER_GUIDE.md
EOF

# Build
mkdocs build

# Deploy to your hosting (S3, Netlify, Vercel, etc.)
aws s3 sync site/ s3://docs.compass.example.com/
```

---

## Monitoring & Logging

### 1. Application Monitoring (Sentry)

```bash
pip install sentry-sdk
```

```python
# backend/main_v1.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

### 2. Logging Configuration

```python
# backend/logging_config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/var/log/compass/api.log')
        ]
    )

# In main_v1.py
from logging_config import setup_logging
setup_logging()
```

### 3. Metrics Collection (Prometheus)

```bash
pip install prometheus-fastapi-instrumentator
```

```python
# backend/main_v1.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

Instrumentator().instrument(app).expose(app)
```

### 4. Health Checks

```python
# backend/main_v1.py
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Check database
        with get_db() as db:
            db.execute("SELECT 1")

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check API health
curl https://api.compass.example.com/health

# Test authentication
curl https://api.compass.example.com/api/v1/stats \
  -H "X-API-Key: your_production_key"

# Verify rate limiting
for i in {1..70}; do
  curl https://api.compass.example.com/api/v1/stats \
    -H "X-API-Key: your_key"
done
# Should see 429 after 60 requests
```

### 2. Create Initial Data

```bash
# Sync feedback sources
curl -X POST https://api.compass.example.com/api/v1/sources/sync \
  -H "X-API-Key: your_key"

# Run clustering
curl -X POST https://api.compass.example.com/api/v1/clustering/run \
  -H "X-API-Key: your_key"

# Generate roadmap
curl -X POST https://api.compass.example.com/api/v1/roadmap/generate \
  -H "X-API-Key: your_key"
```

### 3. Set Up Monitoring Alerts

Configure alerts for:
- API errors (5xx responses)
- High latency (p95 > 1s)
- Rate limit hits
- Webhook failures
- Database connection issues

### 4. Create API Keys for Teams

```bash
# Development team
curl -X POST https://api.compass.example.com/api/v1/api-keys \
  -H "X-API-Key: master_key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Development Team", "expires_in_days": 90}'

# Analytics dashboard
curl -X POST https://api.compass.example.com/api/v1/api-keys \
  -H "X-API-Key: master_key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Analytics Dashboard", "expires_in_days": 365}'
```

### 5. Documentation Announcement

Send to developers:

```
📢 Compass API is now live!

🔗 API Base URL: https://api.compass.example.com
📚 Documentation: https://docs.compass.example.com
🔑 Get API Key: https://app.compass.example.com/api-keys

Getting Started:
- Python: pip install compass-sdk
- TypeScript: npm install compass-sdk

Questions? support@compass.example.com
```

---

## Rollback Plan

If issues occur, rollback steps:

### 1. Revert to Previous API

```bash
# If using Docker
docker-compose down
git checkout previous-stable-tag
docker-compose up -d

# If using systemd
sudo systemctl stop compass
cd /var/www/compass
git checkout previous-stable-tag
sudo systemctl start compass
```

### 2. Database Rollback

```bash
# Restore from backup
pg_restore -U compass_user -d compass_production backup.dump
```

### 3. Notify Users

```
⚠️ Maintenance Notice

We've temporarily reverted to the previous API version due to [issue].
Working on a fix. ETA: [time]

Status: https://status.compass.example.com
```

---

## Maintenance Schedule

### Daily
- Monitor error rates
- Check webhook delivery success rates
- Review API usage metrics

### Weekly
- Review slow queries
- Check disk space
- Update dependencies (security patches)

### Monthly
- Rotate API keys
- Review and optimize database indexes
- Analyze API usage patterns
- Update documentation

### Quarterly
- Major dependency updates
- Performance optimization
- Security audit
- Capacity planning

---

## Checklist

### Pre-Deployment
- [ ] PostgreSQL database set up
- [ ] Environment variables configured
- [ ] CORS origins updated for production
- [ ] SSL certificate installed
- [ ] Master API key created
- [ ] Monitoring tools configured
- [ ] Backup strategy in place

### Deployment
- [ ] API deployed and healthy
- [ ] Database migrated
- [ ] Initial data loaded
- [ ] Rate limiting tested
- [ ] Authentication working

### Post-Deployment
- [ ] Python SDK published to PyPI
- [ ] TypeScript SDK published to NPM
- [ ] Documentation hosted
- [ ] Team API keys created
- [ ] Monitoring alerts configured
- [ ] Announcement sent

### Follow-Up (Week 1)
- [ ] Monitor error rates
- [ ] Check webhook success rates
- [ ] Review API usage
- [ ] Gather developer feedback
- [ ] Update documentation based on feedback

---

## Support Contacts

- **DevOps:** devops@compass.example.com
- **API Support:** api-support@compass.example.com
- **Security:** security@compass.example.com
- **On-Call:** +1-XXX-XXX-XXXX

---

**Deployment Date:** _______________________

**Deployed By:** _______________________

**Sign-Off:** _______________________
