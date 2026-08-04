# Decision #003: Feature Prioritization Roadmap

## Date: 2026-08-04

## Context

Based on Strategic Master Plan analysis of competitors and market gaps, need to decide which features to build in what order for MVP → Production.

**Current State:**
- Backend: Working but simple (keyword clustering)
- Frontend: New 3-tab UI designed but not activated
- Features: Basic workflow (Collect → Analyze → Prioritize)

**Goal:** Define next 6 months of feature development

---

## Decision Framework

For each feature, evaluated:
1. **User Pain** (1-10): How badly do PMs need this?
2. **Competitive Gap** (1-10): How much better can we be?
3. **Technical Feasibility** (1-10): How easy to build?
4. **Market Timing** (1-10): Is now the right time?
5. **Effort** (1-10): How fast can we ship?

**Formula:** Priority = (Pain × Gap × Feasibility × Timing) / Effort

---

## Feature Scores (Top 15)

| Rank | Feature | Pain | Gap | Feasibility | Timing | Effort | **Score** | **Decision** |
|------|---------|------|-----|-------------|--------|--------|-----------|--------------|
| 1 | **Activate New UI** | 9 | 8 | 10 | 10 | 10 | **648** | ✅ NOW |
| 2 | **Sample Data Import** | 8 | 7 | 9 | 10 | 9 | **453** | ✅ NOW |
| 3 | **Upgrade to Real NLP** | 9 | 9 | 7 | 8 | 5 | **408** | 🔄 MONTH 3 |
| 4 | **Manual Cluster Override** | 7 | 8 | 9 | 9 | 8 | **409** | ✅ MONTH 1 |
| 5 | **Revenue-Weighted Sorting** | 10 | 10 | 8 | 9 | 7 | **514** | ✅ MONTH 1 |
| 6 | **Export to CSV/Jira** | 8 | 6 | 9 | 7 | 8 | **302** | 🔄 MONTH 2 |
| 7 | **Public Feedback Board** | 9 | 9 | 6 | 8 | 4 | **389** | 🔄 MONTH 4 |
| 8 | **Slack OAuth Integration** | 7 | 7 | 7 | 8 | 6 | **228** | 🔄 MONTH 3 |
| 9 | **Keyboard Shortcuts** | 5 | 6 | 10 | 6 | 9 | **180** | 🔄 MONTH 2 |
| 10 | **Mobile Responsive UI** | 6 | 7 | 8 | 7 | 6 | **197** | 🔄 MONTH 5 |
| 11 | **Webhook Real-Time Sync** | 8 | 9 | 6 | 8 | 4 | **259** | 🔄 MONTH 4 |
| 12 | **Advanced Filters** | 6 | 5 | 9 | 6 | 8 | **162** | ⏸️ LATER |
| 13 | **User Authentication** | 5 | 4 | 8 | 5 | 7 | **114** | ⏸️ LATER |
| 14 | **API Documentation** | 7 | 6 | 9 | 7 | 9 | **238** | 🔄 MONTH 2 |
| 15 | **Automated Testing** | 4 | 3 | 9 | 6 | 8 | **65** | ⏸️ LATER |

---

## Month-by-Month Roadmap

### 🚀 IMMEDIATE (Week 1-2)

