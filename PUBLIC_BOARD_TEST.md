# Public Feedback Board - Test Guide

## Quick Setup (2 minutes)

### 1. Generate Demo Data

```bash
cd /home/wsl-user/compass/backend
python setup_demo_board.py
```

This creates:
- A demo board at `http://localhost:5173/boards/compass-demo`
- 10 sample posts across different categories
- 50+ votes from enterprise and free users
- Sample comments
- Revenue-weighted scoring enabled

### 2. Start the Application

```bash
# Terminal 1: Backend
cd /home/wsl-user/compass/backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd /home/wsl-user/compass/frontend
npm run dev
```

### 3. Access the Demo Board

Open your browser to: `http://localhost:5173/boards/compass-demo`

---

## Testing Flow (10 minutes)

### Test 1: View Public Board (2 min)

**Steps:**
1. Visit `http://localhost:5173/boards/compass-demo`
2. Observe the board header with title and description
3. See the list of feedback posts with vote counts
4. Notice the sort dropdown (Most Votes, Revenue-Weighted, Recent, Trending)

**Expected:**
- Clean, professional UI like Canny
- Posts displayed with vote buttons, categories, and status badges
- Fast loading (<1 second)

---

### Test 2: Submit New Feedback (2 min)

**Steps:**
1. Click "Submit Feedback" button
2. Fill in:
   - Title: "Add export to PDF"
   - Description: "We need PDF export for reports"
   - Category: Feature Request
   - Your Name: (leave blank for anonymous)
3. Click Submit

**Expected:**
- Modal opens smoothly
- Form validates required fields
- Post appears instantly in the list after submission
- You should see a success indication

---

### Test 3: Vote on Posts (2 min)

**Steps:**
1. Enter your email in the email input box (e.g., `test@example.com`)
2. Click the upvote button on any post
3. Try voting again on the same post
4. Vote on 2-3 different posts

**Expected:**
- Vote count increments immediately (WebSocket update!)
- Button changes to "Voted" state
- Second vote attempt shows "already voted" error
- Vote count updates are instant (<1 second)

---

### Test 4: Revenue-Weighted Voting (3 min) 🌟

**This is the killer feature!**

**Steps:**
1. Click the sort dropdown
2. Select "Revenue-Weighted"
3. Compare the order with "Most Votes"
4. Look for posts with enterprise customer votes

**Expected:**
- Posts with enterprise votes rank higher in revenue-weighted view
- You'll see "Revenue-Weighted Score" badges on posts
- A post with 10 votes from enterprise customers beats a post with 20 votes from free users
- This is the feature that Canny doesn't have!

**Example:**
```
Regular Votes:
- Post A: 20 votes (all free users) = 20 points
- Post B: 10 votes (5 enterprise @ $100k each) = ~30 points

Revenue-Weighted:
Post B ranks higher! 🎯
```

---

### Test 5: Filtering and Sorting (1 min)

**Steps:**
1. Use the category filter dropdown
2. Select "Feature Requests"
3. Switch to "Bugs"
4. Try different sort orders

**Expected:**
- Filters work instantly
- Sorting updates immediately
- URL could update with filter params (nice to have)

---

### Test 6: Admin Dashboard (2 min)

**Steps:**
1. Visit `http://localhost:5173/boards/compass-demo/admin`
2. Enter admin email: `demo@compass.app`
3. Click "Posts" tab
4. Change status of a post from "Open" to "Planned"
5. Click "Analytics" tab
6. Click "Settings" tab

**Expected:**
- Admin dashboard loads with authentication
- Can change post status (dropdown)
- Analytics shows:
  - Total posts, votes, comments
  - Top posts by votes and revenue
  - Top voters by revenue impact
- Settings shows embed code and board info

---

## Advanced Testing

### Test 7: Real-Time Updates (WebSocket)

**Steps:**
1. Open two browser windows side-by-side
2. In window 1: View the board
3. In window 2: Vote on a post
4. Watch window 1 update in real-time

**Expected:**
- Vote count updates instantly in window 1
- No page refresh needed
- Update appears in <1 second

---

### Test 8: Create Your Own Board (3 min)

**Steps:**
1. Visit `http://localhost:5173/boards/create`
2. Fill in:
   - Organization: "My Test Company"
   - Title: "Product Feedback"
   - Description: "Share your ideas"
   - Theme Color: (pick a color)
   - Owner Email: your email
3. Click "Create Public Board"

**Expected:**
- Slug generated automatically: `my-test-company`
- Redirected to your new board
- Can submit feedback immediately
- Admin dashboard accessible with your email

---

### Test 9: Embed Widget (2 min)

**Steps:**
1. Go to admin dashboard
2. Click "Settings" tab
3. Copy the embed code
4. Create a test HTML file and paste the iframe code
5. Open the HTML file in browser

**Expected:**
- Embed code provided as `<iframe>` snippet
- Copy button works
- Board displays correctly when embedded
- Voting and posting works in embedded view

---

## Performance Benchmarks

Expected performance (on local dev):

| Metric | Target | Notes |
|--------|--------|-------|
| Board load | <500ms | Initial page load |
| Post creation | <200ms | From submit to visible |
| Vote action | <100ms | Click to UI update |
| WebSocket latency | <50ms | Vote update to other clients |
| Sort/filter | <50ms | Client-side only |
| Analytics load | <1s | Aggregated queries |

---

## Comparison: Compass vs Canny

| Feature | Canny | Compass |
|---------|-------|---------|
| Basic voting | ✅ | ✅ |
| Anonymous posts | ✅ | ✅ |
| Status tracking | ✅ | ✅ |
| Comments | ✅ | ✅ |
| **Revenue-weighted voting** | ❌ | ✅ 🌟 |
| Real-time updates (WebSocket) | ⚠️ Slow | ✅ <1s |
| Custom branding | ✅ $400/mo | ✅ Free |
| Analytics | ✅ Limited | ✅ Full |
| API access | ✅ $200/mo+ | ✅ Free |
| Pricing | $200-$600/mo | Free (MVP) |

---

## Known Issues / TODO

- [ ] Email validation could be stricter
- [ ] No email verification (users can vote multiple times with different emails)
- [ ] Comments don't have threading/replies yet
- [ ] No file attachments support
- [ ] Search functionality not implemented
- [ ] No spam protection (rate limiting needed)
- [ ] Revenue data must be set manually or via API (no automatic sync yet)
- [ ] No custom domain support yet (just slugs)

---

## Success Criteria

You should be able to:

✅ Create a public board in 2 minutes
✅ Share the link with anyone
✅ Let people submit and vote anonymously
✅ Show revenue-weighted scoring (UNIQUE!)
✅ Compare: "This is what Canny can't do"
✅ Embed widget on any website
✅ Demo in <5 minutes to impress people

---

## Next Steps

After testing:

1. **Share the demo** with potential users
2. **Get feedback** on the revenue-weighted voting feature
3. **Deploy to production** with real domain
4. **Add integrations** (sync customer revenue from Stripe, Salesforce)
5. **Marketing**: "Like Canny, but with revenue-weighted voting"

---

## Support

If you encounter issues:

1. Check backend logs: `tail -f backend/logs/app.log`
2. Check browser console for errors
3. Verify WebSocket connection in Network tab
4. Run database migrations: `python backend/migrate_db.py`
5. Reset demo data: `python backend/setup_demo_board.py`

---

**Enjoy testing the public feedback board! 🚀**

This is the feature that will make Compass stand out from Canny.
