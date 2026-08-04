# COMPASS: ONE-PAGE STRATEGIC SUMMARY

**Date:** 2026-08-04 | **Status:** READY TO EXECUTE

---

## THE OPPORTUNITY

**Market Size:** $500M+ feedback management market, growing 25%/year
**Target:** 130,000 product managers at SaaS startups/scale-ups (underserved)
**Problem:** Existing tools are 3-10x too expensive, 60-min slow, fragmented

**Our Solution:** AI-native platform combining internal feedback + public boards with revenue-weighted prioritization

---

## COMPETITIVE ADVANTAGES (Why We Win)

| Competitor | Weakness | Compass Advantage |
|------------|----------|-------------------|
| **Productboard** | $2,400/year min, 60-min delays, no public board | **$49/mo, real-time, public + internal** |
| **Pendo** | $20k/year, analytics-first (not feedback-first) | **$199/mo, feedback-native, simpler** |
| **Canny** | Public only, no revenue weighting, basic AI | **Public + internal, revenue-weighted, advanced NLP** |
| **ALL** | No MCP, no self-hosted, closed-source | **MCP-native, open-source, community moat** |

**Unique Capabilities (Nobody Else Has):**
1. Revenue-weighted voting (auto-weight by customer ARR)
2. MCP connector framework (community extensibility)
3. Public + internal in one platform (not 2 tools)
4. Open-source self-hosted option (data ownership)
5. Real-time collaboration (Figma-like for PMs)

---

## 12-MONTH ROADMAP

**Q1 (Months 1-3): FOUNDATION**
- Build public feedback board (voting, commenting, moderation)
- Real-time WebSocket updates
- Jira/Linear bi-directional sync
- **Goal:** 50 beta customers, 10 paying ($500 MRR)

**Q2 (Months 4-6): DIFFERENTIATION**
- MCP connector framework (3 connectors)
- GPT-4 AI summarization
- Semantic search (embeddings)
- ProductHunt launch
- **Goal:** 200 customers, 50 paying ($5k MRR)

**Q3 (Months 7-9): SCALE**
- Mobile PWA (responsive, offline)
- Self-hosted Docker/K8s deployment
- White-label option
- Advanced analytics
- **Goal:** 500 customers, 150 paying ($20k MRR)

**Q4 (Months 10-12): ECOSYSTEM**
- MCP connector marketplace
- Enterprise SSO (SAML, Okta)
- Predictive churn alerts
- Native mobile apps
- **Goal:** 1,000 customers, 300 paying ($45k MRR)

---

## PRICING STRATEGY

| Plan | Price | Target | Savings vs Productboard |
|------|-------|--------|------------------------|
| **Open Source** | $0 | Developers, privacy-focused | Self-hosted, unlimited |
| **Starter** | $49/mo | Solo PMs, small teams | **76% cheaper** ($2,400 → $588/year) |
| **Pro** | $199/mo | Growing teams (5-20 PMs) | **67% cheaper** ($7,200 → $2,388/year) |
| **Enterprise** | $499/mo | Large companies (20+ PMs) | **88% cheaper** ($20k → $6k/year) |

---

## FINANCIAL PROJECTIONS (Conservative)

**Year 1:**
- 180 paying customers
- $35k MRR ($420k ARR)
- Team: 2-3 engineers
- Costs: $380k
- **Status:** Pre-revenue to break-even path

**Year 2:**
- 1,200 paying customers (6.7x growth)
- $240k MRR ($2.88M ARR)
- Team: 5-8 people
- **Status:** Break-even, profitable

**Year 3:**
- 3,600 paying customers (3x growth)
- $720k MRR ($8.64M ARR)
- Team: 12-20 people
- **Status:** Market leader (SMB), 30%+ margins

**5-Year Vision:** $36M ARR, 15,000 customers, #1 feedback platform for startups/scale-ups

---

## GO-TO-MARKET

**Distribution:** Product-Led Growth (Not Enterprise Sales Year 1)

**Channels:**
- **Community (40%):** GitHub, HackerNews, Reddit, ProductHunt
- **Content (30%):** SEO ("Productboard alternative"), comparison guides
- **Product (20%):** Free tier, public boards (viral), word-of-mouth
- **Partnerships (10%):** Slack/Linear/Jira app stores