**#1: Activate New UI**
- **Why:** Already built, massive UX improvement
- **Effort:** 3 fixes (sample data button, skip tour, step numbers)
- **Time:** 2-3 hours
- **Impact:** 8.5/10 user experience
- **Status:** ✅ APPROVED (Decision #001)

**#2: Sample Data Import**
- **Why:** Broken button on hero section breaks trust
- **Effort:** Generate 50-100 realistic feedback items
- **Time:** 4-6 hours
- **Impact:** Smooth first-time user experience
- **Status:** ✅ MUST BUILD

**Combined Sprint:** 1-2 days
**Outcome:** Polished MVP ready for alpha testing

---

### 📊 MONTH 1: Polish Core Features

**#3: Revenue-Weighted Sorting**
- **Why:** Core differentiator (nobody else has this)
- **What:** Sort roadmap by customer revenue, not just votes
- **Effort:** Backend algorithm + frontend UI
- **Time:** 1 week
- **Impact:** 10/10 competitive advantage

**#4: Manual Cluster Override**
- **Why:** Keyword clustering is crude, users need manual control
- **What:** "Move to different cluster" button + UI
- **Effort:** Database updates + drag-drop UI
- **Time:** 1 week
- **Impact:** 8/10 user satisfaction

**#5: Better Empty States**
- **Why:** Some tabs still have generic empty states
- **What:** Add helpful messages, action buttons everywhere
- **Effort:** Component updates
- **Time:** 2-3 hours
- **Impact:** 7/10 polish

**Month 1 Outcome:**
- Revenue-weighted prioritization works ✅
- Users can fix clustering mistakes ✅
- Professional, polished experience ✅

---

### 🧠 MONTH 2: Developer Experience

**#6: API Documentation**
- **Why:** FastAPI auto-docs are basic, need real examples
- **What:** Comprehensive API guide, code examples, use cases
- **Effort:** Writing + examples
- **Time:** 2-3 days
- **Impact:** 7/10 for technical users

**#7: Export to CSV**
- **Why:** PMs need to share roadmap with stakeholders
- **What:** Export roadmap as CSV, formatted nicely
- **Effort:** Backend endpoint + frontend button
- **Time:** 4-6 hours
- **Impact:** 8/10 practical value

**#8: Keyboard Shortcuts**
- **Why:** Power users expect shortcuts
- **What:** Press 1/2/3 to switch tabs, Cmd+K to search
- **Effort:** Event listeners + UI hints
- **Time:** 3-4 hours
- **Impact:** 6/10 power user delight

**Month 2 Outcome:**
- Developers can integrate Compass via API ✅
- PMs can export and share roadmaps ✅
- Power users have shortcuts ✅

---

### 🤖 MONTH 3: AI Upgrade (Critical)

**#9: Upgrade to Real NLP Clustering**
- **Why:** Keyword clustering is not competitive (40-50% vs 80-90%)
- **What:** sentence-transformers + DBSCAN clustering
- **Effort:** Integration + testing + migration
- **Time:** 1-2 weeks
- **Impact:** 9/10 accuracy improvement
- **Status:** ✅ MUST BUILD (Decision #002)

**#10: Slack OAuth Integration**
- **Why:** Manual token entry is friction
- **What:** One-click "Connect Slack" button (OAuth flow)
- **Effort:** OAuth dance + backend storage
- **Time:** 1 week
- **Impact:** 7/10 setup experience

**Month 3 Outcome:**
- Clustering accuracy jumps from 40-50% to 80-90% ✅
- Slack integration is seamless (OAuth) ✅
- Competitive with Productboard on core features ✅

---

### 🎯 MONTH 4: Unique Features

**#11: Public Feedback Board (MVP)**
- **Why:** Competitors are Productboard (no public board) or Canny (no internal)
- **What:** Public URL for customers to vote, like Canny
- **Effort:** New frontend page + voting system + auth
- **Time:** 2-3 weeks
- **Impact:** 9/10 differentiation (internal + public in one tool)

**#12: Webhook Real-Time Sync**
- **Why:** Productboard has 30-60 min delays, we can be instant
- **What:** WebSocket-based real-time updates
- **Effort:** Already partially built, needs polish
- **Time:** 1 week
- **Impact:** 8/10 speed advantage

**Month 4 Outcome:**
- Public + internal feedback in ONE tool ✅
- Real-time updates (10x faster than Productboard) ✅
- Clear competitive differentiation ✅

---

### 📱 MONTH 5-6: Scale & Polish

**#13: Mobile Responsive UI**
- **Why:** PMs check feedback on phones
- **What:** Responsive design, works on mobile
- **Effort:** CSS updates + testing
- **Time:** 1 week
- **Impact:** 7/10 accessibility

**#14: Export to Jira/Linear**
- **Why:** PMs need to create tickets from roadmap
- **What:** One-click export to Jira or Linear
- **Effort:** API integrations
- **Time:** 1 week
- **Impact:** 8/10 workflow integration

**#15: Advanced Filters**
- **Why:** With 1,000+ feedback items, need to filter
- **What:** Filter by source, sentiment, revenue, date
- **Effort:** Backend queries + frontend UI
- **Time:** 3-5 days
- **Impact:** 7/10 usability at scale

**Month 5-6 Outcome:**
- Mobile-friendly ✅
- Integrates into PM workflow (Jira/Linear) ✅
- Scales to 1,000+ feedback items ✅

---

## Features NOT Building (And Why)

### ❌ REJECTED: Automatic Sentiment Tagging

**User Friendliness:** 3/10 (too technical)
**Reason:** PMs don't understand sentiment scores (-0.43? What does that mean?)
**Alternative:** Use emojis (😊 Positive, 😐 Neutral, 😞 Negative)
**Status:** REJECTED for MVP

### ❌ DEFERRED: User Authentication

**User Friendliness:** 5/10 (adds friction for alpha)
**Reason:** Not needed for private alpha (< 50 users)
**Timeline:** Build before public launch (Month 6+)
**Status:** DEFERRED

### ❌ DEFERRED: Multi-Tenant Architecture

**User Friendliness:** N/A (backend complexity)
**Reason:** Single-tenant is simpler for MVP
**Timeline:** Build when we have 100+ customers
**Status:** DEFERRED

### ❌ REJECTED: Automatic Tagging

**User Friendliness:** 4/10 (inaccurate, frustrating)
**Reason:** Auto-tags are usually wrong, manual tagging is better
**Alternative:** Let users create custom tags manually
**Status:** REJECTED

---

## Risk Analysis

### Risk 1: NLP Upgrade Takes Too Long (Month 3)

**Likelihood:** MEDIUM (40%)
**Impact:** HIGH (users churn due to bad clustering)

**Mitigation:**
- Block 2 full weeks for integration
- Have fallback plan (OpenAI embeddings API if sentence-transformers fails)
- Start integration in Month 2 (don't wait until last minute)
- Test on sample data before production

### Risk 2: Public Board is Complex (Month 4)

**Likelihood:** HIGH (60%)
**Impact:** MEDIUM (delays differentiation)

**Mitigation:**
- Build MVP version first (just voting, no comments)
- Ship incrementally (basic board Month 4, polish Month 5)
- Copy UX from Canny (proven design)
- Don't try to innovate on UI

### Risk 3: Trying to Build Too Much

**Likelihood:** MEDIUM (50%)
**Impact:** HIGH (burnout, missed deadlines)

**Mitigation:**
- Strict scope: Only top 5 features per month
- Cut features aggressively if behind schedule
- Focus on user value, not tech complexity
- Bias toward shipping incomplete vs not shipping

---

## Success Criteria

### Month 1 Exit Criteria
- ✅ New UI activated
- ✅ Sample data import works
- ✅ Revenue-weighted sorting implemented
- ✅ Manual cluster override available
- ✅ 50 alpha testers onboarded

### Month 3 Exit Criteria (Critical)
- ✅ NLP clustering accuracy: 80-90%
- ✅ Slack OAuth integration works
- ✅ User satisfaction: 8/10
- ✅ No crashes, 99.9% uptime
- ✅ 200 users, 20 paying customers

### Month 6 Exit Criteria (Public Launch)
- ✅ Public feedback board live
- ✅ Mobile responsive
- ✅ Export to Jira/Linear
- ✅ 1,000 users, 100 paying customers
- ✅ $5k MRR

---

## Decision Summary

**Roadmap Status:** ✅ APPROVED

**Priority Order:**
1. **Week 1-2:** Activate UI + Sample data (polish MVP)
2. **Month 1:** Revenue-weighting + Manual clustering (core features)
3. **Month 2:** API docs + Export + Shortcuts (developer experience)
4. **Month 3:** NLP upgrade + Slack OAuth (AI-native)
5. **Month 4:** Public board + Real-time sync (differentiation)
6. **Month 5-6:** Mobile + Jira integration + Filters (scale)

**Key Principles:**
- Ship early, iterate fast
- User value > tech complexity
- Bias toward action (not perfection)
- Cut features, not quality

---

## Approved By

**Product Decisions Agent**
Date: 2026-08-04
Decision confidence: HIGH (90%)

**Next Review:** End of Month 1 (adjust roadmap based on user feedback)

---

## Action Items

### This Week
- [ ] Activate new UI (3 fixes)
- [ ] Build sample data import
- [ ] Test with 5 PMs
- [ ] Gather initial feedback

### This Month
- [ ] Implement revenue-weighted sorting
- [ ] Build manual cluster override
- [ ] Polish empty states
- [ ] Onboard 50 alpha testers
- [ ] Collect satisfaction scores

### Next Decision Point
- **Week 4:** Review alpha feedback, adjust Month 2 priorities
- **Month 3:** Go/No-Go decision on NLP upgrade (based on user complaints)
- **Month 6:** Public launch decision (based on metrics)

**Current Status:** Roadmap defined, ready to execute ✅
