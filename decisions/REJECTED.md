# Rejected Features - Not Building

**Last Updated:** 2026-08-04
**Product Decisions Agent**

---

## ❌ REJECTED for MVP

### 1. Automatic Sentiment Tagging (Numeric Scores)

**User Friendliness:** 3/10 ⚠️

**Reason:**
- PMs don't understand sentiment scores (-0.43 means what?)
- Creates confusion, not clarity
- "Is -0.2 bad or just slightly negative?"
- Numbers feel cold and technical

**User Feedback (Anticipated):**
- "What does this score mean?"
- "Why is this -0.8 and that -0.6? They both seem negative."
- "Can I just see happy, neutral, sad?"

**Better Alternative:**
- Use emojis: 😊 Positive, 😐 Neutral, 😞 Negative
- Show text labels: "Very Negative" → "Very Positive"
- Make it visual, not numeric
- If you must show score, add explanation tooltip

**Status:** ❌ REJECTED
**Consider for:** Never (emojis are better)

---

### 2. Automatic Tagging (AI-Generated Tags)

**User Friendliness:** 4/10 ⚠️

**Reason:**
- AI auto-tags are usually wrong
- Creates noise, not signal
- Users spend time removing bad tags
- False sense of intelligence

**Example Failures:**
- Feedback: "Love the new dashboard!" → Tagged: #bug #complaint
- Feedback: "Search is slow" → Tagged: #feature-request #positive
- Users lose trust in AI

**Better Alternative:**
- Manual tagging (user control)
- Suggested tags (user approves)
- Tag templates (common tags dropdown)
- Copy tags from similar feedback

**Status:** ❌ REJECTED
**Consider for:** Only with 95%+ accuracy (not soon)

---

### 3. Automatic Roadmap Generation (Zero Human Input)

**User Friendliness:** 2/10 ❌

**Reason:**
- PMs HATE when AI makes decisions for them
- Roadmap is strategic, requires judgment
- AI doesn't understand company priorities
- "Black box" decision-making kills trust

**User Reaction:**
- "Why is this feature #1? I disagree."
- "AI doesn't know our strategy."
- "I need to explain this to stakeholders, but I don't know why AI ranked it this way."

**Better Alternative:**
- AI-suggested roadmap (human approves)
- Show scoring logic (transparency)
- Let PM adjust priorities
- "AI copilot" not "AI autopilot"

**Status:** ❌ REJECTED (full auto)
**Approved:** AI-suggested with human approval (current design) ✅

---

### 4. Complex NLP Settings (Exposed to Users)

**User Friendliness:** 2/10 ❌

**Reason:**
- PMs are not data scientists
- "Adjust DBSCAN eps parameter (0.1-1.0)" = confusion
- "Min samples: 2-10" = what does that mean?
- Breaks "AI-native" promise (shouldn't be tuning ML)

**User Reaction:**
- "I don't know what eps means."
- "Just make it work. I don't want to configure this."
- "Why is this my problem?"

**Better Alternative:**
- Smart defaults (no configuration needed)
- Advanced settings buried in expert mode
- Or: Let users give feedback "Too many clusters" → AI adjusts
- Natural language controls, not technical knobs

**Status:** ❌ REJECTED (exposed settings)
**Approved:** Smart defaults only ✅

---

### 5. Multi-Modal Feedback Analysis (Audio, Video, Images)

**User Friendliness:** 6/10 (interesting but premature)

**Reason:**
- Cool technology, but not MVP-critical
- Adds massive complexity (audio transcription, image recognition)
- Most feedback is still text (Slack, email, tickets)
- Niche use case (< 10% of customers need this)

**Better Alternative:**
- Focus on text first (80% of use cases)
- Add audio/video in Month 9-12 (after product-market fit)
- Start with Loom video embed (link preview, not analysis)

**Status:** ⏸️ DEFERRED
**Reconsider:** Month 9+ (after PMF)

---

### 6. Predictive Churn Analysis

**User Friendliness:** 5/10 (advanced, not ready)

**Reason:**
- Requires months of historical data
- ML model needs training
- "This customer will churn in 30 days" = scary if wrong
- Liability if PM relies on bad prediction

**Better Alternative:**
- Start with simpler signals: "Customer stopped engaging"
- Flag customers with negative sentiment trends
- Show recent activity drop-offs
- Manual judgment, not AI prediction

**Status:** ⏸️ DEFERRED
**Reconsider:** Month 12+ (after we have data)

---

### 7. Session Replay Integration (Embedded Videos)

**User Friendliness:** 7/10 (nice-to-have, not must-have)

**Reason:**
- Requires integration with FullStory/LogRocket
- Adds complexity (video playback in UI)
- Most PMs don't use session replay
- Niche power user feature

**Better Alternative:**
- Link to session replay (external)
- Embed via iframe (simple)
- Partner integration (not built by us)

**Status:** ⏸️ DEFERRED
**Reconsider:** Month 9+ (partnerships)

---

## ⚠️ NEEDS REDESIGN (Not Ready Yet)

### 8. Advanced Roadmap View (Timeline, Dependencies, Capacity)

**User Friendliness:** 5/10 (too complex for MVP)

**Reason:**
- Tries to be Jira/Linear (we're not a project management tool)
- PMs already have tools for this
- Adds UI complexity
- 80% of users won't use it

**Better Alternative:**
- Simple ranked list (current design) ✅
- Export to Jira/Linear (integrate, don't replace)
- Focus on prioritization, not execution

**Status:** ⚠️ NEEDS SIMPLIFICATION
**Approved:** Simple list view only ✅

---

### 9. Advanced Sentiment Visualization (Emotion Wheels, Heatmaps)

**User Friendliness:** 4/10 (over-designed)

**Reason:**
- Looks cool in demos, confusing in practice
- "Emotion wheel" = what?
- Heatmaps = hard to interpret
- Data visualization for the sake of it

**Better Alternative:**
- Simple bar charts (Positive, Neutral, Negative)
- Trend lines over time (sentiment improving or worsening?)
- Clear, actionable insights

**Status:** ⚠️ NEEDS SIMPLIFICATION
**Approved:** Simple charts only ✅

---

## Summary: Why We Reject Features

### Rejection Criteria

A feature is rejected if it:
1. **Confuses users** (user friendliness < 5/10)
2. **Adds complexity without value** (nice-to-have, not must-have)
3. **Tries to do too much** (scope creep)
4. **Relies on unproven AI** (accuracy < 85%)
5. **Competes with existing tools** (Jira, Linear, Loom)
6. **Requires months of data** (not possible for MVP)

### Approval Criteria

A feature is approved if it:
1. **Solves real PM pain** (validated in research)
2. **Differentiated from competitors** (nobody else has it)
3. **User-friendly** (7/10+, no documentation needed)
4. **Feasible to build** (< 2 weeks)
5. **Timely** (market is ready now)

---

## Learning: What Good Products Don't Do

**Bad Product Thinking:**
- "Let's add every feature competitors have"
- "AI can do everything automatically"
- "More features = better product"
- "Tech is cool, users will figure it out"

**Good Product Thinking:**
- "What one problem do we solve 10x better?"
- "AI assists, human decides"
- "Fewer features, executed perfectly"
- "If users need docs, we failed"

---

**Next Review:** End of Month 3 (revisit deferred features)
