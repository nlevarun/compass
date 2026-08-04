# Public Board Demo Script (5 Minutes)

## Pre-Demo Setup (Do This First!)

```bash
# 1. Generate demo data
cd /home/wsl-user/compass/backend
python setup_demo_board.py

# 2. Start backend
python main.py

# 3. Start frontend (new terminal)
cd /home/wsl-user/compass/frontend
npm run dev

# 4. Open browser tabs
# Tab 1: http://localhost:5173/boards/compass-demo (public view)
# Tab 2: http://localhost:5173/boards/compass-demo/admin (admin view)
```

---

## Demo Script (5 Minutes)

### Slide 1: The Problem (30 seconds)

**Say:**
> "Companies pay $200-$600/month for tools like Canny to collect customer feedback.
> But they're missing a critical feature: revenue-weighted voting.
>
> Right now, a free user's vote counts the same as a $500k enterprise customer.
> That doesn't make sense for prioritization."

**Show:**
- Canny pricing page (screenshot or open in browser)
- Highlight: $200/mo for basic, $400/mo for growth

---

### Slide 2: The Solution (1 minute)

**Say:**
> "Compass has revenue-weighted voting built-in. Let me show you."

**Demo:**
1. Open public board: `http://localhost:5173/boards/compass-demo`
2. Point out the clean UI:
   - "This is our public feedback board - looks professional, right?"
   - "Users can submit feedback, vote, and comment"
3. Click on sort dropdown
4. Show "Most Votes" first:
   - "Here's regular voting - just counting votes"

---

### Slide 3: Revenue-Weighted Magic (2 minutes) 🌟

**This is the killer demo moment!**

**Say:**
> "Now watch this - I'm switching to revenue-weighted sorting."

**Demo:**
1. Change sort to "Revenue-Weighted"
2. Point out how the order changes:
   - "See how posts with enterprise customer votes jumped to the top?"
   - "This post has fewer total votes, but it has votes from $500k enterprise customers"
3. Hover over the revenue score badge:
   - "Revenue-Weighted Score shows the actual business impact"
   - "Enterprise votes = ~3x weight of free users"

**Say:**
> "This is how product teams SHOULD prioritize:
> - Free user vote = 1 point
> - $10k customer vote = ~2 points
> - $100k customer vote = ~3 points
>
> Only Compass has this."

**Show the math (if time):**
```
Example Post:
- 5 free users voted = 5 points
- 2 enterprise customers ($100k each) = ~6 points
- Total revenue-weighted score = 11 points

vs Regular Post:
- 10 free users = 10 votes
- But revenue score = only 10 points

The enterprise post wins in revenue-weighted view!
```

---

### Slide 4: Real-Time Demo (1 minute)

**Say:**
> "Let me show you another thing Canny can't do well: real-time updates."

**Demo:**
1. Enter your email: `demo@example.com`
2. Vote on a post
3. Show the instant update:
   - "Vote count updates immediately - WebSocket technology"
   - "No page refresh needed"
   - "Update latency: under 1 second"

**Optional (if you have two screens):**
- Open the board in two browser windows
- Vote in one, watch it update in the other
- "Multiple users see updates in real-time"

---

### Slide 5: Admin Dashboard (30 seconds)

**Say:**
> "And here's the admin view."

**Demo:**
1. Switch to admin tab: `http://localhost:5173/boards/compass-demo/admin`
2. Enter admin email: `demo@compass.app`
3. Quick tour:
   - Posts tab: "Change status to 'Planned' or 'In Progress'"
   - Analytics tab: "See top voters by revenue impact"
   - Settings tab: "Embed code for your website"

**Say:**
> "You can see which customers are most engaged by revenue."

---

### Slide 6: Wrap-Up (30 seconds)

**Say:**
> "So to recap - Compass gives you:
>
> ✅ Professional public feedback board
> ✅ Revenue-weighted voting (unique!)
> ✅ Real-time updates (<1 second)
> ✅ Full analytics by customer value
> ✅ Easy embedding
>
> Canny charges $200-$600/mo and doesn't have revenue weighting.
> We're starting at $0 for MVP, scaling based on usage.
>
> Questions?"

---

## Q&A Prep

### Expected Questions

**Q: How do you track customer revenue?**
> A: Three ways:
> 1. Manual entry in admin dashboard
> 2. API integration (when user votes, pass revenue value)
> 3. Auto-sync from Stripe/Salesforce (coming soon)

**Q: What if I don't have revenue data?**
> A: Falls back to regular voting (1 vote = 1 point). Revenue weighting is optional but recommended.

**Q: Can customers see the revenue-weighted scores?**
> A: Yes - it's transparent! They can see how votes are weighted. This encourages enterprises to engage more.

**Q: What about privacy? Does it show customer revenue?**
> A: No - only the weighted score is shown publicly. Actual revenue amounts are private in admin view.

**Q: How is this better than Canny?**
> A:
> 1. Revenue-weighted voting (they don't have this)
> 2. Real-time WebSocket updates (they're slower)
> 3. Lower cost (we're MVP, scaling pricing)
> 4. Full API access from day 1
> 5. Built for product teams who care about revenue impact

**Q: Can I try it now?**
> A: Yes! You can create a board in 2 minutes:
> `http://localhost:5173/boards/create`

---

## Demo Tips

### Do's:
- ✅ Practice the demo 2-3 times beforehand
- ✅ Have the browser tabs open and ready
- ✅ Use your mouse/cursor to point at specific UI elements
- ✅ Speak slowly and clearly when showing the revenue weighting
- ✅ Emphasize: "This is what Canny can't do"
- ✅ Show the instant WebSocket updates - very impressive!

### Don'ts:
- ❌ Don't skip the revenue-weighted sorting demo - it's the key differentiator
- ❌ Don't go too fast - let them absorb each feature
- ❌ Don't get bogged down in technical details (unless they ask)
- ❌ Don't apologize for MVP rough edges - focus on the value
- ❌ Don't compare on every feature - focus on revenue weighting

---

## Post-Demo Actions

After a successful demo:

1. **Send follow-up email** with:
   - Link to create their own board
   - This demo script
   - Pricing info (when ready)
   - Case study on revenue-weighted voting impact

2. **Get feedback**:
   - "What did you think of revenue-weighted voting?"
   - "Would this change how you prioritize features?"
   - "What else would you need to switch from Canny?"

3. **Schedule follow-up**:
   - "Can we set up a 30-minute call to discuss your specific needs?"

---

## One-Liner Pitch

**Use this when you have only 10 seconds:**

> "Compass is like Canny, but with revenue-weighted voting built-in.
> Your $100k enterprise customer's vote counts 3x more than a free user.
> That's how you should prioritize your roadmap."

---

## Backup Demo (If Live Demo Fails)

If the live demo isn't working:

1. **Show screenshots** from `PUBLIC_BOARD_TEST.md`
2. **Walk through the concept** with a whiteboard:
   - Draw the revenue weighting formula
   - Show example calculations
3. **Share screen recording** (record one beforehand!)
4. **Focus on the pitch**: "Even without the live demo, the concept is powerful"

---

## Success Metrics

After the demo, you should have:

- ✅ Clearly communicated the revenue-weighted voting advantage
- ✅ Shown 2-3 "wow" moments (real-time updates, score changes)
- ✅ Answered basic questions about implementation
- ✅ Generated interest in trying the product
- ✅ Scheduled a follow-up or got contact info

---

**Good luck with the demo! 🚀**

Remember: Revenue-weighted voting is your secret weapon. Make sure everyone understands why it's better.