**Launch Sequence:**
- Month 3: Private alpha (20 PMs)
- Month 4: Public beta (HackerNews "Show HN")
- Month 5: ProductHunt (#1 Product of the Day goal)
- Month 6: Enable paid plans (10-15% conversion)

---

## RISKS & MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Productboard copies features | HIGH | MEDIUM | Move faster, build community moat, 2-3 features ahead |
| Can't get users to switch | MEDIUM | HIGH | One-click migration, free service, dual-run period, ROI calc |
| Technical complexity | MEDIUM | HIGH | MVP first, proven stack (Supabase), cut scope |
| Pricing too low | LOW | HIGH | Monitor CAC/LTV, adjust every 6 months, upsell |
| MCP doesn't gain traction | MEDIUM | LOW | Build REST APIs too, MCP is bonus not core |

---

## SUCCESS METRICS

**Northstar Metric:** Weekly revenue-weighted roadmap generations

**Key Targets (Month 12):**
- 2,000 total users (1,700 free + 300 paying)
- $45k MRR ($540k ARR)
- 12% free-to-paid conversion
- 4% monthly churn (annual retention: 60%)
- NPS: 40+ (good, improving)
- 500 roadmap generations/week

**Unit Economics:**
- CAC: $300 (blended across channels)
- LTV: $4,776 (24-month avg lifetime × $199 MRR)
- LTV/CAC: 15.9x (target 3x+)
- Payback: 1.5 months (target < 12 months)

---

## INVESTMENT REQUIRED

**MVP (Months 1-3):** $50k (2 developers, part-time or contract)

**Year 1 Total:** $380k
- Engineering: $300k (2-3 FTE)
- Infrastructure: $24k (Vercel, Supabase, OpenAI)
- Marketing: $36k (content, ads, tools)
- Operations: $20k (legal, accounting, tools)

**Funding Path:**
- **Option A (Recommended):** Bootstrap to $30k MRR (Month 18-20), then decide
- **Option B:** Raise $500k-1M seed after MVP + 100 customers (Month 6)

**Break-Even:** Month 18-20 at $32k MRR (160 customers @ $199/mo)

---

## NEXT STEPS (THIS WEEK)

**Validation:**
- [ ] Reddit post: "Building revenue-weighted prioritization - would you use this?"
- [ ] Interview 20 PMs (10 Productboard, 10 Canny users)
- [ ] Survey: How many want self-hosted? (data ownership demand)

**Technical:**
- [ ] Spike: WebSocket real-time (Supabase POC)
- [ ] Spike: Public board schema (posts/votes/comments)
- [ ] Spike: OAuth flow (Google/GitHub)

**Business:**
- [ ] Finalize pricing (validate tiers)
- [ ] Financial model (3-year projections)
- [ ] Funding decision (bootstrap vs seed)

---

## THE DECISION

**Question:** Are we building this?

**If YES:**
- Code next week
- Alpha Month 3
- Launch Month 5
- $1M ARR Month 18

**If NO:**
- Someone else will
- Market opportunity wasted
- Productboard stays vulnerable

---

## WHY THIS WILL WORK

1. **Real Pain:** PMs drowning in feedback (validated 500+ reviews)
2. **Unfair Advantages:** Revenue-weighting, MCP, open-source, real-time (nobody has all 4)
3. **Wedge Strategy:** Start SMB (underserved), expand upmarket
4. **Perfect Timing:** MCP NOW, AI-native NOW, real-time NOW, PLG NOW
5. **Can Execute:** Small team, modern stack, bootstrap-friendly, defensible moats

---

**THE VISION:**

Not just a feedback tool.

**The operating system for product roadmaps.**

Aggregate everywhere → Understand (NLP) → Prioritize (revenue-weighted) → Roadmap (AI copilot) → Execute (Jira/Linear) → Close loop

All in one platform. Real-time. Affordable. Open-source.

---

**STATUS: READY TO BUILD**

**Let's go. The market is waiting.**

---

*Full Strategic Master Plan: `/home/wsl-user/compass/STRATEGIC_MASTER_PLAN.md` (30 pages)*
*Research Foundation: 300+ pages across Pendo, Productboard, Canny, Dovetail, MCP analysis*
