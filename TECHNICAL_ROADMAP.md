# Compass Technical Architecture & 18-Month Implementation Roadmap

**Document Version:** 1.0
**Date:** 2026-08-04
**Author:** Technical Architecture Team
**Purpose:** Strategic technical roadmap to position Compass as the dominant AI-native feedback intelligence platform

---

## Executive Summary

**Current State:** MVP with solid foundations (NLP clustering, WebSocket real-time, basic integrations)
**Target State:** Enterprise-grade, AI-native platform beating Productboard/Canny at 5x lower cost
**Timeline:** 18 months to market dominance
**Investment Required:** 4-6 engineers (phased), $150-200k infrastructure over 18 months

**Key Differentiators:**
1. Real-time everything (<1s feedback ingestion vs Productboard's 60 minutes)
2. AI-native architecture (MCP server, semantic search, predictive analytics)
3. 85%+ NLP accuracy (vs competitors' 60-70%)
4. Revenue-weighted prioritization (unique to Compass)
5. Cost-efficient at scale (3-5x cheaper than competitors)

---

## 1. Current State Assessment

### 1.1 What's Built and Working ✅

**Backend (Python/FastAPI):**
- ✅ Core API with 40+ endpoints (FastAPI auto-docs at /docs)
- ✅ SQLAlchemy models (7 tables: Source, Feedback, Cluster, RoadmapItem, ImportJob, JiraIssue, LinearIssue, Release, FeatureBuild, Webhook, WebhookDelivery)
- ✅ WebSocket real-time system (ConnectionManager with room subscriptions)
- ✅ Webhook system with retry logic and dead letter queue
- ✅ Python SDK with resource clients (sources, feedback, clusters, roadmap, webhooks)
- ✅ NLP clustering with sentence-transformers (all-MiniLM-L6-v2) + DBSCAN
- ✅ VADER + TextBlob ensemble sentiment analysis
- ✅ Advanced priority calculator (frequency × revenue × sentiment × LTV × churn risk × velocity / effort × complexity)
- ✅ Slack integration (OAuth, real-time message ingestion)
- ✅ Jira/Linear sync integrations (one-way currently)
- ✅ GitHub tracker for PR/commit linking to roadmap items

**Frontend (React/Vite/Tailwind):**
- ✅ Dashboard with real-time stats
- ✅ FeedbackInbox with filters/search
- ✅ ClusterView with expandable cards
- ✅ RoadmapDashboard with prioritized list
- ✅ PriorityAnalysis component
- ✅ WebSocket service with auto-reconnect and exponential backoff
- ✅ Offline-first architecture with local caching
- ✅ PWA support (installable, offline banner)
- ✅ Toast notifications
- ✅ Error boundaries

**Database:**
- ✅ SQLite for MVP (PostgreSQL-ready schema)
- ✅ Indexed for performance (14 indexes)
- ✅ JSON columns for flexibility (embeddings, metadata)

**Integrations:**
- ✅ 1 real (Slack OAuth)
- ✅ 7 mock sources (Email, Support, Surveys, App Reviews, Sales, Interviews, Social)
- ✅ Mock data generator (500+ realistic feedback entries)

**Performance:**
- ✅ <30s roadmap generation (target met)
- ✅ Real-time WebSocket updates (<100ms)
- ⚠️ Clustering: ~2-3 minutes for 500 items (needs optimization)

### 1.2 What Needs Improvement ⚠️

**Backend:**
- ⚠️ NLP: Using basic DBSCAN (need BERTopic for production-grade clustering)
- ⚠️ No semantic search (embeddings stored but not indexed)
- ⚠️ SQLite bottleneck (needs PostgreSQL + pgvector)
- ⚠️ No caching layer (needs Redis for hot data)
- ⚠️ Polling for some sources (need webhooks for all)
- ⚠️ No predictive analytics (churn risk, NPS impact)
- ⚠️ No MCP server (AI-native integration missing)
- ⚠️ One-way integrations (Jira/Linear should be bidirectional)

**Frontend:**
- ⚠️ Basic UI/UX (needs polishing and animations)
- ⚠️ No mobile responsiveness optimization
- ⚠️ Limited accessibility (ARIA labels missing)
- ⚠️ No public feedback board UI

**Infrastructure:**
- ⚠️ No monitoring/alerting (need Sentry, Datadog)
- ⚠️ No CI/CD pipeline
- ⚠️ No load testing/benchmarks
- ⚠️ No Docker/K8s deployment configs

**Security:**
- ⚠️ Basic API key auth (need OAuth2, SSO)
- ⚠️ No rate limiting per user (only global)
- ⚠️ No audit logs
- ⚠️ No GDPR compliance features (data export, deletion)

### 1.3 What's Missing vs Competitors ❌

**Critical Gaps:**
- ❌ Public feedback board (Canny's core feature)
- ❌ GPT-4 insight generation (Productboard has this)
- ❌ Semantic search (Canny AI has basic version)
- ❌ Multi-modal analysis (audio/video transcription)
- ❌ Predictive analytics (churn risk, revenue impact)
- ❌ Mobile app (Productboard has iOS/Android)
- ❌ Self-hosted Docker option (community request)
- ❌ SSO/SAML (enterprise requirement)
- ❌ White-label capabilities (enterprise feature)
- ❌ Session replay integration (Canny partners with FullStory)

**Nice-to-Have Gaps:**
- ❌ Zapier/Make connectors
- ❌ GraphQL API (REST only currently)
- ❌ SDK in TypeScript, Ruby, Go (Python only)
- ❌ Embeddable widget (public board + feedback form)
- ❌ Changelog feature (linked to releases)
- ❌ In-app tours/onboarding
- ❌ Customer health scores

### 1.4 Technical Debt to Address 🔧

**High Priority:**
1. **Database migration to PostgreSQL** - SQLite won't scale beyond 1,000 active users
2. **Async job queue** - Clustering blocks API (need Celery/Redis)
3. **Caching strategy** - Hitting DB on every request (need Redis)
4. **NLP model optimization** - sentence-transformers too slow (need model quantization or switch to BERTopic)
5. **Webhook reliability** - Need dead letter queue monitoring

**Medium Priority:**
6. **API versioning** - Currently no /v1/ versioning strategy
7. **Frontend state management** - Using useState (need Zustand/Redux for complexity)
8. **Test coverage** - <20% coverage (need 80%+)
9. **Documentation** - Missing architecture diagrams, deployment guides
10. **Error handling** - Inconsistent error responses

**Low Priority:**
11. **Code organization** - Some 500+ line files (need refactoring)
12. **TypeScript migration** - Frontend is JS (need TS for type safety)
13. **Internationalization** - English only (need i18n)

---

## 2. Target Architecture (18 Months)

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Web App (React)  │  Mobile App (React Native)  │  Embeddable Widget  │
│  MCP Clients      │  CLI Tool                    │  Browser Extension │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Nginx/Caddy (reverse proxy, SSL termination, rate limiting)           │
│  • REST API (FastAPI)                                                   │
│  • GraphQL API (Strawberry/Ariadne)                                    │
│  • MCP Server (Model Context Protocol)                                 │
│  • WebSocket Server (real-time)                                        │
│  • SSE Server (long-polling fallback)                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
    ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐
    │   API SERVICES    │  │   AI/NLP LAYER    │  │ INTEGRATION HUB  │
    ├───────────────────┤  ├───────────────────┤  ├──────────────────┤
    │ • Auth/AuthZ      │  │ • BERTopic Engine │  │ • Slack Webhook  │
    │ • CRUD Endpoints  │  │ • GPT-4 Insights  │  │ • GitHub Webhook │
    │ • Search API      │  │ • Embeddings Gen  │  │ • Jira Bi-Sync   │
    │ • Webhook Mgmt    │  │ • Sentiment ML    │  │ • Linear Bi-Sync │
    │ • Job Queue       │  │ • Churn Predictor │  │ • Intercom       │
    └───────────────────┘  │ • NPS Impact ML   │  │ • Zendesk        │
                           │ • Semantic Search │  │ • Zapier         │
                           └───────────────────┘  └──────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
    ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐
    │   DATA LAYER      │  │   CACHE LAYER     │  │   QUEUE LAYER    │
    ├───────────────────┤  ├───────────────────┤  ├──────────────────┤
    │ PostgreSQL + ext: │  │ Redis Cluster:    │  │ Redis Queue:     │
    │ • pgvector        │  │ • Session cache   │  │ • Celery/BullMQ  │
    │ • pg_trgm         │  │ • API cache       │  │ • Job priority   │
    │ • timescaledb     │  │ • WS pub/sub      │  │ • Retry logic    │
    │                   │  │ • Rate limiting   │  │ • Dead letter Q  │
    │ ClickHouse:       │  └───────────────────┘  └──────────────────┘
    │ • Analytics       │
    │ • Time-series     │
    │                   │
    │ S3/Minio:         │
    │ • File uploads    │
    │ • Audio/video     │
    │ • Backups         │
    └───────────────────┘
                │
                ▼
    ┌───────────────────────────────────────────┐
    │      MONITORING & OBSERVABILITY           │
    ├───────────────────────────────────────────┤
    │ • Sentry (error tracking)                 │
    │ • Datadog/Prometheus (metrics)            │
    │ • Loki/ELK (logs)                         │
    │ • Uptimerobot (uptime monitoring)         │
    └───────────────────────────────────────────┘
```

### 2.2 Real-Time Layer Architecture

**Problem:** Productboard takes 60 minutes to ingest feedback. Users complain.

**Solution:** Sub-second feedback ingestion with real-time UI updates.

```python
# Webhook → Processing → Broadcast Pipeline

# 1. Webhook receives event (Slack message posted)
@app.post("/webhooks/slack")
async def slack_webhook(event: SlackEvent, background_tasks: BackgroundTasks):
    # Immediate acknowledgment (<50ms)
    background_tasks.add_task(process_slack_event, event)
    return {"status": "ok"}

# 2. Background processing (async, non-blocking)
async def process_slack_event(event):
    # Parse and validate
    feedback = extract_feedback_from_slack(event)

    # Store in DB (with embedding generation queued)
    db_feedback = await store_feedback(feedback)

    # Queue embedding generation (heavy ML task)
    await queue_job("generate_embedding", feedback_id=db_feedback.id)

    # Immediate broadcast to WebSocket clients (<100ms total)
    await ws_manager.broadcast({
        "event": "feedback.new",
        "data": feedback.dict()
    }, room="feedback")

    # Trigger clustering if threshold reached (async)
    if await should_recluster():
        await queue_job("run_clustering", priority="high")

# 3. Embedding generation (background worker)
@celery.task
def generate_embedding(feedback_id):
    feedback = Feedback.get(feedback_id)
    embedding = model.encode(feedback.text)
    feedback.embedding = embedding.tolist()
    feedback.save()

    # Check for similar posts (duplicate detection)
    similar = find_similar_feedback(embedding, threshold=0.90)
    if similar:
        notify_admin_of_potential_duplicate(feedback, similar)
```

**Performance Targets:**
- Webhook acknowledgment: <50ms
- Feedback stored in DB: <200ms
- WebSocket broadcast: <100ms
- Embedding generation: <2s (background)
- Clustering: <30s for 1,000 items (vs current 3 minutes)

### 2.3 AI/NLP Layer Upgrade

**Current:** sentence-transformers + DBSCAN (basic, slow)
**Target:** BERTopic + GPT-4 + pgvector (production-grade, fast)

```python
# Upgraded NLP Pipeline

class AIFeedbackProcessor:
    """Production-grade NLP pipeline"""

    def __init__(self):
        # BERTopic for clustering (better than DBSCAN)
        self.topic_model = BERTopic(
            embedding_model="all-MiniLM-L6-v2",
            umap_model=UMAP(n_components=5, metric="cosine"),
            hdbscan_model=HDBSCAN(min_cluster_size=10),
            calculate_probabilities=True
        )

        # OpenAI for insight generation
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Sentiment ensemble (keep existing VADER + TextBlob)
        self.sentiment_analyzer = EnsembleSentimentAnalyzer()

    async def process_feedback_batch(self, feedback_items: List[Feedback]):
        """Process batch of feedback with full NLP pipeline"""

        # 1. Generate embeddings (batch for efficiency)
        texts = [f.text for f in feedback_items]
        embeddings = self.generate_embeddings_batch(texts)

        # 2. Store embeddings in pgvector
        await self.store_embeddings_bulk(feedback_items, embeddings)

        # 3. Run clustering (BERTopic auto-determines cluster count)
        topics, probs = self.topic_model.fit_transform(texts)

        # 4. Generate topic labels with GPT-4
        topic_labels = await self.generate_topic_labels_gpt4(topics, texts)

        # 5. Sentiment analysis (parallel with asyncio)
        sentiments = await asyncio.gather(*[
            self.sentiment_analyzer.analyze(text) for text in texts
        ])

        # 6. Store clusters in DB
        clusters = await self.create_clusters_from_topics(
            topics, topic_labels, feedback_items, sentiments
        )

        return clusters

    async def generate_topic_labels_gpt4(self, topics, texts):
        """Use GPT-4 to generate descriptive labels"""

        labels = {}
        for topic_id in set(topics):
            if topic_id == -1:  # Outliers
                continue

            # Get sample texts from topic
            topic_texts = [texts[i] for i, t in enumerate(topics) if t == topic_id][:10]

            # GPT-4 prompt
            prompt = f"""Analyze these customer feedback messages and generate a concise, descriptive label (3-5 words):

{chr(10).join(f"- {text}" for text in topic_texts)}

Label (3-5 words):"""

            response = await self.openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20
            )

            labels[topic_id] = response.choices[0].message.content.strip()

        return labels

    async def semantic_search(self, query: str, limit: int = 20) -> List[Feedback]:
        """Semantic search using pgvector"""

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # pgvector cosine similarity search
        results = await db.execute(f"""
            SELECT id, text, 1 - (embedding <=> :query_embedding::vector) AS similarity
            FROM feedback
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :query_embedding::vector
            LIMIT :limit
        """, {"query_embedding": query_embedding, "limit": limit})

        return [Feedback.from_db_row(row) for row in results]

    async def predict_churn_risk(self, customer_id: int) -> ChurnRiskScore:
        """ML model to predict customer churn risk"""

        # Get customer feedback history
        feedback_history = await Feedback.filter(customer_id=customer_id).order_by("-submitted_at").limit(50)

        # Feature engineering
        features = {
            "feedback_count_30d": len([f for f in feedback_history if (now() - f.submitted_at).days <= 30]),
            "avg_sentiment": np.mean([f.sentiment_score for f in feedback_history]),
            "negative_trend": self._calculate_sentiment_trend(feedback_history),
            "response_time_avg": await self._avg_response_time(customer_id),
            "feature_requests_open": await self._count_open_requests(customer_id),
            "competitor_mentions": self._count_competitor_mentions(feedback_history),
            "escalation_count": await self._count_escalations(customer_id),
        }

        # ML model prediction (scikit-learn RandomForest trained on historical churn data)
        churn_probability = self.churn_model.predict_proba([list(features.values())])[0][1]

        return ChurnRiskScore(
            customer_id=customer_id,
            risk_score=churn_probability,
            risk_level="high" if churn_probability > 0.7 else "medium" if churn_probability > 0.4 else "low",
            contributing_factors=self._identify_risk_factors(features, churn_probability)
        )
```

**Performance Improvements:**
- Clustering: 3 min → 30s (6x faster with BERTopic + batch processing)
- Semantic search: N/A → <100ms (pgvector indexed)
- Duplicate detection: 70% accuracy → 90%+ (embeddings vs keyword matching)
- Topic labels: Generic → Descriptive (GPT-4 generated)

### 2.4 Integration Layer (Webhook-First Architecture)

**Current:** Polling-based (inefficient, slow)
**Target:** Webhook-based for all sources (real-time, efficient)

```python
# Webhook-First Integration Architecture

class WebhookIntegrationHub:
    """Central hub for managing all external integrations"""

    SUPPORTED_INTEGRATIONS = {
        "slack": SlackWebhookHandler,
        "github": GitHubWebhookHandler,
        "jira": JiraWebhookHandler,
        "linear": LinearWebhookHandler,
        "intercom": IntercomWebhookHandler,
        "zendesk": ZendeskWebhookHandler,
        "stripe": StripeWebhookHandler,  # For customer revenue tracking
        "segment": SegmentWebhookHandler,  # For user events
    }

    @app.post("/webhooks/{integration}/events")
    async def webhook_receiver(
        integration: str,
        request: Request,
        background_tasks: BackgroundTasks
    ):
        """Universal webhook receiver with signature verification"""

        handler = SUPPORTED_INTEGRATIONS.get(integration)
        if not handler:
            raise HTTPException(404, "Integration not supported")

        # Verify webhook signature
        if not handler.verify_signature(request):
            raise HTTPException(403, "Invalid signature")

        # Parse event
        event = await handler.parse_event(request)

        # Immediate acknowledgment
        background_tasks.add_task(handler.process_event, event)
        return {"status": "ok"}

class JiraWebhookHandler:
    """Bi-directional Jira sync with webhook support"""

    @staticmethod
    async def setup_webhook(jira_config):
        """Register webhook with Jira"""

        webhook_url = f"{settings.API_BASE_URL}/webhooks/jira/events"

        await jira_api.register_webhook(
            url=webhook_url,
            events=["jira:issue_created", "jira:issue_updated", "comment_created"],
            filters={"project": jira_config.project_key}
        )

    @staticmethod
    async def process_event(event: JiraEvent):
        """Process Jira webhook event"""

        if event.type == "jira:issue_updated":
            # Jira issue updated → Update Compass roadmap item
            issue_key = event.data.key

            # Find linked roadmap item
            roadmap_item = await RoadmapItem.filter(
                jira_issues__jira_key=issue_key
            ).first()

            if roadmap_item:
                # Sync status
                jira_status = event.data.fields.status.name
                compass_status = map_jira_status_to_compass(jira_status)

                if roadmap_item.status != compass_status:
                    roadmap_item.status = compass_status
                    await roadmap_item.save()

                    # Notify via WebSocket
                    await ws_manager.broadcast({
                        "event": "roadmap.updated",
                        "data": roadmap_item.dict()
                    }, room="roadmap")

                    # Notify customers (close the loop!)
                    await notify_customers_of_status_change(roadmap_item)

        elif event.type == "jira:issue_created":
            # New Jira issue → Check if related to Compass cluster
            description = event.data.fields.description

            # Semantic search to find related cluster
            related_clusters = await semantic_search_clusters(description)

            if related_clusters:
                # Auto-link to cluster
                await JiraIssue.create(
                    jira_key=event.data.key,
                    cluster_id=related_clusters[0].id,
                    title=event.data.fields.summary
                )

class LinearWebhookHandler:
    """Bi-directional Linear sync (already excellent API)"""

    @staticmethod
    async def process_event(event: LinearEvent):
        """Linear has best-in-class webhooks - leverage them"""

        if event.type == "Issue":
            issue = event.data

            # Find linked roadmap item
            roadmap_item = await RoadmapItem.filter(
                linear_issues__linear_id=issue.id
            ).first()

            if roadmap_item:
                # Sync bidirectionally
                await sync_linear_to_compass(issue, roadmap_item)
            else:
                # Auto-link based on semantic similarity
                similar_items = await semantic_search_roadmap(issue.title)
                if similar_items and similar_items[0].similarity > 0.85:
                    await link_linear_issue_to_roadmap(issue, similar_items[0].item)
```

### 2.5 Data Layer (PostgreSQL + Extensions)

**Migration Strategy:**

```sql
-- PostgreSQL + Extensions Setup

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;        -- pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS pg_trgm;       -- Trigram indexes for fuzzy search
CREATE EXTENSION IF NOT EXISTS timescaledb;   -- Time-series data (analytics)

-- Migrate feedback table with pgvector
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    text TEXT NOT NULL,
    title VARCHAR(500),
    customer_name VARCHAR(200),
    customer_revenue DECIMAL(12, 2),
    sentiment_score REAL,
    submitted_at TIMESTAMP NOT NULL,
    ingested_at TIMESTAMP DEFAULT NOW(),
    cluster_id INTEGER REFERENCES clusters(id),

    -- pgvector for semantic search
    embedding vector(384),  -- all-MiniLM-L6-v2 produces 384-dim vectors

    -- JSONB for flexible metadata
    source_metadata JSONB,
    external_ids JSONB,

    -- Full-text search
    text_search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', text), 'B')
    ) STORED
);

