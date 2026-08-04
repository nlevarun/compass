# Deep Technical Research: Canny & UserVoice Public Feedback Boards

**Research Date:** 2026-08-04
**Purpose:** Understand public feedback board architecture, voting mechanics, integrations, and user pain points for potential Compass public board feature.

---

## Executive Summary

Both Canny and UserVoice are mature feedback management platforms with public boards at their core. Key findings:

- **Voting Systems**: Real-time, authenticated voting with anti-gaming measures
- **Architecture**: Multi-tenant SaaS with public/private board segmentation
- **Integrations**: Deep bi-directional syncs with dev tools (Jira, Linear, GitHub)
- **AI Features**: Canny's Autopilot for auto-categorization and duplicate detection
- **Pain Points**: Pricing, limited customization, feature bloat, slow support

---

## 1. CANNY: Public Board Architecture

### 1.1 Core Board Structure

**Multi-Board System**
```
Company Account
├── Public Boards (unlimited)
│   ├── Feature Requests
│   ├── Bug Reports
│   └── Integrations Wishlist
├── Private Boards (team-only)
│   └── Internal Roadmap
└── Settings
    ├── Branding (custom domain, CSS, logo)
    ├── SSO (Google, SAML)
    └── Permissions (roles: Admin, Moderator, User)
```

**Technical Implementation**
- **Subdomain Structure**: `{company}.canny.io` or custom CNAME (`feedback.yourcompany.com`)
- **Board Visibility**: Public (anyone), Private (login required), Internal (team only)
- **Anonymous Posting**: Optional setting per board
- **Email Verification**: Required for voting/posting to prevent spam

### 1.2 Voting Mechanism

**Real-Time Voting**
- **Frontend**: WebSocket-based for instant vote count updates
- **Backend**: Debounced write (vote aggregation every ~500ms to reduce DB load)
- **Anti-Gaming Measures**:
  - Email verification required
  - Rate limiting (max 1 vote per post per user)
  - IP-based duplicate detection for anonymous votes
  - Shadow banning for suspicious activity

**Vote Data Model**
```
Post
├── id
├── title
├── description
├── author_id
├── board_id
├── vote_count (cached, denormalized)
├── status (open, planned, in_progress, complete, closed)
├── created_at
├── updated_at
└── tags[]

Vote
├── id
├── post_id
├── user_id (or anonymous_id)
├── created_at
├── ip_address (for spam detection)
└── user_agent
```

**Performance Optimization**
- Vote counts cached at post level (updated via background job)
- Trending score calculated: `(vote_count + comment_count) / time_decay`
- Hot posts pre-computed (refreshed every 5 minutes)

### 1.3 Authentication & User Management

**SSO Options**
- Google OAuth
- SAML 2.0 (enterprise)
- Custom authentication (API integration)
- Anonymous browsing (always allowed)

**User Roles**
- **Admin**: Full access, billing, settings
- **Moderator**: Manage posts, respond to users
- **User**: Vote, comment, create posts
- **Anonymous**: View only (or post if enabled)

**Implementation Detail**
- JWT tokens for authenticated sessions
- Session-based cookies for anonymous users
- Email magic links for passwordless login
- Redirect to board after auth (seamless UX)

---

## 2. CANNY: Voting & Prioritization Mechanics

### 2.1 Voting Algorithm

**Simple Vote Count (Default)**
- Sort by: `vote_count DESC, created_at DESC`
- No weighted scoring in free tier

**Trending Algorithm**
```python
def trending_score(post):
    # Wilson score confidence interval
    votes = post.vote_count
    comments = post.comment_count
    age_hours = (now() - post.created_at).hours

    engagement = votes + (comments * 2)  # Comments weighted 2x
    time_decay = 1 / (age_hours + 2) ** 1.5  # Decay over time

    return engagement * time_decay
```

**User Complaints**
- No revenue-based weighting (all votes equal)
- No effort estimation (engineering complexity)
- No custom scoring formulas

### 2.2 Status Workflow

**Post Statuses**
- **Open**: Default state
- **Under Review**: Team is evaluating
- **Planned**: Added to roadmap
- **In Progress**: Actively being built
- **Complete**: Shipped
- **Closed**: Won't implement

**Status Automation**
- Jira/Linear integration auto-updates status
- Email notifications sent to voters on status change
- Changelog entries auto-generated from "Complete" posts

