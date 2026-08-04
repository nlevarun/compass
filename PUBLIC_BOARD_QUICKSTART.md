# Public Feedback Board - Quick Start (5 Minutes)

## TL;DR

```bash
# 1. Install dependencies
cd /home/wsl-user/compass/frontend
npm install react-router-dom@6.22.0

# 2. Update frontend
cd src
mv App.jsx App.old.jsx
mv App.new.jsx App.jsx

# 3. Initialize database (if needed)
cd /home/wsl-user/compass/backend
source venv/bin/activate
python database.py

# 4. Generate demo data
python setup_demo_board.py

# 5. Start backend (Terminal 1)
python main.py

# 6. Start frontend (Terminal 2)
cd ../frontend
npm run dev

# 7. Visit demo board
# Open: http://localhost:5173/boards/compass-demo
```

---

## What You'll See

### Public Board
- URL: `http://localhost:5173/boards/compass-demo`
- 10 sample feedback posts
- Vote buttons with instant updates
- Sort by: Most Votes, **Revenue-Weighted** (key feature!), Recent, Trending
- Submit new feedback button

### Admin Dashboard
- URL: `http://localhost:5173/boards/compass-demo/admin`
- Admin Email: `demo@compass.app`
- Manage post status (open, planned, in-progress, completed, closed)
- View analytics (top posts, top voters by revenue)
- Get embed code

---

## Key Features to Demo

### 1. Revenue-Weighted Voting (THE KILLER FEATURE!)

**Regular Voting:**
```
Post A: 20 votes (all free users) = 20 points
Post B: 10 votes (5 enterprise @ $100k) = ~30 points

In "Most Votes" view: Post A wins
In "Revenue-Weighted" view: Post B wins! 🎯
```

**Try it:**
1. Visit the board
2. Click sort dropdown
3. Switch between "Most Votes" and "Revenue-Weighted"
4. See how enterprise feedback bubbles to the top

### 2. Real-Time Updates (WebSocket)

**Try it:**
1. Open two browser windows side-by-side
2. Vote in one window
3. Watch the other window update instantly (<1 second)
4. No refresh needed!

### 3. Public Feedback Submission

**Try it:**
1. Click "Submit Feedback"
2. Fill in: Title, Description, Category
3. Submit (anonymous or with name)
4. Post appears immediately in the list

---

## One-Minute Pitch

> "Compass is like Canny, but with revenue-weighted voting.
>
> Canny charges $200-$600/month and treats all votes equally.
> We prioritize by customer value: enterprise votes count 3x more.
>
> That's how you should prioritize your roadmap."

---

## Create Your Own Board (2 minutes)

```bash
# Visit
http://localhost:5173/boards/create

# Fill in:
- Organization: "Your Company"
- Title: "Product Feedback"
- Theme Color: (pick your brand color)
- Owner Email: your@email.com

# Click "Create Public Board"
# Share the URL with your team!
```

---

## Files Created

```
✅ backend/models.py              - Added 4 new tables
✅ backend/public_board_api.py    - 15+ API endpoints
✅ backend/setup_demo_board.py    - Demo data generator
✅ frontend/src/components/PublicBoard.jsx    - Public view
✅ frontend/src/components/BoardCreator.jsx   - Create board
✅ frontend/src/components/BoardAdmin.jsx     - Admin dashboard
✅ PUBLIC_BOARD_TEST.md           - Testing guide
✅ DEMO_PUBLIC_BOARD.md           - Demo script
✅ PUBLIC_BOARD_SETUP.md          - Full setup guide
✅ PUBLIC_BOARD_QUICKSTART.md     - This file
```

---

## Common Issues

### "Module not found: react-router-dom"
```bash
cd /home/wsl-user/compass/frontend
npm install react-router-dom@6.22.0
```

### "Table 'public_boards' doesn't exist"
```bash
cd /home/wsl-user/compass/backend
python database.py
```

### "Board not found"
```bash
# Generate demo data
python setup_demo_board.py
```

---

## Next Steps

1. ✅ **Test**: Follow `PUBLIC_BOARD_TEST.md`
2. ✅ **Demo**: Use `DEMO_PUBLIC_BOARD.md` for presentations
3. ✅ **Deploy**: Follow `PUBLIC_BOARD_SETUP.md` for production
4. ✅ **Market**: Position as "Canny alternative with revenue-weighted voting"

---

## Success Metrics

After setup, you should be able to:

- ✅ Create a public board in 2 minutes
- ✅ Share the link with anyone
- ✅ Show revenue-weighted voting in action
- ✅ Vote and see instant updates (<1 second)
- ✅ Access admin dashboard for moderation
- ✅ Get embed code for your website
- ✅ Demo in <5 minutes to impress people

---

**That's it! You're ready to compete with Canny! 🚀**

Questions? Check the full guides:
- Testing: `PUBLIC_BOARD_TEST.md`
- Demo: `DEMO_PUBLIC_BOARD.md`
- Setup: `PUBLIC_BOARD_SETUP.md`