-- Indexes for performance
CREATE INDEX idx_feedback_source_submitted ON feedback(source_id, submitted_at DESC);
CREATE INDEX idx_feedback_cluster ON feedback(cluster_id) WHERE cluster_id IS NOT NULL;
CREATE INDEX idx_feedback_sentiment ON feedback(sentiment_score) WHERE sentiment_score IS NOT NULL;
CREATE INDEX idx_feedback_text_search ON feedback USING GIN(text_search_vector);

-- pgvector indexes (choose based on dataset size)
-- For <1M vectors: IVFFlat (faster build, good recall)
CREATE INDEX idx_feedback_embedding_ivfflat ON feedback
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- For >1M vectors: HNSW (slower build, better recall)
-- CREATE INDEX idx_feedback_embedding_hnsw ON feedback
-- USING hnsw (embedding vector_cosine_ops);

-- Semantic search query (sub-100ms)
PREPARE semantic_search AS
SELECT
    id,
    text,
    customer_name,
    1 - (embedding <=> $1::vector) AS similarity
FROM feedback
WHERE embedding IS NOT NULL
ORDER BY embedding <=> $1::vector
LIMIT $2;

-- Execute: EXECUTE semantic_search('[0.1, 0.2, ...]', 20);
```

**ClickHouse for Analytics:**

```sql
-- ClickHouse table for analytics (time-series optimized)