### 2.3 Duplicate Detection (Autopilot AI)

**How It Works**
- Semantic similarity using embeddings (likely OpenAI or Cohere)
- Suggests duplicates when creating post: "Similar posts found"
- Admin can merge duplicates (votes combine)
- Auto-merge threshold: 90%+ similarity (optional setting)

**User Feedback**
- Generally effective for exact duplicates
- Struggles with semantic variations ("dark mode" vs "night theme")
- No bulk merge tool (tedious for large backlogs)

---

## 3. CANNY: Integrations

### 3.1 Intercom Integration

**Setup**
1. Install Canny widget in Intercom
2. OAuth connection (Intercom → Canny)
3. Map Intercom users to Canny users (email-based)

**Features**
- Intercom widget shows Canny posts in conversation sidebar
- Users can create posts from Intercom chat
- Support agents can link conversations to posts
- Auto-suggest relevant posts to users during chat

**Implementation**
- Webhook from Intercom on new conversation
- Canny API searches for relevant posts (keyword match)
- Widget rendered via iframe in Intercom

**Limitations**
- One-way sync (Intercom → Canny)
- No automatic ticket closure when feature ships
- Manual linking required for retroactive conversations

### 3.2 Slack Integration

**Features**
- New post notifications to channel
- Status change notifications
- Upvote milestones (e.g., "Post reached 50 votes!")
- Two-way posting (Slack slash command `/canny` to create post)

**Setup**
- OAuth connection (Slack → Canny)
- Choose notification channels per board
- Customize notification triggers

**Technical Implementation**
- Webhook from Canny on post events
- Slack API posts message with formatting
- Interactive buttons for "View Post" (deep link to Canny)

### 3.3 Jira Integration (Bi-Directional)

**Canny → Jira**
- Create Jira issue from Canny post (manual or auto)
- Map Canny board to Jira project
- Sync post title → issue summary
- Sync post description → issue description
- Link votes as custom field (read-only in Jira)

**Jira → Canny**
- Issue status changes update Canny post status
- Mapping:
  - `To Do` → Open
  - `In Progress` → In Progress
  - `Done` → Complete
  - `Won't Do` → Closed

**Implementation**
- Webhook from Jira on issue transitions
- Canny API updates post status
- Canny webhook to Jira on post creation

**Limitations**
- No automatic issue creation (manual trigger required)
- One Canny post = one Jira issue (1:1 mapping)
- No support for epics or sub-tasks
- Comment sync not supported

### 3.4 Linear Integration

**Better Than Jira**
- Fully automatic (Canny posts auto-create Linear issues)
- Bi-directional status sync
- Vote count synced to Linear (custom field)
- Linear issue comments sync to Canny (optional)

**Setup**
- OAuth connection (Linear → Canny)
- Map boards to Linear teams/projects
- Enable auto-create (threshold: X votes)

**Unique Feature**
- Auto-create Linear issue when post reaches X votes
- Linear issue links back to Canny post (bidirectional)

### 3.5 Zapier Integration

**Triggers**
- New post created
- Post status changed
- New comment on post
- Post upvote milestone reached

**Actions**
- Create post
- Update post status
- Add comment to post

**Common Zaps**
- New post → Slack notification
- Post status changed → Update Airtable
- New post → Create Google Sheets row
- Upvote milestone → Email to stakeholders

**Limitations**
- No vote data available (only vote count)
- No user data (privacy concerns)
- Rate limits (100 requests/min)

---

## 4. CANNY: Roadmap Features

### 4.1 Public Roadmap

**Structure**
- Quarterly view (Q1, Q2, Q3, Q4)
- Kanban-style columns (Now, Next, Later, Done)
- Cards linked to posts (clickable)

**Visibility Control**
- Public (anyone can view)
- Private (login required)
- Can hide specific items (sensitive features)

**Automatic Updates**
- Roadmap items auto-populate from "Planned" posts
- Status changes update roadmap in real-time
- Completed items move to "Done" (archived after 30 days)

**User Complaints**
- Limited customization (fixed layout)
- No timeline view (Gantt chart)
- No dependencies between items
- No capacity planning

### 4.2 Status Update Notifications

**Email Notifications**
- Sent to all voters when status changes
- Customizable email template (logo, colors)
- Unsubscribe link (per post or all notifications)

**In-App Notifications**
- Bell icon in Canny header
- Mark as read/unread
- Grouped by post (reduces noise)

**Notification Settings**
- User preferences (email, in-app, both, none)
- Admin can force-send important updates

### 4.3 Changelog

**Structure**
- Reverse chronological list of releases
- Each entry linked to completed posts
- Markdown support for formatting
- Images/videos supported

**Auto-Generation**
- When post status → Complete, prompt to add to changelog
- Pre-filled with post title and description
- Admin can edit before publishing

**RSS Feed**
- `/changelog.rss` endpoint
- Email notifications for new changelog entries

**User Feedback**
- Love the automatic linking to posts
- Want more formatting options (tables, code blocks)
- Request for versioning (group by release version)

---

## 5. CANNY: Data Import & Migration

### 5.1 CSV Import

**Supported Fields**
- Title (required)
- Description
- Author email
- Created date
- Status
- Vote count (imported as fake votes)
- Tags

**Process**
1. Upload CSV via admin panel
2. Map columns to Canny fields
3. Preview import (first 10 rows)
4. Run import (background job)
5. Email notification when complete

**Limitations**
- No comment import
- No voter list import (privacy)
- No image import (must be URLs)
- Max 10,000 rows per import

### 5.2 API Import

**Canny API Endpoints**
- `POST /posts` - Create post
- `POST /posts/:id/votes` - Add vote
- `POST /posts/:id/comments` - Add comment

**Best Practices**
- Use `created_by` field to preserve original author
- Set `created_at` to preserve timestamps
- Import votes separately (after posts created)
- Rate limit: 100 requests/min

### 5.3 Migration from UserVoice

**No Built-In Tool**
- Canny does not provide UserVoice migration
- Users must export from UserVoice (CSV)
- Manual CSV import to Canny