CREATE TABLE feedback_analytics (
    id UInt64,
    source_id UInt32,
    customer_name String,
    customer_revenue Decimal(12, 2),
    sentiment_score Float32,
    cluster_id Nullable(UInt32),
    submitted_at DateTime,
    ingested_at DateTime,

    -- Additional dimensions
    year UInt16 MATERIALIZED toYear(submitted_at),
    month UInt8 MATERIALIZED toMonth(submitted_at),
    week UInt8 MATERIALIZED toWeek(submitted_at),
    day_of_week UInt8 MATERIALIZED toDayOfWeek(submitted_at)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(submitted_at)
ORDER BY (source_id, submitted_at);

-- Queries run 10-100x faster than PostgreSQL for time-series analytics
SELECT
    toStartOfWeek(submitted_at) AS week,
    count() AS feedback_count,
    avg(sentiment_score) AS avg_sentiment,
    sum(customer_revenue) AS total_revenue
FROM feedback_analytics
WHERE submitted_at >= now() - INTERVAL 90 DAY
GROUP BY week
ORDER BY week;
```

### 2.6 Mobile Layer (Phase 4-5)

**React Native App Architecture:**

```
compass-mobile/
├── src/
│   ├── screens/
│   │   ├── Dashboard.tsx
│   │   ├── FeedbackList.tsx
│   │   ├── ClusterDetail.tsx
│   │   ├── RoadmapView.tsx
│   │   └── Settings.tsx
│   ├── components/
│   │   ├── FeedbackCard.tsx
│   │   ├── VoteButton.tsx
│   │   ├── PriorityBadge.tsx
│   │   └── OfflineSync.tsx
│   ├── services/
│   │   ├── api.ts          # REST API client
│   │   ├── websocket.ts    # WebSocket for real-time
│   │   ├── storage.ts      # AsyncStorage for offline
│   │   └── sync.ts         # Offline sync queue
│   ├── store/
│   │   └── redux/          # Redux for state management
│   └── navigation/
│       └── AppNavigator.tsx
```

**Offline-First Architecture:**

```typescript
// Offline sync queue with conflict resolution

class OfflineSyncManager {
    private syncQueue: SyncOperation[] = [];

    async queueOperation(operation: SyncOperation) {
        // Add to queue
        this.syncQueue.push(operation);
        await this.persistQueue();

        // Try to sync immediately if online
        if (await NetInfo.fetch().then(state => state.isConnected)) {
            await this.processQueue();
        }
    }

    async processQueue() {
        while (this.syncQueue.length > 0) {
            const operation = this.syncQueue[0];

            try {
                await this.executeOperation(operation);
                this.syncQueue.shift();
                await this.persistQueue();
            } catch (error) {
                if (error.code === 'NETWORK_ERROR') {
                    // Stop processing, will retry when back online
                    break;
                } else if (error.code === 'CONFLICT') {
                    // Server state changed, merge conflicts
                    await this.resolveConflict(operation, error.serverState);
                } else {
                    // Unrecoverable error, remove from queue
                    this.syncQueue.shift();
                    await this.persistQueue();
                    this.logError(operation, error);
                }
            }
        }
    }

    async resolveConflict(operation: SyncOperation, serverState: any) {
        // Last-write-wins or manual resolution
        const strategy = operation.conflictStrategy || 'server-wins';

        if (strategy === 'server-wins') {
            // Discard local changes
            this.syncQueue.shift();
        } else if (strategy === 'client-wins') {
            // Force overwrite server
            operation.force = true;
        } else {
            // Manual resolution required
            await this.notifyUserOfConflict(operation, serverState);
        }
    }
}
```

---

## 3. Migration Path (18-Month Phased Roadmap)

### Phase 1: Foundations (Months 1-3) 🏗️

**Goal:** Fix scalability bottlenecks, add real-time everywhere

**Backend Tasks:**
1. ✅ Migrate SQLite → PostgreSQL + pgvector (Week 1-2)
   - Create migration scripts
   - Test on staging with 10k+ feedback items
   - Deploy with zero downtime (read replica cutover)

2. ✅ Add Redis caching layer (Week 2-3)
   - API response caching (60s TTL)
   - WebSocket pub/sub (replace in-memory manager)
   - Rate limiting (per-user, per-IP)
   - Session storage

3. ✅ Implement Celery job queue (Week 3-4)
   - Move clustering to background jobs
   - Move embedding generation to workers
   - Add job status tracking API
   - Configure auto-scaling workers (AWS ECS)

4. ✅ Upgrade NLP to BERTopic (Week 4-6)
   - Replace DBSCAN with BERTopic
   - Add GPT-4 for topic label generation
   - Benchmark: 500 items in <30s
   - A/B test: old vs new clustering accuracy

5. ✅ Switch polling → webhooks (Week 6-8)
   - Slack: Already webhooks ✅
   - GitHub: Add webhook receiver
   - Jira: Setup webhook + bidirectional sync
   - Linear: Setup webhook + bidirectional sync

6. ✅ Add semantic search with pgvector (Week 8-10)
   - Index all existing embeddings
   - Build search API endpoint
   - Add to frontend UI
   - Benchmark: <100ms for 100k items

7. ✅ Monitoring & alerting (Week 10-12)
   - Sentry for error tracking
   - Datadog for metrics (API latency, DB queries, job queue)
   - PagerDuty for on-call alerts
   - Custom dashboard for KPIs

**Frontend Tasks:**
8. ✅ UI polish and animations (Week 1-4)
   - Framer Motion for transitions
   - Loading skeletons
   - Error states
   - Empty states

9. ✅ Mobile responsiveness (Week 4-6)
   - Responsive grid layouts
   - Touch-friendly interactions
   - Bottom nav for mobile

10. ✅ Accessibility improvements (Week 6-8)
    - ARIA labels
    - Keyboard navigation
    - Screen reader testing
    - WCAG 2.1 AA compliance

**Infrastructure Tasks:**
11. ✅ Docker containers (Week 1-2)
    - Dockerfile for backend (FastAPI + Celery)
    - Dockerfile for frontend (Nginx + React build)
    - docker-compose for local dev
    - Multi-stage builds for size optimization

12. ✅ CI/CD pipeline (Week 2-4)
    - GitHub Actions for CI (test, lint, build)
    - Automated deployments to staging
    - Blue-green deployments to production
    - Rollback strategy

13. ✅ Load testing (Week 8-10)
    - k6 scripts for API endpoints
    - Target: 1000 RPS sustained
    - Identify bottlenecks
    - Optimize slow queries

**Success Metrics:**
- ✅ API p95 latency: <200ms
- ✅ Clustering time: <30s for 1,000 items
- ✅ Zero downtime deployments
- ✅ 99.9% uptime
- ✅ <10 Sentry errors per day

**Estimated Effort:** 2 engineers × 3 months = 6 engineer-months

---

### Phase 2: Differentiation (Months 4-6) 🚀

**Goal:** Build features that competitors don't have

**Backend Tasks:**
1. ✅ Build public feedback board API (Week 1-3)
   - Posts, votes, comments tables
   - Public API endpoints (no auth for read)
   - Admin moderation API
   - Status workflow (Open → Planned → In Progress → Complete)

2. ✅ MCP server implementation (Week 3-5)
   - MCP protocol implementation (Model Context Protocol)
   - Natural language queries: "Show me high-priority feedback from enterprise customers"
   - AI-native integration for Claude, ChatGPT, etc.
   - Example queries documented

3. ✅ Session replay integration (Week 5-6)
   - Partner with FullStory or LogRocket
   - Link feedback to session replays
   - Embed replay player in feedback detail view

**Frontend Tasks:**
4. ✅ Public feedback board UI (Week 1-4)
   - Public board view (no login required)
   - Post creation form with duplicate detection
   - Voting UI with real-time updates
   - Status filters and search

5. ✅ Embeddable feedback widget (Week 4-6)
   - Lightweight JS widget (<50kb)
   - Customizable styling
   - Screenshot capture
   - Email notification to admins

**Success Metrics:**
- ✅ MCP server: <500ms query response
- ✅ Public board: 10k votes/day supported
- ✅ Widget: <100ms load time

**Estimated Effort:** 2 engineers × 3 months = 6 engineer-months

---

### Phase 3: AI Powerhouse (Months 7-9) 🤖

**Goal:** Become the most intelligent feedback platform

**Backend Tasks:**
1. ✅ GPT-4 insight generation (Week 1-3)
   - Automatic insight generation for clusters
   - "Why this matters" explanations
   - Suggested next actions
   - Revenue impact predictions

2. ✅ Predictive analytics (Week 3-6)
   - Churn risk prediction model
   - NPS impact estimation
   - Feature adoption forecasting
   - Customer health scores

3. ✅ Multi-modal analysis (Week 6-9)
   - Audio transcription (Whisper API)
   - Video analysis (upload support calls)
   - Image OCR (screenshot text extraction)
   - PDF parsing (survey results)

**Frontend Tasks:**
4. ✅ AI insights dashboard (Week 1-4)
   - Insight cards with explanations
   - Predictive charts (churn risk over time)
   - Recommended actions

5. ✅ Advanced search (Week 4-6)
   - Natural language search
   - Multi-modal search (text + audio + video)
   - Saved searches
   - Search analytics

**Success Metrics:**
- ✅ Insight generation: <5s per cluster
- ✅ Churn prediction: >80% accuracy
- ✅ Multi-modal processing: <30s per file

**Estimated Effort:** 3 engineers × 3 months = 9 engineer-months (includes ML engineer)

---

### Phase 4: Ecosystem (Months 10-12) 🔌

**Goal:** Become integration hub for product teams

**Backend Tasks:**
1. ✅ GraphQL API (Week 1-3)
   - Complement REST with GraphQL
   - Strawberry + FastAPI integration
   - Subscriptions for real-time
   - Schema documentation

2. ✅ Zapier integration (Week 3-5)
   - Zapier CLI app
   - Triggers: New feedback, cluster created, roadmap updated
   - Actions: Create post, update status, add comment
   - Publish to Zapier marketplace

3. ✅ SDK packages (Week 5-8)
   - TypeScript SDK (with full types)
   - Ruby SDK (for Rails apps)
   - Go SDK (for backend services)
   - Auto-generated from OpenAPI spec

4. ✅ Self-hosted Docker (Week 8-10)
   - Docker Compose stack (all services)
   - Kubernetes Helm charts
   - One-line install script
   - Documentation for on-prem deployment

**Frontend Tasks:**
5. ✅ Mobile app MVP (Week 1-8)
   - React Native app (iOS + Android)
   - Core features: Dashboard, feedback list, voting
   - Offline-first architecture
   - Push notifications

6. ✅ Browser extension (Week 8-10)
   - Chrome/Firefox extension
   - Capture feedback from any webpage
   - Screenshot + URL + DOM inspection
   - Quick submit to Compass

**Success Metrics:**
- ✅ GraphQL: <100ms query response
- ✅ Zapier: 50+ active users in first month
- ✅ SDK downloads: 100+ in first month
- ✅ Self-hosted: 10+ deployments in first quarter
- ✅ Mobile app: 4.5+ star rating

**Estimated Effort:** 3 engineers × 3 months = 9 engineer-months

---

### Phase 5: Enterprise (Months 13-18) 🏢

**Goal:** Enterprise-ready for Fortune 500

**Backend Tasks:**
1. ✅ SSO (SAML, OIDC) (Week 1-3)
   - SAML 2.0 support (Okta, OneLogin, Azure AD)
   - OIDC support (Google, GitHub, GitLab)
   - Role-based access control (RBAC)
   - Audit logs

2. ✅ Advanced security (Week 3-6)
   - SOC 2 Type II compliance
   - GDPR compliance (data export, deletion, anonymization)
   - Encryption at rest (AWS KMS)
   - IP whitelisting
   - 2FA/MFA

3. ✅ SLA monitoring (Week 6-8)
   - Uptime tracking (99.9% SLA)
   - Performance budgets
   - Automated failover
   - Disaster recovery

4. ✅ White-label (Week 8-10)
   - Custom domain (feedback.yourcompany.com)
   - Custom branding (logo, colors, fonts)
   - Custom email templates
   - Embed anywhere

5. ✅ Enterprise integrations (Week 10-14)
   - Salesforce bi-directional sync
   - HubSpot integration
   - Intercom advanced features
   - Zendesk Suite integration

6. ✅ Advanced analytics (Week 14-18)
   - Custom dashboards
   - Data warehouse export (Snowflake, BigQuery)
   - BI tool connectors (Tableau, Looker)
   - Customer success playbooks

**Frontend Tasks:**
7. ✅ Admin portal (Week 1-6)
   - User management
   - SSO configuration
   - Billing and invoices
   - Usage analytics

8. ✅ Custom workflows (Week 6-10)
   - Workflow builder (no-code)
   - Approval processes
   - Automatic actions (rules engine)
   - Integration with Linear/Jira sprints

**Success Metrics:**
- ✅ SSO: <500ms login time
- ✅ SOC 2: Certification achieved
- ✅ SLA: 99.95% uptime
- ✅ White-label: 5+ enterprise customers
- ✅ Enterprise integrations: 90%+ sync success rate

**Estimated Effort:** 4 engineers × 6 months = 24 engineer-months

---

## 4. Performance Targets (Beating Competitors)

### 4.1 Productboard Weaknesses → Compass Targets

| Metric | Productboard | Compass Target | Strategy |
|--------|--------------|----------------|----------|
| **Feedback ingestion** | 60 minutes | <1 second | Webhooks + Redis pub/sub |
| **Clustering** | 5 minutes (manual) | <30 seconds | BERTopic + Celery workers |
| **Dashboard load** | 3-5 seconds | <500ms | Redis caching + CDN |
| **API response (p95)** | 500ms+ | <100ms | PostgreSQL indexes + caching |
| **Search** | 2-3 seconds | <200ms | pgvector + full-text indexes |
| **Uptime** | 99.5% | 99.9% | Multi-region + auto-failover |

### 4.2 Performance Benchmarks

**API Latency (p95):**
```
GET /api/v1/feedback?limit=100         <50ms
GET /api/v1/clusters                   <100ms
POST /api/v1/clustering/run            <30s (async job)
GET /api/v1/search?q=mobile            <200ms (semantic search)
WS message (feedback.new)              <100ms (broadcast)
```

**Throughput:**
```
API requests:           10,000 RPS sustained (100k peak)
WebSocket connections:  50,000 concurrent
Feedback ingestion:     1,000 items/second
Clustering:             10,000 items in <2 minutes
Database queries:       <10ms p95 (indexed)
```

**Resource Usage (per 1,000 active users):**
```
Backend: 2 × t3.xlarge (4 vCPU, 16GB RAM)
Workers: 4 × t3.large (2 vCPU, 8GB RAM)
Database: db.r6g.xlarge (4 vCPU, 32GB RAM)
Redis: cache.r6g.large (2 vCPU, 13GB RAM)
Total cost: ~$800/month (vs $6,000/mo for Productboard at scale)
```

---

## 5. Cost Analysis

### 5.1 Infrastructure Costs by Scale

**100 customers (avg 10 users each = 1,000 users):**

| Service | Spec | Monthly Cost |
|---------|------|--------------|
| Application servers (2x) | AWS ECS Fargate, 4 vCPU, 8GB RAM | $150 |
| Worker nodes (4x) | AWS ECS Fargate, 2 vCPU, 4GB RAM | $120 |
| PostgreSQL | RDS db.t4g.large (2 vCPU, 8GB RAM) | $80 |
| Redis | ElastiCache cache.t4g.medium | $50 |
| S3 storage | 100GB | $3 |
| CloudFront CDN | 1TB transfer | $85 |
| Monitoring (Sentry + Datadog) | - | $100 |
| **Total** | - | **$588/month** |
| **Per customer** | - | **$5.88/mo** |

**1,000 customers (avg 10 users each = 10,000 users):**

| Service | Spec | Monthly Cost |
|---------|------|--------------|
| Application servers (4x) | AWS ECS Fargate, 4 vCPU, 16GB RAM | $600 |
| Worker nodes (8x) | AWS ECS Fargate, 2 vCPU, 8GB RAM | $480 |
| PostgreSQL | RDS db.r6g.xlarge (4 vCPU, 32GB RAM) | $350 |
| Redis | ElastiCache cache.r6g.large | $200 |
| ClickHouse (analytics) | EC2 c6g.2xlarge | $250 |
| S3 storage | 1TB | $25 |
| CloudFront CDN | 10TB transfer | $500 |
| Monitoring | - | $400 |
| **Total** | - | **$2,805/month** |
| **Per customer** | - | **$2.81/mo** |

**10,000 customers (avg 10 users each = 100,000 users):**

| Service | Spec | Monthly Cost |
|---------|------|--------------|
| Application servers (12x) | AWS ECS Fargate, 8 vCPU, 32GB RAM | $3,600 |
| Worker nodes (20x) | AWS ECS Fargate, 4 vCPU, 16GB RAM | $2,400 |
| PostgreSQL | RDS Aurora Multi-AZ (16 vCPU, 128GB RAM) | $2,500 |
| Redis Cluster | ElastiCache 6-node cluster | $1,200 |
| ClickHouse Cluster | 3 × c6g.4xlarge | $2,250 |
| S3 storage | 10TB | $230 |
| CloudFront CDN | 100TB transfer | $4,000 |
| Monitoring + Observability | - | $1,500 |
| OpenAI API (GPT-4) | 10M tokens/month | $300 |
| **Total** | - | **$17,980/month** |
| **Per customer** | - | **$1.80/mo** |

**Key Insights:**
- Economies of scale: Cost per customer decreases as we grow
- Infrastructure costs are 85-90% lower than competitors (usage-based pricing vs per-seat)
- OpenAI API costs are negligible compared to value provided (<2% of infrastructure)
- Can sustain 10,000 customers on <$20k/mo infrastructure (vs $600k+/mo for Productboard)

### 5.2 Revenue vs Cost Projections

**Year 1 Target: 100 customers, $100k ARR**

| Tier | Customers | Price/mo | ARR | Infrastructure | Gross Margin |
|------|-----------|----------|-----|----------------|--------------|
| Starter ($49) | 60 | $49 | $35,280 | $588 | **98.3%** |
| Pro ($199) | 35 | $199 | $83,580 | $588 | **99.2%** |
| Enterprise ($499) | 5 | $499 | $29,940 | $588 | **99.5%** |
| **Total** | **100** | - | **$148,800** | **$7,056** | **95.3%** |

**Year 2 Target: 1,000 customers, $1M ARR**

| Tier | Customers | Price/mo | ARR | Infrastructure | Gross Margin |
|------|-----------|----------|-----|----------------|--------------|
| Starter ($49) | 500 | $49 | $294,000 | $2,805 | **98.9%** |
| Pro ($199) | 400 | $199 | $954,400 | $2,805 | **99.6%** |
| Enterprise ($499) | 100 | $499 | $598,800 | $2,805 | **99.8%** |
| **Total** | **1,000** | - | **$1,847,200** | **$33,660** | **98.2%** |

**SaaS Benchmarks:**
- Compass gross margin: **95-98%** (excellent for SaaS)
- Productboard gross margin: ~80% (per-seat pricing + support costs)
- Target: Maintain 90%+ gross margin at scale

---

## 6. Team Requirements

### 6.1 Engineering Team Evolution

**Current (Month 0):**
- 1-2 developers (generalist full-stack)

**Phase 1 (Months 1-3): Foundations**
- +1 Backend Engineer (Python/FastAPI)
- +1 DevOps Engineer (part-time contractor)
- **Total: 3 engineers**

**Phase 2-3 (Months 4-9): Differentiation + AI**
- +1 Backend Engineer (API design)
- +1 ML Engineer (NLP/AI features)
- +1 Frontend Engineer (React)
- **Total: 6 engineers**

**Phase 4-5 (Months 10-18): Ecosystem + Enterprise**
- +1 Mobile Engineer (React Native)
- +1 Backend Engineer (integrations)
- +1 DevOps Engineer (full-time)
- +1 QA Engineer (testing automation)
- **Total: 10 engineers**

### 6.2 Role Breakdown

**Backend Engineers (4x):**
- FastAPI/Python expertise
- PostgreSQL/Redis optimization
- WebSocket/real-time systems
- Integration experience (REST/GraphQL/Webhooks)

**Frontend Engineers (2x):**
- React/TypeScript expertise
- WebSocket/real-time UI
- Accessibility (WCAG 2.1)
- Performance optimization

**ML Engineer (1x):**
- NLP/embedding models (sentence-transformers, BERTopic)
- GPT-4 prompt engineering
- Predictive analytics (scikit-learn, XGBoost)
- Model deployment (Docker, AWS SageMaker)

**Mobile Engineer (1x):**
- React Native expertise
- Offline-first architecture
- Push notifications
- App store deployment (iOS + Android)

**DevOps Engineer (1x):**
- AWS infrastructure (ECS, RDS, ElastiCache)
- CI/CD (GitHub Actions)
- Monitoring (Datadog, Sentry)
- Security (SOC 2 compliance)

**QA Engineer (1x):**
- Test automation (Playwright, pytest)
- Load testing (k6)
- Security testing (OWASP)
- Regression testing

### 6.3 Hiring Timeline

```
Month  0: [Dev1, Dev2]
Month  1: [Dev1, Dev2, BE1, DevOps-Contract]
Month  4: [Dev1, Dev2, BE1, BE2, ML1, FE1, DevOps-Contract]
Month 10: [Dev1, Dev2, BE1, BE2, BE3, BE4, ML1, FE1, FE2, Mobile1, DevOps, QA1]
```

**Compensation Budget (Year 1):**
- Backend Engineer: $120-150k
- Frontend Engineer: $110-140k
- ML Engineer: $140-170k
- Mobile Engineer: $120-150k
- DevOps Engineer: $130-160k
- QA Engineer: $90-120k

**Total Year 1 Payroll:** ~$700k (6 engineers avg)

---

## 7. Risk Mitigation

### 7.1 Technical Risks

**Risk: MCP not mature enough**
- **Mitigation:** Build REST API first (already done ✅), add MCP as Layer 2
- **Timeline:** If MCP fails, delay by 3 months, no critical dependency

**Risk: Webhook reliability (dropped events)**
- **Mitigation:**
  - Retry logic with exponential backoff (already implemented ✅)
  - Dead letter queue for manual review
  - Webhook delivery monitoring dashboard
  - Fallback to polling if webhooks fail 3x

**Risk: Scale issues (PostgreSQL bottleneck at 1M+ feedback items)**
- **Mitigation:**
  - Horizontal scaling with read replicas (PostgreSQL supports up to 15 replicas)
  - Sharding by org_id if needed (post-10k customers)
  - ClickHouse for analytics queries (offload time-series)
  - Regular VACUUM and index maintenance

**Risk: Cost explosion (OpenAI API usage)**
- **Mitigation:**
  - Set per-customer quotas (max 100 GPT-4 calls/month)
  - Use GPT-3.5 for non-critical tasks (5x cheaper)
  - Cache common insights (Redis)
  - Batch processing (combine multiple queries)
  - Monitoring dashboard for API spend

**Risk: NLP accuracy degrades with domain-specific terminology**
- **Mitigation:**
  - Fine-tune embedding models on customer data (BERTopic supports this)
  - Manual cluster review tool for admins
  - Feedback loop: Users can re-assign feedback to correct clusters
  - Track accuracy metrics per customer

### 7.2 Competitive Risks

**Risk: Canny adds revenue-weighted voting**
- **Mitigation:** Compass has deeper ML (BERTopic, predictive analytics, GPT-4 insights)
- **Timeline:** 6-12 months to implement well (we have 6-month lead)

**Risk: Productboard acquires Canny**
- **Mitigation:**
  - Compass is 10x cheaper (price advantage remains)
  - Open-source option (data ownership)
  - Simpler UX (Productboard is notoriously complex)
  - Better NLP (competitive moat)

**Risk: Linear/Jira add feedback boards natively**
- **Mitigation:**
  - Deep integration with their platforms (bi-directional sync)
  - Multi-source ingestion (not just their platform)
  - AI-powered insights (they lack NLP expertise)
  - Position as "feedback intelligence layer" not just a board

### 7.3 Execution Risks

**Risk: Building takes longer than 18 months**
- **Mitigation:**
  - MVP approach (ship Phase 1-2, iterate on 3-5)
  - Hire experienced engineers (not juniors)
  - Use proven tech stack (FastAPI, React, PostgreSQL)
  - Avoid rewriting working code

**Risk: Can't hire ML engineer**
- **Mitigation:**
  - Use pre-trained models (BERTopic, OpenAI GPT-4)
  - Outsource to ML consultants (Upwork, Toptal)
  - Defer predictive analytics to Phase 4

**Risk: Performance targets not met**
- **Mitigation:**
  - Load testing in Phase 1 (identify bottlenecks early)
  - Over-provision infrastructure initially (scale down later)
  - Hire performance consultant if needed

### 7.4 Market Risks

**Risk: Economic downturn (companies cut SaaS spend)**
- **Mitigation:**
  - Free self-hosted option (keeps users in ecosystem)
  - Lower price tier ($19/mo for solopreneurs)
  - ROI-focused marketing (prove value)

**Risk: Customers don't see value in AI features**
- **Mitigation:**
  - Make AI opt-in (not mandatory)
  - Transparent explanations (show how insights are generated)
  - Free trial to prove value before charging

**Risk: Data privacy concerns (GDPR, SOC 2)**
- **Mitigation:**
  - SOC 2 Type II in Phase 5 (Month 13-15)
  - GDPR compliance from day 1 (data export, deletion)
  - Self-hosted option for sensitive data

---

## 8. Testing Strategy

### 8.1 Test Coverage Targets

**Backend:**
- Unit tests: 85%+ coverage (pytest)
- Integration tests: 70%+ coverage (TestClient)
- E2E tests: Critical paths only (Playwright)

**Frontend:**
- Unit tests: 80%+ coverage (Vitest)
- Component tests: 70%+ coverage (React Testing Library)
- E2E tests: User flows (Playwright)

**Performance:**
- Load tests: k6 scripts for all API endpoints
- Stress tests: Find breaking point (10x expected load)
- Soak tests: 24-hour sustained load

### 8.2 Test Pyramid

```
         /\
        /  \   E2E Tests (Playwright)
       /    \  • User registration
      /      \ • Feedback submission
     /        \• Clustering workflow
    /----------\
   / Integration \ API Tests (FastAPI TestClient)
  /    Tests     \• All endpoints
 /                \• WebSocket connections
/------------------\
/   Unit Tests      \ Component Tests (pytest, Vitest)
/                    \• Business logic
/______________________\• React components
```

### 8.3 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml

name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run pytest
        run: pytest --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Run tests
        run: cd frontend && npm test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E tests
        run: docker-compose -f docker-compose.test.yml up --abort-on-container-exit

  deploy-staging:
    needs: [test-backend, test-frontend, e2e-tests]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: ./scripts/deploy-staging.sh

  deploy-production:
    needs: [deploy-staging]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production (blue-green)
        run: ./scripts/deploy-production.sh
```

---

## 9. Code Examples for Key Patterns

### 9.1 Real-Time Feedback Ingestion Pattern

```python
# High-performance feedback ingestion with sub-second latency

from fastapi import APIRouter, BackgroundTasks, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/webhooks/slack")
async def slack_webhook(
    event: SlackEvent,
    background_tasks: BackgroundTasks,
    redis: Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db)
):
    """
    Slack webhook receiver with <50ms acknowledgment.

    Performance targets:
    - Acknowledgment: <50ms
    - DB insert: <200ms (async)
    - WebSocket broadcast: <100ms
    - Total user-facing latency: <300ms
    """

    # 1. Immediate acknowledgment (Slack requires <3s response)
    background_tasks.add_task(process_slack_event, event, redis, db)
    return {"ok": True}

async def process_slack_event(event: SlackEvent, redis: Redis, db: AsyncSession):
    """Background task for processing Slack event"""

    # 2. Parse and validate
    feedback_data = parse_slack_message(event)

    # 3. Store in database (async, non-blocking)
    feedback = Feedback(**feedback_data)
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # 4. Publish to Redis for WebSocket broadcast
    await redis.publish(
        "feedback:new",
        feedback.json()
    )

    # 5. Queue heavy tasks (embedding generation, clustering check)
    await queue_task("generate_embedding", feedback_id=feedback.id)
    await queue_task("check_clustering_needed")

    # 6. Cache invalidation
    await redis.delete(f"feedback:list:*")  # Invalidate cached lists

# WebSocket subscriber (separate service)
async def websocket_subscriber():
    """Subscribe to Redis pub/sub and broadcast to WebSocket clients"""

    pubsub = redis.pubsub()
    await pubsub.subscribe("feedback:new", "cluster:new", "roadmap:updated")

    async for message in pubsub.listen():
        if message["type"] == "message":
            # Broadcast to all connected WebSocket clients in relevant room
            await ws_manager.broadcast(
                json.loads(message["data"]),
                room=message["channel"].split(":")[0]  # e.g., "feedback"
            )
```

### 9.2 Semantic Search with pgvector

```python
# Semantic search with sub-100ms response time

from pgvector.sqlalchemy import Vector
from sqlalchemy import select, func

async def semantic_search(
    query: str,
    limit: int = 20,
    similarity_threshold: float = 0.7,
    db: AsyncSession = Depends(get_db)
) -> List[FeedbackSearchResult]:
    """
    Semantic search using pgvector cosine similarity.

    Performance: <100ms for 100k+ feedback items (with index)
    """

    # 1. Generate query embedding (cached in Redis if query seen before)
    cache_key = f"embedding:query:{hash(query)}"
    query_embedding = await redis.get(cache_key)

    if not query_embedding:
        query_embedding = generate_embedding(query)
        await redis.setex(cache_key, 3600, query_embedding.tobytes())  # Cache 1 hour
    else:
        query_embedding = np.frombuffer(query_embedding, dtype=np.float32)

    # 2. pgvector similarity search (uses HNSW index for speed)
    stmt = select(
        Feedback.id,
        Feedback.text,
        Feedback.customer_name,
        (1 - Feedback.embedding.cosine_distance(query_embedding)).label("similarity")
    ).where(
        Feedback.embedding.isnot(None)
    ).order_by(
        Feedback.embedding.cosine_distance(query_embedding)
    ).limit(limit)

    results = await db.execute(stmt)

    # 3. Filter by similarity threshold and return
    search_results = []
    for row in results:
        if row.similarity >= similarity_threshold:
            search_results.append(FeedbackSearchResult(
                id=row.id,
                text=row.text,
                customer_name=row.customer_name,
                similarity=row.similarity
            ))

    return search_results

# Example query:
# results = await semantic_search("mobile app performance issues")
# Returns feedback semantically similar to query, even if exact words don't match
```

### 9.3 MCP Server Implementation

```python
# MCP server for AI-native querying

from mcp import MCPServer, Tool, Resource

mcp_server = MCPServer(name="compass", version="1.0.0")

@mcp_server.tool
async def search_feedback(
    query: str,
    filters: Optional[dict] = None
) -> List[dict]:
    """
    Search customer feedback using natural language.

    Examples:
    - "Show me feedback from enterprise customers about mobile app"
    - "What are customers saying about performance lately?"
    - "Find complaints from customers at risk of churning"
    """

    # Parse natural language query
    parsed = parse_nl_query(query)

    # Apply filters
    search_params = {
        "search": parsed.keywords,
        "min_revenue": parsed.min_revenue,
        "sentiment_range": parsed.sentiment_range,
        "time_range": parsed.time_range,
    }

    # Perform search
    results = await semantic_search(**search_params)

    return [r.dict() for r in results]

@mcp_server.tool
async def generate_insights(cluster_id: int) -> dict:
    """
    Generate AI insights for a feedback cluster.

    Returns:
    - Summary of feedback
    - Key themes
    - Recommended actions
    - Estimated revenue impact
    """

    cluster = await Cluster.get(cluster_id)
    feedback_items = await cluster.feedback.all()

    # Generate insights with GPT-4
    prompt = f"""Analyze this customer feedback cluster:

Cluster: {cluster.label}
Feedback count: {len(feedback_items)}
Total revenue: ${cluster.total_revenue:,.0f}
Avg sentiment: {cluster.avg_sentiment:.2f}

Sample feedback:
{chr(10).join(f.text for f in feedback_items[:5])}

Provide:
1. Summary (2-3 sentences)
2. Key themes (3-5 bullet points)
3. Recommended actions (prioritized list)
4. Estimated revenue impact if addressed
"""

    response = await openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    insights = parse_gpt4_response(response.choices[0].message.content)

    return insights

@mcp_server.resource("feedback")
async def get_feedback_resource(resource_id: str) -> dict:
    """Get feedback item by ID (MCP resource)"""
    feedback = await Feedback.get(int(resource_id))
    return feedback.dict()

# Start MCP server
# mcp_server.run(host="localhost", port=8001)
```

---

## 10. Migration Scripts & Deployment

### 10.1 SQLite → PostgreSQL Migration

```python
# migration_sqlite_to_postgres.py

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, Feedback, Cluster, RoadmapItem  # All models

# Source (SQLite)
sqlite_engine = create_async_engine("sqlite+aiosqlite:///compass.db")
SqliteSession = sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)

# Target (PostgreSQL)
postgres_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/compass")
PostgresSession = sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)

async def migrate_table(model_class, batch_size=1000):
    """Migrate a single table with batching"""

    print(f"Migrating {model_class.__tablename__}...")

    async with SqliteSession() as sqlite_session:
        # Get total count
        result = await sqlite_session.execute(select(func.count(model_class.id)))
        total = result.scalar()
        print(f"  Total rows: {total}")

        # Migrate in batches
        offset = 0
        while offset < total:
            # Read batch from SQLite
            result = await sqlite_session.execute(
                select(model_class).offset(offset).limit(batch_size)
            )
            rows = result.scalars().all()

            # Write batch to PostgreSQL
            async with PostgresSession() as postgres_session:
                for row in rows:
                    # Detach from SQLite session
                    sqlite_session.expunge(row)
                    # Add to PostgreSQL session
                    postgres_session.add(row)

                await postgres_session.commit()

            offset += batch_size
            print(f"  Migrated {min(offset, total)}/{total} rows")

async def migrate_all():
    """Migrate all tables"""

    # Create schema in PostgreSQL
    async with postgres_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Migrate tables in order (respecting foreign keys)
    await migrate_table(Source)
    await migrate_table(Feedback)
    await migrate_table(Cluster)
    await migrate_table(RoadmapItem)
    # ... more tables

    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_all())
```

### 10.2 Docker Compose for Local Development

```yaml
# docker-compose.yml

version: '3.8'

services:
  # PostgreSQL database
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: compass
      POSTGRES_USER: compass
      POSTGRES_PASSWORD: compass_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-postgres.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U compass"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://compass:compass_dev_password@postgres:5432/compass
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Celery workers
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    depends_on:
      - postgres
      - redis
      - backend
    environment:
      DATABASE_URL: postgresql+asyncpg://compass:compass_dev_password@postgres:5432/compass
      REDIS_URL: redis://redis:6379
    volumes:
      - ./backend:/app
    command: celery -A celery_app worker --loglevel=info

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    depends_on:
      - backend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_URL: http://localhost:8000
      VITE_WS_URL: ws://localhost:8000/ws
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
```

### 10.3 Production Deployment Checklist

```bash
# Production Deployment Checklist

## Pre-Deployment
- [ ] Run full test suite (unit, integration, E2E)
- [ ] Run load tests (k6) against staging
- [ ] Review Sentry errors (0 unresolved critical errors)
- [ ] Database backup created
- [ ] Blue-green deployment slots ready
- [ ] Rollback plan documented

## Deployment Steps
1. [ ] Set maintenance mode (optional for major releases)
2. [ ] Deploy to "green" slot (inactive)
3. [ ] Run database migrations (idempotent, non-destructive)
4. [ ] Smoke tests on "green" slot
5. [ ] Switch traffic to "green" slot (gradual: 10% → 50% → 100%)
6. [ ] Monitor metrics for 15 minutes
7. [ ] If issues: Rollback to "blue" slot (instant)
8. [ ] If success: Decommission "blue" slot

## Post-Deployment
- [ ] Monitor Sentry for new errors (30 minutes)
- [ ] Monitor Datadog for performance regressions
- [ ] Check API latency (p95, p99)
- [ ] Check WebSocket connection health
- [ ] Check Celery worker queue length
- [ ] Notify team in Slack
- [ ] Update deployment log

## Rollback (if needed)
1. [ ] Switch traffic back to "blue" slot
2. [ ] Rollback database migrations (if any)
3. [ ] Investigate issue in "green" slot
4. [ ] Fix and re-deploy

## Emergency Contacts
- On-call engineer: [PagerDuty]
- Database admin: [Email]
- DevOps lead: [Slack]
```

---

## 11. Conclusion & Next Steps

### 11.1 Summary

**Current State:**
- Solid MVP with WebSocket real-time, basic NLP, and integrations
- Ready for pilot customers (50-100 users)

**Target State (18 months):**
- Enterprise-grade platform beating Productboard/Canny at 5x lower cost
- AI-native with GPT-4 insights, predictive analytics, semantic search
- 85%+ NLP accuracy, <1s feedback ingestion, <100ms API latency
- 10,000+ users, $1-2M ARR

**Investment:**
- 4-6 engineers (phased hiring)
- $150-200k infrastructure over 18 months
- $700k-1.5M payroll (depending on team size)

**ROI:**
- Year 1: $150k ARR (breakeven on infrastructure)
- Year 2: $1.8M ARR (98% gross margin)
- 3-5x cheaper pricing than competitors
- Market opportunity: $500M+ TAM

### 11.2 Immediate Next Steps (This Week)

1. **Review Roadmap with Team**
   - Align on priorities (Phase 1 vs Phase 2)
   - Identify blockers
   - Assign owners

2. **Setup Infrastructure**
   - Provision PostgreSQL + pgvector (AWS RDS)
   - Setup Redis cluster (AWS ElastiCache)
   - Configure Sentry + Datadog monitoring

3. **Start Phase 1 Development**
   - Migrate SQLite → PostgreSQL (Week 1)
   - Implement Redis caching (Week 2)
   - Setup Celery job queue (Week 3)

4. **Hire Backend Engineer**
   - Post job description (focus on FastAPI + PostgreSQL)
   - Target: Start in Month 1

### 11.3 Success Metrics (6-Month Checkpoints)

**Month 3 (End of Phase 1):**
- ✅ PostgreSQL + Redis live
- ✅ API p95 latency <200ms
- ✅ Clustering time <30s for 1,000 items
- ✅ 10 pilot customers

**Month 6 (End of Phase 2):**
- ✅ Public feedback board live
- ✅ MCP server operational
- ✅ 50 active customers
- ✅ $10k MRR

**Month 9 (End of Phase 3):**
- ✅ GPT-4 insights live
- ✅ Predictive analytics (churn risk)
- ✅ 100 active customers
- ✅ $30k MRR

**Month 12 (End of Phase 4):**
- ✅ Mobile app live
- ✅ Zapier integration
- ✅ Self-hosted Docker option
- ✅ 250 active customers
- ✅ $60k MRR

**Month 18 (End of Phase 5):**
- ✅ Enterprise features (SSO, white-label)
- ✅ SOC 2 certified
- ✅ 500 active customers
- ✅ $120k MRR
- ✅ 99.95% uptime

---

**End of Technical Roadmap**

*This roadmap is a living document and will be updated quarterly based on customer feedback, market changes, and technical discoveries.*

**Last Updated:** 2026-08-04
**Next Review:** 2026-11-04 (3 months)