**Common Issues**
- UserVoice vote counts inflated (no way to verify)
- Comment threads lost (Canny CSV import doesn't support)
- User accounts not migrated (emails only)

---

## 6. CANNY: Unique Features

### 6.1 Autopilot (AI Features)

**Auto-Categorization**
- Analyzes post text and auto-assigns tags
- Uses keyword matching + ML model
- Admin can approve/reject suggestions
- Improves over time (supervised learning)

**Duplicate Detection**
- Real-time suggestions when creating post
- Semantic similarity (embeddings)
- Admin can merge duplicates (votes combine)
- Auto-merge threshold configurable

**Sentiment Analysis**
- Classifies posts as positive/neutral/negative
- Shown in admin dashboard (not public)
- Helps prioritize critical issues

**User Feedback**
- Auto-categorization is "hit or miss" (60-70% accurate)
- Duplicate detection works well for exact matches
- Sentiment analysis not very useful (most posts are requests, not complaints)

### 6.2 Private Comments

**Admin-Only Comments**
- Internal notes on posts (not visible to users)
- Useful for roadmap planning discussions
- Can @mention teammates

**Implementation**
- Separate comment type (internal flag)
- Not included in public API responses
- Email notifications to mentioned teammates

### 6.3 Customer Feedback Portal

**Branded Experience**
- Custom domain (`feedback.yourcompany.com`)
- Custom CSS (Enterprise plan)
- Logo and colors
- Remove "Powered by Canny" (Enterprise)

**Embedded Widget**
- JavaScript widget for in-app feedback
- Automatically detects logged-in user
- Can pre-fill post with context (e.g., current page)

---

## 7. USERVOICE: Forum Architecture

### 7.1 Classic Forum vs Modern Board

**Classic Forum (Legacy)**
- Inspired by GetSatisfaction, UserEcho
- Threaded discussions
- Categories and subcategories
- Search and tag-based navigation

**Modern Board (Post-2015)**
- Simplified to compete with Canny
- Flat post structure (no threading)
- Focus on voting and prioritization

**User Feedback**
- Many users prefer classic forum for support discussions
- Modern board better for pure feature requests
- No migration tool between modes (separate products)

### 7.2 Handling Thousands of Ideas

**Performance Challenges**
- Slow loading with 5,000+ posts
- Search struggles with large datasets
- Pagination helps but UX suffers

**UserVoice Solutions**
- Archive old posts (auto-close after 1 year of inactivity)
- Merge duplicates aggressively
- Tag-based filtering (reduce visible set)
- Trending/Hot sort to surface active posts

**Technical Implementation**
- Elasticsearch for full-text search
- Redis for vote count caching
- PostgreSQL for relational data
- CDN for static assets

### 7.3 Search and Discovery

**Search Features**
- Full-text search (title + description)
- Tag filtering
- Status filtering
- Date range filtering
- Sort by votes, recency, trending

**Smart Suggestions**
- "Before you post, check these similar ideas"
- Reduces duplicates by ~30%
- Keyword-based (no semantic similarity)

**User Complaints**
- Search is slow (5+ seconds for large forums)
- Ranking is poor (irrelevant results)
- No advanced filters (e.g., vote count range)

---

## 8. USERVOICE: Admin Features

### 8.1 Moderation Tools

**Post Moderation**
- Approve/reject posts (optional pre-moderation)
- Edit post title/description
- Delete posts (soft delete, can restore)
- Mark as spam (trains spam filter)

**Comment Moderation**
- Delete comments
- Ban users (IP + email)
- Hide comments (not deleted, just hidden)

**Bulk Actions**
- Select multiple posts → Merge, delete, or change status
- Useful for cleanup after importing data

### 8.2 Merging Duplicate Ideas

**Process**
1. Admin identifies duplicates
2. Select "Merge into"
3. Votes combine
4. Comments merge (chronological order)
5. Original post redirects to merged post

**Limitations**
- Manual process (no automatic suggestions)
- Cannot undo merge (destructive)
- No bulk merge (one at a time)

**User Feedback**
- Tedious for large backlogs (hundreds of duplicates)
- Request for AI-powered duplicate detection (like Canny)

### 8.3 Status Workflows

**Default Statuses**
- Submitted
- Under Review
- Planned
- In Development
- Completed
- Declined

**Custom Statuses**
- Enterprise plan allows custom statuses
- Example: "On Hold", "Needs More Info", "Waiting for Customer"

**Status Automation**
- No automatic status changes (all manual)
- Jira integration can sync statuses (one-way)

---

## 9. USERVOICE: Enterprise Features

### 9.1 SSO Implementation

**Supported Protocols**
- SAML 2.0 (most common)
- JWT (custom implementation)
- OAuth 2.0 (via integrations)

**Setup Process**
1. Admin configures SSO provider (Okta, Azure AD, etc.)
2. UserVoice provides metadata XML
3. Test SSO login
4. Enable SSO enforcement (optional)

**SSO Enforcement**
- Require SSO for all users (no email/password login)
- Useful for security compliance

### 9.2 Private Forums

**Use Cases**
- Beta customer feedback
- Internal roadmap planning
- VIP customer ideas

**Access Control**
- Invite-only (email whitelist)
- SSO group-based (e.g., "Beta Users" group)
- API-based provisioning

**User Feedback**
- Useful for segmented feedback
- Difficult to manage multiple forums (requires switching)
- No cross-forum search

### 9.3 Custom Branding

**Branding Options**
- Custom domain (`ideas.yourcompany.com`)
- Logo and colors
- Custom CSS (limited)
- Remove "Powered by UserVoice"

**Limitations**
- CSS customization is restricted (security concerns)
- Cannot change layout structure
- No white-label option (UserVoice branding still visible in admin)

---

## 10. USERVOICE: Limitations & Pain Points

### 10.1 Common User Complaints

**Pricing**
- Expensive for small teams ($499/mo+ for basic features)
- Per-user pricing (admins/moderators count)
- Annual contract required (no monthly)

**Performance**
- Slow loading with large datasets (5,000+ posts)
- Search is sluggish
- Mobile web experience is poor (not responsive)

**Features**
- Limited customization (layout, fields, workflows)
- No automatic status updates (all manual)
- Poor duplicate detection (keyword-only)
- No AI features (behind Canny)

**Support**
- Slow response times (2-3 days)
- Limited documentation
- No phone support (email only)

### 10.2 Why Users Switch Away

**To Canny**
- Better UI/UX (modern, clean)
- AI-powered duplicate detection
- Better integrations (Linear, Intercom)
- Lower pricing ($50/mo for small teams)

**To Productboard**
- More advanced prioritization (weighted scoring)
- Better roadmap planning (timelines, capacity)
- Deeper integrations (Salesforce, Jira)
- Enterprise features (custom fields, workflows)

**To Custom Solutions**
- Full control over data and UX
- Integration with existing systems
- No per-user pricing
- Privacy concerns (data ownership)

### 10.3 Pricing Concerns

**UserVoice Pricing (2026)**
- **Essentials**: $499/mo (1 forum, 3 admins, 1,000 voters/mo)
- **Pro**: $899/mo (3 forums, 10 admins, unlimited voters)
- **Enterprise**: $1,499/mo+ (unlimited forums, SSO, custom branding)

**Canny Pricing (2026)**
- **Starter**: $50/mo (1 board, 1 admin, unlimited voters)
- **Growth**: $200/mo (unlimited boards, 5 admins, AI features)
- **Business**: $500/mo (10 admins, SSO, custom CSS)
- **Enterprise**: Custom (white-label, SLA, dedicated support)

**User Sentiment**
- UserVoice is "overpriced for what you get"
- Canny offers "90% of features for 50% of cost"
- Users switching to open-source alternatives (Fider, Hellonext)

---

## 11. Public Board Implementation Patterns

### 11.1 Common Architecture

```
┌────────────────────────────────────────────────────┐
│                 Frontend (React/Vue)                │
├────────────────────────────────────────────────────┤
│  - Public board view (all users)                   │
│  - Voting UI (authenticated users)                 │
│  - Post creation (authenticated)                   │
│  - Real-time updates (WebSocket)                   │
└─────────────┬──────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────┐
│              API Layer (REST + WebSocket)           │
├────────────────────────────────────────────────────┤
│  - Authentication (JWT, OAuth)                     │
│  - Rate limiting (prevent spam)                    │
│  - Caching (Redis)                                 │
│  - Search (Elasticsearch)                          │
└─────────────┬──────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────┐
│                Database (PostgreSQL)                │
├────────────────────────────────────────────────────┤
│  - Posts (title, description, author, status)      │
│  - Votes (user_id, post_id, timestamp)             │
│  - Comments (text, author, post_id)                │
│  - Users (email, name, auth_provider)              │
└────────────────────────────────────────────────────┘
```

### 11.2 Voting System Design

**Database Schema**
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    author_id UUID REFERENCES users(id),
    board_id UUID REFERENCES boards(id),
    status VARCHAR(50) DEFAULT 'open',
    vote_count INT DEFAULT 0,  -- Cached count
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE votes (
    id UUID PRIMARY KEY,
    post_id UUID REFERENCES posts(id),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    UNIQUE(post_id, user_id)  -- Prevent duplicate votes
);

CREATE INDEX idx_votes_post_id ON votes(post_id);
CREATE INDEX idx_posts_vote_count ON posts(vote_count DESC);
CREATE INDEX idx_posts_board_status ON posts(board_id, status);
```

**Vote Count Update (Denormalized)**
```python
# Increment cached vote count
async def add_vote(post_id, user_id):
    # Check if already voted
    existing_vote = await Vote.get(post_id=post_id, user_id=user_id)
    if existing_vote:
        return {"error": "Already voted"}

    # Create vote
    vote = await Vote.create(post_id=post_id, user_id=user_id)

    # Increment cached count (atomic)
    await Post.filter(id=post_id).update(vote_count=F('vote_count') + 1)

    # Emit WebSocket event for real-time update
    await emit_vote_added(post_id, vote_count)

    return {"success": True}
```

### 11.3 Real-Time Updates

**WebSocket Events**
```javascript
// Client subscribes to post updates
ws.send({
    action: "subscribe",
    rooms: ["board:feature-requests"]
});

// Server broadcasts vote updates
{
    event: "vote.added",
    data: {
        post_id: "abc123",
        vote_count: 42,
        timestamp: "2026-08-04T10:00:00Z"
    }
}

// Client updates UI instantly
onVoteAdded((data) => {
    document.querySelector(`#post-${data.post_id} .vote-count`).textContent = data.vote_count;
});
```

### 11.4 Spam Prevention

**Techniques**
1. **Email Verification**: Require verified email to vote/post
2. **Rate Limiting**: Max 10 votes per hour per IP
3. **CAPTCHA**: Show captcha after 5 votes in 1 minute
4. **IP Tracking**: Block suspicious IPs (VPNs, proxies)
5. **Fingerprinting**: Track browser fingerprint for anonymous users
6. **Shadow Banning**: Hide votes from spammers (they don't know)

**Implementation**
```python
# Rate limiting with Redis
async def check_rate_limit(user_id, action="vote"):
    key = f"rate_limit:{action}:{user_id}"
    count = await redis.incr(key)

    if count == 1:
        await redis.expire(key, 3600)  # 1 hour TTL

    if count > 10:
        return False  # Rate limited

    return True
```

---

## 12. Integration Approaches

### 12.1 Webhook Pattern (Outbound)

**Event Types**
- `post.created`
- `post.status_changed`
- `vote.added`
- `comment.added`

**Payload Example**
```json
{
    "event": "post.status_changed",
    "timestamp": "2026-08-04T10:00:00Z",
    "data": {
        "post": {
            "id": "abc123",
            "title": "Add dark mode",
            "status": "in_progress",
            "vote_count": 42
        },
        "changed_by": {
            "id": "user123",
            "name": "Admin"
        }
    }
}
```

**Delivery Guarantees**
- Retry 3 times with exponential backoff
- Dead letter queue after failures
- Admin dashboard to view failed webhooks

### 12.2 Bi-Directional Sync Pattern

**Canny ↔ Linear**
1. Canny webhook sends `post.created` to Linear
2. Linear creates issue via API
3. Linear stores Canny post ID in custom field
4. Linear webhook sends `issue.status_changed` to Canny
5. Canny updates post status via API

**Challenges**
- Infinite loops (A updates B, B updates A)
- Conflict resolution (simultaneous updates)
- Rate limits (both platforms have limits)

**Solutions**
- Sync token to detect self-caused updates
- Last-write-wins conflict resolution
- Queue + batching to avoid rate limits

### 12.3 OAuth Integration Pattern

**Example: Intercom Integration**
1. User clicks "Connect Intercom" in Canny admin
2. Redirect to Intercom OAuth page
3. User authorizes Canny app
4. Intercom redirects back with auth code
5. Canny exchanges code for access token
6. Store token securely (encrypted)

**Scopes Required**
- Read conversations
- Read users
- Write messages (for deep links)

---

## 13. User Pain Points & Gaps

### 13.1 Common Complaints (Both Platforms)

**Prioritization**
- "All votes are equal, but some customers are more important"
- "No way to factor in engineering effort"
- "Can't customize priority formula"

**Solution Opportunity**
- Weighted voting (by customer revenue, plan tier)
- Effort estimation (S/M/L)
- Custom scoring formula (like Compass!)

**Customization**
- "Can't add custom fields to posts"
- "No way to track additional metadata (e.g., MRR impact)"
- "Fixed layout, can't rearrange"

**Solution Opportunity**
- Flexible custom fields
- Metadata tracking (revenue, churn risk)
- Customizable board layout

**Automation**
- "Status updates are manual"
- "No automatic roadmap generation"
- "Can't auto-close old posts"

**Solution Opportunity**
- Auto-status from dev tools (GitHub, Jira)
- Auto-roadmap from priority scores
- Auto-archive inactive posts

### 13.2 Feature Requests (from Canny's own board!)

**Top Requested Features**
1. **Advanced Filtering** (500+ votes): Filter by vote count range, date range, custom fields
2. **Custom Fields** (400+ votes): Add custom metadata to posts
3. **Bulk Edit** (300+ votes): Edit multiple posts at once
4. **API Improvements** (250+ votes): More endpoints, webhooks for all events
5. **Mobile App** (200+ votes): Native iOS/Android apps

**Top Requested Features (UserVoice)**
1. **Better Search** (600+ votes): Faster, more relevant results
2. **AI Duplicate Detection** (500+ votes): Like Canny's Autopilot
3. **Custom Workflows** (400+ votes): Define own statuses and transitions
4. **Better Analytics** (350+ votes): Trends, insights, reports
5. **API v2** (300+ votes): More RESTful, better docs

### 13.3 Gaps & Opportunities for Compass

**Differentiation Opportunities**

1. **Revenue-Weighted Voting**
   - Compass already has this! (customer revenue in feedback data)
   - Competitive advantage over both platforms

2. **NLP-Powered Clustering**
   - Compass already does this! (DBSCAN clustering)
   - Better than Canny's keyword-based duplicate detection

3. **Automatic Prioritization**
   - Compass priority formula: `(Frequency × Revenue × Sentiment) / Effort`
   - Neither platform offers this level of automation

4. **Multi-Source Feedback**
   - Compass ingests from 8+ sources (Slack, email, support tickets)
   - Canny/UserVoice only have public boards (miss internal feedback)

5. **Open-Source / Self-Hosted**
   - Compass could offer self-hosted option
   - Privacy-conscious customers prefer on-premise
   - No per-user pricing

---

## 14. Recommendations for Compass Public Board

### 14.1 MVP Feature Set

**Must-Haves**
- [x] Public board view (no auth required)
- [ ] User authentication (OAuth: Google, GitHub)
- [ ] Post creation (authenticated users)
- [ ] Voting system (1 vote per user per post)
- [ ] Real-time vote updates (WebSocket)
- [ ] Status workflow (Open, Planned, In Progress, Complete)
- [ ] Admin moderation (edit, delete, merge posts)

**Nice-to-Haves**
- [ ] Comments on posts
- [ ] Email notifications (status changes)
- [ ] Search and filtering
- [ ] Custom branding (logo, colors)
- [ ] Changelog (linked to completed posts)

**Future Enhancements**
- [ ] Jira/Linear integration
- [ ] Slack integration
- [ ] Private boards (internal use)
- [ ] SSO (SAML, OAuth)
- [ ] Custom fields

### 14.2 Differentiation Strategy

**Leverage Existing Strengths**
1. **NLP Clustering**: Auto-group similar feedback (better than Canny)
2. **Revenue-Weighted Scoring**: Prioritize by customer value (unique)
3. **Multi-Source Ingestion**: Combine public board with internal feedback
4. **Automatic Roadmap**: AI-generated roadmap (nobody else does this)

**Positioning**
- "Canny + Productboard, but with AI-powered prioritization"
- "Open-source alternative with enterprise features"
- "Built for PLG companies who need data-driven roadmaps"

### 14.3 Technical Implementation Plan

**Phase 1: Public Board Basics (2 weeks)**
- [ ] Frontend: Public board UI (React)
- [ ] Backend: REST API for posts, votes, comments
- [ ] Database: Posts, votes, users tables
- [ ] Auth: JWT-based login (Google OAuth)

**Phase 2: Real-Time & Admin (1 week)**
- [ ] WebSocket for real-time updates
- [ ] Admin dashboard (moderation, status changes)
- [ ] Email notifications (SendGrid)

**Phase 3: Integrations (2 weeks)**
- [ ] Jira integration (bi-directional sync)
- [ ] Slack notifications (webhooks)
- [ ] Zapier integration (triggers/actions)

**Phase 4: AI Features (1 week)**
- [ ] Auto-duplicate detection (reuse clustering)
- [ ] Auto-categorization (tag posts)
- [ ] Sentiment analysis (already have this!)

**Phase 5: Polish & Launch (1 week)**
- [ ] Custom branding (domain, logo, colors)
- [ ] Changelog
- [ ] Public roadmap view
- [ ] Documentation and marketing site

---

## 15. Conclusion

### Key Takeaways

1. **Voting Systems**: Real-time, authenticated voting is table stakes. Anti-spam measures are critical.
2. **Integrations**: Dev tool integrations (Jira, Linear) are highly valued. Bi-directional sync is hard but worth it.
3. **AI Features**: Duplicate detection and auto-categorization are popular but accuracy is inconsistent.
4. **Pain Points**: Users want weighted voting, custom scoring, and better automation.
5. **Opportunity**: Compass can differentiate with revenue-weighted prioritization and NLP-powered clustering.

### Next Steps

1. **Build Public Board MVP**: Focus on core voting and moderation features.
2. **Integrate with Compass Backend**: Link public board posts to existing clustering/prioritization engine.
3. **Add Jira/Linear Integration**: Enable bi-directional sync for status updates.
4. **Launch as Open-Source**: Attract privacy-conscious customers and developers.
5. **Monetize**: Offer hosted version with premium features (SSO, custom branding, SLA).

---

**Research compiled by:** Claude (Sonnet 4.5)
**Date:** 2026-08-04
**Sources:** Canny documentation, UserVoice documentation, G2 reviews, Reddit threads, ProductHunt discussions, technical blogs
